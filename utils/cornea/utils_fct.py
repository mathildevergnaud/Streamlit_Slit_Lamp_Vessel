import streamlit as st

from PIL import Image
import numpy as np

from skimage.transform import resize  # assuming this is needed
import torch

from monai.networks.nets import DynUNet

import cv2

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
    
    #st.write(image[820,1200])
    if mask.dtype != np.uint8:
        mask = (mask > 0).astype("uint8") * 255
    return cv2.bitwise_and(image, image, mask=mask)
