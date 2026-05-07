import streamlit as st

from PIL import Image
import numpy as np

from skimage.transform import resize  # assuming this is needed
import torch

from monai.networks.nets import DynUNet

import cv2

import Vessel as vessel
import Cornea as cornea

st.cache_data.clear()
st.cache_resource.clear()

def set_page(page):
    st.session_state.page = page

if "images" not in st.session_state:
    st.session_state.images = {}
    st.session_state.page = "home"
    
if "segmentations" not in st.session_state:
    st.session_state.segmentations = {}
    
uploaded_files = st.sidebar.file_uploader("Upload images", accept_multiple_files=True, type=["jpg", "jpeg", "png"])
if uploaded_files:
    for file in uploaded_files:
        img = Image.open(file)
        st.session_state.images[file.name] = img

selected_image_key = st.sidebar.radio("Select an image:", list(st.session_state.images.keys()), key="image_select")

col1, col2, col3 = st.columns([1, 1, 6])

with col1:
    if st.button("🏠 Main", use_container_width=True):
        st.write('main')
        #st.switch_page("main.py")

with col2:
    if st.button("Cornea Segmentation", on_click=set_page, args=("cornea",),use_container_width=True):
        if st.session_state.page == "cornea":
            cornea.run()

with col3:
    if st.button("Vessel Segmentation", on_click=set_page, args=("vessel",),use_container_width=True):
        if st.session_state.page == "vessel":
            vessel.run()
    
    #     # st.session_state.vessel_mode = "menu"
    #     # st.sidebar.write("Choose option:")
        
    #     # if st.sidebar.button("Option A"):
    #     #     st.session_state.vessel_mode = "A"
    
    #     # if st.sidebar.button("Option B"):
    #     #     st.session_state.vessel_mode = "B"

    #     # if st.session_state.vessel_mode == "A":
    #     #     st.sidebar.write("Please upload images")
    #     def run():
    # st.title("Cornea Segmentation")

    # if "segmentations" not in st.session_state:
    #     st.session_state.segmentations = {}

    # key = st.text_input("Image key")

    # if key:
    #     seg_key = key + "_cornea"

    #     if seg_key in st.session_state.segmentations:
    #         st.image(st.session_state.segmentations[seg_key])
    #     else:
    #         st.info("No cornea result yet.")
    #     #     uploaded_file = st.sidebar.file_uploader(
    #     #         "Upload image",
    #     #         type=["jpg", "jpeg", "png"],
    #     #         key="Mask_upload"
    #     #     )
        
    #     #     if uploaded_file is not None:
    #     #         mask = Image.open(uploaded_file)
    #     #         st.session_state.segmentations[selected_image_key + "_Mask"] = mask
    #     #         st.success("Mask saved")



    # st.image(image, caption=selected_image, use_container_width=True)
    
