import streamlit as st
from PIL import Image
import numpy as np
from skimage.transform import resize  # assuming this is needed
import torch
from monai.networks.nets import DynUNet

st.cache_data.clear()
st.cache_resource.clear()

def load_model(device):
    net = build_model().to(device)
    net.load_state_dict(torch.load("./utils/cornea/model.pt", map_location=device))
    net.eval()
    return net

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

# Initialize session state
if "images" not in st.session_state:
    st.session_state.images = {}
if "segmentations" not in st.session_state:
    st.session_state.segmentations = {}

# Upload images
uploaded_files = st.file_uploader("Upload images", accept_multiple_files=True, type=["jpg", "jpeg", "png"])
if uploaded_files:
    for file in uploaded_files:
        img = Image.open(file)
        st.session_state.images[file.name] = img

# Select an image
selected_image_key = st.radio("Select an image:", list(st.session_state.images.keys()), key="image_select")

# Process the selected image when the button is clicked
if st.sidebar.button("Cornea Segmentation"):
    if selected_image_key:
        original_image = st.session_state.images[selected_image_key]
        # Process the image through the model
        img_array = np.array(original_image).astype(np.float32)
        resized_img = resize(img_array, (512, 512))  # Ensure correct import

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        model = load_model(device)
        
        im = torch.from_numpy(resized_img).permute(2, 0, 1).unsqueeze(0).to(device)

        print(im.shape, im.dtype)
        pred = torch.sigmoid(model(im))[0,0,:,:].cpu().detach().numpy().astype(np.uint8)
        
        # Assuming model is loaded here
        # model = load_model()  # Placeholder for model loading
        # output = model.predict(resized_img[np.newaxis, ...])  # Add batch dimension
        # mask = (output[0, :, :, 0] > 0.5).astype(np.uint8) * 255  # Assuming binary segmentation
        
        # Example dummy mask (replace with actual prediction)
        #mask = np.random.randint(0, 256, size=(512, 512), dtype=np.uint8)  # Dummy data
        
        segmented_image = Image.fromarray(pred)
        st.session_state.segmentations[selected_image_key + "_segmented"] = segmented_image
    else:
        st.sidebar.error("Please select an image first.")

# Display selected image and segmentation
st.write("Selected Image:")
if selected_image_key:
    st.image(st.session_state.images[selected_image_key], caption="Original Image")

st.write("Segmentation Result:")
if selected_image_key and selected_image_key + "_segmented" in st.session_state.segmentations:
    st.image(st.session_state.segmentations[selected_image_key + "_segmented"], caption="Segmented Image")
else:
    st.write("No segmentation result yet.")


####################

# import streamlit as st
# from PIL import Image

# from monai.networks.nets import DynUNet

# #from utils.cornea.train_monai_pl_v2 import EyeBVSegm

# import torch
# import torchvision.transforms as transforms

# import skimage
# import numpy as np

# @st.cache_resource
# def build_model():
#     return DynUNet(
#         spatial_dims=2,
#         in_channels=3,
#         out_channels=1,
#         kernel_size=[(3, 3)] * 5,
#         strides=[(1, 1), (2, 2), (2, 2), (2, 2), (2, 2)],
#         upsample_kernel_size=[(2, 2)] * 4,
#         norm_name="BATCH",
#         dropout=0.2,
#     )

# @st.cache_resource
# def load_model(device):
#     net = build_model().to(device)
#     net.load_state_dict(torch.load("./utils/cornea/model.pt", map_location=device))
#     net.eval()
#     return net
    
# #st.set_page_config(layout="wide")

# # -------- Sidebar --------
# st.sidebar.title("Upload Images")

# uploaded_files = st.sidebar.file_uploader(
#     "Choose images",
#     type=["png", "jpg", "jpeg"],
#     accept_multiple_files=True
# ) 

# # Session state
# if "images" not in st.session_state:
#     st.session_state.images = {}

# # Store uploaded images
# if uploaded_files:
#     for file in uploaded_files:
#         if file.name not in st.session_state.images:
#             st.session_state.images[file.name] = Image.open(file)

# # Image selector
# st.sidebar.title("Image List")
# image_names = list(st.session_state.images.keys())

# selected_image = None
# if image_names:
#     selected_image = st.sidebar.radio("Select an image", image_names)

#     device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#     model = load_model(device)

# if st.sidebar.button("Cornea_Segmentation"):
#     st.sidebar.write("Button was clicked 🎉")

# if selected_image is not None:
#     image = st.session_state.images[selected_image]
#     # ensure numpy float32
#     image = np.array(image).astype(np.float32)
#     # resize
#     im = skimage.transform.resize(
#         image,
#         (512, 512),
#         anti_aliasing=True
#     ).astype(np.float32)

# if selected_image is not None:
#     image = st.session_state.images[selected_image]
#     # ensure numpy float32
#     image = np.array(image).astype(np.float32)
#     # resize
#     im = skimage.transform.resize(
#         image,
#         (512, 512),
#         anti_aliasing=True
#     ).astype(np.float32)
    
#     # convert to tensor properly
#     im = torch.from_numpy(im).permute(2, 0, 1).unsqueeze(0).to(device)

#     pred = model(im)
    
#     st.sidebar.write(im.shape)
    
    # try:
    #     prediction = model(im)
    # except Exception as e:
    #     st.error(str(e))
    #     raise
    
# -------- Main Layout --------
#st.title("Image Viewer")

#     pred = model(im)

#     #predict_im = pred[0,0,:,:].cpu().detach().numpy()

#     #to_show = Image.fromarray(blank_image.astype(np.uint8)*255.0
    
#     st.sidebar.write(im.shape)
    
#     # try:
#     #     prediction = model(im)
#     # except Exception as e:
#     #     st.error(str(e))
#     #     raise
    
# # -------- Main Layout --------
# st.title("Image Viewer")

# if selected_image:
#     image = st.session_state.images[selected_image]
#     st.image(image, caption=selected_image, use_container_width=True)
    
