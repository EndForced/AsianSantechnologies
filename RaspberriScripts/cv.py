zones = {
}
#sec/first - floors, right/left - u know, 1/2 - floors, c/f - close/far
sec_right1c = [(341, 250), (657, 246), (795, 602), (317, 598), (337, 254)]#
sec_left1c = [(36, 272), (316, 253), (290, 598), (3, 601), (8, 319), (37, 271)] #
sec_fl_right1f = [(355, 98), (334, 247), (646, 251), (561, 98), (357, 97)] #
sec_fl_left1f = [(158, 101), (59, 238), (328, 226), (347, 93), (158, 98)]#

first_right1c = [(714, 599), (361, 597), (359, 301), (596, 306)]#
first_left1c = [(339, 330), (72, 326), (5, 590), (330, 600), (341, 331)] #
first_right1f = [(369, 143), (356, 241), (663, 245), (606, 144), (373, 138)]#
first_left1f = [(190, 153), (359, 144), (350, 271), (128, 278), (188, 154)] #

first_right2c = [(353, 334), (333, 583), (621, 591), (557, 329), (350, 335)]#
first_right2f = [(358, 192), (346, 313), (553, 320), (529, 186), (354, 188)]#
first_left2_c = [(328, 602), (74, 597), (162, 362), (342, 364), (329, 601)]#
first_left2f = [(216, 226), (169, 330), (345, 330), (352, 217), (216, 218)]#




# dat_l_f = [(339, 330), (72, 326), (5, 590), (330, 600), (341, 331)]
# dat_r_f = [(510, 238), (513, 266), (546, 261), (546, 233), (509, 238)]
# dat_l_c = [(220, 514), (213, 565), (265, 570), (269, 516), (220, 513)]
# dat_r_c = [(584, 487), (592, 577), (715, 573), (702, 479), (594, 487)]


cam1floor1 = [first_right1c, first_left1c, first_right1f, first_left1f,    sec_right1c, sec_left1c, sec_fl_right1f, sec_fl_left1f]
cam1floor2 = [first_right1c, first_left1c, sec_fl_right1f, first_left1f,    first_right2c, first_left2_c, first_right2f, first_left2f]
# dats1 = [dat_l_f, dat_r_f, dat_l_c, dat_r_c]

hsw_red = [(5,83,180), (179,255,254)]
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
    borders = []

    if floor == 1:
        slices = [cv2.resize(extract_polygon_with_white_bg(frame, cam1floor1[i]), (200, 200)) for i in range(8)]
        leads = []
        borders = check_for_borders(frame, 1)

        # Обработка бордеров
        border_flags = {
            'fc': False,  # Близкий бордер - полный сброс
            'ff': False,  # Дальний бордер - отключаем проверку для индексов 2 и 3
            'sc': False,  # Близкий второй бордер
            'sf': False  # Дальний второй бордер
        }

        # if borders:
        #     for border in borders:
        #         if border in border_flags:
        #             border_flags[border] = True

        # Если есть близкий бордер - полный сброс
        if border_flags['fc']:
            return frame, []

        for i in range(4):
            # Определяем цвет области
            if np.mean(slices[i]) < mean_const:
                lead = "black"
            else:
                lead = "white"
            leads.append(lead)

            # Пропускаем индексы 2 и 3 если есть дальний бордер
            if (i == 2 or i == 3) and border_flags['ff']:
                list_of_slices.append("unr")
                continue

            # Пропускаем индексы 1 и 3 если есть близкий второй бордер
            if (i == 1 or i == 3) and border_flags['sc']:
                list_of_slices.append("unr")
                continue

            # Проверка зависимостей между индексами
            if i == 2 and leads[0] == "black":
                list_of_slices.append("unr")
                continue

            if i == 3 and leads[1] == "black":
                list_of_slices.append("unr")
                continue

            # Отрисовка в зависимости от цвета
            if lead == "white":
                result_frame = draw_on_image(result_frame, cam1floor1[i])
                list_of_slices.append(slices[i])
            else:
                result_frame = draw_on_image(result_frame, cam1floor1[i + 4], color=(0, 0, 255))
                list_of_slices.append(slices[i + 4])

    if floor == 2:
        slices = [cv2.resize(extract_polygon_with_white_bg(frame, cam1floor2[i]), (200, 200)) for i in range(8)]
        # for i in slices:
        #     cv2.imshow("o", i)
        #     cv2.waitKey(0)
        leads = []
        borders = check_for_borders(frame, 1)

        # Обработка бордеров
        border_flags = {
            'fc': False,  # Близкий бордер - полный сброс
            'ff': False,  # Дальний бордер - отключаем проверку для индексов 2 и 3
            'sc': False,  # Близкий второй бордер
            'sf': False  # Дальний второй бордер
        }

        # if borders:
        #     for border in borders:
        #         if border in border_flags:
        #             border_flags[border] = True

        # Если есть близкий бордер - полный сброс
        if border_flags['fc']:
            return frame, []

        for i in range(4):
            # Определяем цвет области
            if np.mean(slices[i]) < mean_const:
                lead = "black"
            else:
                lead = "white"
            leads.append(lead)

            # Пропускаем индексы 2 и 3 если есть дальний бордер
            if (i == 2 or i == 3) and border_flags['ff']:
                list_of_slices.append("unr")
                continue

            # Пропускаем индексы 1 и 3 если есть близкий второй бордер
            if (i == 1 or i == 3) and border_flags['sc']:
                list_of_slices.append("unr")
                continue

            # Проверка зависимостей между индексами
            # if i == 2 and leads[0] != "black":
            #     list_of_slices.append("unr")
            #     continue
            #
            # if i == 3 and leads[1] != "black":
            #     list_of_slices.append("unr")
            #     continue

            # Отрисовка в зависимости от цвета
            if lead == "black":
                result_frame = draw_on_image(result_frame, cam1floor2[i])
                list_of_slices.append(slices[i])
            else:
                result_frame = draw_on_image(result_frame, cam1floor2[i + 4], color=(0, 0, 255))
                list_of_slices.append(slices[i + 4])

    return result_frame, list_of_slices, borders

