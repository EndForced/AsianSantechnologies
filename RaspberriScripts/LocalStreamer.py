# camera_service.py (работает в системном Python)
from picamera2 import Picamera2
import socket
import pickle
import time
import cv2


def camera_service():
    picam2 = Picamera2()
    config = picam2.create_video_configuration(main={"size": (640, 480)})
    picam2.configure(config)
    picam2.start()

    # Создаем сокет для передачи данных
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('localhost', 65432))
        s.listen()
        conn, addr = s.accept()

        try:
            while True:
                frame = picam2.capture_array("main")
                _, buffer = cv2.imencode('.jpg', frame)
                data = pickle.dumps(buffer)
                conn.sendall(len(data).to_bytes(4, 'big')  # Отправляем длину
                conn.sendall(data)  # Отправляем данные
        finally:
            picam2.stop()


if __name__ == "__main__":
    camera_service()