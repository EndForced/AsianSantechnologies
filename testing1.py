from RaspberriScripts.CvProcessing.CellDetector import check_for_borders, count_pixels, process_image
import numpy as np
import cv2

img = cv2.imread("Warped.png")
b, frame = check_for_borders(img, 1)
cv2.imshow("o",frame)
cv2.waitKey(0)