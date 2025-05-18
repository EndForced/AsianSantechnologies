import socket
import pickle
import base64
import cv2
import numpy as np


def get_single_uncompressed_frame(camera_id=1):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('localhost', 65432))

        # Запрашиваем одно несжатое изображение
        s.sendall(b"GET_UNCOMPRESSED")
        s.sendall(str(camera_id).encode())

        # Получаем данные
        length_bytes = s.recv(4)
        length = int.from_bytes(length_bytes, 'big')
        data = s.recv(length)

        frame_data = pickle.loads(data)
        if "type" in frame_data.keys() and frame_data["type"] == "uncompressed":
            img_data = base64.b64decode(frame_data['uncompressed'])
            nparr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return frame


# Использование
while not get_single_uncompressed_frame(1):
    frame = get_single_uncompressed_frame(1)
    if frame:
        cv2.imwrite("Uncompressed Frame", frame)
# cv2.waitKey(0)
# cv2.destroyAllWindows()