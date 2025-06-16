import cv2
import numpy as np
import glob

CHECKERBOARD = (4, 5)
square_size = 2.0

objp = np.zeros((1, CHECKERBOARD[0]*CHECKERBOARD[1], 3), np.float32)
objp[0,:,:2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
objp *= square_size

objpoints = []
imgpoints = []

images = glob.glob('chess_frames/*.png')

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD,
                cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE)
    print(f"{fname}: corners found = {ret}, count = {len(corners) if corners is not None else 0}")

    if ret:
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        corners_subpix = cv2.cornerSubPix(gray, corners, (3,3), (-1,-1), criteria)

        imgpoints.append(corners_subpix)
        objpoints.append(objp)

        cv2.drawChessboardCorners(img, CHECKERBOARD, corners_subpix, ret)
        cv2.imshow('Corners', img)
        cv2.waitKey(500)

cv2.destroyAllWindows()

# if len(objpoints) < 10:
#     print("Недостаточно изображений с найденными углами для надежной калибровки.")
#     exit()

K = np.zeros((3,3))
D = np.zeros((4,1))
rvecs = []
tvecs = []

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 1e-6)
flags = cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC + cv2.fisheye.CALIB_CHECK_COND

rms, K, D, rvecs, tvecs = cv2.fisheye.calibrate(
    objpoints,
    imgpoints,
    gray.shape[::-1],
    K,
    D,
    rvecs,
    tvecs,
    flags,
    criteria
)

print(f"RMS ошибки калибровки: {rms}")
print(f"Матрица камеры: \n{K}")
print(f"Коэффициенты искажения: \n{D}")