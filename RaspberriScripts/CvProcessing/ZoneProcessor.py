import cv2
import numpy as np
from itertools import combinations
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#тут многа констант. Но если не работает, стоит менять меан конст и хсв красного

zones = {
    'sec_right1c': [(341, 250), (657, 246), (795, 602), (317, 598), (337, 254)],
    'sec_left1c': [(36, 272), (316, 253), (290, 598), (3, 601), (8, 319)],
    'sec_fl_right1f': [(355, 98), (334, 247), (646, 251), (561, 98), (357, 97)],
    'sec_fl_left1f': [(166, 116), (34, 271), (334, 274), (364, 106), (170, 111)],

    'first_right1c': [(356, 311), (328, 603), (701, 600), (601, 319), (356, 310)],
    'first_left1c': [(339, 330), (72, 326), (5, 590), (330, 600), (341, 331)],
    'first_right1f': [(357, 165), (344, 309), (582, 310), (524, 161), (357, 164)],
    'first_left1f': [(190, 153), (359, 144), (350, 271), (128, 278), (188, 154)],

    'first_right2c': [(353, 334), (333, 583), (621, 591), (557, 329), (350, 335)],
    'first_right2f': [(358, 192), (346, 313), (553, 320), (529, 186), (354, 188)],
    'first_left2_c': [(328, 602), (74, 597), (162, 362), (342, 364), (329, 601)],
    'first_left2f': [(216, 226), (169, 330), (345, 330), (352, 217), (216, 218)]
}

cam1floor1 = [zones['first_right1c'], zones['first_left1c'], zones['first_right1f'], zones['first_left1f'],
              zones['sec_right1c'], zones['sec_left1c'], zones['sec_fl_right1f'], zones['sec_fl_left1f']]
cam1floor2 = [zones['first_right1c'], zones['first_left1c'], zones['first_right1f'], zones['first_left1f'],
              zones['first_right2c'], zones['first_left2_c'], zones['first_right2f'], zones['first_left2f']]


hsw_red = [(5, 83, 180), (179, 255, 254)]
mean_const = 160


def fix_perspective(frame):

    K = np.array(
        [
            [3.19241098e+02, 8.48447347e-02, 2.78952483e+02],
            [0.00000000e+00, 3.17958710e+02, 1.98634298e+02],
            [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]
        ])
    D = np.array([
    [ 0.05878302],
    [-0.02615866],
    [-0.04267542],
    [ 0.03454424]
])

    # Загрузка изображения
    img = frame
    if img is None:
        raise ValueError("Не удалось загрузить изображение! Проверьте путь.")

    # 1. Добавляем 50-пиксельные поля вокруг изображения
    border_size = 100
    img_with_border = cv2.copyMakeBorder(
        img,
        border_size, border_size, border_size, border_size,
        cv2.BORDER_CONSTANT,
        value=(0, 0, 0)  # Черный цвет фона
    )

    # 2. Обновляем параметры камеры для увеличенного изображения
    h, w = img_with_border.shape[:2]
    K_border = K.copy()
    K_border[0, 2] += border_size  # Сдвигаем центр по x
    K_border[1, 2] += border_size  # Сдвигаем центр по y

    # 3. Устранение дисторсии
    undistorted = cv2.fisheye.undistortImage(
        img_with_border,
        K=K_border,
        D=D,
        Knew=K_border,
        new_size=(w, h)
    )

    return undistorted


def extract_warped(image, points, output_size=500):
    #если бы я только знал что тут происходит...
    if len(points) != 5:
        raise ValueError("Tochki chekni prekolist")

    points = np.array(points, dtype=np.float32)

    # Находим 2 ближайшие точки
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
        fr = frame[-70:-30, :]
        red_count_close = count_pixels(fr, hsw_red[0], hsw_red[1])[0]
        if red_count_close > 2000:
            found.append("fc")

        # front far
        fr = frame[260:330, :]
        red_count_far = count_pixels(fr, hsw_red[0], hsw_red[1])[0]
        if red_count_far > 1500:
            found.append("ff")

        #side close
        if "fc" not in found:
            fr = frame[:, 300:400]
            red_count_side = count_pixels(fr, hsw_red[0], hsw_red[1])[0]
            if red_count_side > 1500:
                found.append("sc")
    return found


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