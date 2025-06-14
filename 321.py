# import cv2
# import numpy as np
#
#
# def extract_polygon(image, points):
#     """
#     Вырезает область изображения, заданную полигоном
#     :param image: исходное изображение
#     :param points: список точек полигона в формате [(x1,y1), (x2,y2), ...]
#     :return: вырезанная область и маска
#     """
#     # Создаем маску
#     mask = np.zeros(image.shape[:2], dtype=np.uint8)
#     pts = np.array(points, dtype=np.int32)
#
#     # Заполняем полигон на маске белым цветом
#     cv2.fillPoly(mask, [pts], 255)
#
#     # Применяем маску к изображению
#     result = cv2.bitwise_and(image, image, mask=mask)
#
#     # Находим ограничивающий прямоугольник
#     x, y, w, h = cv2.boundingRect(pts)
#
#     # Вырезаем область
#     cropped = result[y:y + h, x:x + w]
#
#     return cropped, mask
#
#
# # Загрузка изображения
# image = cv2.imread('frame_1.png')
# if image is None:
#     print("Ошибка: не удалось загрузить изображение!")
#     exit()
#
# # Координаты полигона (в порядке обхода)
# polygon_points = [(9, 163), (237, 148), (201, 479), (62, 479), (5, 443), (6, 164)]
#
# # Вырезаем область
# cropped_region, mask = extract_polygon(image, polygon_points)
#
# # Рисуем полигон на исходном изображении
# image_with_polygon = image.copy()
# pts = np.array(polygon_points, dtype=np.int32)
# cv2.polylines(image_with_polygon, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
#
# # Отображаем результаты
# cv2.imshow('Original with Polygon', image_with_polygon)
# cv2.imshow('Mask', mask)
# cv2.imshow('Cropped Region', cropped_region)
#
# print("Нажмите любую клавишу для выхода...")
# cv2.waitKey(0)
# cv2.destroyAllWindows()


import cv2
import numpy as np

# Параметры камеры
def fix_perspct(frame):
    K = np.array([[386.26166874,   8.86539874, 278.66589351],
                  [0., 407.63805824, 219.29121805],
                  [0., 0., 1.]])
    D = np.array([[-0.17621875],
                  [-0.15100755],
                  [0.66708108],
                  [-0.61169934]])

    # Загрузка изображения
    img = cv2.imread("chess_frames/frame_test.png")
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

# 5. Отображение результатов
cv2.imshow('Original', img)
# cv2.imshow('With Border', img_with_border)
cv2.imshow('Undistorted', undistorted)
# cv2.imshow('Final Result', result)
cv2.waitKey(0)
cv2.destroyAllWindows()