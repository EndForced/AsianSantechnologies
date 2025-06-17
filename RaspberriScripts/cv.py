zones = {
}
#sec/first - floors, right/left - u know, 1/2 - cams, c/f - close/far
sec_right1c = [(341, 250), (657, 246), (795, 602), (317, 598), (337, 254)]#
sec_left1c = [(36, 272), (316, 253), (290, 598), (3, 601), (8, 319), (37, 271)] #
sec_fl_right1f = [(355, 98), (334, 247), (646, 251), (561, 98), (357, 97)] #
sec_fl_left1f = [(158, 101), (59, 238), (328, 226), (347, 93), (158, 98)]#

first_right1c = [(714, 599), (361, 597), (359, 301), (596, 306)]#
first_left1c = [(339, 330), (72, 326), (5, 590), (330, 600), (341, 331)] #
first_right1f = [(369, 143), (356, 241), (663, 245), (606, 144), (373, 138)]#
first_left1f = [(190, 153), (359, 144), (350, 271), (128, 278), (188, 154)] #

# dat_l_f = [(339, 330), (72, 326), (5, 590), (330, 600), (341, 331)]
# dat_r_f = [(510, 238), (513, 266), (546, 261), (546, 233), (509, 238)]
# dat_l_c = [(220, 514), (213, 565), (265, 570), (269, 516), (220, 513)]
# dat_r_c = [(584, 487), (592, 577), (715, 573), (702, 479), (594, 487)]

cam1floor1 = [first_right1c, first_left1c, first_right1f, first_left1f, sec_right1c, sec_left1c, sec_fl_right1f, sec_fl_left1f]
# dats1 = [dat_l_f, dat_r_f, dat_l_c, dat_r_c]

hsw_red = [(5,83,180), (179,255,254),  ]
hsw_blue  = (114.08,178.85,68.38)
hsw_range = (5,15,15)

mean_const = 160
#hehehe mnogo constant

import cv2
import numpy as np
from collections import defaultdict


def update_frame_smart(frame, floor):
    result_frame = frame.copy()
    list_of_slices = []

    if floor == 1:
        slices = [cv2.resize(extract_polygon_with_white_bg(frame, cam1floor1[i]), (200,200)) for i in range(8)]
        leads = []
        borders = check_for_borders(frame, 1)

        for i in range(4):
            flag1 = 1
            if np.mean(slices[i]) < mean_const:
                lead = "black"
            else:
                lead = "white"
            leads.append(lead)


            if borders:
                if borders[0] == "fc":
                    return frame, [] # близко бордер - в попу скан
                elif borders[0] == "ff":
                    flag1 = 0

            if (i == 2 or i == 3) and  not flag1:
                list_of_slices.append("unr")
                continue

            if i == 2 and leads[0] == "black":
                flag = 0
                list_of_slices.append("unr")

            elif i == 3 and leads[1] == "black":
                flag = 0
                list_of_slices.append("unr")
            else:
                flag = 1

            if lead == "white" and flag:
                result_frame = draw_on_image(result_frame, cam1floor1[i])
                list_of_slices.append(slices[i])

            elif lead == "black" and flag:
                result_frame = draw_on_image(result_frame, cam1floor1[i+4], color=(0,0,255))
                list_of_slices.append(slices[i+4])

    return result_frame, list_of_slices

def check_for_borders(frame,camnum):
    found = []
    if camnum == 1:
        fr = frame[-70:-30, :] #close line
        red_count_close = count_pixels(fr, hsw_red[0], hsw_red[1])[0]
        if red_count_close > 500:
            found.append("fc")#close front

        fr = frame[260:330, :]  # close line
        red_count_far = count_pixels(fr, hsw_red[0], hsw_red[1])[0]
        if red_count_far > 500:
            found.append("ff")  # close front

    return found


def fix_perspct(frame):

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


