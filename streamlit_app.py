import streamlit as st
from PIL import Image

from monai.networks.nets import DynUNet

from utils.cornea.train_monai_pl_v2 import EyeBVSegm

import torch

@st.cache_resource
def build_model():
    return DynUNet(
        spatial_dims=2,
        in_channels=3,
        out_channels=1,
        kernel_size=[(3, 3)] * 5,
        strides=[(1, 1), (2, 2), (2, 2), (2, 2), (2, 2)],
        upsample_kernel_size=[(2, 2)] * 4,
        norm_name="BATCH",
        dropout=0.2,
    )

@st.cache_resource
def load_model(device):
    net = build_model().to(device)
    net.eval()
    return net

st.set_page_config(layout="wide")

# -------- Sidebar --------
st.sidebar.title("Upload Images")

uploaded_files = st.sidebar.file_uploader(
    "Choose images",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)

# Session state
if "images" not in st.session_state:
    st.session_state.images = {}

# Store uploaded images
if uploaded_files:
    for file in uploaded_files:
        if file.name not in st.session_state.images:
            st.session_state.images[file.name] = Image.open(file)

# Image selector
st.sidebar.title("Image List")
image_names = list(st.session_state.images.keys())

selected_image = None
if image_names:
    selected_image = st.sidebar.radio("Select an image", image_names)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = load_model(device)

if st.sidebar.button("Cornea_Segmentation"):
    st.sidebar.write("Button was clicked 🎉")

    
    model.to(device)

# -------- Main Layout --------
st.title("Image Viewer")

if selected_image:
    image = st.session_state.images[selected_image]
    st.image(image, caption=selected_image, use_container_width=True)
    


