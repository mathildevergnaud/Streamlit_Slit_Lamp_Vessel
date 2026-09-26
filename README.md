# Streamlit_Slit_Lamp_Vessel

## Overview

Cornea and neo-corneavascularisation segmentation and morpho-analyses from slit-lamp images

<p align="center">
<img src="readme_example/figure1bis.png" alt="Pipeline" width="400"/>
</p>

## Streamlit app

We develop an interface with streamlit, an test acces can be accessible via this link : https://6w8d8hjcyf7gtkqrbyjuw4.streamlit.app/

To use it locally the app and the dependencies are in the app folder. 

### Installation

First clone the repository :

```bash
git clone https://github.com/votre-utilisateur/Streamlit_Slit_Lamp_Vessel.git
```

Our streamlit app is compatible with CPU-only environment.

```bash
cd ++++

# Creation env
conda create -n slit-lamp-vessel python=3.10
conda activate slit-lamp-vessel
pip install -r app/requirements.txt

# To run the app 
streamlit run app/streamlit_app.py
```

The app will be available in a localhost. ex : http://localhost:xxxx](http://localhost:xxxx).

### Usage

The streamlit has two parts "single image" and "batch processing". The first one let the user select to use an automatic segmentation (and wich segmentation) or not and then to quantify morphemetrics parameters

(add images)

The second part, let the user analyses multiples images in ones, at the ends it obtains .zip with the segmentations of all the images and a .csv with the morphetrics results

(add images)

## Notebook 

(see if i kept this part)

### Installation

## Dataset



## Modele Checkpoints

https://zenodo.org/records/22975963

##

