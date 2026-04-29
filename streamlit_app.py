import streamlit as st
from PIL import Image

import torch


def load_model():
    model = torch.load("utils/cornea/model.pt")  # Replace with your model path
    model.eval()  # Set to evaluation mode
    return model

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

    model = load_model()

if st.sidebar.button("Cornea_Segmentation"):
    st.sidebar.write("Button was clicked 🎉")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

# -------- Main Layout --------
st.title("Image Viewer")

if selected_image:
    image = st.session_state.images[selected_image]
    st.image(image, caption=selected_image, use_container_width=True)
    


