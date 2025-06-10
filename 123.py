# # import cv2
# # import numpy as np
# #
# # # Загрузка изображений
# # frame1 = cv2.imread('frame_1.png')
# # frame2 = cv2.imread('frame_2.png', cv2.IMREAD_UNCHANGED)
# #
# # if frame1 is None or frame2 is None:
# #     print("Ошибка: Не удалось загрузить изображения!")
# #     exit()
# #
# # # Создаем холст в 2 раза больше исходного кадра
# # canvas_width = frame1.shape[1] * 2
# # canvas_height = frame1.shape[0] * 2
# # canvas = np.zeros((canvas_height, canvas_width, 3), dtype=np.uint8)
# #
# # # Центрируем frame1 на холсте
# # x_offset = (canvas_width - frame1.shape[1]) // 2
# # y_offset = (canvas_height - frame1.shape[0]) // 2
# # canvas[y_offset:y_offset + frame1.shape[0], x_offset:x_offset + frame1.shape[1]] = frame1
# #
# # # Инициализация параметров
# # alpha = 0.5
# # x_pos, y_pos = canvas_width // 2, canvas_height // 2  # Начальная позиция по центру
# # scale = 1.0
# #
# # # Создаем окно
# # cv2.namedWindow('Image Blending', cv2.WINDOW_NORMAL)
# # cv2.resizeWindow('Image Blending', 1000, 800)
# #
# #
# # def correct_perspective(img, src_points, output_size):
# #     # src_points - 4 точки исходного изображения
# #     # output_size - (width, height) выходного изображения
# #
# #     dst_points = np.array([
# #         [0, 0],
# #         [output_size[0] - 1, 0],
# #         [output_size[0] - 1, output_size[1] - 1],
# #         [0, output_size[1] - 1]
# #     ], dtype=np.float32)
# #
# #     M = cv2.getPerspectiveTransform(src_points, dst_points)
# #     warped = cv2.warpPerspective(img, M, output_size)
# #     return warped
# #
# #
# # def nothing(x):
# #     pass
# #
# #
# # # Создаем trackbars
# # cv2.createTrackbar('Alpha', 'Image Blending', 50, 100, nothing)
# # cv2.createTrackbar('X Position', 'Image Blending', x_pos, canvas_width, nothing)
# # cv2.createTrackbar('Y Position', 'Image Blending', y_pos, canvas_height, nothing)
# # cv2.createTrackbar('Scale', 'Image Blending', 100, 200, nothing)
# #
# # while True:
# #     # Получаем параметры
# #     alpha = cv2.getTrackbarPos('Alpha', 'Image Blending') / 100.0
# #     x_pos = cv2.getTrackbarPos('X Position', 'Image Blending')
# #     y_pos = cv2.getTrackbarPos('Y Position', 'Image Blending')
# #     scale = cv2.getTrackbarPos('Scale', 'Image Blending') / 100.0
# #
# #     # Масштабируем frame2
# #     if scale != 1.0:
# #         frame2_resized = cv2.resize(frame2, None, fx=scale, fy=scale)
# #     else:
# #         frame2_resized = frame2.copy()
# #
# #     # Создаем копию холста
# #     blended = canvas.copy()
# #     h, w = frame2_resized.shape[:2]
# #
# #     # Обработка альфа-канала
# #     if frame2_resized.shape[2] == 4:
# #         overlay = frame2_resized[:, :, :3]
# #         mask = frame2_resized[:, :, 3:] / 255.0 * alpha
# #     else:
# #         overlay = frame2_resized
# #         mask = np.ones((h, w, 1)) * alpha
# #
# #     # Вычисляем область для вставки
# #     y1, y2 = max(0, y_pos), min(canvas_height, y_pos + h)
# #     x1, x2 = max(0, x_pos), min(canvas_width, x_pos + w)
# #
# #     if y2 > y1 and x2 > x1:
# #         # Обрезаем overlay и mask если нужно
# #         overlay_cropped = overlay[y1 - y_pos:y2 - y_pos, x1 - x_pos:x2 - x_pos]
# #         mask_cropped = mask[y1 - y_pos:y2 - y_pos, x1 - x_pos:x2 - x_pos]
# #
# #         # Наложение
# #         blended[y1:y2, x1:x2] = (blended[y1:y2, x1:x2] * (1 - mask_cropped) + overlay_cropped * mask_cropped)
# #         cv2.imshow('Image Blending', blended)
# #
# #         # Выход по ESC
# #         if cv2.waitKey(1) == 27:
# #             break
# #
# # cv2.destroyAllWindows()
#
#
# import cv2
# import numpy as np
#
#
# def undistort_image(input_image_path, output_image_path, calibration_data_path=None):
#     """
#     Исправляет искажения на изображении с помощью параметров калибровки камеры.
#
#     Параметры:
#         input_image_path: путь к исходному искаженному изображению
#         output_image_path: путь для сохранения исправленного изображения
#         calibration_data_path: путь к файлу с параметрами калибровки (если None, используются стандартные значения)
#     """
#     # Загрузка изображения
#     img = cv2.imread(input_image_path)
#     if img is None:
#         print(f"Ошибка: не удалось загрузить изображение {input_image_path}")
#         return
#
#     # Параметры калибровки камеры
#     if calibration_data_path:
#         # Загрузка параметров калибровки из файла
#         try:
#             data = np.load(calibration_data_path)
#             mtx = data['mtx']
#             dist = data['dist']
#         except Exception as e:
#             print(f"Ошибка загрузки данных калибровки: {e}")
#             return
#     else:
#         # Стандартные параметры (примерные)
#         h, w = img.shape[:2]
#         mtx = np.array([[w, 0, w / 2],
#                         [0, h, h / 2],
#                         [0, 0, 1]], dtype=np.float32)
#         dist = np.array([-0.4, 0.1, 0.0, 0.0, 0.0], dtype=np.float32)
#
#     # Исправление искажения
#     undistorted_img = cv2.undistort(img, mtx, dist, None, mtx)
#
#     # Сохранение результата
#     cv2.imwrite(output_image_path, undistorted_img)
#     print(f"Исправленное изображение сохранено как {output_image_path}")
#
#     # Отображение результатов
#     combined = np.hstack((img, undistorted_img))
#     cv2.imshow('Сравнение: Исходное -> Исправленное', combined)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
#
#
# # Пример использования
# if __name__ == "__main__":
#     input_image = "frame_2.png"  # Укажите ваш файл изображения
#     output_image = "undistorted1.jpg"
#     calibration_file = None  # Или укажите путь к файлу калибровки "calibration_data.npz"
#
#     undistort_image(input_image, output_image, calibration_file)
import cv2

