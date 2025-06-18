import cv2
import numpy as np
from ZoneProcessor import *

COLOR_RANGES = {
    "Red": (np.array([0, 100, 80]), np.array([20, 255, 255]),
            np.array([150, 100, 80]), np.array([180, 255, 255])),
    "Green": (np.array([65, 90, 90]), np.array([95, 255, 255])),
    "Blue": (np.array([110, 90, 90]), np.array([140, 255, 255]))
}


def search_for_color(frame, color, min_area=50):
    if color not in COLOR_RANGES:
        raise ValueError(f"Unknown color: {color}")

    frame_height, frame_width = frame.shape[:2]
    if color == "Red":
        frame = frame[int(frame_height * 0.1):int(frame_height * 0.9),
                int(frame_width * 0.1):int(frame_width * 0.9)]
        lower1, upper1, lower2, upper2 = COLOR_RANGES[color]
        mask1 = cv2.inRange(frame, lower1, upper1)
        mask2 = cv2.inRange(frame, lower2, upper2)
        mask = cv2.bitwise_or(mask1, mask2)
    else:
        lower, upper = COLOR_RANGES[color]
        mask = cv2.inRange(frame, lower, upper)

    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    x, y, w, h = 0, 0, 0, 0

    for cont in contours:
        area = cv2.contourArea(cont)
        if area > min_area:
            x1, y1, w1, h1 = cv2.boundingRect(cont)
            if w1 * h1 > w * h:
                x, y, w, h = x1, y1, w1, h1

    return x, y, w, h

def tile_to_code(frame):
    if frame.shape[:2] != (200, 200):
        frame = cv2.resize(frame, (200, 200))

    frame_blur = cv2.blur(frame, (5, 5))
    hsv = cv2.cvtColor(frame_blur, cv2.COLOR_BGR2HSV)

    # Поиск зеленых труб
    x, y, h, w = search_for_color(hsv, "Green")
    if h * w:
        if w > h:
            return 61 if (y + h / 2) > 100 else 63
        else:
            return 62 if (x + w / 2) > 100 else 64

    # Поиск синих объектов (рампа)
    xb, yb, hb, wb = search_for_color(hsv, "Blue")
    if hb * wb:
        xr, yr, hr, wr = search_for_color(hsv, "Red")
        delta_x = xb - xr
        delta_y = yb - yr

        if abs(delta_x) < abs(delta_y):
            return 34 if delta_y < 0 else 32
        else:
            return 33 if delta_x < 0 else 31

    # Определение высоты
    elevation = 1 if np.mean(frame_blur) > 150 else 2

    # Поиск красных труб
    x, y, h, w = search_for_color(hsv, "Red")
    if h * w:
        return 32 + elevation * 10 if h / w > 1.2 else 31 + elevation * 10

    return elevation * 10

def process_borders(slices, borders, leads):
    ignore_mask = {i: False for i in range(4)}  # Инициализируем маску

    border_flags = {
        'fc': 'fc' in borders,
        'ff': 'ff' in borders,
        'sc': 'sc' in borders,
        'sf': 'sf' in borders
    }

    #front close = skip
    if border_flags['fc']:
        return {i: True for i in range(4)}

    for i in range(4):
        # front far
        if (i == 2 or i == 3) and border_flags['ff']:
            ignore_mask[i] = True

        # side close
        if (i == 1 or i == 3) and border_flags['sc']:
            ignore_mask[i] = True

        # ignore black behind white
        if i == 2 and leads[0] == "black":
            ignore_mask[i] = True

        if i == 3 and leads[1] == "black":
            ignore_mask[i] = True

    return ignore_mask


def analyze_frame(frame, floor):
    #я пытался делать модульный код (вроде работает)
    result_frame = frame.copy()
    dict_of_slices = {}
    borders = []

    if floor == 1:
        slices = [cv2.resize(extract_warped(frame, cam1floor1[i]), (200, 200)) for i in range(8)]
        borders = check_for_borders(frame, 1)

        leads = []
        for i in range(4):
            leads.append("black" if np.mean(slices[i]) < mean_const else "white")


        ignore_mask = process_borders(slices, borders, leads)


        for i in range(4):
            if ignore_mask[i]:
                dict_of_slices[i] = "unr"
                continue

            if leads[i] == "white":
                result_frame = draw_on_image(result_frame, cam1floor1[i])
                dict_of_slices[i] = slices[i]
            else:
                result_frame = draw_on_image(result_frame, cam1floor1[i + 4], color=(0, 0, 255))
                dict_of_slices[i] = slices[i + 4]

    return result_frame, dict_of_slices, borders