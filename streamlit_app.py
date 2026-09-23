import io
import os

import streamlit as st

from PIL import Image
import cv2
import pandas as pd
import numpy as np


from streamlit_option_menu import option_menu

import Vessel as vessel
import Cornea as cornea
import Quantif as quantif

import utils.cornea.utils_fct as fct

import zipfile

def reshape_morpho(morpho_info, parts):
    # Maps a metric's suffix to its category label
    CATEGORY_MAP = {
        "lenght_": "Vessel Length",
        "dia_": "Vessel Diameter",
        "tor_": "Tortuosity",
        "junction": "Junctions/Endpoints",
        "endpoint": "Junctions/Endpoints",
        "percent_vessel": "Vessel Density (%)",
    }

    def categorize(metric_name):
        for prefix, category in CATEGORY_MAP.items():
            if metric_name.startswith(prefix):
                return category
        return "Other"

    rows = {}
    for part in parts:
        prefix = part + "_"
        row = {}
        for key, value in morpho_info.items():
            if key.startswith(prefix):
                metric_name = key[len(prefix):]  # e.g. "lenght_min"
                category = categorize(metric_name)
                row[(category, metric_name)] = value
        rows[part] = row

    df = pd.DataFrame.from_dict(rows, orient="index")
    df.columns = pd.MultiIndex.from_tuples(df.columns, names=["Category", "Metric"])
    df.index.name = "part"

    # Optional: sort columns so categories are grouped together
    df = df.sort_index(axis=1, level=0)

    return df

def make_overlay(original_img, cornea_mask, vessel_mask,
                  cornea_color=(255, 255, 0), vessel_color=(255, 0, 0),
                  cornea_alpha=0.10, vessel_alpha=0.25):
    """
    original_img : PIL.Image (RGB)
    cornea_mask  : PIL.Image or np.ndarray, binary/grayscale mask (white = cornea)
    vessel_mask  : PIL.Image or np.ndarray, binary/grayscale mask (white = vessel)
    """
    orig = original_img.convert("RGB")
    size = orig.size  # (width, height)

    def to_bool_mask(mask):
        if not isinstance(mask, Image.Image):
            mask = Image.fromarray(mask)
        mask = mask.convert("L").resize(size)
        return np.array(mask) > 127

    orig_arr = np.array(orig).astype(np.float32)
    cornea_bool = to_bool_mask(cornea_mask)
    vessel_bool = to_bool_mask(vessel_mask)

    result = orig_arr.copy()

    for c in range(3):
        result[..., c] = np.where(
            cornea_bool,
            result[..., c] * (1 - cornea_alpha) + cornea_color[c] * cornea_alpha,
            result[..., c],
        )
        result[..., c] = np.where(
            vessel_bool,
            result[..., c] * (1 - vessel_alpha) + vessel_color[c] * vessel_alpha,
            result[..., c],
        )

    return Image.fromarray(result.astype(np.uint8))

USE_MODEL = "Use the model"
USE_MANUAL = "Upload my own mask"
USE_IN_MEMORY = "Already in memory"

st.set_page_config(page_title="Slit Lamp Vessel/Cornea Segmentation", layout="wide")

st.title("Cornea neocorneavascularisation segmentation and morpho analysis")

st.warning(
    "This is a research tool under development, not to be used for patient care.",
    icon="⚠️",
)

st.caption("Please only use cornea slit-lamp images with a .jpg or .png format. \n "
          " We proposed two versions : \n "
          "- one where the user can add their one segmentatiom or use our model for each images \n"
          "- The second option, it's a fully automated versiom the user can add all their images and the segmentations and quantifications is automatically done. \n")

# -------------------------------------------------
# Session State Initialization
# -------------------------------------------------
if "images" not in st.session_state:
    st.session_state.images = {}
if "segmentations" not in st.session_state:
    st.session_state.segmentations = {}
if "page" not in st.session_state:
    st.session_state.page = "Main"
if "selected_image_key" not in st.session_state:
    st.session_state.selected_image_key = None

if "cornea_done" not in st.session_state:
    st.session_state.cornea_done = False


# # -------------------------------------------------
# # Navigation
# # -------------------------------------------------

st.sidebar.header("Image Selection")
st.sidebar.caption("Here, all the session images \n"
"If you close the app every results will be erased")

selectable_keys = [k for k in st.session_state.images if not k.endswith("_or")]

selected_image_key = None
selected_image = None

if selectable_keys:
    selected_image_key = st.sidebar.radio(
        "Select an image:",
        selectable_keys,
        key="image_select",
    )
    selected_image = st.session_state.images.get(selected_image_key)
    st.session_state.selected_image_key = selected_image_key
    #st.rerun() 


tab_single, tab_batch = st.tabs(["Single image", "Batch processing"])

