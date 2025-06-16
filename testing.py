import cv2
import numpy as np


def detect_square_zones(image_path, output_path="zones_output.jpg"):
    # Загрузка и предобработка изображения
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Улучшение контраста (CLAHE)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Адаптивная бинаризация
    binary = cv2.adaptiveThreshold(enhanced, 255,
                                   cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)

    # Морфологические операции
    kernel = np.ones((3, 3), np.uint8)
    processed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)
    processed = cv2.morphologyEx(processed, cv2.MORPH_OPEN, kernel, iterations=1)

    # Поиск контуров
    contours, _ = cv2.findContours(processed, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # Списки для зон
    white_zones = []
    black_zones = []

    for cnt in contours:
        # Аппроксимация контура
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)

        # Фильтрация четырехугольников
        if len(approx) == 4:
            # Вычисление характеристик
            area = cv2.contourArea(approx)
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = float(w) / h

            # Критерии квадрата
            if area > 1000 and 0.2 <= aspect_ratio <= 3:
                # Создание маски для анализа цвета
                mask = np.zeros(gray.shape, dtype=np.uint8)
                cv2.drawContours(mask, [approx], -1, 255, -1)

                # Определение средней яркости
                mean_val = cv2.mean(gray, mask=mask)[0]

                # Классификация зон
                if mean_val > 210:  # Белая зона
                    white_zones.append(approx)
                elif mean_val < 170:  # Черная зона
                    black_zones.append(approx)

    # Визуализация результатов
    result = img.copy()

    # Рисуем белые зоны (синий)
    for zone in white_zones:
        cv2.drawContours(result, [zone], -1, (255, 0, 0), 3)
        M = cv2.moments(zone)
        if M['m00'] != 0:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            cv2.putText(result, f"W:{cv2.contourArea(zone):.0f}", (cx - 20, cy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

    # Рисуем черные зоны (красный)
    for zone in black_zones:
        cv2.drawContours(result, [zone], -1, (0, 0, 255), 3)
        M = cv2.moments(zone)
        if M['m00'] != 0:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            cv2.putText(result, f"B:{cv2.contourArea(zone):.0f}", (cx - 20, cy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    # Сохранение и вывод
    cv2.imwrite(output_path, result)
    print(f"Найдено: {len(white_zones)} белых и {len(black_zones)} черных зон")

    cv2.imshow("Detected Zones", result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# Использование
detect_square_zones("warped.png")