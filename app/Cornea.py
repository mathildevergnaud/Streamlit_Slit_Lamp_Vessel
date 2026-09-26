import streamlit as st

from PIL import Image
import numpy as np

from skimage.transform import resize  # assuming this is needed
import torch

from monai.networks.nets import DynUNet

import requests
from pathlib import Path

import cv2
import numpy as np

#

BASE_DIR = Path(__file__).resolve().parent 

CORNEA_MODEL_URL = "https://zenodo.org/records/22975963/files/cornea_model.pt?download=1"
CORNEA_MODEL_PATH = BASE_DIR / "utils" / "cornea" / "cornea_model.pt"

def download_if_missing(url: str, path: Path):
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, stream=True)
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
                
def load_model(device):
    download_if_missing(CORNEA_MODEL_URL, CORNEA_MODEL_PATH)
    net = build_model().to(device)
    net.load_state_dict(torch.load(CORNEA_MODEL_PATH, map_location=device))
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
    if mask.dtype != np.uint8:
        mask = (mask > 0).astype("uint8") * 255
    return cv2.bitwise_and(image, image, mask=mask)


def run(selected_image_key):

    if "segmentations" not in st.session_state:
        st.session_state.segmentations = {}

    st.write(selected_image_key)
        
    if selected_image_key:
        
        original_image = st.session_state.images[selected_image_key+'_or']
        
        np_image = np.array(original_image).astype(np.uint8)
        img_array = np.array(original_image).astype(np.float32)/255.0
        size= img_array.shape
        
        resized_img = np.array(resize(img_array, (512, 512), anti_aliasing=True), dtype=np.float32)  
        
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = load_model(device)
        
        im = torch.from_numpy(resized_img).permute(2, 0, 1).unsqueeze(0).to(device)
        
        pred = torch.sigmoid(model(im))[0,0].cpu().detach().numpy()  
        pred = (pred * 255).astype("uint8")
        
        pred = np.array(resize(pred, (size[0], size[1]), anti_aliasing=True), dtype=np.uint8)                
        pred = encompasse_cornea(pred)
        
        segmented_image = Image.fromarray(pred)
        
        cornea_selected = Image.fromarray(Cornea_Crop(np_image, pred))

        return segmented_image, cornea_selected
    

