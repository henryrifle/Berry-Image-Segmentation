# Mac Os Version

#Required Imports

import matplotlib.pyplot as plt
import cv2
import numpy as np
from skimage import io,measure
import glob
from scipy import ndimage
import os.path
import pandas as pd
from scipy import ndimage as nd
from skimage.color import label2rgb
import os
from matplotlib import pyplot as plt
from skimage import io,measure
from PIL import Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

def find_contours(img):
    """Remove noise and find countours from the image
    Args:
        img: image file (cv2)
    Return:
        contours and rgb image
    
    """
    # SEGMENTATION
    img = cv2.imread(img)  
    b,g,r = cv2.split(img)
    rgb_img = cv2.merge([r,g,b])
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    
    # noise removal
    kernel = np.ones((2,2),np.uint8)
    #opening = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel, iterations = 2)
    closing = cv2.morphologyEx(thresh,cv2.MORPH_CLOSE,kernel, iterations = 2)
    # sure background area
    sure_bg = cv2.dilate(closing,kernel,iterations=3)
    # Finding sure foreground area
    dist_transform = cv2.distanceTransform(sure_bg,cv2.DIST_L2,3)
    # Threshold
    ret, sure_fg = cv2.threshold(dist_transform,0.1*dist_transform.max(),255,0)
    # Finding unknown region
    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(sure_bg,sure_fg)
    # Marker labelling
    ret, markers = cv2.connectedComponents(sure_fg)
    # Add one to all labels so that sure background is not 0, but 1
    markers = markers+1
    # Now, mark the region of unknown with zero
    markers[unknown==255] = 0
    # markers = cv2.watershed(img,markers)
    img[markers == -1] = [255,0,0]
    
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)


    return contours,rgb_img

def segmentation_pipeline(img_path, df, index, img_save_location):
    """segment images and save the info in the df
    Args:
        img_path: image file path (str)
        df: a dataframe consisting all the info
        index: an integer with the value of size of df
    returns:
        save segmented images and return a dataframe with the info
    """
    # Attempt to read the image
    try:
        contours, rgb_img = find_contours(img_path)  # Use img_path instead of path_to_image
    except Exception as e:
        print(f"Error reading image {img_path}: {e}")
        return df  # Return the dataframe without changes if there's an error

    for i in range(len(contours)):
        
        temp = []
        for j in contours[i]:
            temp.append(j[0])

        lst = np.array(temp)
        x_list = sorted(lst, key=lambda x: x[0], reverse=False) #x
        y_list = sorted(lst, key=lambda x: x[1], reverse=False) #y

        x_min = x_list[0][0]
        x_max = x_list[-1][0]
        y_min = y_list[0][1]
        y_max = y_list[-1][1]
        
        if x_min - 10 < 0:
            x_min = 10
        if y_min - 10 < 0:
            y_min = 10

        try:
            single_berry = rgb_img[y_min-10 : y_max+10, x_min-10 : x_max+10]
            #filtering noise images
            if single_berry.shape[0]<40 or single_berry.shape[1]<30:
                continue
            else:
                df.loc[index] = [str(index)+'.png', x_min, x_max,y_min,y_max]
                # save the ROI image in the selected folder
                plt.imsave(img_save_location+str(index)+'.png',rgb_img[y_min-10 : y_max+10, x_min-10 : x_max+10])
                index += 1
        except:
            continue

    #print(df)
    
    return df


def read_images_from_directory(directory,csv_filename):
    """Read the data from a directory and call segmentation pipeline
    Args:
        directory: directory path to read image file
        csv_filename: name to save the dataframe consisting all the info
    """
    # Create an empty list to store the images
    images = []
    df = pd.DataFrame(  columns =  ['Image Filename', 'X Min','X Max','Y Min','Y Max'])

    # Loop through all the subdirectories and files in the given directory
    for root, dirs, files in os.walk(directory):
        # Loop through all the files in the current directory
        print(f"Processing: {root[80:]}")
        for file in files:
            # Check if the file is an image by checking its extension
            if file.endswith('.jpg') or file.endswith('.jpeg') or file.endswith('.png')or file.endswith('.PNG'):
                # Load the image using PIL library
                image = cv2.imread(os.path.join(root, file))
                df = segmentation_pipeline(image,df,len(df))
                print(os.path.join(root, file))
                
                # Append the image to the list of images
                # images.append(image)       
    # Return the list of images
    df.to_csv(csv_filename)
    # return images
    #print(df)

    return

def color_filter(os_walk_directory,exclude_set):
	"""
	filter out all the berries using hsv values

	Args:
	os_walk_directory:string of the path to the directory
	exclude_set:set of all the images you dont want to 

	"""
	counter=1
	#add to exclude certain directories that you dont want
	exclude = exclude_set
	#walks through your directories in choosen path
	for root,dirs, files in os.walk(os_walk_directory,topdown=True):
		dirs[:] = [d for d in dirs if d not in exclude]
		#Loop through all the files in the current directory
		print(f"Processing: {root[80:]}")
		for file in files:
			if file.endswith('.jpg') or file.endswith('.jpeg') or file.endswith('.png') or file.endswith('.PNG'):
				#reads each image
				img=io.imread(os.path.join(root, file))
				#converts image to hsv
				hsv= cv2.cvtColor(img,cv2.COLOR_RGB2HSV)

				#uses hsv values to filter out the red images
				red1=cv2.inRange(hsv,(159,50,70),(180,255,255))  
				red2=cv2.inRange(hsv,(0,50,70),(9,255,255))      
				mask=red1+red2

				closed_mask= nd.binary_closing(mask,np.ones((7,7)))

				label_image=measure.label(closed_mask)
				#finds the perimeter of the image after filtering red

				threshold=measure.perimeter(closed_mask)

				#threshold values determined based on the output of images
				#this range can be adjusted based off of your given results
				if threshold < 195:
					os.remove(os.path.join(root, file))
				if threshold >1000:
					os.remove(os.path.join(root, file))
	return

			