with tab_single:
    st.caption("Upload one or a batch of images : \n"
               "For each images, please enter if you want to use the proposed segmentation or to use another segmentation.")
    uploaded_files = st.file_uploader(
        "Upload images",
        accept_multiple_files=True,
        type=["jpg", "jpeg", "png"],
        key="uploader_single"
    )

    if uploaded_files:
        new_files_added = False
        for file in uploaded_files:
            if file.name not in st.session_state.images:
                image_bytes = file.read()
                try:
                    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                    st.session_state.images[file.name] = image_bytes
                    st.session_state.images[file.name + "_or"] = img
                    new_files_added = True
                except Exception as e:
                    st.error(f"Error loading {file.name}: {e}")

        if new_files_added:
            st.session_state.cornea_done = False
            st.rerun() 

                
        col_c, col_v = st.columns(2)
        with col_v:
            if selected_image_key + "_mask" in st.session_state.segmentations and selected_image_key + "_cornea" in st.session_state.segmentations : 
                
                vessel_choice = st.radio("Vessels:", [USE_MODEL, USE_MANUAL, USE_IN_MEMORY], key="vessel_choice")
                manual_vessel_file = None
                
                if vessel_choice == USE_MANUAL:
                    manual_vessel_file = st.file_uploader(
                        "Manual vessel mask", type=["jpg", "jpeg", "png"], key="manual_vessel")
            else :
                
                vessel_choice = st.radio("Vessels:", [USE_MODEL, USE_MANUAL], key="vessel_choice")
                manual_vessel_file = None
                
                if vessel_choice == USE_MANUAL:
                    manual_vessel_file = st.file_uploader(
                        "Manual vessel mask", type=["jpg", "jpeg", "png"], key="manual_vessel")
                
                    
        with col_c:
            
            cornea_choice = st.radio("Cornea:", [USE_MODEL, USE_MANUAL], key="cornea_choice")
            manual_cornea_file = None
            if cornea_choice == USE_MANUAL:
                manual_cornea_file = st.file_uploader(
                    "Manual cornea mask", type=["jpg", "jpeg", "png"], key="manual_cornea"
                )

        needs_both = (vessel_choice == USE_MODEL) and (cornea_choice == USE_MODEL)

        needs_vessel = (vessel_choice == USE_MODEL) and (cornea_choice == USE_MANUAL)

        if needs_both:
            run = st.button("Run segmentation", type="primary")
            
            if run:
                try:
                    mask, cornea_seg = cornea.run(selected_image_key)   
                    
                    st.session_state.segmentations[selected_image_key + "_mask"] = mask
                    st.session_state.segmentations[selected_image_key + "_cornea"] = cornea_seg
                    st.session_state.cornea_done = True

                    if selected_image_key and selected_image_key + "_mask" in st.session_state.segmentations:
                        vessel_seg = vessel.run(selected_image_key)	
                        st.session_state.segmentations[selected_image_key + "_vessel"] = vessel_seg
                        st.rerun()
                        
                except Exception as e:      
                    st.error(f"Erreur : {e}")

        if needs_vessel :
            run = st.button("Run segmentation", type="primary")
            
            if run:
                if manual_cornea_file :
                    image_bytes = manual_cornea_file.read()
                    
                    try:
                        mask = Image.open(io.BytesIO(image_bytes)).convert("L")
                        st.session_state.segmentations[selected_image_key + "_mask"] = mask

                        st.write(mask.size)
                        np_mask = np.array(mask)#.astype(np.uint8)
                        np_or = np.array(st.session_state.images[selected_image_key + "_or"]).astype(np.uint8)
                        
                        st.session_state.segmentations[selected_image_key + "_cornea"] = Image.fromarray(fct.Cornea_Crop(np_or,np_mask))
                        st.session_state.cornea_done = True
    
                        if selected_image_key and selected_image_key + "_mask" in st.session_state.segmentations:
                            vessel_seg = vessel.run(selected_image_key)	
                            st.session_state.segmentations[selected_image_key + "_vessel"] = vessel_seg
                            st.rerun()
                            
                    except Exception as e:      
                        st.error(f"Erreur : {e}")

        col_0, col_1 = st.columns(2)
        with col_0:
            try : 
                st.image(st.session_state.images[selected_image_key + "_or"], caption = 'Original Image') 
                
            except Exception as e:      
                st.write(f"Misssing Original")

        with col_1:
            try : 
                overlay_img = make_overlay(
                            st.session_state.images[selected_image_key + "_or"],
                            st.session_state.segmentations[selected_image_key + "_mask"],
                            st.session_state.segmentations[selected_image_key + "_vessel"],
                        )
                st.image(overlay_img, caption="Cornea (yellow) + Vessel (red) overlay")

            except Exception as e:
                st.write("Missing segmentation(s) for overlay")

        try : 
            vessel_key = selected_image_key + "_vessel"
            mask_key = selected_image_key + "_mask"

            col_0, col_1, col_2 = st.columns(3)
            with col_0:
                try : 

                    st.image(st.session_state.segmentations[selected_image_key + "_cornea"], caption = 'Cornea')

                    cornea_arr = np.array(st.session_state.segmentations[selected_image_key + "_cornea"])
                    success, encoded_cornea = cv2.imencode(".png", cornea_arr)
                    
                    st.download_button(
                        label="Download Cornea",
                        data=encoded_cornea.tobytes(),
                        file_name="mask_" + selected_image_key + ".png",
                        mime="image/png",
                    )
                    
                except Exception as e:      
                    st.write(f"Misssing Mask")

            with col_1:
                try : 
                    st.image(st.session_state.segmentations[selected_image_key + "_mask"], caption = 'Mask') 

                    mask_arr = np.array(st.session_state.segmentations[selected_image_key + "_mask"])
                    success, encoded_mask = cv2.imencode(".png", mask_arr)
                    
                    st.download_button(
                        label="Download Mask",
                        data=encoded_mask.tobytes(),
                        file_name="mask_" + selected_image_key + ".png",
                        mime="image/png",
                    )
                    
                except Exception as e:      
                    st.write(f"Misssing Cornea")

            with col_2:
                try :          
                    st.image(st.session_state.segmentations[selected_image_key + "_vessel"], caption = 'Vessel')

                    vessel_arr = np.array(st.session_state.segmentations[selected_image_key + "_vessel"])
                    success, encoded_vessel = cv2.imencode(".png", vessel_arr)
                    
                    st.download_button(
                        label="Download Vessel",
                        data=encoded_vessel.tobytes(),
                        file_name="mask_" + selected_image_key + ".png",
                        mime="image/png",
                    )

                except Exception as e:      
                    st.write(f"Misssing Vessl")

            if vessel_key in st.session_state.segmentations or mask_key in st.session_state.segmentations:
                run_quant = st.button("Run Quantification", type="primary")

                if run_quant:

                    try : 

                        morpho, composite  = quantif.run(selected_image_key)   
                        st.write("Quantification done!")
                        parts = ['eyes', 'middle', 'nasal', 'bottom', 'temporal', 'top']
                        df_morpho= reshape_morpho(morpho, parts)

                        st.session_state.segmentations[selected_image_key + "_morpho"] = df_morpho
                        st.session_state.segmentations[selected_image_key + "_composite_graph"] = composite

                    except Exception as e :
                        st.error(f"Something went wrong: {e}")
                        st.exception(e) 

            try :
                st.image(st.session_state.segmentations[selected_image_key + "_composite_graph"], caption = 'Quadrant and graph')
                st.dataframe(st.session_state.segmentations[selected_image_key + "_morpho"])
        

            except Exception as e:      
                st.write(f"Misssing morphology analyse")                

        except Exception as e :
            st.error(f"Something went wrong: {e}")
            st.exception(e)  

