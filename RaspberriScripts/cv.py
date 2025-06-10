zones = {
}
cam2_floor1 = [[(74,226),(247,410)], [(269,240),(449,388)],
               [(4,408),(267,624)], [(278,430),(474,594)]]

import cv2
import numpy as np

def update_frame(frame):
    for pt1, pt2 in cam2_floor1:
        cv2.rectangle(frame, pt1, pt2, (0, 0, 0), thickness=4)
        part = frame[pt1[1]:pt2[1], pt1[0]:pt2[0]].copy()
        part = lead_color(part)[0]
        frame[pt1[1]:pt2[1], pt1[0]:pt2[0]] = part
    return frame


def lead_color(img_slice, threshold=0.5, text_position=(10, 30)):
        """
        Определяет преобладающий цвет на изображении/срезе и добавляет соответствующую надпись

        Параметры:
            img_slice: срез изображения (numpy array)
            threshold: порог для определения (0.5 = 50%)
            text_position: позиция текста (x, y)

        Возвращает:
            Изображение с надписью и строку с результатом
        """
        # Конвертируем в grayscale
        gray = cv2.cvtColor(img_slice, cv2.COLOR_BGR2GRAY)

        # Бинаризация (черное = 0, белое = 255)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

        # Подсчет пикселей
        white_pixels = np.sum(binary == 255)
        black_pixels = np.sum(binary == 0)
        total_pixels = binary.size

        # Определение преобладающего цвета
        white_ratio = white_pixels / total_pixels
        result = "white" if white_ratio > threshold else "black"

        # Добавление текста на изображение
        font = cv2.FONT_HERSHEY_SIMPLEX
        color = (0, 255, 0)  # Зеленый цвет текста
        cv2.putText(img_slice, result, text_position, font, 1, color, 2, cv2.LINE_AA)

        return img_slice, result
