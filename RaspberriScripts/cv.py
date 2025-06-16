zones = {
}
#sec/first - floors, right/left - u know, 1/2 - cams, c/f - close/far
sec_right1c = [(341, 250), (657, 246), (795, 602), (317, 598), (337, 254)]#
sec_left1c = [(36, 272), (316, 253), (290, 598), (3, 601), (8, 319), (37, 271)] #
sec_fl_right1f = [(355, 98), (334, 247), (646, 251), (561, 98), (357, 97)] #
sec_fl_left1f = [(343, 96), (323, 250), (37, 262), (137, 112), (342, 96)]#

first_right1c = [(346, 311), (592, 310), (713, 594), (324, 597), (346, 312)]#
first_left1c = [(317, 310), (284, 601), (4, 594), (13, 321), (316, 309)] #
first_right1f = [(340, 302), (337, 602), (708, 600), (591, 305), (341, 302)]#
first_left1f = [(323, 300), (297, 599), (13, 597), (96, 314), (323, 300)]#

cam1floor1 = [first_right1c, first_left1c, first_right1f, first_left1f, sec_right1c, sec_left1c, sec_fl_right1f, sec_fl_left1f]

hsv_white = (83.05,47.49,120.47)
hsw_red = (83.32,193.15,129.74)
hsw_blue  = (114.08,178.85,68.38)
hsw_range = (5,15,15)




import cv2
import numpy as np
from collections import defaultdict


def update_frame_smart(frame, floor):
    result_frame = frame.copy()
    list_of_slices = []

    if floor == 1:
        slices = [extract_polygon_with_white_bg(frame, cam1floor1[i]) for i in range(8)]
        leads = []
        for i in range(4):
            slice_to_check = slices[i][0:50,::]
            lead = lead_color(slice_to_check, white_hsv_base= hsv_white)[1]
            leads.append(lead)

            if i == 2 and leads[0] == "black":
                flag = 0
                list_of_slices.append("unr")
            elif i == 3 and leads[1] == "black":
                flag = 0
                list_of_slices.append("unr")

            else: flag = 1

            # print(i, flag)
            # cv2.imshow("o", slice_to_check)
            # print(lead)
            # cv2.waitKey(0)

            if lead == "white" and flag:
                result_frame = draw_on_image(result_frame, cam1floor1[i])
                list_of_slices.append(slices[i])

            elif lead == "black":
                result_frame = draw_on_image(result_frame, cam1floor1[i+4], color = (0,0,255))
                list_of_slices.append(slices[i+4])






    return result_frame, list_of_slices


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

