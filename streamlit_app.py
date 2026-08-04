import io

import streamlit as st
from PIL import Image
import pandas as pd
from streamlit_option_menu import option_menu

import Vessel as vessel
import Cornea as cornea

USE_MODEL = "Use the model"
USE_MANUAL = "Upload my own mask"



st.set_page_config(page_title="Slit Lamp Vessel/Cornea Segmentation", layout="wide")

st.title("Corneal vessel & cornea segmentation -- interactive preview")

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

# # -------------------------------------------------
# # Navigation
# # -------------------------------------------------

tab_single, tab_batch = st.tabs(["Single image", "Batch processing"])

with tab_single:
    st.caption(
        "Upload one or a batch of images"
    )

    uploaded = uploaded_files = st.file_uploader(
        "Upload images",
        accept_multiple_files=True,
        type=["jpg", "jpeg", "png"],
    )

    if uploaded_files:
        for file in uploaded_files:
            image_bytes = file.read()
            try:
                img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                st.session_state.images[file.name] = image_bytes
                st.session_state.images[file.name + "_or"] = img
            except Exception as e:
                st.error(f"Error loading {file.name}: {e}")
                
        col_v, col_c = st.columns(2)
        with col_v:
            vessel_choice = st.radio("Vessels:", [USE_MODEL, USE_MANUAL], key="vessel_choice")
            manual_vessel_file = None
            if vessel_choice == USE_MANUAL:
                manual_vessel_file = st.file_uploader(
                    "Manual vessel mask", type=IMAGE_TYPES, key="manual_vessel"
                )
        with col_c:
            cornea_choice = st.radio("Cornea:", [USE_MODEL, USE_MANUAL], key="cornea_choice")
            manual_cornea_file = None
            if cornea_choice == USE_MANUAL:
                manual_cornea_file = st.file_uploader(
                    "Manual cornea mask", type=IMAGE_TYPES, key="manual_cornea"
                )

        needs_model = (vessel_choice == USE_MODEL) or (cornea_choice == USE_MODEL)

# PAGE_INDEX = {"Main": 0, "Cornea": 1, "Vessel": 2}

# selected = option_menu(
#     menu_title=None,
#     options=["Main", "Cornea", "Vessel"],
#     icons=["house", "eye", "activity"],
#     orientation="horizontal",
#     default_index=PAGE_INDEX.get(st.session_state.page, 0),
# )
# st.session_state.page = selected

# # -------------------------------------------------
# # Image Selector
# #
# # NOTE: st.session_state.images stores TWO entries per uploaded file:
# #   - "<filename>"      -> raw bytes (for display)
# #   - "<filename>_or"    -> decoded PIL.Image (consumed internally by Cornea.py)
# # The "_or" entries must NOT be offered as selectable "images" in the
# # picker below, or every upload shows up twice (this was a bug in the
# # original version).
# # -------------------------------------------------
# selectable_keys = [k for k in st.session_state.images if not k.endswith("_or")]

# selected_image_key = None
# selected_image = None

# if selectable_keys:
#     selected_image_key = st.radio(
#         "Select an image:",
#         selectable_keys,
#         key="image_select",
#     )
#     st.session_state.selected_image_key = selected_image_key
#     selected_image = st.session_state.images.get(selected_image_key)

# # -------------------------------------------------
# # MAIN PAGE
# # -------------------------------------------------
# if selected == "Main":
#     uploaded_files = st.file_uploader(
#         "Upload images",
#         accept_multiple_files=True,
#         type=["jpg", "jpeg", "png"],
#     )

#     if uploaded_files:
#         for file in uploaded_files:
#             image_bytes = file.read()
#             try:
#                 img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
#                 st.session_state.images[file.name] = image_bytes
#                 st.session_state.images[file.name + "_or"] = img
#             except Exception as e:
#                 st.error(f"Error loading {file.name}: {e}")

#     if selected_image is not None:
#         st.image(selected_image, caption=f"Selected Image: {selected_image_key}")

#         col1, col2 = st.columns(2)

#         with col1:
#             st.subheader("Cornea")
#             cornea_key = f"{selected_image_key}_cornea"
#             if cornea_key in st.session_state.segmentations:
#                 st.image(st.session_state.segmentations[cornea_key], caption="Cornea Segmentation")
#             else:
#                 st.info("No cornea segmentation yet")

#         with col2:
#             st.subheader("Vessel")
#             vessel_key = f"{selected_image_key}_vessel"
#             if vessel_key in st.session_state.segmentations:
#                 st.image(st.session_state.segmentations[vessel_key], caption="Vessel Segmentation")
#             else:
#                 st.info("No vessel segmentation yet")
#     else:
#         st.info("Upload one or more images to get started.")

# # -------------------------------------------------
# # CORNEA PAGE
# # -------------------------------------------------
# elif selected == "Cornea":
#     if selected_image_key:
#         try:
#             cornea.run(selected_image_key)
#         except Exception as e:
#             st.error(f"Cornea segmentation failed: {e}")
#     else:
#         st.warning("Upload and select an image first.")

# # -------------------------------------------------
# # VESSEL PAGE
# # -------------------------------------------------
# elif selected == "Vessel":
#     if selected_image_key:
#         try:
#             vessel.run(selected_image_key)
#         except Exception as e:
#             st.error(f"Vessel segmentation failed: {e}")
#     else:
#         st.warning("Upload and select an image first.")
