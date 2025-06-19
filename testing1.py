from RaspberriScripts.CvProcessing.CellDetector import check_for_borders, count_pixels, process_image
import numpy as np
import cv2

# Пример использования
if __name__ == "__main__":
    cv2.imshow("o", process_image(cv2.imread("Warped.png")))
    cv2.waitKey(0)