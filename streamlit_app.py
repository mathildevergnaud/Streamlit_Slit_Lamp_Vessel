import io

import streamlit as st
from PIL import Image
from streamlit_option_menu import option_menu

import Vessel as vessel
import Cornea as cornea

<<<<<<< HEAD
st.set_page_config(page_title="Slit Lamp Vessel/Cornea Segmentation", layout="wide")

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
PAGE_INDEX = {"Main": 0, "Cornea": 1, "Vessel": 2}
=======
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
>>>>>>> e2cf0ae596b352bb27a943cd6e26749947bb4561

selected = option_menu(
    menu_title=None,
    options=["Main", "Cornea", "Vessel"],
    icons=["house", "eye", "activity"],
    orientation="horizontal",
<<<<<<< HEAD
    default_index=PAGE_INDEX.get(st.session_state.page, 0),
=======
    default_index=page_index.get(st.session_state.page, 0)
>>>>>>> e2cf0ae596b352bb27a943cd6e26749947bb4561
)
st.session_state.page = selected

# -------------------------------------------------
# Image Selector
#
# NOTE: st.session_state.images stores TWO entries per uploaded file:
#   - "<filename>"      -> raw bytes (for display)
#   - "<filename>_or"    -> decoded PIL.Image (consumed internally by Cornea.py)
# The "_or" entries must NOT be offered as selectable "images" in the
# picker below, or every upload shows up twice (this was a bug in the
# original version).
# -------------------------------------------------
selectable_keys = [k for k in st.session_state.images if not k.endswith("_or")]

<<<<<<< HEAD
selected_image_key = None
selected_image = None

if selectable_keys:
=======
st.session_state.page = selected


# -------------------------------------------------
# Image Selector
# -------------------------------------------------
selected_image_key = None
selected_image = None

if st.session_state.images:

>>>>>>> e2cf0ae596b352bb27a943cd6e26749947bb4561
    selected_image_key = st.radio(
        "Select an image:",
        selectable_keys,
        key="image_select",
    )
    st.session_state.selected_image_key = selected_image_key
    selected_image = st.session_state.images.get(selected_image_key)

# -------------------------------------------------
# MAIN PAGE
# -------------------------------------------------
if selected == "Main":
    uploaded_files = st.file_uploader(
        "Upload images",
        accept_multiple_files=True,
        type=["jpg", "jpeg", "png"],
    )

<<<<<<< HEAD
=======
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

>>>>>>> e2cf0ae596b352bb27a943cd6e26749947bb4561
    if uploaded_files:

        for file in uploaded_files:
            image_bytes = file.read()
<<<<<<< HEAD
            try:
                img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                st.session_state.images[file.name] = image_bytes
                st.session_state.images[file.name + "_or"] = img
=======
            
            try:
                img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                st.session_state.images[file.name] = image_bytes
                st.session_state.images[file.name+'_or'] = img
            
>>>>>>> e2cf0ae596b352bb27a943cd6e26749947bb4561
            except Exception as e:
                st.error(f"Error loading {file.name}: {e}")

    if selected_image is not None:
<<<<<<< HEAD
        st.image(selected_image, caption=f"Selected Image: {selected_image_key}")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Cornea")
            cornea_key = f"{selected_image_key}_cornea"
            if cornea_key in st.session_state.segmentations:
                st.image(st.session_state.segmentations[cornea_key], caption="Cornea Segmentation")
            else:
                st.info("No cornea segmentation yet")

        with col2:
            st.subheader("Vessel")
            vessel_key = f"{selected_image_key}_vessel"
            if vessel_key in st.session_state.segmentations:
                st.image(st.session_state.segmentations[vessel_key], caption="Vessel Segmentation")
            else:
                st.info("No vessel segmentation yet")
    else:
        st.info("Upload one or more images to get started.")

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
=======

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
>>>>>>> e2cf0ae596b352bb27a943cd6e26749947bb4561

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
