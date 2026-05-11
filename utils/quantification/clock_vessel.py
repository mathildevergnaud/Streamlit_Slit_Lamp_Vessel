import PIL 
import cv2
import numpy

from skimage import measure

import matplotlib.pyplot as plt

#from utils.create_graph import create_graph
import os

#import math

def test_in_the_midle(x, y, r , centeri, centerj):
    if  pow(x-centeri,2)+ pow(y-centerj,2) <= pow(r,2):
        return True

    else: return False

def test_bellow_the_line(x_h,y_h,x_b,y_b,ytest,xtest):

    #newrefy0 = image.shape[1] - y0
    #newrefy1 =image.shape[1] -  y1
    #newrefytest = image.shape[1] - ytest #image.shape[1] - 

    a = (int(y_h)-int(y_b)) /(int(x_h)-int(x_b)) 
    b =-a*x_h+y_h 

    r = a*(xtest)-(ytest) +b

    return r

class clock():
    image_clock = []
    part_clock = []
    diameter = []
    radius = 0

    def __init__(self,image):
        self.image_clock = image
        self.define_clock()

    def define_clock (self):

        #contours = measure.find_contours(self.image, 0.8)

        box = cv2.boundingRect(self.image_clock)

        x_0 = box[0]+box[2]
        y_0 = box[1]

        x_1 = box[0]
        y_1 = box[1]+box[3]

        new_im = cv2.cvtColor(self.image_clock,cv2.COLOR_GRAY2RGB)*255
        self.diameter = (box[2]+box[3])/2

        cnt, _ = cv2.findContours((self.image_clock*255.0).astype(numpy.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        print(len(cnt))
        #print(cv2.minEnclosingCircle(cnt[1]))
        maxel = cnt[0]
        for el in cnt:

            el1 = cv2.minEnclosingCircle(el)
            el2 = cv2.minEnclosingCircle(maxel)

            #(el1[1], el2[1] )

            if el1[1] > el2[1] :
                maxel = el
                #print(cv2.minEnclosingCircle(maxel)[1]) 

        #print(maxel)

        if cv2.contourArea(maxel) > 150:
            (x,y), radius = cv2.minEnclosingCircle(maxel)
            center = (int(x), int(y))
            self.radius = int(radius)
            print('radius', self.radius)
            cv2.circle(self.image_clock, center, self.radius, (0,255,0), 2)
            
        

        #x,y,w,h = cv2.boundingRect(self.image)
        #cv2.rectangle(new_im,(x,y),(x+w,y+h),(0,255,0),5)
        #plt.imshow(self.image)
        #plt.show()

        for i in range (self.image_clock.shape[0]):
            for j in range (self.image_clock.shape[1]):

                if self.image_clock[i,j] > 0 :
                    #print(box[2]/2)
                    if test_in_the_midle(j,i, (box[2]+box[3])/8 , box[2]/2+box[0], box[3]/2+box[1]) == True:
                        new_im[i,j,] = [255,0,0]

                    else : 
                        r1 = test_bellow_the_line(x_1, y_0,x_0,y_1, i,j )
                        r2 = test_bellow_the_line(x_0,y_0, x_1,y_1,i,j )

                        if r1 >= 0 and r2 >= 0 :
                            new_im[i,j,] = [0,0,255]

                        elif r1 >= 0 and r2  < 0 : 
                            new_im[i,j,] = [255,255,0]
                        
                        elif r1 < 0 and r2 >= 0 :
                             new_im[i,j,] = [255,0,255]
                            
                        else:
                            new_im[i,j,] = [0,255,0]
        plt.imshow(new_im)
        plt.show()

        self.part_clock = new_im


if __name__ == "__main__":
    #g = create_graph() #03_020_HJN_LA_26_01_06.tiff')#test_im.tiff')06_060_MW_RA_08_03_07_2.tiff

    for name in os.listdir("./figures/Image/"):
        
        cornea = PIL.Image.open("./figures/Mask_ROI/"+name).convert('L')
        cornea = numpy.array(cornea)
        
        image = clock(cornea)
        
        orimage = PIL.Image.open("./figures/Image/"+name).convert('RGBA')
        
        
        new_part = PIL.Image.fromarray(image.part_clock).convert('RGBA')
        
        cor_part = PIL.Image.blend(orimage, new_part, 0.1)

        cor_part.save('03_017.png')
        
        plt.imshow(cor_part)
        plt.show()



