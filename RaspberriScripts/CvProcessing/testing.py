import cv2
import numpy as np
from matplotlib import pyplot as plt


def fix_perspective(img, K, D, border_size=100):
    img_with_border = cv2.copyMakeBorder(
        img,
        border_size, border_size, border_size, border_size,
        cv2.BORDER_CONSTANT,
        value=(0, 0, 0)  # Черный цвет фона
    )

    h, w = img_with_border.shape[:2]
    K_border = K.copy()
    K_border[0, 2] += border_size
    K_border[1, 2] += border_size

    undistorted = cv2.fisheye.undistortImage(
        img_with_border,
        K=K_border,
        D=D,
        Knew=K_border,
        new_size=(w, h)
    )

    return undistorted


def update(val=None):
    # Получаем текущие значения ползунков
    fx = cv2.getTrackbarPos('fx', 'Controls') / 100
    fy = cv2.getTrackbarPos('fy', 'Controls') / 100
    cx = cv2.getTrackbarPos('cx', 'Controls') / 100
    cy = cv2.getTrackbarPos('cy', 'Controls') / 100

    k1 = cv2.getTrackbarPos('k1', 'Controls') / 10000 - 0.5
    k2 = cv2.getTrackbarPos('k2', 'Controls') / 10000 - 0.5
    k3 = cv2.getTrackbarPos('k3', 'Controls') / 10000 - 0.5
    k4 = cv2.getTrackbarPos('k4', 'Controls') / 10000 - 0.5

    border = cv2.getTrackbarPos('border', 'Controls')

    # Обновляем матрицы K и D
    K = np.array([
        [fx, 0, cx],
        [0, fy, cy],
        [0, 0, 1]
    ])

    D = np.array([[k1, k2, k3, k4]])

    # Применяем коррекцию
    result = fix_perspective(img, K, D, border)

    # Показываем результат
    cv2.imshow('Undistorted', result)
