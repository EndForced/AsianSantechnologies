import socket
import pickle
import cv2
import numpy as np


def get_single_uncompressed_frame(camera_id=1):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('localhost', 65432))

        try:
            # Отправляем запрос
            s.sendall(b"GET_UNCOMPRESSED")

            # Получаем подтверждение
            response = s.recv(1024)
            if response != b"accepted":
                print("Server didn't accept the request")
                return None

            # Отправляем номер камеры
            s.sendall(str(camera_id).encode())

            # Получаем данные кадра
            length_bytes = s.recv(4)
            if not length_bytes:
                return None

            length = int.from_bytes(length_bytes, 'big')
            data = s.recv(length)

            frame_data = pickle.loads(data)
            if "type" in frame_data and frame_data["type"] == "uncompressed":
                nparr = np.frombuffer(frame_data['uncompressed'], np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                return frame

        except (socket.timeout, ConnectionError) as e:
            print(f"Connection error: {e}")
            return None


# Пример использования
frame = get_single_uncompressed_frame(1)
if frame is not None:
    cv2.imshow("Uncompressed Frame", frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()