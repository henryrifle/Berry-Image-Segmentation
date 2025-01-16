# Berry Image Segmentation Project

## Project Overview
This color filter code is used to filter out non berry photos by using the hsv values of the red berries.
First the program separates all contours using the segmentation pipline 
After the images contours are found the color filter function will separate all the berry contours from the others


## Technologies Used
- **Programming Language**: Python
- **Libraries and Frameworks**: 
  - mathplotlib
  - opencv(cv2)
  - numpy
  - skimage
  -  glob
  -  scipy
  -  os
  - pillow
- **All Requirements in requirements.txt**



## Instruction
This code is runnable on both mac and windows with only slight adjustments.
Before running be sure to check you are running the correct version of the code which will be commented in the top left of the code.

All changes needed to be made to run this code on your personal device can be made in the main block,the following changes are below:

- Replace  path_to _image variable with the path to the image you want to segment
- Replace img_save_location to the path of the directory you would like to save you images (ends with Image because that is what all segmented images will be labeled )
- Replace os_walk_directory variable with the path of the directory you would like to walk through checking for images that were previously saved
- Replace exclude_set variable with all the directorys you wish not to walk through to check images



## Future Scope
- **Improve Accuracy of the segmentation**
- **Expand to segemnt the Berry Bush images**

## Contributors
- **Henry Kern**
  





