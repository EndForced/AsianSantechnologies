import cv2
import numpy as np

frame = np.array(cv2.imread("tst.png"))

mean_r = np.mean(frame[:,:,0])
mean_g = np.mean(frame[:,:,1])
mean_b = np.mean(frame[:,:,2])

print(mean_r, mean_g, mean_b)