def DataFrame(os_walk_directory,exclude_set):
	"""
	prints out a database of all the berries and the characteristics of each berry

	Args:
	os_walk_directory:string of the path to the directory
	exclude_set:set of all the images you dont want to 

	"""
	counter=1
	df=pd.DataFrame(columns=['area','area_ratio','pixels','equivalent_diameter','eccentricity','mean_intensity'])
	#add to exclude certain directories that you dont want
	exclude = exclude_set
	#walks through your directories in choosen path
	for root,dirs, files in os.walk(os_walk_directory,topdown=True):
		dirs[:] = [d for d in dirs if d not in exclude]
		#Loop through all the files in the current directory
		print(f"Processing: {root[80:]}")
		for file in files:
			if file.endswith('.jpg') or file.endswith('.jpeg') or file.endswith('.png'):
				#reads each image
				img=io.imread(os.path.join(root, file))
				#converts images to hsv
				hsv= cv2.cvtColor(img,cv2.COLOR_RGB2HSV)
				#uses hsv values to filter out the red images
				red1=cv2.inRange(hsv,(159,50,70),(180,255,255))  
				red2=cv2.inRange(hsv,(0,50,70),(9,255,255))      
				mask=red1+red2
				closed_mask= nd.binary_closing(mask,np.ones((7,7)))
				label_image=measure.label(closed_mask)
			
				props=measure.regionprops_table(label_image,img,properties=['area','equivalent_diameter','eccentricity','mean_intensity'])
				print("\nBerry",counter)
				
				#converts image to grayscale
				gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
				thresh = cv2.threshold(gray,0,255,cv2.THRESH_OTSU + cv2.THRESH_BINARY)[1]

				#counts all the nonzero pixels
				pixels = cv2.countNonZero(thresh)
				#pixels = len(np.column_stack(np.where(thresh > 0)))


				#calculates the image area and its ratio
				image_area = img.shape[0] * img.shape[1]
				area_ratio = (pixels / image_area) * 100


				#prints all the data of the database for each berry
				print('pixels', pixels)
				print('area',props['area'][0])
				print('area ratio', area_ratio)
				print("equivalent_diameter",props['equivalent_diameter'][0])
				print('eccentricity',props['eccentricity'][0])
				print('mean_intensity',props['mean_intensity-3'][0])
				df.loc[counter]=[props['area'][0],area_ratio,pixels,props['equivalent_diameter'][0],props['eccentricity'][0],props['mean_intensity-3'][0]]
				counter=counter+1
	print("\n",df)
	return

def clear_berries(os_walk_directory,exclude_set):
	"""
	clear all the berries from the given directory

	Args:
	os_walk_directory:string of the path to the directory
	exclude_set:set of all the images you dont want to 

	"""
	#add to exclude certain directories that you dont want
	exclude = exclude_set
	print(os_walk_directory)
	#walks through your directories in choosen path
	for root,dirs, files in os.walk(os_walk_directory,topdown=True):
		dirs[:] = [d for d in dirs if d not in exclude]
		#Loop through all the files in the current directory
		print(f"Processing: {root[80:]}")
		for file in files:
			if file.endswith('.jpg') or file.endswith('.jpeg') or file.endswith('.png')or file.endswith('.PNG'):
				if file.startswith('Images'):
					os.remove(os.path.join(root, file))
				
	return





if __name__ == '__main__':
	#path to the image you want to use
	path_to_image="/Users/henrykern/Desktop/Resume_Prodjects/Python_Prodjects/USDA/Images/Images/Berry_Bush/ayt_2013_bog10_row9_col1_frame1640_GX010228_cropped.jpg"
	#directory you would want to walk through checking for images
	os_walk_directory="/Users/henrykern/Desktop/Resume_Prodjects/Python_Prodjects/USDA"
	#set of directories you dont want to walk through
	exclude_set=set(["Notes","Programs","Other","Berry_Box_Masks"])
	#location where you would want to save your images
	img_save_location="/Users/henrykern/Desktop/Resume_Prodjects/Python_Prodjects/USDA/Images"
	df = pd.DataFrame(  columns =  ['Image Filename', 'X Min','X Max','Y Min','Y Max']) 
	
	#Functions,remove comments to run

	#segmentation_pipeline(path_to_image,df,len(df),img_save_location)
	#color_filter(os_walk_directory,exclude_set)
	#DataFrame(os_walk_directory,exclude_set)
	#clear_berries(os_walk_directory,exclude_set)
      
	

				

				
				







