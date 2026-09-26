import streamlit as st

from PIL import Image
import numpy as np
import cv2

import torch
import torchvision.transforms as transforms

from monai.networks.nets import DynUNet

import requests
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent 

VESSEL_MODEL_URL = "https://zenodo.org/records/22975963/files/vessel_model.pt?download=1"
VESSEL_MODEL_PATH = BASE_DIR / "utils" / "vessel" / "vessel_model.pt"

def download_if_missing(url: str, path: Path):
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, stream=True)
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
                
def load_model(device):
    download_if_missing(VESSEL_MODEL_URL, VESSEL_MODEL_PATH)
    net = build_model().to(device)
    net.load_state_dict(torch.load(VESSEL_MODEL_PATH, map_location=device))
    net.eval()
    return net

def build_model():
    return DynUNet(
    spatial_dims=2,
    in_channels=4,
    out_channels=1,
    kernel_size=[(3, 3), (3, 3), (3, 3),(3,3), (3,3)],
    strides=[(1, 1), (2, 2), (2, 2),(2,2),(2,2)],           
    upsample_kernel_size=[(2, 2), (2,2),(2,2),(2,2)],
    norm_name="BATCH")

def gaussian_2D(center, sig, size_im):
    x, y = np.meshgrid(np.linspace(0, size_im[1], size_im[1]), np.linspace(0, size_im[0], size_im[0]))
    gauss = np.exp((-1*(x-center[0])**2)/((sig**2)/2) + (-1*(y-center[1])**2)/((sig**2)/2))
    return 1-gauss

def powder_trail_filter(img, tresh_high=0.85, tresh_low=0.25):#0.87 #0.25
    img = img/img.max()
    img_tops = (img>tresh_high)*255.0
    img_tops = img_tops.astype(np.uint8)
    img_hills = (img>tresh_low)*255.0
    img_hills = img_hills.astype(np.uint8)
    
    img_ = np.zeros(img.shape)
    ret, markers = cv2.connectedComponents(img_hills)
    for i in range(ret):
        if np.sum(img_tops[markers==i])>0:
            img_[markers==i]=1
    return img_

def func_f(x):
    if x<=0:
        return 0
    else:
        return np.exp(-1/x)
		
def func_g(x):
	return func_f(x)/(func_f(x)+func_f(1-x))

def trans_func(x, a, b):
	return func_g((x-a)/(b-a))

def flt32_to_unint8(img):
    return np.round((((img - img.min())/(img.max()-img.min()) * 255)).astype(np.uint8)) 

def shiny_stitching(image, imagette, i, j, size_im, mask):
	image_ = np.zeros((x_im,y_im))
	image_mask = np.zeros((x_im,y_im))
	image_[i:i + size_im[0], j: j + size_im[1]] = imagette
	image_mask[i:i + size_im[0], j:j +size_im[1]] = mask
	
	image=image*(1-image_mask)+image_*image_mask
	
	return image

def cut_im_2(image_in, mask_in, device = 'cpu'):
	global x_im 
	global y_im
	global bordure
	
	size_im = [576,576]
	bordure = 100
		
	cnt, _ = cv2.findContours((mask_in).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	contour = max(cnt, key = cv2.contourArea)
	
	(x,y), radius = cv2.minEnclosingCircle(contour)
	center = (int(x), int(y))
	radius = int(radius)
	
	g = gaussian_2D(center, radius, mask_in.shape)
	g = ((mask_in*g)/255.0).astype(np.float32)
	
	im = np.concatenate((image_in, g[:,:,None]), axis=2)
	im = im.astype(np.float32)/255.0
	
	transform = transforms.Compose([transforms.ToTensor()])
	new_imagette_list=[]
	
	x_im,y_im,*_  = im.shape 
	i, j = 0,0
	
	while i + size_im[0] < x_im :
		while j + size_im[1] < y_im:
			new_imagette_list.append(transform(im[i :i+size_im[0], j: j+size_im[1]]).to(device))
			j+= size_im[1]-bordure
		
		new_imagette_list.append(transform(im[i :i+size_im[0], y_im-size_im[1]:y_im]).to(device))
		i += size_im[0]-bordure
		j = 0
	
	while j + size_im[1] < y_im:
		new_imagette_list.append(transform(im[x_im -size_im[0] :x_im, j: j+size_im[1]]).to(device))
		j+= size_im[1]-bordure
	new_imagette_list.append(transform(im[x_im -size_im[0] :x_im, y_im-size_im[1]:y_im]).to(device))
	
	return new_imagette_list

def recfin_im_2(list_im):
	
	size_im = [576,576]
	mask = np.zeros((size_im[0], size_im[1]))
	for i in range(size_im[0]):
		for j in range(size_im[1]):
			mask[i,j] = trans_func(i, 0, bordure)*trans_func(j, 0,bordure)
	image =  np.zeros((x_im,y_im))
	i, j = 0,0
	im_num = 0
	
	while i + size_im[0] < x_im :
		while j + size_im[1] < y_im:
			
			imagette = list_im[im_num].astype(np.float32)
			
			image = shiny_stitching(image, imagette, i,j , size_im, mask)
			im_num += 1
			j+= size_im[1]-bordure
			
		imagette = list_im[im_num].astype(np.float32)
		image = shiny_stitching(image, imagette, i, y_im-size_im[1], size_im, mask)
		im_num += 1
		i += size_im[0]-bordure
		j = 0
		
	while j + size_im[1] < y_im:
		imagette = list_im[im_num].astype(np.float32)
		image = shiny_stitching(image, imagette, x_im-size_im[0],j , size_im, mask)
		im_num += 1
		
		j+= size_im[1]-bordure
		
	imagette = list_im[im_num].astype(np.float32)
	image = shiny_stitching(image, imagette, x_im-size_im[0],y_im-size_im[1] , size_im, mask)
	im_num += 1
	
	j+= size_im[1]-bordure
	
	image[image>1]=1
	image[image<0]=0
	return image

def run(selected_image_key):

	input = st.session_state.segmentations[selected_image_key + "_cornea"]
	mask_in = st.session_state.segmentations[selected_image_key + "_mask"]		
	
	input_array = np.array(input).astype(np.uint8)
	mask_array = np.array(mask_in).astype(np.uint8)
	
	device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
	model = load_model(device)

	imagette = cut_im_2(input_array, mask_array, device)

	outputs = []

	for inp in imagette : 
		out = model(inp.to(device).unsqueeze(0))
		pred = torch.sigmoid(out)[0,0].cpu().detach().numpy()
		outputs.append(pred)
	
	output_image = (powder_trail_filter(recfin_im_2(outputs))*255).astype(np.uint8)
	Vessel_seg = Image.fromarray(output_image)

	return Vessel_seg





