import cv2
import numpy as np


def find_field_corners(image_path):
    # Загрузка изображения
    img = cv2.imread(image_path)
    if img is None:
        print("Не удалось загрузить изображение")
        return None

    # Преобразование в HSV цветовое пространство для лучшего выделения красного цвета
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Определение диапазонов красного цвета в HSV
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    # Создание масок для красного цвета и их объединение
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(mask1, mask2)

    # Улучшение маски с помощью морфологических операций
    kernel = np.ones((5, 5), np.uint8)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel, iterations=1)

    # Поиск контуров
    contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        print("Красная линия не найдена")
        return None

    # Выбор самого большого контура (предполагаем, что это поле)
    largest_contour = max(contours, key=cv2.contourArea)

    # Аппроксимация контура для упрощения
    epsilon = 0.02 * cv2.arcLength(largest_contour, True)
    approx = cv2.approxPolyDP(largest_contour, epsilon, True)

    # Если контур имеет 4 угла, считаем его прямоугольником
    if len(approx) == 4:
        # Сортируем углы в порядке: верхний-левый, верхний-правый, нижний-правый, нижний-левый
        corners = approx.reshape((4, 2))
        corners = sorted(corners, key=lambda x: x[0])
        left = sorted(corners[:2], key=lambda x: x[1])
        right = sorted(corners[2:], key=lambda x: x[1])
        sorted_corners = np.array([left[0], right[0], right[1], left[1]], dtype=np.float32)

        # Визуализация (для отладки)
        for i, corner in enumerate(sorted_corners):
            x, y = corner
            cv2.circle(img, (int(x), int(y)), 10, (0, 255, 0), -1)
            cv2.putText(img, str(i), (int(x) + 10, int(y) + 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        cv2.imshow("Detected Corners", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        return sorted_corners
    else:
        print("Не удалось найти прямоугольное поле")
        return None


# Использование функции
image_path = "field.jpg"  # Укажите путь к вашему изображению
corners = find_field_corners(image_path)

if corners is not None:
    print("Найдены углы поля:")
    for i, (x, y) in enumerate(corners):
        print(f"Угол {i}: ({x:.1f}, {y:.1f})")

find_field_corners()