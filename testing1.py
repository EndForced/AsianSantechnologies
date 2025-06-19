from RaspberriScripts.CvProcessing.CellDetector import check_for_borders

import cv2
a = cv2.imread("Warped.png")
print(check_for_borders(a, 1))
a = a[-70:-30,-450:-100:]
cv2.imshow("a",a)
cv2.waitKey(0)
cv2.imwrite("border.png", a)