import skimage.measure
from skimage.io import imread, imsave
import networkx as nx
import heapq
import cv2

import skimage
import numpy
import PIL

from utils.quantification.create_graph import create_graph


import matplotlib.pyplot as plt

import csv
import glob ,os
from datetime import datetime

def countpixelwhite(image):
    countpixel = 0
    for pixel in image.flatten():
        
        if pixel== 255: 
            countpixel+=1

    return countpixel

def _load_images(data_path, image_folder):
    """Charge toutes les images depuis le répertoire spécifié"""
    image_files = [f for f in os.listdir(os.path.join(data_path, image_folder)) 
                    if f.lower().endswith(('.png', '.jpg', '.jpeg','.tif','.tiff','.JPG'))]
    
    return sorted(image_files)

def extract_info(pairs):

    name_im = pairs[0].split('/')[-1]

    text,*_ = name_im.split(".")

    x = text.split("_")
    typ = x[0]+x[1]
    date = x[4]+x[5]+x[6]
    lr = x[3]

    date = datetime.strptime(date, '%d%m%y').date()

    im_info = None

    if lr[0] == 'R':

        #print('r')

        cornea =  PIL.Image.open(pairs[1]).convert('L')
        cornea = numpy.array(cornea)

        orimage = PIL.Image.open(pairs[2])
        orimage = numpy.array(orimage)

        seg = PIL.Image.open(pairs[0]).convert('L')
        seg = numpy.array(seg)

        im_info = {"class":typ , "date":date, 'side:':lr, 'name': name_im, 'or': orimage, 
                'seg' : seg, 'cornea' : cornea, 'junction' : None, 'endpoint' : None, '%vessel/cornea' : None, 
                'diameter_min' : None, 'diameter_max' : None, 'diameter_moy' : None, 'diameter_med' : None,
                'vessel_min' : None, 'vessel_max' : None, 'vessel_moy' : None, 'vessel_med' : None,
                'lenghest_path': None}

    if lr[0] == 'L': 


        cornea =  PIL.Image.open(pairs[1]).convert('L').transpose(PIL.Image.FLIP_LEFT_RIGHT)
        cornea = numpy.array(cornea)

        orimage = PIL.Image.open(pairs[2]).transpose(PIL.Image.FLIP_LEFT_RIGHT)
        orimage = numpy.array(orimage)

        seg = PIL.Image.open(pairs[0]).convert('L').transpose(PIL.Image.FLIP_LEFT_RIGHT)
        seg = numpy.array(seg)

        im_info = {"class":typ , "date":date, 'side:':lr, 'name': name_im, 'or': orimage, 
                'seg' : seg, 'cornea' : cornea, 'junction' : None, 'endpoint' : None, '%vessel/cornea' : None, 
                'diameter_min' : None, 'diameter_max' : None, 'diameter_moy' : None, 'diameter_med' : None,
                'vessel_min' : None, 'vessel_max' : None, 'vessel_moy' : None, 'vessel_med' : None,
                'lenghest_path': None,
                'middle' : None, 'left' : None, 'bottom' : None, 'right' : None, 'top' : None,
                'tor_min' : None, 'tor_max' : None, 'tor_moy' : None, 'tor_med' : None}

    return im_info

class vessel_caracterisation() :

    def __init__(self,graph,  area = 'eyes'):

        self.H = graph

        if area != 'eyes':
            print(area)

            #self.H = nx.Graph([(u,v,d)for (u,v,d) in  self.graph.edges(data=True) if d['quadrant']==area])
            self.H.remove_edges_from([(u,v,d) for (u,v,d) in  self.H.edges(data=True) if d['quadrant']!=area])
            self.H.remove_nodes_from(list(nx.isolates(self.H)))

    def Lenght_between_2_junction(self):

        moyen = 0
        median = []
        max_v = 0
        min_v = 100000 

        dash = 0

        if self.H.number_of_edges() > 0:

            for edge in self.H.edges(data=True):

                moyen += edge[2]['len_list']
                median.append(edge[2]['len_list'])

                if max_v < int(edge[2]['len_list']):
                    max_v = int(edge[2]['len_list'])
                
                elif min_v > int(edge[2]['len_list']):
                    min_v =int(edge[2]['len_list'])


            print('dash',dash)
            moyen = moyen / len(self.H.edges)
            median.sort()

            index = median[int(len(median)/2)]
            index25 = median[int(len(median)/4)]
            index75 = median[int(len(median)*3/4)]
            index5 = median[int(len(median)*0.05)]
            index95 = median[int(len(median)*0.95)]

            #print(min,max,moyen,index)

            print(index, index25, index5)

            print(float(min_v),float(max_v),float(moyen), float(index), float(index25), float(index75), float(index5),float(index95) )

            return float(min_v) ,float(max_v),float(moyen), float(index), float(index25), float(index75), float(index5),float(index95)
        
        else :
            return 0, 0, 0, 0, 0, 0, 0, 0 

        

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

        print('pix cornea : ',countpixelcornea, ' pix vessel : ', countpixelvessel)

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

