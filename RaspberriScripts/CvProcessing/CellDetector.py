import os
import sys
from itertools import combinations

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import cv2
import numpy as np

# тут многа констант. Но если не работает, стоит менять меан конст и хсв красного

zones = {
    'sec_right1c': [(341, 250), (657, 246), (795, 602), (317, 598), (337, 254)],
    'sec_left1c': [(36, 272), (316, 253), (290, 598), (3, 601), (8, 319)],
    'sec_fl_right1f': [(355, 98), (334, 247), (646, 251), (561, 98), (357, 97)],
    'sec_fl_left1f': [(166, 116), (34, 271), (334, 274), (364, 106), (170, 111)],

    'first_right1c': [(356, 311), (328, 603), (701, 600), (601, 319), (356, 310)],
    'first_left1c': [(339, 330), (72, 326), (5, 590), (330, 600), (341, 331)],
    'first_right1f': [(355, 155), (345, 290), (580, 290), (525, 155), (355, 155)],
    'first_left1f': [(190, 145), (360, 145), (350, 285), (128, 285), (190, 145)],

    'first_right2c': [(353, 334), (333, 583), (621, 591), (557, 329), (350, 335)],
    'first_right2f': [(358, 192), (346, 313), (553, 320), (529, 186), (354, 188)],
    'first_left2c': [(328, 602), (74, 597), (162, 362), (342, 364), (329, 601)],
    'first_left2f': [(216, 226), (169, 330), (345, 330), (352, 217), (216, 218)]
}

cam1floor1 = [zones['first_right1c'], zones['first_left1c'], zones['first_right1f'], zones['first_left1f'],
              zones['sec_right1c'], zones['sec_left1c'], zones['sec_fl_right1f'], zones['sec_fl_left1f']]
cam1floor2 = [zones['first_right2c'], zones['first_left2c'], zones['first_right2f'], zones['first_left2f'],
              zones['first_right1c'], zones['first_left1c'], zones['first_right1f'], zones['first_left1f']]

mean_const = 160

COLOR_RANGES = {
    "Red": [np.array([0, 90, 172]), np.array([22, 255, 255]),
            np.array([150, 100, 80]), np.array([180, 255, 255])],
    "Red1": [np.array([0, 70, 0]), np.array([20, 255, 255]),
             np.array([150, 70, 0]), np.array([180, 255, 255])],
    "Green": (np.array([72, 161, 163]), np.array([85, 255, 196])),
    "Blue": (np.array([110, 90, 90]), np.array([140, 255, 255]))
}


def fix_perspective(img):
    # больше констант??????????
    K = np.array(
        [
            [3.19241098e+02, 8.48447347e-02, 2.78952483e+02],
            [0.00000000e+00, 3.17958710e+02, 1.98634298e+02],
            [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]
        ])
    D = np.array([
        [0.05878302],
        [-0.02615866],
        [-0.04267542],
        [0.03454424]
    ])

    border_size = 100
    img_with_border = cv2.copyMakeBorder(
        img,
        border_size, border_size, border_size, border_size,
        cv2.BORDER_CONSTANT,
        value=(0, 0, 0)  # Черный цвет фона
    )

    h, w = img_with_border.shape[:2]
    K_border = K.copy()
    K_border[0, 2] += border_size
    K_border[1, 2] += border_size

    undistorted = cv2.fisheye.undistortImage(
        img_with_border,
        K=K_border,
        D=D,
        Knew=K_border,
        new_size=(w, h)
    )

    return undistorted


def extract_warped(image, points, output_size=500):
    # если бы я только знал что тут происходит...
    if len(points) != 5:
        raise ValueError("Tochki chekni prekolist")

    points = np.array(points, dtype=np.float32)

    min_dist = float('inf')
    closest_pair = None

    for (p1, p2) in combinations(points, 2):
        dist = np.linalg.norm(p1 - p2)
        if dist < min_dist:
            min_dist = dist
            closest_pair = (p1, p2)

    avg_point = (closest_pair[0] + closest_pair[1]) / 2
    remaining_points = [p for p in points if
                        not np.array_equal(p, closest_pair[0]) and not np.array_equal(p, closest_pair[1])]
    final_points = np.vstack([remaining_points, avg_point])

    center = np.mean(final_points, axis=0)
    angles = np.arctan2(final_points[:, 1] - center[1], final_points[:, 0] - center[0])
    final_points_sorted = final_points[np.argsort(angles)]

    dst_points = np.array([
        [0, 0], [output_size, 0],
        [output_size, output_size], [0, output_size]
    ], dtype=np.float32)

    M = cv2.getPerspectiveTransform(final_points_sorted, dst_points)
    return cv2.warpPerspective(image, M, (output_size, output_size))


def check_for_borders(frame, cam_num):
    found = []
    if cam_num == 1:
        # front close
        fr = frame[580:680, 360:740]
        fr = cv2.cvtColor(fr, cv2.COLOR_BGR2HSV)
        width = fr.shape[1]
        _, __, w, h = search_for_color(fr, "Red1", min_area=20)
        if w > 0.5 * width:
            print(w, "fc")
            found.append("fc")

        # front far
        fr = frame[260:330, -450:-100]
        fr = cv2.cvtColor(fr, cv2.COLOR_BGR2HSV)
        width = fr.shape[1]
        # cv2.rectangle(frame, (390, 610), (740, 650), (100, 0, 200), 3)
        _, __, w, h = search_for_color(fr, "Red1", min_area=20)
        if w > 0.5 * width:
            print(w, "ff")
            found.append("ff")

        # side close
        # fr = frame[100:550, 300:400]
        # red_count_side = count_pixels(fr, hgsw_red[0], hsw_red[1])[0]
        # print(red_count_side, "sc")
        # if red_count_side > 5000:
        #     found.append("sc")
    return found, frame


