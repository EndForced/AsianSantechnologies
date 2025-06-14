zones = {
}
#sec/first - floors, right/left - u know, 1/2 - cams, c/f - close/far
sec_right1c = [(233, 151), (534, 170), (574, 321), (563, 478), (196, 482), (233, 152), (237, 151), (237, 151)]
sec_left1c = [(9, 163), (237, 148), (201, 479), (62, 479), (5, 443), (6, 164)]
sec_fl_right1f = [(535, 172), (242, 144), (269, 6), (441, 4), (459, 12), (536, 171)]
sec_fl_left1f = [(15, 155), (237, 144), (264, 10), (100, 17), (14, 153)]

first_right1c = [(253, 189), (493, 203), (525, 483), (221, 475), (251, 190)]
first_left1c = [(51, 187), (217, 191), (175, 468), (8, 394), (49, 189)]
first_right1f = [(281, 42), (262, 182), (488, 194), (444, 57), (369, 43), (282, 43)]
first_left1f = [(123, 58), (258, 49), (238, 189), (58, 183), (121, 58)]

cam1floor1 = [first_right1c, first_left1c, first_right1f, first_left1f, sec_right1c, sec_left1c, sec_fl_right1f, sec_fl_left1f]


import cv2
import numpy as np


def update_frame_smart(frame, floor):
    result_frame = frame.copy()
    list_of_slices = []

    if floor == 1:
        slices = [extract_polygon_with_white_bg(frame, cam1floor1[i]) for i in range(8)]
        leads = []
        for i in range(4):
            slice_to_check = slices[i][0:50,::]
            lead = lead_color(slice_to_check)[1]
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

#H: 83.05, S: 47.49, V: 120.47
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


if __name__ == "__main__":
    fr, slices = update_frame_smart(cv2.imread("frame_1.png"), 1)
    # cv2.imshow("o", slices[0][0])
    cv2.imshow("p", fr)

    for i in range(len(slices)):
        if str(slices[i]) != "unr":
            cv2.imshow(f"{i}", slices[i])

    cv2.waitKey(0)