with tab_batch:
    st.caption("Upload one or a batch of images \n "
               "The default segmentation will be used for every images.\n "
               "At the end of the operations, you will be able to download the results")

    uploaded_batch = st.file_uploader(
        "Upload images",
        accept_multiple_files=True,
        type=["jpg", "jpeg", "png"],
        key="uploader_batch",
    )

    if uploaded_batch:
        # Load new files into session_state.images (same pattern as tab_single)
        batch_keys = []
        for file in uploaded_batch:
            if file.name not in st.session_state.images:
                image_bytes = file.read()
                try:
                    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                    st.session_state.images[file.name] = image_bytes
                    st.session_state.images[file.name + "_or"] = img
                except Exception as e:
                    st.error(f"Error loading {file.name}: {e}")
            batch_keys.append(file.name)

        run_batch = st.button("Run batch segmentation", type="primary", key="run_batch_button")

        if run_batch:
            progress = st.progress(0, text="Starting batch segmentation...")
            errors = []

            for i, key in enumerate(batch_keys):
                progress.progress(
                    (i) / len(batch_keys),
                    text=f"Processing {key} ({i+1}/{len(batch_keys)})",
                )
                try:
                    mask, cornea_seg = cornea.run(key)
                    st.session_state.segmentations[key + "_mask"] = mask
                    st.session_state.segmentations[key + "_cornea"] = cornea_seg

                    vessel_seg = vessel.run(key)
                    st.session_state.segmentations[key + "_vessel"] = vessel_seg

                except Exception as e:
                    errors.append((key, str(e)))

            progress.progress(1.0, text="Batch segmentation done!")

            if errors:
                st.warning(f"{len(errors)} image(s) failed:")
                for key, err in errors:
                    st.write(f"- {key}: {err}")
            else:
                st.success(f"All {len(batch_keys)} images processed successfully!")

            st.session_state["batch_done"] = True
            st.session_state["batch_keys"] = batch_keys


        if st.session_state.get("batch_done") and st.session_state.get("batch_keys"):

            def build_zip(keys):
                buffer = io.BytesIO()
                with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                    for key in keys:
                        for suffix in ["_mask", "_cornea", "_vessel"]:
                            seg_key = key + suffix
                            if seg_key in st.session_state.segmentations:
                                img = st.session_state.segmentations[seg_key]
                                arr = np.array(img)
                                success, encoded = cv2.imencode(".png")
                                if success:
                                    filename = f"{os.path.splitext(key)[0]}{suffix}.png"
                                    zf.writestr(filename, encoded.tobytes())
                buffer.seek(0)
                return buffer

            zip_buffer = build_zip(st.session_state["batch_keys"])

            st.download_button(
                label="Download all results (ZIP)",
                data=zip_buffer,
                file_name="batch_segmentation_results.zip",
                mime="application/zip",
                key="download_batch_zip",
            )

