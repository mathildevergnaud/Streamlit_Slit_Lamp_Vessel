import skimage.measure
import skimage.morphology
from PIL import Image

import networkx as nx
import cv2

import skimage
import numpy
import numpy as np

import os
import math

#import matplotlib.pyplot as plt

from utils.quant.clock_vessel import clock

def position_vessel(node1, node2, graph_clock):

    #print(node1, node2)

    midlle_vessel = [int((node1[0]+node2[0])/2), int((node1[1]+node2[1])/2)]

    if graph_clock[midlle_vessel[0], midlle_vessel[1],][0] == 255 and graph_clock[midlle_vessel[0], midlle_vessel[1],][1] ==0 and graph_clock[midlle_vessel[0], midlle_vessel[1],][2] ==0 :
        return 'middle'

    elif graph_clock[midlle_vessel[0], midlle_vessel[1],][0] == 255 and graph_clock[midlle_vessel[0], midlle_vessel[1],][1] ==255 and graph_clock[midlle_vessel[0], midlle_vessel[1],][2] ==0 :
        return 'nasal'#

    elif graph_clock[midlle_vessel[0], midlle_vessel[1],][0] == 0 and graph_clock[midlle_vessel[0], midlle_vessel[1],][1] ==255 and graph_clock[midlle_vessel[0], midlle_vessel[1],][2] ==0 :
        return 'bottom'#temporal

    elif graph_clock[midlle_vessel[0], midlle_vessel[1],][0] == 255 and graph_clock[midlle_vessel[0], midlle_vessel[1],][1] ==0 and graph_clock[midlle_vessel[0], midlle_vessel[1],][2] ==255 :
        return 'temporal'

    elif graph_clock[midlle_vessel[0], midlle_vessel[1],][0] == 0 and graph_clock[midlle_vessel[0], midlle_vessel[1],][1] ==0 and graph_clock[midlle_vessel[0], midlle_vessel[1],][2] ==255 :
        return 'top'

    else:
        return 'poubelle'

def heuristic(node, goal):
    d1 = abs(int(node[0]) - int(goal[0]))
    d2 = abs(int(node[1]) - int(goal[1]))

    if d1 > d2 :
        return d1
    else:
        return d2

def diameter_mean(line, image):

    mean_diameter = 0
    for pixel in line:
        mean_diameter += image[pixel[0]][pixel[1]]*2
    
    mean_diameter = mean_diameter/len(line)

    return mean_diameter


def tortuosity(len1, len2):
    if len1 < len2 :
        return  1.0
                
    else :
        return float(len1 / len2) 

def hsv_mean(line, image):

    h_mean = 0
    v_mean = 0
    s_mean = 0

    for pixel in line:
        h_mean += image[pixel[0]][pixel[1]][0]
        s_mean += image[pixel[0]][pixel[1]][1]
        v_mean += image[pixel[0]][pixel[1]][2]
    
    h_mean = h_mean/len(line)
    s_mean = s_mean/len(line)
    v_mean = v_mean/len(line)

    return h_mean, s_mean, v_mean

def test_in_list(node, line):

        bbox = node[2]
    
        for pixel in line : 

            if pixel[0] >= bbox[0] and pixel[0] <= bbox[2] and pixel[1] >= bbox[1] and pixel[1] <= bbox[3]:
                return True
            
        return False

def fine_junctions(image):
    
    node_junction = numpy.zeros((image.shape),numpy.uint8)      

    for i in range(1,int(image.shape[0])-1): 
        for j in range(1,int(image.shape[1])-1):
            imagette = image[i-1: (i+2), j-1: j+2]
            if image[i,j] > 0:
                if imagette.max()>0 and numpy.sum(imagette > 0) > 3:
                    node_junction[i,j,] = 255 #[225,50,10]

                if imagette.max()>0 and numpy.sum(imagette > 0) == 2:
                    node_junction[i,j,] = 255 #[10,225,100]

    regionnodes = skimage.measure.regionprops(skimage.measure.label(node_junction))

    return node_junction, regionnodes

