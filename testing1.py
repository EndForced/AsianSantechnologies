# from RaspberriScripts.CvProcessing.CellDetector import check_for_borders, count_pixels
#
# r = [(0, 0, 172), (23, 255, 255)]
#
# import cv2
# a = cv2.imread("Warped.png")
# print(check_for_borders(a, 1))
# a = a[100:550, 300:400]
#
# print(count_pixels(a,r[0], r[1]))
# cv2.imshow("a",a)
# cv2.waitKey(0)
# cv2.imwrite("border.png", a)

import cv2
import numpy as np
from sklearn.neighbors import KDTree

# Определяем известные цвета в формате BGR (как использует OpenCV)
known_colors = {
    "Red": [
        np.array([172, 0, 0]),  # BGR для первого диапазона Red
        np.array([255, 22, 22])  # BGR для второго диапазона Red
    ],
    "Gray": [
        np.array([80, 100, 150]),  # BGR для первого диапазона Gray
        np.array([255, 255, 180])  # BGR для второго диапазона Gray
    ],
    "Green": [
        np.array([163, 161, 72]),  # BGR для первого диапазона Green
        np.array([196, 255, 85])  # BGR для второго диапазона Green
    ],
    "Blue": [
        np.array([90, 90, 110]),  # BGR для первого диапазона Blue
        np.array([255, 255, 140])  # BGR для второго диапазона Blue
    ],
    "Black": [
        np.array([68, 61, 75]),  # BGR для первого диапазона Black
        np.array([38, 40, 142])  # BGR для второго диапазона Black
    ]
}

# Создаем список всех эталонных цветов для поиска ближайшего
reference_colors = []
color_names = []

for name, colors in known_colors.items():
    for color in colors:
        reference_colors.append(color)
        color_names.append(name)

# Преобразуем в массив numpy и строим KD-дерево для быстрого поиска
ref_array = np.array(reference_colors)
kdtree = KDTree(ref_array)


def replace_with_nearest_color(image):
    # Получаем размеры изображения
    height, width, _ = image.shape

    # Преобразуем изображение в массив пикселей
    pixels = image.reshape(-1, 3)

    # Находим ближайшие известные цвета для всех пикселей
    _, indices = kdtree.query(pixels, k=1)

    # Заменяем цвета пикселей на ближайшие известные
    replaced_pixels = ref_array[indices.flatten()]

    # Восстанавливаем форму изображения
    result_image = replaced_pixels.reshape(height, width, 3)

    return result_image.astype(np.uint8)


# Пример использования
if __name__ == "__main__":
    # Загружаем изображение
    image = cv2.imread('Warped.png')

    if image is not None:
        # Заменяем цвета
        result = replace_with_nearest_color(image)

        # Сохраняем результат
        cv2.imwrite('output.jpg', result)
        print("Обработка завершена. Результат сохранен как output.jpg")
    else:
        print("Не удалось загрузить изображение")