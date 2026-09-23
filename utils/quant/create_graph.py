import skimage.measure
import skimage.morphology
from PIL import Image

import matplotlib.cm as cm

import networkx as nx
import cv2

import skimage
import numpy
import numpy as np

import os
import math

import matplotlib.pyplot as plt

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


def plot(X, labels, probabilities=None, parameters=None, ground_truth=False, ax=None):
    if ax is None:
        _, ax = plt.subplots(figsize=(10, 4))
    labels = labels if labels is not None else np.ones(X.shape[0])
    probabilities = probabilities if probabilities is not None else np.ones(X.shape[0])
    # Black removed and is used for noise instead.
    unique_labels = set(labels)
    colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]
    # The probability of a point belonging to its labeled cluster determines
    # the size of its marker
    proba_map = {idx: probabilities[idx] for idx in range(len(labels))}
    for k, col in zip(unique_labels, colors):
        if k == -1:
            # Black used for noise.
            col = [0, 0, 0, 1]

        class_index = (labels == k).nonzero()[0]
        for ci in class_index:
            ax.plot(
                X[ci, 0],
                X[ci, 1],
                "x" if k == -1 else "o",
                markerfacecolor=tuple(col),
                markeredgecolor="k",
                markersize=4 if k == -1 else 1 + 5 * proba_map[ci],
            )
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    preamble = "True" if ground_truth else "Estimated"
    title = f"{preamble} number of clusters: {n_clusters_}"
    if parameters is not None:
        parameters_str = ", ".join(f"{k}={v}" for k, v in parameters.items())
        title += f" | {parameters_str}"
    ax.set_title(title)
    plt.tight_layout()

def heuristic(node, goal):
    d1 = abs(int(node[0]) - int(goal[0]))
    d2 = abs(int(node[1]) - int(goal[1]))
    #d = math.sqrt(math.pow(int(node[0]) - int(goal[0]),2) + math.pow(int(node[1]) - (goal[1]),2))

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
    
    #plt.imshow(color1)
    #plt.show()

    for i in range(color1.shape[0]):
       for j in range(color1.shape[1]):
           sum_col = color1[i][j][0]+color1[i][j][1]+color1[i][j][2]
           if image [i][j]> 0.0 and sum_col == 0: 
               color1[i][j] =[255.0,255.0,255.0] 


    #fig, ax = plt.subplots()
    #ax.imshow(color1, cmap=plt.cm.gray)

    #for props in region_nodes:

    #    minr, minc, maxr, maxc = props.bbox
    #    bx = (minc-1, maxc+1, maxc+1, minc-1, minc-1)
    #    by = (minr-1, minr-1, maxr+1, maxr+1, minr-1)

        #ax.plot(bx, by, '-r', linewidth=2.5)

    #plt.show()

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

        plt.imshow(image_or)
        plt.show()

        self.skel, self.diameter = skimage.morphology.medial_axis(self.image, return_distance=True)
        
        self.skel = skimage.morphology.skeletonize(self.image , method='lee')
        self.skel = skimage.morphology.area_opening(self.skel, 30, connectivity=8)
        
        #plt.imshow(self.skel,cmap='gray')
        #plt.show()

        #plt.imshow(self.diameter)
        #plt.show()

        #Image.fromarray(self.skel).save('./skel_cat.png', 'PNG')
        #self.hsv_im = cv2.cvtColor(self.hsv_im, cv2.COLOR_RGB2HSV)

        self._graph()

        #pos = nx.get_node_attributes(self.graph, 'info')
        #pos_correct = {n: (y, x) for n,(x,y) in pos.items()}

        # color_map = []

        # for node in self.graph.nodes:

        #     if self.graph.nodes[node]['_endpoint'] != True:

        #         color = "#094446"
        #         color_map.append(color)

        #     else :

        #         color = "#B33102"
        #         color_map.append(color)
        # #print(pos)
        # plt.imshow(image_or, origin="lower")



        # nx.draw(self.graph, pos_correct, with_labels=False, node_color=color_map, node_size=10)

        # #plt.xlim(0,image_or.shape[1])
        # #plt.ylim(0,image_or.shape[0])
        # plt.show()

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

            #bbox = props.bbox[0]-1,  props.bbox[1]-1, props.bbox[2]+1,  props.bbox[3]+1 
            bbox = props.bbox[0]-1,  props.bbox[1]-1, props.bbox[2]+1,  props.bbox[3]+1

            _nodes.append([node_id,props.centroid,bbox])
                
            self.graph.add_node(node_id, info = [int(props.centroid[0]),int(props.centroid[1])])
            node_id = node_id +1

        id = 0
        for list_in in edges:
           
            node_links = []
            #print(len(list_in), list_in)

            for node in _nodes:

                object = test_in_list(node, list_in)

                if object == True:
                    node_links.append(node[0])
        
            if len(node_links) == 2: 

                len_h = heuristic(_nodes[node_links[0]][1], _nodes[node_links[1]][1])

                mean_dia = diameter_mean(list_in, self.diameter)



                quadrant = position_vessel(_nodes[node_links[0]][1], _nodes[node_links[1]][1], self.part_clock)

                #mean_hsv = hsv_mean(list_in, self.hsv_im)
                #print(mean_hsv)


                #print('id : ', id,node_links, 'len_list :', len(list_in), 'len_h :', len_h, 'mean_diameter' , mean_dia)
                #if mean_hsv[0] > 360.0 or mean_hsv[0] < 30.0 :

                tor = tortuosity(len(list_in)+3, len_h )
   
                self.graph.add_edge(node_links[0], node_links[1],len_list = (len(list_in)+3) / self.radius/0.0001, len_heur = (len_h/ self.radius/0.0001), diameter = (mean_dia / self.radius/0.0001), quadrant = quadrant, tor = tor)#, hsv = mean_hsv
                
            id = id+1
        
        list_node_to_remove = []
        for node in self.graph.nodes:
            if self.graph.degree(node) > 1:
                self.graph.nodes[node]['_endpoint'] = False
            
            elif self.graph.degree(node) == 0:
                list_node_to_remove.append(node)
                #self.graph.remove_node(node)

            else :
                self.graph.nodes[node]['_endpoint'] = True
        
        for node in list_node_to_remove:
            self.graph.remove_node(node)

        del node_links, edges, nodes_img, region_nodes, _nodes, list_node_to_remove







