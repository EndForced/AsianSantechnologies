import cv2
a = cv2.imread("Warped.png")
a = a[260:310,:]
cv2.imshow("a",a)
cv2.waitKey(0)
cv2.imwrite("border.png", a)

# import cv2
# import numpy as np
#
# # Создаём окно с ползунками
# cv2.namedWindow('HSV Mask Tuner')
#
# # Начальные значения HSV (можно менять)
# initial_values = {
#     'H_min': 0, 'H_max': 179,
#     'S_min': 0, 'S_max': 255,
#     'V_min': 0, 'V_max': 255
# }
#
# # Создаём trackbars
# cv2.createTrackbar('H_min', 'HSV Mask Tuner', initial_values['H_min'], 179, lambda x: None)
# cv2.createTrackbar('H_max', 'HSV Mask Tuner', initial_values['H_max'], 179, lambda x: None)
# cv2.createTrackbar('S_min', 'HSV Mask Tuner', initial_values['S_min'], 255, lambda x: None)
# cv2.createTrackbar('S_max', 'HSV Mask Tuner', initial_values['S_max'], 255, lambda x: None)
# cv2.createTrackbar('V_min', 'HSV Mask Tuner', initial_values['V_min'], 255, lambda x: None)
# cv2.createTrackbar('V_max', 'HSV Mask Tuner', initial_values['V_max'], 255, lambda x: None)
#
# # Захват видео с камеры (или загрузка видеофайла)
# cap = cv2.imread("border.png")  # 0 - первая камера, или укажите путь к видео
#
# while True:
#     frame = cv2.imread("border.png")
#
#
#     # Получаем текущие значения ползунков
#     h_min = cv2.getTrackbarPos('H_min', 'HSV Mask Tuner')
#     h_max = cv2.getTrackbarPos('H_max', 'HSV Mask Tuner')
#     s_min = cv2.getTrackbarPos('S_min', 'HSV Mask Tuner')
#     s_max = cv2.getTrackbarPos('S_max', 'HSV Mask Tuner')
#     v_min = cv2.getTrackbarPos('V_min', 'HSV Mask Tuner')
#     v_max = cv2.getTrackbarPos('V_max', 'HSV Mask Tuner')
#
#     # Формируем нижнюю и верхнюю границы HSV
#     lower_hsv = np.array([h_min, s_min, v_min])
#     upper_hsv = np.array([h_max, s_max, v_max])
#
#     # Конвертируем в HSV и создаём маску
#     hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
#     mask = cv2.inRange(hsv, lower_hsv, upper_hsv)
#
#     # Применяем маску к оригинальному изображению
#     result = cv2.bitwise_and(frame, frame, mask=mask)
#
#     # Отображаем результат
#     cv2.imshow('Original', frame)
#     cv2.imshow('HSV Mask', mask)
#     cv2.imshow('Result', result)
#
#     # Выход по нажатию 'q'
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#
# cap.release()
# cv2.destroyAllWindows()