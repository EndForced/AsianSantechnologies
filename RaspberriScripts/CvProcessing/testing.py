import cv2

from CellDetector import *

# Пример использования
frame = cv2.imread("zones_output.jpg")
# corrected_frame = fix_perspective(frame)
processed_frame, cells, borders = analyze_frame(frame, floor=1)
cv2.imshow("tile", processed_frame)
cv2.waitKey(0)

# for key, item in cells.items():
#     if str(item) != "unr":
#         cv2.imshow("tile", item)
#         print(tile_to_code(item))
#         cv2.waitKey(0)
