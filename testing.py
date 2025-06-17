import cv2
a = cv2.imread("Warped.png")
a = a[-100:,:]
cv2.imshow("a",a)
cv2.waitKey(0)
cv2.imwrite("border.png", a)