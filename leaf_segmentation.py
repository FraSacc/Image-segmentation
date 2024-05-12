# -*- coding: utf-8 -*-
"""
Created on Mon Jun 12 16:42:17 2023

@author: sacco004
"""
import easygui as egui
import os
import cv2
import numpy as np

def scale_bar_finder(img,value):
    #Find color black
    mask_black = cv2.inRange(hsv,(0,254,0),(255,255,2))
    
    #Apply mask to image
    res_black = cv2.bitwise_and(img, img, mask=mask_black)
    
    #Convert image to greyscale and find contour
    gray_black = cv2.cvtColor(res_black, cv2.COLOR_BGR2GRAY)
    contour_black = cv2.findContours(gray_black, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    
    #find boundaries of scale bar
    my_list = [[],[]]
    for j in range(2):
        for i in contour_black:
            my_list[j].append(i[0][0][j])
    scale_bar=[np.min(my_list[0]),np.max(my_list[0]),np.min(my_list[1]),np.max(my_list[1])]
    
    #Calculate cm2/pixel
    d=np.sqrt((scale_bar[1]-scale_bar[0])**2+(scale_bar[3]-scale_bar[2])**2) #d=sqrt((x1-x0)**2+(y1-y0)**2)
    scale=(value/d)**2
    return scale_bar,scale

def contour_finder(img,color_space):
    # find the green color 
    mask_green = cv2.inRange(hsv, (36,50,100), (86,250,250))
    
    # Bitwise-AND mask and original image
    res = cv2.bitwise_and(img,img, mask= mask_green)
    
    # Find contour of plant
    gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)    # Make a grey image first
    contours= cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    return res, gray, contours

def area_counter(gray):
    #Fill the contour with polygons
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
    opening = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel, iterations=2)
    
    counter=0
    for i in opening:
        for j in i:
            if j>0:
                counter+=1
    area=scale*counter #cm2

    return opening, area

''' Main code '''

path = str(egui.fileopenbox("Select Images to Analyse")) #selec
current_dir = str(os.path.dirname('/'.join(path.split('\\'))))
os.chdir(current_dir)
base_path = os.getcwd()
files = filter(os.path.isfile, os.listdir( os.curdir))
files = [ff for ff in os.listdir('.') if os.path.isfile(ff)]
data_files = [x for x in files if x.endswith(".jpg")]

for image in data_files:
    im =  cv2.imread(image)
    img = cv2.resize(im, None, fx = 0.2, fy = 0.2)                # Resize image to make it fit
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)      # Define hsv color space
    
    scale_bar,scale = scale_bar_finder(img)
    res, gray, contours = contour_finder(img,hsv)
    opening,area=area_counter(gray)
    
    for i in contours:
        cv2.drawContours(gray,[i], 0, (255,255,255), -1)
    
    cv2.drawContours(img, contours, -1, (255,0,0), thickness = 2)
    cv2.line(img,(scale_bar[0],scale_bar[2]),(scale_bar[1],scale_bar[3]),(100,0,0),5)
    cv2.imshow("Original", img)
    cv2.imshow("Masked", res)
    cv2.imshow('opening', opening)
    
    cv2.imwrite(f"{image.split('.')[0]}_Original.png", img)
    # cv2.imwrite("Masked.png", res)
    # cv2.imwrite("Binary.png", opening)
    
    cv2.imwrite("with_scalebar.png",img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    np.sqrt(area)


