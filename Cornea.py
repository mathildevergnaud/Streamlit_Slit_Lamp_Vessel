import streamlit as st

from PIL import Image
import numpy as np

from skimage.transform import resize  # assuming this is needed
import torch

from monai.networks.nets import DynUNet

import cv2

import utils.cornea.utils_fct as fct

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
        dropout=0.2)

def encompasse_cornea(cornea):

    contours, hierarchy = cv2.findContours(cornea, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    blank_image = np.zeros((cornea.shape), np.uint8)

    if len(contours) != 0:
       c = max(contours, key = cv2.contourArea)
       convexHull = cv2.convexHull(c)
       cv2.fillConvexPoly(blank_image, convexHull, 255)
    
    return blank_image

def Cornea_Crop(image, mask):
    #st.write("Shape:", image.shape)
    #st.write("Dtype:", image.dtype)
    
    st.write(image[820,1200])
    if mask.dtype != np.uint8:
        mask = (mask > 0).astype("uint8") * 255
    return cv2.bitwise_and(image, image, mask=mask)


def run(selected_image_key):
    st.title("Cornea Segmentation")

    if "segmentations" not in st.session_state:
        st.session_state.segmentations = {}

    st.write(selected_image_key)
        
    if selected_image_key:
        
        original_image = st.session_state.images[selected_image_key]
        st.image(original_image, caption="Segmented Image")
        
        np_image = np.array(original_image).astype(np.uint8)
        img_array = np.array(original_image).astype(np.float32)/255.0
        size= img_array.shape
        
        resized_img = np.array(resize(img_array, (512, 512), anti_aliasing=True), dtype=np.float32)  
        
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = fct.load_model(device)
        
        im = torch.from_numpy(resized_img).permute(2, 0, 1).unsqueeze(0).to(device)
        
        pred = torch.sigmoid(model(im))[0,0].cpu().detach().numpy()  
        pred = (pred * 255).astype("uint8")
        
        pred = np.array(resize(pred, (size[0], size[1]), anti_aliasing=True), dtype=np.uint8)                
        pred = fct.encompasse_cornea(pred)
        
        segmented_image = Image.fromarray(pred)
        
        Cornea_select = Image.fromarray(fct.Cornea_Crop(np_image, pred))
        #st.sidebar.write(np.array(original_image)[0,0], np.array(original_image).dtype, type(np.array(original_image)), pred.dtype, type(pred), pred.max())
        
        st.session_state.segmentations[selected_image_key + "_segmented"] = segmented_image
        st.session_state.segmentations[selected_image_key + "_cornea"] = Cornea_select
    else:
        st.sidebar.error("Please select an image first.")


    st.write("Segmentation Result:")
    if selected_image_key and selected_image_key + "_segmented" in st.session_state.segmentations:
        st.image(st.session_state.segmentations[selected_image_key + "_segmented"], caption="Segmented Image")
    else:
        st.write("No segmentation result yet.")
    
    st.write("Cornea:")
    if selected_image_key and selected_image_key + "_cornea" in st.session_state.segmentations:
        st.image(st.session_state.segmentations[selected_image_key + "_cornea"], caption="Cornea")
    else:
        st.write("No segmentation result yet.")

