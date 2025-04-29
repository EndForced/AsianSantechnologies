import cv2
import numpy as np


class VisualizeMatrix:
    import cv2
    import numpy as np
    def __init__(self, matrix, picture):
        self.matrix = matrix
        self.picture = picture
        self.pictureResolution = self.picture.shape()

pic = np.zeros((600,600))
cv2.imshow(pic)
cv2.waitKey(0)