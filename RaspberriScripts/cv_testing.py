# import cv2
# import numpy as np
# from itertools import combinations
#
def crop_and_correct_perspective_5_points(image, points, output_size=500):

    # Находим 2 ближайшие точки
    min_dist = float('inf')
    closest_pair = None

    # Перебираем все возможные пары точек
    for (p1, p2) in combinations(points, 2):
        dist = np.linalg.norm(np.array(p1) - np.array(p2))
        if dist < min_dist:
            min_dist = dist
            closest_pair = (p1, p2)

    if closest_pair is None:
        raise ValueError("Не удалось найти ближайшую пару точек")

    # Заменяем их на среднюю точку
    avg_point = (
        (closest_pair[0][0] + closest_pair[1][0]) // 2,
        (closest_pair[0][1] + closest_pair[1][1]) // 2
    )

    # Оставшиеся 3 точки + новая средняя
    remaining_points = [p for p in points if p not in closest_pair]
    final_points = remaining_points + [avg_point]

    # Сортируем точки по углу относительно их центра масс
    center = np.mean(final_points, axis=0)
    def sort_key(p):
        return np.arctan2(p[1] - center[1], p[0] - center[0])
    final_points_sorted = sorted(final_points, key=sort_key)

    # Преобразуем в numpy array
    src_points = np.array(final_points_sorted, dtype="float32")

    # Целевые точки (квадрат)
    dst_points = np.array([
        [0, 0],
        [output_size, 0],
        [output_size, output_size],
        [0, output_size]
    ], dtype="float32")

    # Вычисляем матрицу перспективы и применяем её
    M = cv2.getPerspectiveTransform(src_points, dst_points)
    warped = cv2.warpPerspective(image, M, (output_size, output_size))

    return warped


# Загрузка изображения
image = cv2.imread("Warped.png")

# 5 точек (все углы, но одна лишняя)
points = [(216, 226), (169, 330), (345, 330), (352, 217), (216, 218)]


# Обработка
result = crop_and_correct_perspective_5_points(image, points)

# Сохранение
cv2.imwrite("output.jpg", result)