if __name__ == "__main__":

    # Data path
    data_path = 'data_t' #data

    ### Folder 
    vessel_name = 'vessel'
    cornea_name = 'cornea'
    original_name = 'original'

    # Load images
    vessel_folder = _load_images(data_path,vessel_name)
    cornea_folder  = _load_images(data_path, cornea_name)
    original_folder = _load_images(data_path, original_name)

    pairs = []

    for img_file in vessel_folder:
        for mask_file in cornea_folder:
            for original_file in original_folder:

                img = img_file.split('.')[0]
                mask = mask_file.split('.')[0]
                original = original_file.split('.')[0]


                if img == mask and original == mask:
                    pairs.append([os.path.join(data_path,vessel_name, img_file),os.path.join(data_path ,cornea_name ,mask_file ),os.path.join(data_path, original_name, original_file)])

            for p in pairs:
                im_info = extract_info(p)

                v_c = vessel_caracterisation(im_info['seg'], im_info['cornea'])

                im_info['%vessel/cornea']=v_c.percent_vessel()

                im_info['diameter_min'],im_info['diameter_max'], im_info['diameter_moy'], im_info['diameter_med'] = v_c.Diameter_vessel()
                im_info['vessel_min'],im_info['vessel_max'], im_info['vessel_moy'], im_info['vessel_med'] = v_c.Lenght_between_2_junction()
                #im_info['lenghest_path'] = v_c.Lenght_max_vessel()
                im_info['endpoint'], im_info['junction'] = v_c.number_junction_endpoint()
                im_info['middle'], im_info['left'], im_info['bottom'], im_info['right'], im_info['top'] = v_c.position_vessel()
                im_info['tor_min'],im_info['tor_max'], im_info['tor_moy'], im_info['tor_med'] = v_c.tortuosity()



    #for name in os.listdir(".data"):#"./3Mounths/seg/"
        
    #    print(name)
    #    vessel = vessel_caracterisation('./6Mounths/High/seg/'+name)
    #    #vessel('./vessel_seg/'+name) #'03010_Visit6_2_12Aug2010.png'
    #    vessel.define_position_cornea_('./6Mounths/High/mask/'+ name )
    #    vessel.position_vessel()
    #    vessel.Lenght_between_2_junction()
    #    vessel.Diameter_vessel()
        #vessel.define_junction() #'./cornea/03010_Visit1_1_10Dec2009.png'
        #vessel.define_edges()

    #    min_vessel, max_vessel, moyen_vessel, median_vessel = vessel.Lenght_between_2_junction()

    #    middle, left , bottom,  right, top  = vessel.position_vessel()

        #Lenght_max = vessel.Lenght_max_vessel()

    #    percent_vessel =vessel.percent_vessel()

    #    min_diameter, max_diameter, moyen_diameter, median_diameter =  vessel.Diameter_vessel()

    #    nx.draw(vessel.graph)  
    #    plt.savefig('graph_im.png')
    #    plt.show()

        # save_data = []

        # save_data.append({'Name' : name , 'Percent_vessel' : percent_vessel,'Min_Lenght_Vessel' : min_vessel,'Max_Lenght_Vessel' : max_vessel, 
        #                 'Moyen_Lenght_Vessel' : moyen_vessel,'Median_Lenght_Vessel': median_vessel,'Middle' : middle,'Left' : left,'Top' : top, 'Right': right,'Bottom' : bottom,
        #                 'Min_Lenght_Diameter' : min_diameter,'Max_Lenght_Diameter' : max_diameter, 'Moyen_Lenght_Diameter' : moyen_diameter,'Median_Lenght_Diameter': median_diameter})
        

        # with open('results_6Mounths_High.csv', 'a', newline='') as csvfile: #3Mounths/Low/
        #     fieldnames= ['Name', 'Percent_vessel','Min_Lenght_Vessel','Max_Lenght_Vessel', 'Moyen_Lenght_Vessel','Median_Lenght_Vessel','Middle','Left','Top',
        #                     'Right','Bottom' , 'Min_Lenght_Diameter','Max_Lenght_Diameter', 'Moyen_Lenght_Diameter','Median_Lenght_Diameter']
            
        #     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        #     writer.writeheader()

        #     for data in save_data:

        #         writer.writerow(data)   
        

        # del(vessel)
