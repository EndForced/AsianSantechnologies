zones = {
}
cam2_floor1 = [[(74,226),(247,410)], [(269,240),(449,388)],
               [(4,408),(267,624)], [(278,430),(474,594)]]

cam2_floor2 = [[(66,215),(270,369)],[(261,220),(447,369)],
                [(7,361),(286,638)],[(273,368),(475,640)]]

sec_fl_mid2 =[(233, 151), (534, 170), (574, 321), (563, 478), (196, 482), (233, 152), (237, 151), (237, 151)]


import cv2
import numpy as np


def update_frame_smart(frame):
    result_frame = frame.copy()
    list_of_slices = []

    for i, ((pt1_floor1, pt2_floor1), (pt1_floor2, pt2_floor2)) in enumerate(zip(cam2_floor1, cam2_floor2)):
        floor1_slice = frame[pt1_floor1[1]:pt2_floor1[1], pt1_floor1[0]:pt2_floor1[0]].copy()
        floor2_slice = frame[pt1_floor2[1]:pt2_floor2[1], pt1_floor2[0]:pt2_floor2[0]].copy()
        _, dominant_color = lead_color(floor1_slice)

        if dominant_color == "black":
            cv2.rectangle(result_frame, pt1_floor2, pt2_floor2, (0, 0, 255), 4)
            list_of_slices.append(floor2_slice)
            cv2.putText(result_frame, f"floor2_{i}", (pt1_floor2[0], pt1_floor2[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)


        else:
            cv2.rectangle(result_frame, pt1_floor1, pt2_floor1, (0, 255, 0), 2)
            list_of_slices.append(floor1_slice)
            cv2.putText(result_frame, f"floor1_{i}", (pt1_floor1[0], pt1_floor1[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)


    return result_frame, list_of_slices


def lead_color(img_slice, threshold=0.5):
    gray = cv2.cvtColor(img_slice, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    white_pixels = np.sum(binary == 255)
    total_pixels = binary.size

    white_ratio = white_pixels / total_pixels
    result = "white" if white_ratio > threshold else "black"

    cv2.putText(img_slice, result, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    return img_slice, result



