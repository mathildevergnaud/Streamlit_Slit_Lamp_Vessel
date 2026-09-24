import streamlit as st

from PIL import Image, ImageDraw
import numpy as np
import networkx as nx

import cv2

import torch
import torchvision.transforms as transforms

import pandas as pd

from utils.quant.Carracterize_vessel import vessel_caracterisation
from utils.quant.create_graph import create_graph

QUADRANT_COLORS = {
    'middle':   (255, 0, 0),
    'nasal':    (255, 255, 0),
    'bottom':   (0, 255, 0),
    'temporal': (255, 0, 255),
    'top':      (0, 0, 255),
}

def get_quadrant_mask(part_clock, part):
    """Boolean mask (H, W) of pixels belonging to a given quadrant."""
    color = QUADRANT_COLORS.get(part)
    if color is None:
        return None  # unknown part, e.g. 'eyes' -> no restriction

    arr = np.array(part_clock)
    return (
        (arr[..., 0] == color[0]) &
        (arr[..., 1] == color[1]) &
        (arr[..., 2] == color[2])
    )

def percent_vessel(image_clock, image_vessel, part_clock=None, part='eyes'):
    cornea_bool = np.array(image_clock) == 255
    vessel_bool = np.array(image_vessel) == 255

    if part != 'eyes' and part_clock is not None:
        quadrant_mask = get_quadrant_mask(part_clock, part)
        if quadrant_mask is not None:
            cornea_bool = cornea_bool & quadrant_mask
            vessel_bool = vessel_bool & quadrant_mask

    countpixelcornea = np.count_nonzero(cornea_bool)
    countpixelvessel = np.count_nonzero(vessel_bool)

    if countpixelcornea == 0:
        return 0.0

    return countpixelvessel / countpixelcornea * 100


ENDPOINT_COLOR = (179, 49, 2)     # "#B33102"
JUNCTION_COLOR = (9, 68, 70)      # "#094446"

def plot_image_quadrants_graph(original_img, part_clock, graph,
                                quadrant_alpha=0.25, node_radius=4, edge_width=1):
    """
    original_img : PIL.Image (RGB)
    part_clock   : np.ndarray or PIL.Image, color-coded quadrant map
    graph        : networkx graph, node attr 'info' = [row, col], node attr '_endpoint'
    Returns a PIL.Image ready for st.image()
    """
    orig = original_img.convert("RGB")
    size = orig.size  # (width, height)

    part_arr = np.array(part_clock)
    if part_arr.shape[:2] != (size[1], size[0]):
        part_arr = np.array(Image.fromarray(part_arr).resize(size))

    orig_arr = np.array(orig).astype(np.float32)
    composite = orig_arr.copy()

    # Blend quadrant colors
    for part, color in QUADRANT_COLORS.items():
        mask = (
            (part_arr[..., 0] == color[0]) &
            (part_arr[..., 1] == color[1]) &
            (part_arr[..., 2] == color[2])
        )
        for c in range(3):
            composite[..., c] = np.where(
                mask,
                composite[..., c] * (1 - quadrant_alpha) + color[c] * quadrant_alpha,
                composite[..., c],
            )

    composite_img = Image.fromarray(composite.astype(np.uint8))
    draw = ImageDraw.Draw(composite_img)

    # Node positions: 'info' is [row, col] -> PIL draws in (x, y) = (col, row)
    pos = nx.get_node_attributes(graph, 'info')
    pos_xy = {n: (coord[1], coord[0]) for n, coord in pos.items()}

    # Draw edges first (so nodes sit on top)
    for u, v in graph.edges():
        if u in pos_xy and v in pos_xy:
            draw.line([pos_xy[u], pos_xy[v]], fill=(255, 255, 255), width=edge_width)

    # Draw nodes
    for n in graph.nodes():
        if n not in pos_xy:
            continue
        x, y = pos_xy[n]
        color = ENDPOINT_COLOR if graph.nodes[n].get('_endpoint') else JUNCTION_COLOR
        draw.ellipse(
            [x - node_radius, y - node_radius, x + node_radius, y + node_radius],
            fill=color,
        )
    return composite_img

def run(selected_image_key):


	vessel_in = st.session_state.segmentations[selected_image_key + "_vessel"]
	mask_in = st.session_state.segmentations[selected_image_key + "_mask"]	
	cornea_in = st.session_state.segmentations[selected_image_key + "_cornea"]		
	
	vessel_array = np.array(vessel_in).astype(np.uint8)
	mask_array = np.array(mask_in).astype(np.uint8)
	cornea_array = np.array(cornea_in).astype(np.uint8)

	morpho_info = {}

	gra = create_graph(vessel_array,mask_array, cornea_array)

	overlay_img = plot_image_quadrants_graph(
        st.session_state.images[selected_image_key + "_or"],
        gra.part_clock,
        gra.graph,
    )

	for part in ['eyes', 'middle', 'nasal', 'bottom', 'temporal', 'top']:

		try:
			eyes = vessel_caracterisation(
				gra.graph.copy(),
				part
			)

			morpho_info[part + '_percent_vessel'] = percent_vessel(mask_array, vessel_array, gra.part_clock, part)

			morpho_info[part+'_lenght_min'], morpho_info[part+'_lenght_max'], morpho_info[part+'_lenght_moy'], morpho_info[part+'_lenght_med'], morpho_info[part+'_lenght_25p'],  morpho_info[part+'_lenght_75p'], morpho_info[part+'_lenght_05p'], morpho_info[part+'_lenght_95p'],morpho_info[part+'_lenght_all']= eyes.Lenght_between_2_junction()
			morpho_info[part+'_dia_min'], morpho_info[part+'_dia_max'], morpho_info[part+'_dia_moy'], morpho_info[part+'_dia_med'], morpho_info[part+'_dia_25p'],  morpho_info[part+'_dia_75p'], morpho_info[part+'_dia_05p'], morpho_info[part+'_dia_95p']= eyes.Diameter_vessel()
					
			morpho_info[part+'_tor_min'], morpho_info[part+'_tor_max'], morpho_info[part+'_tor_moy'], morpho_info[part+'_tor_med'], morpho_info[part+'_tor_25p'],  morpho_info[part+'_tor_75p'], morpho_info[part+'_tor_05p'], morpho_info[part+'_tor_95p']= eyes.tortuosity()
					
			morpho_info[part+'_junction'], morpho_info[part+'_endpoint'] = eyes.number_junction_endpoint()
			morpho_info[part+'_junctions_endpoint'] = morpho_info[part+'_junction'] + morpho_info[part+'_endpoint'] 



		except Exception as e:
			st.error(f"Error for part = {part}")
			st.exception(e)
			break

		del eyes

	return morpho_info, overlay_img









