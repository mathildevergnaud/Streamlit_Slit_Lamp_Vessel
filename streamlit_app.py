import io

import streamlit as st
from PIL import Image
from streamlit_option_menu import option_menu

import Vessel as vessel
import Cornea as cornea

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


# -------------------------------------------------
# Navigation
# -------------------------------------------------
page_index = {
    "Main": 0,
    "Cornea": 1,
    "Vessel": 2
}

selected = option_menu(
    menu_title=None,
    options=["Main", "Cornea", "Vessel"],
    icons=["house", "eye", "activity"],
    orientation="horizontal",
    default_index=page_index.get(st.session_state.page, 0)
)

st.session_state.page = selected


# -------------------------------------------------
# Image Selector
# -------------------------------------------------
selected_image_key = None
selected_image = None

if st.session_state.images:

    selected_image_key = st.radio(
        "Select an image:",
        list(st.session_state.images.keys()),
        key="image_select"
    )

    st.session_state.selected_image_key = selected_image_key

    if selected_image_key in st.session_state.images:
        selected_image = st.session_state.images[selected_image_key]


# -------------------------------------------------
# MAIN PAGE
# -------------------------------------------------
if selected == "Main":

    uploaded_files = st.file_uploader(
        "Upload images",
        accept_multiple_files=True,
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_files:

        for file in uploaded_files:
            image_bytes = file.read()
            
            try:
                img = Image.open(io.BytesIO(image_bytes)).verify()
                
                if img.mode != "RGB":
                    img = img.convert("RGB")

                st.session_state.images[file.name] = image_bytes
            
            except Exception as e:
                st.error(f"Error loading {file.name}: {e}")

    if selected_image is not None:

        st.image(
            selected_image,
            caption=f"Selected Image: {selected_image_key}"
        )

        # Cornea
        cornea_key = f"{selected_image_key}_cornea"

        if cornea_key in st.session_state.segmentations:
            st.image(
                st.session_state.segmentations[cornea_key],
                caption="Cornea Segmentation"
            )
        else:
            st.info("No cornea segmentation yet")

        # Vessel
        vessel_key = f"{selected_image_key}_vessel"

        if vessel_key in st.session_state.segmentations:
            st.image(
                st.session_state.segmentations[vessel_key],
                caption="Vessel Segmentation"
            )
        else:
            st.info("No vessel segmentation yet")


# -------------------------------------------------
# CORNEA PAGE
# -------------------------------------------------
elif selected == "Cornea":

    if selected_image_key:

        try:
            cornea.run(selected_image_key)

        except Exception as e:
            st.error(f"Cornea segmentation failed: {e}")

    else:
        st.warning("Upload and select an image first.")


# -------------------------------------------------
# VESSEL PAGE
# -------------------------------------------------
elif selected == "Vessel":

    if selected_image_key:

        try:
            vessel.run(selected_image_key)

        except Exception as e:
            st.error(f"Vessel segmentation failed: {e}")

    else:
        st.warning("Upload and select an image first.")


# import streamlit as st
# from streamlit_option_menu import option_menu

# from PIL import Image
# import numpy as np

# from skimage.transform import resize  # assuming this is needed
# import torch

# from monai.networks.nets import DynUNet

# import cv2

# import Vessel as vessel
# import Cornea as cornea

# #st.cache_data.clear()
# st.cache_resource.clear()
# #st.cache_resource

# if "page" not in st.session_state:
#     st.session_state.page = "Main"

# if "images" not in st.session_state:
#     st.session_state.images = {}
    
# if "segmentations" not in st.session_state:
#     st.session_state.segmentations = {}
    

# page_index = {
#     "Main": 0,
#     "Cornea": 1,
#     "Vessel": 2
# }

# selected = option_menu(
#     menu_title=None,
#     options=["Main", "Cornea", "Vessel"],
#     icons=["house", "eye", "vessel"],
#     orientation="horizontal",
#     default_index=page_index[st.session_state.page]
# )

# selected_image_key = None
# selected_image = None

# st.session_state.page = selected

# if st.session_state.images:
#     selected_image_key = st.radio(
#         "Select an image:",
#         list(st.session_state.images.keys()),
#         key="image_select"
#     )

#     st.session_state.selected_image_key = selected_image_key
#     selected_image = st.session_state.images[selected_image_key]

# if selected == "Main":
#     st.write('Images')
#     uploaded_files = st.file_uploader("Upload images", accept_multiple_files=True, type=["jpg", "jpeg", "png"])
#     if uploaded_files:
#         for file in uploaded_files:
#             img = Image.open(file)
            
#             if img.mode != 'RGB':
#                 st.error(f"Skipping {file.name}: Not an RGB image (current mode: {img.mode}).")
#             else:
#                 st.session_state.images[file.name] = img
                
#     if selected_image is not None: 
#         st.image(selected_image, caption=f"Selected Image: {st.session_state.selected_image_key}")
        
#     if selected_image_key and f"{selected_image_key}_cornea" in st.session_state.segmentations:
#         st.image(st.session_state.segmentations[f"{selected_image_key}_cornea"], caption="Cornea Segmentation")
#     else:
#         st.write("No cornea segmentation yet")
    
#     if selected_image_key and f"{selected_image_key}_vessel" in st.session_state.segmentations:
#         st.image(st.session_state.segmentations[f"{selected_image_key}_vessel"], caption="Vessel Segmentation")
#     else:
#         st.write("No vessel segmentation yet")

# if st.session_state.page == "Cornea":
#     if "selected_image_key" in st.session_state:
#         cornea.run(st.session_state.selected_image_key)
#     else:
#         st.warning("Please upload and select an image first.")

# if st.session_state.page == "Vessel":
#     if "selected_image_key" in st.session_state:
#         vessel.run(st.session_state.selected_image_key)
#     else:
#         st.warning("Please upload and select an image first.")


    # st.image(image, caption=selected_image, use_container_width=True)
    