def draw_on_image(img, coordinates, shape_type='polygon', color=(0, 255, 0),
                  thickness=2, is_closed=True, fill=False, output_path=None):
    """
    Рисует фигуры на изображении по координатам

    Параметры:
    image_path - путь к исходному изображению
    coordinates - список точек в формате [(x1,y1), (x2,y2), ...]
    shape_type - тип фигуры: 'polygon', 'line', 'rectangle', 'circle', 'points'
    color - цвет в формате BGR (по умолчанию зеленый)
    thickness - толщина линии (для заливки используйте -1)
    is_closed - замыкать ли фигуру (для polygon и line)
    fill - заливать фигуру (если поддерживается)
    output_path - путь для сохранения результата (None - не сохранять)
    """
    # Загрузка изображения

    # Преобразуем координаты в numpy массив
    pts = np.array(coordinates, dtype=np.int32)

    # Рисуем в зависимости от типа фигуры
    if shape_type == 'polygon':
        if fill:
            cv2.fillPoly(img, [pts], color)
        else:
            cv2.polylines(img, [pts], isClosed=is_closed, color=color, thickness=thickness)

    elif shape_type == 'line':
        for i in range(len(pts) - 1):
            cv2.line(img, tuple(pts[i]), tuple(pts[i + 1]), color, thickness)
        if is_closed and len(pts) > 2:
            cv2.line(img, tuple(pts[-1]), tuple(pts[0]), color, thickness)

    elif shape_type == 'rectangle':
        if len(pts) >= 2:
            x1, y1 = pts[0]
            x2, y2 = pts[1]
            if fill:
                cv2.rectangle(img, (x1, y1), (x2, y2), color, -1)
            else:
                cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness)

    elif shape_type == 'circle':
        if len(pts) >= 2:
            center = pts[0]
            radius = int(np.sqrt((pts[1][0] - pts[0][0]) ** 2 + (pts[1][1] - pts[0][1]) ** 2))
            if fill:
                cv2.circle(img, tuple(center), radius, color, -1)
            else:
                cv2.circle(img, tuple(center), radius, color, thickness)

    elif shape_type == 'points':
        for point in pts:
            cv2.circle(img, tuple(point), thickness, color, -1)

    # Сохраняем результат если нужно
    if output_path:
        cv2.imwrite(output_path, img)
        print(f"Результат сохранен в {output_path}")

    return img

def extract_polygon_with_white_bg(image, points):
    """
    Вырезает область изображения, заданную полигоном, с белым фоном
    (Гарантированно работает с 3-канальными изображениями)

    :param image: исходное изображение (BGR или GRAY)
    :param points: список точек полигона в формате [(x1,y1), (x2,y2), ...]
    :return: 3-канальное изображение с вырезанной областью и белым фоном
    """
    # Проверяем количество каналов и конвертируем при необходимости
    if len(image.shape) == 2 or image.shape[2] == 1:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    # Создаем маску (одноканальную)
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    pts = np.array(points, dtype=np.int32)

    # Заполняем полигон на маске белым цветом
    cv2.fillPoly(mask, [pts], 255)

    # Создаем 3-канальный белый фон того же размера и типа, что и изображение
    white_bg = np.full_like(image, 255)

    # Преобразуем маску в 3-канальную для операции where
    mask_3ch = cv2.merge([mask, mask, mask])

    # Копируем только область внутри полигона на белый фон
    result = np.where(mask_3ch.astype(bool), image, white_bg)

    # Находим ограничивающий прямоугольник
    x, y, w, h = cv2.boundingRect(pts)

    # Вырезаем область
    cropped = result[y:y + h, x:x + w]

    return cropped


def count_pixels(image, lower_hsv, upper_hsv):

    # Конвертация из BGR в HSV
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Создание маски для заданного диапазона HSV
    lower = np.array(lower_hsv, dtype=np.uint8)
    upper = np.array(upper_hsv, dtype=np.uint8)
    mask = cv2.inRange(hsv_image, lower, upper)

    # Подсчет ненулевых пикселей в маске
    pixel_count = cv2.countNonZero(mask)

    return pixel_count, mask




if __name__ == "__main__":
    fr, slices = update_frame_smart(cv2.imread("warped.png"), 1)
    # cv2.imshow("o", slices[0][0])
    cv2.imshow("p", fr)

    # for i in range(len(slices)):
    #     if str(slices[i]) != "unr":
    #         slices[i] = cv2.resize(slices[i],(300,300))
    #         count, mask = analyze_color_shape(slices[i], hsw_blue, hsw_range)
    #         print(count)
    #         cv2.imshow(f"{i}", mask)
    #         cv2.waitKey(0)

    cv2.waitKey(0)