def check_for_borders(frame,camnum):
    found = []
    if camnum == 1:
        fr = frame[-70:-30, :] #close line
        red_count_close = count_pixels(fr, hsw_red[0], hsw_red[1])[0]
        if red_count_close > 2000:
            print(f"Close front: {red_count_close}")
            found.append("fc")#close front

        fr = frame[260:330, :]  # close line
        red_count_far = count_pixels(fr, hsw_red[0], hsw_red[1])[0]
        if red_count_far > 1500:
            print(f"far front: {red_count_far}")
            found.append("ff")  # close front

        if "fc" not in found:
            fr = frame[:,300:400]  # close line
            red_count_far = count_pixels(fr, hsw_red[0], hsw_red[1])[0]
            if red_count_far > 1500:
                print(f"Side close: {red_count_far}")
                found.append("sc")  # side close


    # print(found)
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

def search_for_color(frame_, color, min_area=50):
    hsv = {"R": [[0, 0, 0], [180, 255, 255]],
           "R1": [[0, 0, 0], [180, 255, 255]],
           "G": [[0, 0, 0], [180, 255, 255]],
           "B": [[0, 0, 0], [180, 255, 255]]}

    if color == "Red":
        frame_height, frame_width = frame_.shape[:2]
        frame_ = frame_[int(frame_height * 0.1):int(frame_height * 0.9),
                 int(frame_width * 0.1):int(frame_width * 0.9)]
        mask1 = cv2.inRange(frame_, hsv["R"][0], hsv["R"][1])
        mask2 = cv2.inRange(frame_, hsv["R1"][0], hsv["R1"][1])
        mask = cv2.bitwise_or(mask1, mask2)
    elif color == "Green":
        mask = cv2.inRange(frame_, hsv["G"][0], hsv["G"][1])
    elif color == "Blue":
        mask = cv2.inRange(frame_, hsv["B"][0], hsv["B"][1])
    else:
        print(f"Unknown color: {color}")
        return 0, 0, 0, 0

    contours, k = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    x, y, w, h = 0, 0, 0, 0
    for cont in contours:
        area = cv2.contourArea(cont)
        if area > min_area:
            x1, y1, w1, h1 = cv2.boundingRect(cont)
            if w1 * h1 > w * h:
                x, y, w, h = x1, y1, w1, h1

    return x, y, w, h

def tile_to_code(frame200x200):
    frame_height, frame_width = frame200x200.shape[:2]
    if frame_height != 200 or frame_width != 200:
        print("bebebe, wrong size of tile \nRESIZING...")
        frame200x200 = cv2.resize(frame200x200, [200, 200])
        frame_height, frame_width = frame200x200.shape[:2]

    frame_b = cv2.blur(frame200x200, [11, 11])

    ImageHSV = cv2.cvtColor(frame_b, cv2.COLOR_BGR2HSV)

    x, y, h, w = search_for_color(ImageHSV, "Green")
    if h * w:  # если найдена зеленая труба
        if w > h:
            if (y + h / 2) > frame_height / 2:
                result = 61
            else:
                result = 63  # это вроде невозможный вариант (чтобы увидеть такое нужно быть вне поля)
        else:
            if (x + w / 2) > frame_width / 2:
                result = 62
            else:
                result = 64
        message = "stand " + str(result - 60)
        return result

    x, y, h, w = search_for_color(ImageHSV, "Blue")
    if h * w:  # если найден синий
        xr, yr, hr, wr = search_for_color(ImageHSV, "Red")
        delta_x = x - xr
        delta_y = y - yr
        if abs(delta_x) < abs(delta_y):
            if delta_y < 0:
                result = 34  # рампа направо (синий ближе к роботу)
            else:
                result = 32  # рампа налево (красный ближе к роботу)
        else:
            if delta_x < 0:
                result = 33  # рампа назад (верх ближе к роботу)
            else:
                result = 31  # рампа вперед (низ ближе к роботу)
        message = "ramp " + str(result - 30)
        return result

    elevation = 1 if np.mean(frame_b) > 150 else 2
    x, y, h, w = search_for_color(ImageHSV, "Red")
    if h * w:  # если найден красный
        if h / w > 1.2:
            result = 32 + elevation * 10  # рампа направо (синий ближе к роботу)
        else:
            result = 31 + elevation * 10  # рампа направо (синий ближе к роботу)
        message = "tube " + str(result - 40)
        return result

    return elevation * 10.


if __name__ == "__main__":
    fr, slices, borders = update_frame_smart(cv2.imread("warped.png"), 2)
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


