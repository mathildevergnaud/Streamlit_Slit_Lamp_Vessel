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
    
uploaded_files = st.file_uploader("Upload images", accept_multiple_files=True, type=["jpg", "jpeg", "png"])
if uploaded_files:
    for file in uploaded_files:
        img = Image.open(file)
        st.session_state.images[file.name] = img

selected_image_key = st.radio("Select an image:", list(st.session_state.images.keys()), key="image_select")

if st.sidebar.button("Cornea Segmentation", on_click=set_page, args=("cornea",)):
    if st.session_state.page == "cornea":
        cornea.run()
#     '''
#     if selected_image_key:
        
#         original_image = st.session_state.images[selected_image_key]
#         image = np.array(original_image).astype(np.uint8)
        
#         img_array = np.array(original_image).astype(np.float32)/255.0
#         size= img_array.shape
        
#         resized_img = np.array(resize(img_array, (512, 512), anti_aliasing=True), dtype=np.float32)  
        
#         device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#         model = load_model(device)
        
#         im = torch.from_numpy(resized_img).permute(2, 0, 1).unsqueeze(0).to(device)
        
#         pred = torch.sigmoid(model(im))[0,0].cpu().detach().numpy()  
#         pred = (pred * 255).astype("uint8")

#         pred = np.array(resize(pred, (size[0], size[1]), anti_aliasing=True), dtype=np.uint8)
#         pred = encompasse_cornea(pred)
        
#         segmented_image = Image.fromarray(pred)
        
#         Cornea_select = Image.fromarray(Cornea_Crop(image, pred))
#         #st.sidebar.write(np.array(original_image)[0,0], np.array(original_image).dtype, type(np.array(original_image)), pred.dtype, type(pred), pred.max())
        
#         st.session_state.segmentations[selected_image_key + "_segmented"] = segmented_image
#         st.session_state.segmentations[selected_image_key + "_cornea"] = Cornea_select
#     else:
#         st.sidebar.error("Please select an image first.")
# '''

# # Display selected image and segmentation
# '''
# st.write("Selected Image:")
# if selected_image_key:
#     st.image(st.session_state.images[selected_image_key], caption="Original Image")

# # st.write("Segmentation Result:")
# # if selected_image_key and selected_image_key + "_segmented" in st.session_state.segmentations:
# #     st.image(st.session_state.segmentations[selected_image_key + "_segmented"], caption="Segmented Image")
# # else:
# #     st.write("No segmentation result yet.")

# st.write("Cornea:")
# if selected_image_key and selected_image_key + "_cornea" in st.session_state.segmentations:
#     st.image(st.session_state.segmentations[selected_image_key + "_cornea"], caption="Cornea")
# else:
#     st.write("No segmentation result yet.")
# '''

if st.sidebar.button("Vessel Segmentation", on_click=set_page, args=("vessel",)):
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
    