def count_pixels(image, lower_hsv, upper_hsv):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower = np.array(lower_hsv, dtype=np.uint8)
    upper = np.array(upper_hsv, dtype=np.uint8)
    mask = cv2.inRange(hsv_image, lower, upper)
    return cv2.countNonZero(mask), mask

def draw_on_image(img, coordinates, color=(0, 255, 0), thickness=2, fill=False):
    pts = np.array(coordinates, dtype=np.int32)
    if fill:
        cv2.fillPoly(img, [pts], color)
    else:
        cv2.polylines(img, [pts], isClosed=True, color=color, thickness=thickness)
    return img

def search_for_color(frame, color, min_area=50):
    if color not in COLOR_RANGES:
        raise ValueError(f"Unknown color: {color}")

    frame_height, frame_width = frame.shape[:2]
    if color == "Red" or "Red1" == color:
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
    x, y, w, h = search_for_color(hsv, "Green")
    if h * w:
        if w > h:
            return 61 if (y + h / 2) > 50 else 63
        else:
            return 62 if (x + w / 2) > 100 else 64

    # Поиск синих объектов (рампа)
    xb, yb, wb, hb = search_for_color(hsv, "Blue")
    if hb * wb:
        xr, yr, wr, hr = search_for_color(hsv, "Red")
        delta_x = xb - xr
        delta_y = yb - yr

        if abs(delta_x) < abs(delta_y):
            return 34 if delta_y < 0 else 32
        else:
            return 33 if delta_x < 0 else 31

    # Определение высоты
    mini1 = frame_blur[120:200, 30:70]
    mini2 = frame_blur[120:200, 130:170]
    elevation = 1 if ((np.mean(mini1) + np.mean(mini2)) / 2) > 150 else 2

    # Поиск красных труб
    x, y, w, h = search_for_color(hsv, "Red")
    if h * w:
        return 32 + elevation * 10 if h / w > 1.2 else 31 + elevation * 10

    return elevation * 10

def process_borders(slices, borders, leads, floor):
    ignore_mask = {i: False for i in range(4)}  # Инициализируем маску

    border_flags = {
        'fc': 'fc' in borders,
        'ff': 'ff' in borders,
        'sc': 'sc' in borders,
        'sf': 'sf' in borders
    }

    # front close = skip
    if border_flags['fc']:
        return {i: True for i in range(4)}

    for i in range(4):
        # front far
        if (i == 2 or i == 3) and border_flags['ff']:
            ignore_mask[i] = True

        if floor == 1:
            # ignore  behind white
            if i == 2 and leads[0] == "black"and tile_to_code(slices[0]) != 31:
                ignore_mask[i] = True
                # print("heh")

            if i == 3 and leads[1] == "black"  and tile_to_code(slices[1]) != 31:
                ignore_mask[i] = True
                # print("huh")
        # elif floor == 2:

    print("ignore", ignore_mask)
    return ignore_mask

def analyze_frame(frame, floor):
    # я пытался делать модульный код (вроде работает)
    result_frame = frame.copy()
    dict_of_slices = {}
    borders = []
    slices = []

    if floor == 1:
        slices = [cv2.resize(extract_warped(frame, cam1floor1[i]), (200, 200)) for i in range(8)]
    elif floor == 2:
        slices = [cv2.resize(extract_warped(frame, cam1floor2[i]), (200, 200)) for i in range(8)]

    borders, frame = check_for_borders(frame, 1)

    cv2.rectangle(result_frame, (780 - 450, 260), (680, 330), (100, 0, 200), 2)
    cv2.rectangle(result_frame, (360, 580), (740, 680), (100, 0, 200), 2)

    leads = []
    for i in range(4):
        mini1 = slices[i][120:200, 30:70]
        mini2 = slices[i][120:200, 130:170]
        leads.append("black" if (np.mean(mini1) + np.mean(mini2)) / 2 < mean_const else "white")
    print(leads)


    ignore_mask = process_borders(slices, borders, leads, floor)

    for i in range(4):
        if ignore_mask[i]:
            dict_of_slices[i] = "unr"
            continue
        if floor == 1:
            if leads[i] == "white":
                result_frame = draw_on_image(result_frame, cam1floor1[i])
                dict_of_slices[i] = slices[i]
            else:
                result_frame = draw_on_image(result_frame, cam1floor1[i + 4], color=(0, 0, 255))
                dict_of_slices[i] = slices[i + 4]
        elif floor == 2:
            if leads[i] == "white":
                result_frame = draw_on_image(result_frame, cam1floor2[i])
                dict_of_slices[i] = slices[i]
            else:
                result_frame = draw_on_image(result_frame, cam1floor2[i + 4], color=(0, 0, 255))
                dict_of_slices[i] = slices[i + 4]

    return result_frame, dict_of_slices, borders
