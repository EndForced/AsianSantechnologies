import cv2
import numpy as np

# допустим, у тебя есть калибровочные данные
camera_matrix = np.array([[700, 0, 350],
                          [0, 700, 350],
                          [0, 0, 1]], dtype=np.float32)

pic = np.full((750, 750, 3), fill_value=0, dtype=np.uint8)

dist_coeffs = np.array([-0.392, -0.028, 0.0105, 0.0006], dtype=np.float32)

img = cv2.imread('1.jpg')

# cap = cv2.VideoCapture("rtsp://192.168.1.100:8554/live")  # 0 — это номер камеры (обычно встроенная)
#
# for i in range(30):
#     ret, frame = cap.read()
#     cv2.waitKey(1)
#
# ret, frame = cap.read()
# if ret:
#     img = frame[0:480, 0:480]
#     cv2.imshow("Кадр", img)
#     cv2.imwrite("112.jpg", img)

img = cv2.flip(img, -1)
img = cv2.resize(img, [600, 600])

pic[75:675, 75:675] = img
# cv2.imshow("",pic)
undistorted = cv2.undistort(pic, camera_matrix, dist_coeffs)
new = undistorted
cv2.imwrite("11.jpg", new)

COLOR_RANGES = {
    "Red": [np.array([0, 90, 172]), np.array([22, 255, 255]),
            np.array([150, 100, 80]), np.array([180, 255, 255])],
    "Red1": [np.array([0, 80, 0]), np.array([20, 255, 255]),
             np.array([150, 80, 0]), np.array([180, 255, 255])],
    "Green": (np.array([50, 70, 40]), np.array([100, 255, 255])),
    "Blue": (np.array([110, 70, 40]), np.array([140, 255, 255]))
}


def search_for_color(frame, color, min_area=50):
    if color not in COLOR_RANGES:
        raise ValueError(f"Unknown color: {color}")

    frame_height, frame_width = frame.shape[:2]
    if color == "Red" or "Red1" == color:
        if color == "Red":
            frame = frame[int(frame_height * 0.1):int(frame_height * 0.9),
                    int(frame_width * 0.1):int(frame_width * 0.9)]
        lower1, upper1, lower2, upper2 = COLOR_RANGES[color]
        mask1 = cv2.inRange(frame, lower1, upper1)
        mask2 = cv2.inRange(frame, lower2, upper2)
        mask = cv2.bitwise_or(mask1, mask2)
    else:
        lower, upper = COLOR_RANGES[color]
        mask = cv2.inRange(frame, lower, upper)
    mask = cv2.blur(mask, [5, 5])
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    x, y, w, h = 0, 0, 0, 0

    for cont in contours:
        area = cv2.contourArea(cont)
        if area > min_area:
            x1, y1, w1, h1 = cv2.boundingRect(cont)
            if w1 * h1 > w * h:
                x, y, w, h = x1, y1, w1, h1

    return x, y, w, h


def tile_to_code(frame):
    if frame.shape[:2] != (200, 200):
        frame = cv2.resize(frame, (200, 200))

    frame_blur = cv2.blur(frame, (5, 5))
    hsv = cv2.cvtColor(frame_blur, cv2.COLOR_BGR2HSV)

    # Поиск зеленых труб
    x, y, w, h = search_for_color(hsv, "Green")
    if h * w:
        if w > h:
            return 61 if (y + h / 2) > 100 else 63
        else:
            return 62 if (x + w / 2) > 100 else 64

    # Поиск синих объектов (рампа)
    xb, yb, wb, hb = search_for_color(hsv, "Blue")
    if hb * wb:
        xr, yr, wr, hr = search_for_color(hsv, "Red")
        delta_x = xb - xr
        delta_y = yb - yr

        if abs(delta_x) < abs(delta_y):
            return 34 if delta_y < 0 else 32
        else:
            return 33 if delta_x < 0 else 31

    # Определение высоты
    elevation = 1 if (np.mean(frame_blur)) > 120 else 2

    # Поиск красных труб
    x, y, w, h = search_for_color(hsv, "Red")
    if h * w:
        return 32 + elevation * 10 if h / w > 1.2 else 31 + elevation * 10

    return elevation * 10