import cv2
import numpy as np

# Исходное изображение
img = cv2.imread("frame_2.png")
if img is None:
    print("Ошибка: не удалось загрузить изображение")
    exit()

# Копия изображения для работы
working_img = img.copy()

# Начальные координаты прямоугольника
x1, y1 = 40, 200  # Левый верхний угол
x2, y2 = 300, 450  # Правый нижний угол

# Создаем окно
cv2.namedWindow("Управление прямоугольником", cv2.WINDOW_NORMAL)


# Функция обновления изображения
def update_image():
    global working_img

    # Создаем копию исходного изображения
    working_img = img.copy()

    # Рисуем прямоугольник
    cv2.rectangle(working_img, (x1, y1), (x2, y2), (0, 0, 255), 2)

    # Создаем правую панель с информацией
    info_panel = np.full((img.shape[0], 300, 3), 240, dtype=np.uint8)

    # Добавляем текст с координатами
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.7
    color = (0, 0, 0)
    thickness = 1

    text = [
        "Координаты прямоугольника:",
        "",
        f"Левый верхний: ({x1}, {y1})",
        f"Правый нижний: ({x2}, {y2})",
        "",
        "Для копирования:",
        f"({x1}, {y1}, {x2}, {y2})",
        "",
        "Управление:",
        "ESC - выход",
        "'s' - сохранить",
        "'c' - скопировать в буфер"
    ]

    y_pos = 40
    for i, line in enumerate(text):
        if i in [2, 3, 6]:  # Выделяем важные строки
            cv2.putText(info_panel, line, (20, y_pos), font, scale, (0, 0, 255), thickness)
        else:
            cv2.putText(info_panel, line, (20, y_pos), font, scale, color, thickness)
        y_pos += 30

    # Объединяем изображение и панель информации
    combined = np.hstack((working_img, info_panel))
    cv2.imshow("Управление прямоугольником", combined)


# Функция обновления координат
def update_coord(coord, value):
    global x1, y1, x2, y2

    if coord == 'x1':
        x1 = value
    elif coord == 'y1':
        y1 = value
    elif coord == 'x2':
        x2 = value
    elif coord == 'y2':
        y2 = value

    # Гарантируем, что x2 > x1 и y2 > y1
    if x2 <= x1: x2 = x1 + 1
    if y2 <= y1: y2 = y1 + 1

    update_image()


# Создаем trackbars
cv2.createTrackbar("X1", "Управление прямоугольником", x1, img.shape[1], lambda x: update_coord('x1', x))
cv2.createTrackbar("Y1", "Управление прямоугольником", y1, img.shape[0], lambda x: update_coord('y1', x))
cv2.createTrackbar("X2", "Управление прямоугольником", x2, img.shape[1], lambda x: update_coord('x2', x))
cv2.createTrackbar("Y2", "Управление прямоугольником", y2, img.shape[0], lambda x: update_coord('y2', x))

# Первоначальное отображение
update_image()

# Основной цикл
while True:
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC для выхода
        break
    elif key == ord('s'):  # Сохранить координаты
        print(f"Координаты для копирования: ({x1}, {y1}, {x2}, {y2})")
    elif key == ord('c'):  # Копировать в буфер обмена (требуется pyperclip)
        try:
            import pyperclip

            pyperclip.copy(f"({x1}, {y1}, {x2}, {y2})")
            print("Координаты скопированы в буфер обмена!")
        except:
            print("Установите pyperclip для копирования в буфер: pip install pyperclip")

cv2.destroyAllWindows()