def lead_color(img_slice, threshold=0.5,
               ignore_white=True,
               white_hsv_base=(83, 47, 120),
               white_h_range=180,
               white_s_range=25,
               white_v_range=25):
    """
    Определяет доминирующий цвет на изображении (белый/черный) с настройкой
    белого цвета через базовое значение и диапазоны.

    Параметры:
    img_slice - входное изображение (BGR или GRAY)
    threshold - порог для определения (0-1)
    ignore_white - игнорировать ли пиксели в диапазоне белого
    white_hsv_base - базовое значение HSV для белого (Hue, Saturation, Value)
    white_h_range - диапазон для Hue (0-180)
    white_s_range - диапазон для Saturation (0-255)
    white_v_range - диапазон для Value (0-255)

    Возвращает:
    img_slice - изображение с результатом
    result - "white" или "black"
    """
    # Проверяем количество каналов
    if len(img_slice.shape) == 2 or img_slice.shape[2] == 1:
        # Если изображение уже в градациях серого
        gray = img_slice
        # Для маски белого и вывода создаем 3-канальное изображение
        img_slice_bgr = cv2.cvtColor(img_slice, cv2.COLOR_GRAY2BGR)
    else:
        # Цветное изображение
        gray = cv2.cvtColor(img_slice, cv2.COLOR_BGR2GRAY)
        img_slice_bgr = img_slice.copy()

    # Маска белых пикселей (если нужно игнорировать)
    if ignore_white:
        if len(img_slice.shape) == 2 or img_slice.shape[2] == 1:
            # Для grayscale изображений используем только V-канал
            v_base = white_hsv_base[2]
            lower = max(0, v_base - white_v_range)
            upper = min(255, v_base + white_v_range)
            white_mask = cv2.inRange(img_slice, lower, upper)
        else:
            # Для цветных изображений используем HSV-диапазон
            hsv = cv2.cvtColor(img_slice, cv2.COLOR_BGR2HSV)
            h_base, s_base, v_base = white_hsv_base

            # Рассчитываем границы с учетом диапазонов
            lower = (
                max(0, h_base - white_h_range),
                max(0, s_base - white_s_range),
                max(0, v_base - white_v_range)
            )
            upper = (
                min(180, h_base + white_h_range),
                min(255, s_base + white_s_range),
                min(255, v_base + white_v_range)
            )
            white_mask = cv2.inRange(hsv, lower, upper)

        mask = cv2.bitwise_not(white_mask)
        total_pixels = cv2.countNonZero(mask)
        masked_gray = cv2.bitwise_and(gray, gray, mask=mask)
    else:
        masked_gray = gray
        total_pixels = gray.size

    # Бинаризация
    _, binary = cv2.threshold(masked_gray, 127, 255, cv2.THRESH_BINARY)

    # Подсчет белых пикселей
    white_pixels = np.sum(binary == 255)

    # Определение результата
    if total_pixels == 0:
        result = "white"
    else:
        white_ratio = white_pixels / total_pixels
        result = "white" if white_ratio > threshold else "black"

    # Рисуем результат на изображении (в BGR формате)
    cv2.putText(img_slice_bgr, result, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    return img_slice_bgr, result


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


def analyze_color_shape(image, target_hsv, hsv_range=(10, 50, 50), min_area=100):
    """
    Анализирует цветовые области и определяет их форму

    Параметры:
    - image: исходное изображение (BGR)
    - target_hsv: целевой цвет в HSV (H, S, V)
    - hsv_range: допустимый диапазон (H_range, S_range, V_range)
    - min_area: минимальная площадь для анализа формы

    Возвращает:
    - Словарь с результатами анализа для каждой найденной области
    - Изображение с разметкой
    """
    # Конвертируем в HSV и создаем маску
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_bound = np.array([max(0, target_hsv[0] - hsv_range[0]),
                            max(0, target_hsv[1] - hsv_range[1]),
                            max(0, target_hsv[2] - hsv_range[2])])
    upper_bound = np.array([min(179, target_hsv[0] + hsv_range[0]),
                            min(255, target_hsv[1] + hsv_range[1]),
                            min(255, target_hsv[2] + hsv_range[2])])
    color_mask = cv2.inRange(hsv_image, lower_bound, upper_bound)

    # Находим контуры
    contours, _ = cv2.findContours(color_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    results = defaultdict(dict)
    marked_image = image.copy()

    for idx, cnt in enumerate(contours):
        area = cv2.contourArea(cnt)
        if area < min_area:
            continue

        # Основные параметры контура
        perimeter = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.04 * perimeter, True)
        num_sides = len(approx)

        # Определяем форму по количеству сторон
        if num_sides == 3:
            shape = "triangle"
        elif num_sides == 4:
            # Проверяем, насколько близок к прямоугольнику
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = float(w) / h
            shape = "square" if 0.95 <= aspect_ratio <= 1.05 else "rectangle"
        elif num_sides == 5:
            shape = "pentagon"
        elif num_sides == 6:
            shape = "hexagon"
        elif num_sides > 12:
            # Проверяем круглость
            (x, y), radius = cv2.minEnclosingCircle(cnt)
            circle_area = np.pi * (radius ** 2)
            circularity = area / circle_area
            shape = "circle" if circularity > 0.85 else "oval"
        else:
            shape = f"polygon_{num_sides}sides"

        # Вычисляем моменты для центра масс
        M = cv2.moments(cnt)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        else:
            cX, cY = 0, 0

        # Сохраняем результаты
        results[idx] = {
            "shape": shape,
            "area": area,
            "perimeter": perimeter,
            "center": (cX, cY),
            "num_sides": num_sides,
            "contour": cnt
        }

        # Рисуем разметку
        cv2.drawContours(marked_image, [cnt], -1, (0, 255, 0), 2)
        cv2.putText(marked_image, shape, (cX - 20, cY - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    return dict(results), marked_image
# if __name__ == "__main__":
#     fr, slices = update_frame_smart(cv2.imread("frame_1.png"), 1)
#     # cv2.imshow("o", slices[0][0])
#     cv2.imshow("p", fr)
#
#     for i in range(len(slices)):
#         if str(slices[i]) != "unr":
#             slices[i] = cv2.resize(slices[i],(300,300))
#             count, mask = analyze_color_shape(slices[i], hsw_blue, hsw_range)
#             print(count)
#             cv2.imshow(f"{i}", mask)
#             cv2.waitKey(0)
#
#     cv2.waitKey(0)