points = [(68, 48), (710, 40), (715, 710), (52, 685)]


def extract_warped(image, output_size=640):
    global points

    """
    Выполняет перспективное преобразование изображения, чтобы выровнять четырехугольник в квадрат.

    Параметры:
        image: входное изображение
        points: массив из 4 точек в формате np.array([[x1,y1], [x2,y2], [x3,y3], [x4,y4]])
        output_size: размер выходного квадратного изображения

    Возвращает:
        Выровненное квадратное изображение
    """
    if len(points) != 4:
        raise ValueError("Функция ожидает ровно 4 точки для перспективного преобразования")

    points = np.array(points, dtype=np.float32)

    # Сортируем точки в порядке: верх-лев, верх-прав, низ-прав, низ-лев
    # 1. Разделяем точки на верхние и нижние по координате y
    sorted_y = points[np.argsort(points[:, 1])]
    top = sorted_y[:2]
    bottom = sorted_y[2:]

    # 2. Для верхних и нижних точек определяем левую и правую по x
    top = top[np.argsort(top[:, 0])]
    (tl, tr) = top

    bottom = bottom[np.argsort(bottom[:, 0])]
    (bl, br) = bottom

    # Итоговый порядок точек
    final_points = np.array([tl, tr, br, bl], dtype=np.float32)

    # Точки назначения (квадрат)
    dst_points = np.array([
        [0, 0],
        [output_size, 0],
        [output_size, output_size],
        [0, output_size]
    ], dtype=np.float32)

    # Вычисляем матрицу преобразования и применяем ее
    M = cv2.getPerspectiveTransform(final_points, dst_points)
    return cv2.warpPerspective(image, M, (output_size, output_size))


warped = extract_warped(undistorted)

# 83*8

stepic = [72, 75, 85, 88, 88, 85, 75, 72]
cords = [sum(stepic[0:i]) for i in range(9)]
mat  = []
print(cords)
for y in range(8):
    row = []
    for x in range(8):
        local = warped[cords[y]:cords[y + 1], cords[x]:cords[x + 1]]
        res = tile_to_code(local)
        cv2.rectangle(warped, (cords[x] , cords[y] ), (cords[x + 1], cords[y + 1] ), (240, 240, 240), 2)
        cv2.putText(warped, str(res), (cords[x] , cords[y] + int(70 * 0.8)), fontScale=1, color=(240, 240, 240),
                    thickness=2, fontFace=1)
        print(res, end=' ')
        row.append(res)
    print()
    mat.append(row)

for i in range(len(points)):
    cv2.circle(new, (int(points[i][0]), int(points[i][1])), 5, (0, 200, 200), 2)

cv2.imshow("warped", warped)

cv2.imshow("1", new)

for i in range(8):
    print(mat[i])

import requests
import json

# URL сервера (адрес Flask-приложения из предыдущего примера)
url = 'http://192.168.2.221:5000/data'

# Данные для отправки (в формате словаря)
data_to_send = {
    'mat': str(mat),
}

# Отправляем POST-запрос
try:
    # Вариант 1: отправка JSON-данных
    response = requests.post(
        url,
        json=data_to_send,  # автоматически конвертирует в JSON и устанавливает Content-Type
        timeout=5, # таймаут на выполнение запроса (секунды)
        verify = False
    )

    # Вариант 2: можно отправить как form-data (раскомментировать если нужно)
    # response = requests.post(url, data=data_to_send)

    # Выводим результат
    print(f"Статус код: {response.status_code}")
    print("Ответ сервера:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

except requests.exceptions.RequestException as e:
    print(f"Ошибка при выполнении запроса: {e}")

cv2.waitKey(0)
cv2.destroyAllWindows()