def fine_edges(node_junction, im_fur_edges, image,dia):

    coords = numpy.argwhere(node_junction == 255.0)

    node_junction = (node_junction.astype(numpy.float32))/255.0

    im_fur_edges = im_fur_edges - node_junction

    edge_labels = skimage.measure.label(im_fur_edges,connectivity=2,return_num=False)

    list_labels = numpy.unique(edge_labels)

    edges_list_pixels = []

    for label in list_labels:
        if label != 0:
            coord_edges = numpy.argwhere(edge_labels == label*1.0)
            edges_list_pixels.append(coord_edges)


    color1 = skimage.color.label2rgb(edge_labels, image=im_fur_edges, bg_label=0,  alpha=1.)    
    region_nodes = skimage.measure.regionprops(skimage.measure.label(node_junction))
    color1 = color1 + dia[:, :, numpy.newaxis]/125.0
    

    for i in range(color1.shape[0]):
       for j in range(color1.shape[1]):
           sum_col = color1[i][j][0]+color1[i][j][1]+color1[i][j][2]
           if image [i][j]> 0.0 and sum_col == 0: 
               color1[i][j] =[255.0,255.0,255.0] 

    return edges_list_pixels

class create_graph(clock):

    name_i = []
    skel = []
    diameter = []
    graph = []
    image = []
    hsv_im = []
    image_or = []
     
    def __init__(self, image, image_clock, image_or):

        clock.__init__(self, image_clock)

        self.image = image
        self.hsv_im = image_or
        self.image_or = image_or


        self.skel, self.diameter = skimage.morphology.medial_axis(self.image, return_distance=True)
        
        self.skel = skimage.morphology.skeletonize(self.image , method='lee')
        self.skel = skimage.morphology.area_opening(self.skel, 30, connectivity=8)
        

        self._graph()


    def __call__(self, *args, **kwargs):
        return self.graph

    def _graph(self):

        nodes_img, region_nodes = fine_junctions(self.skel)
        edges = fine_edges(nodes_img, self.skel,self.image,self.diameter)

        #region_nodes = self.test_overlap(region_nodes)
        self.graph = nx.Graph()

        _nodes = []

        node_id = 0
        for props in region_nodes:
            bbox = props.bbox[0]-1,  props.bbox[1]-1, props.bbox[2]+1,  props.bbox[3]+1

            _nodes.append([node_id,props.centroid,bbox])
                
            self.graph.add_node(node_id, info = [int(props.centroid[0]),int(props.centroid[1])])
            node_id = node_id +1

        id = 0
        for list_in in edges:
           
            node_links = []

            for node in _nodes:

                object = test_in_list(node, list_in)

                if object == True:
                    node_links.append(node[0])
        
            if len(node_links) == 2: 

                len_h = heuristic(_nodes[node_links[0]][1], _nodes[node_links[1]][1])
                mean_dia = diameter_mean(list_in, self.diameter)
                quadrant = position_vessel(_nodes[node_links[0]][1], _nodes[node_links[1]][1], self.part_clock)
                tor = tortuosity(len(list_in)+3, len_h )
   
                self.graph.add_edge(node_links[0], node_links[1],len_list = (len(list_in)+3) / self.radius/0.0001, len_heur = (len_h/ self.radius/0.0001), diameter = (mean_dia / self.radius/0.0001), quadrant = quadrant, tor = tor)#, hsv = mean_hsv
                
            id = id+1
        
        list_node_to_remove = []
        for node in self.graph.nodes:
            if self.graph.degree(node) > 1:
                self.graph.nodes[node]['_endpoint'] = False
            
            elif self.graph.degree(node) == 0:
                list_node_to_remove.append(node)

            else :
                self.graph.nodes[node]['_endpoint'] = True
        
        for node in list_node_to_remove:
            self.graph.remove_node(node)

        del node_links, edges, nodes_img, region_nodes, _nodes, list_node_to_remove







