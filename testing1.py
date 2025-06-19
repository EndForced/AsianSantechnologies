from RaspberriScripts.CvProcessing.CellDetector import check_for_borders, count_pixels, process_image
import numpy as np
import cv2

img = cv2.imread("Warped.png")
img = img[-70:-30,-450:-100:]
cv2.imshow("o", img)
cv2.imwrite("border.png", img)
cv2.waitKey(0)