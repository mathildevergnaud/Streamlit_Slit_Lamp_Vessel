import skimage.measure
from skimage.io import imread, imsave
import networkx as nx
import heapq
import cv2

import skimage
import numpy
import PIL

#from utils.quantification.create_graph import create_graph

import csv
import glob ,os
from datetime import datetime



def countpixelwhite(image):
    countpixel = 0
    for pixel in image.flatten():
        
        if pixel== 255: 
            countpixel+=1

    return countpixel


class vessel_caracterisation() :

    def __init__(self,graph,  area = 'eyes'):

        self.H = graph

        if area != 'eyes':
            print(area)

            #self.H = nx.Graph([(u,v,d)for (u,v,d) in  self.graph.edges(data=True) if d['quadrant']==area])
            self.H.remove_edges_from([(u,v,d) for (u,v,d) in  self.H.edges(data=True) if d['quadrant']!=area])
            self.H.remove_nodes_from(list(nx.isolates(self.H)))



    def Lenght_between_2_junction(self):

        cumul = 0
        median = []
        max_v = 0
        min_v = 100000 

        dash = 0

        if self.H.number_of_edges() > 0:

            for edge in self.H.edges(data=True):

                cumul += edge[2]['len_list']
                median.append(edge[2]['len_list'])

                if max_v < int(edge[2]['len_list']):
                    max_v = int(edge[2]['len_list'])
                
                elif min_v > int(edge[2]['len_list']):
                    min_v =int(edge[2]['len_list'])

            moyen = cumul / len(self.H.edges)
            median.sort()

            index = median[int(len(median)/2)]
            index25 = median[int(len(median)/4)]
            index75 = median[int(len(median)*3/4)]
            index5 = median[int(len(median)*0.05)]
            index95 = median[int(len(median)*0.95)]

            #print(min,max,moyen,index)

            #print(index, index25, index5)

            #print(float(min_v),float(max_v),float(moyen), float(index), float(index25), float(index75), float(index5),float(index95) )

            return float(min_v) ,float(max_v),float(moyen), float(index), float(index25), float(index75), float(index5),float(index95), float(cumul)
        
        else :
            return 0, 0, 0, 0, 0, 0, 0, 0 ,0

        

    def Lenght_max_vessel(self):

        _node_for_path = []

        for node in self.graph.nodes :
            _endpoint = self.graph.nodes[node]['_endpoint']

            if _endpoint == True: 
                _node_for_path.append(node)

            _lght_weight = 0

        for start in _node_for_path:
            for target in _node_for_path: 

                if start != target  and nx.has_path(self.graph, start, target) == True : 

                    res =nx.dijkstra_path_length(self.graph, start, target, weight='len_list')
                    if res > _lght_weight:
                       _lght_weight = res
        
        #ratio_lght_weight = _lght_weight/ self.radius *100
        #print(ratio_lght_weight)

        return _lght_weight#ratio_lght_weight
    
    def number_junction_endpoint(self):

        junctions = 0
        endpoints = 0

        for node in self.H.nodes :

            if self.H.nodes[node]['_endpoint'] == True :
                endpoints = endpoints + 1

            if self.H.nodes[node]['_endpoint'] == False:
                junctions = junctions + 1 

        return endpoints, junctions

    
    def Diameter_vessel(self):
        moyen = 0
        median = []
        max_d = 0
        min_d = 100000


        if self.H.number_of_edges() > 0:

            for edge in self.H.edges(data=True):

                moyen += edge[2]["diameter"]
                median.append(edge[2]["diameter"])

                if max_d < int(edge[2]["diameter"]):
                    max_d = int(edge[2]["diameter"])
                
                elif min_d > int(edge[2]["diameter"]):
                    min_d = edge[2]["diameter"]

            moyen = moyen / len(self.H.edges)
            median.sort()

            index = median[int(len(median)/2)]

            index = median[int(len(median)/2)] 
            index25 = median[int(len(median)/4)] 
            index75 = median[int(len(median)*3/4)] 
            index5 = median[int(len(median)*0.05)] 
            index95 = median[int(len(median)*0.95)] 

            return float(min_d),float(max_d),float(moyen), float(index), float(index25), float(index75), float(index5),float(index95) 
        else :
            return 0, 0, 0, 0, 0, 0, 0, 0 


    
    def percent_vessel(self):

        #plt.imshow(self.clock_cornea.image)
        #plt.show()

        countpixelcornea = countpixelwhite(self.image_clock)
        countpixelvessel = countpixelwhite(self.image)

        #print('pix cornea : ',countpixelcornea, ' pix vessel : ', countpixelvessel)

        percent_vessel_cornea = countpixelvessel/ countpixelcornea*100

        #print(percent_vessel_cornea)

        return percent_vessel_cornea
    
    def tortuosity(self):

        moyen = 0
        median = []
        max_d = 0
        min_d = 100000


        if self.H.number_of_edges() > 0:

            for edge in self.H.edges(data=True):

                moyen += edge[2]["tor"]
                median.append(edge[2]["tor"])

                if max_d < int(edge[2]["tor"]):
                    max_d = int(edge[2]["tor"])
                
                elif min_d > int(edge[2]["tor"]):
                    min_d = edge[2]["tor"]

            moyen = moyen / len(self.H.edges)
            median.sort()

            index = median[int(len(median)/2)]

            index = median[int(len(median)/2)]
            index25 = median[int(len(median)/4)]
            index75 = median[int(len(median)*3/4)]
            index5 = median[int(len(median)*0.05)]
            index95 = median[int(len(median)*0.95)]

            return float(min_d),float(max_d),float(moyen), float(index), float(index25), float(index75), float(index5),float(index95) 
        else :
            return 0, 0, 0, 0, 0, 0, 0, 0     
