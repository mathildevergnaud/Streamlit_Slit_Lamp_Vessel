import PIL 
import cv2
import numpy

from skimage import measure

import os

def test_in_the_midle(x, y, r , centeri, centerj):
    if  pow(x-centeri,2)+ pow(y-centerj,2) <= pow(r,2):
        return True

    else: return False

def test_bellow_the_line(x_h,y_h,x_b,y_b,ytest,xtest):

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
        
        box = cv2.boundingRect(self.image_clock)

        x_0 = box[0]+box[2]
        y_0 = box[1]

        x_1 = box[0]
        y_1 = box[1]+box[3]

        new_im = cv2.cvtColor(self.image_clock,cv2.COLOR_GRAY2RGB)*255
        self.diameter = (box[2]+box[3])/2

        cnt, _ = cv2.findContours((self.image_clock*255.0).astype(numpy.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        maxel = cnt[0]
        for el in cnt:

            el1 = cv2.minEnclosingCircle(el)
            el2 = cv2.minEnclosingCircle(maxel)

            if el1[1] > el2[1] :
                maxel = el

        if cv2.contourArea(maxel) > 150:
            (x,y), radius = cv2.minEnclosingCircle(maxel)
            center = (int(x), int(y))
            self.radius = int(radius)
 
            cv2.circle(self.image_clock, center, self.radius, (0,255,0), 2)

        for i in range (self.image_clock.shape[0]):
            for j in range (self.image_clock.shape[1]):

                if self.image_clock[i,j] > 0 :

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

        self.part_clock = new_im




