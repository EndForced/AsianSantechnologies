from picamera2 import Picamera2
import cv2
import socket
import pickle
import threading
import logging
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CameraServer:
    def __init__(self):
        self.picam2 = Picamera2()
        self.stream_active = False
        self.lock = threading.Lock()

        # Оптимальные настройки для OV5647
        self.config = self.picam2.create_video_configuration(
            main={
                "size": (1280, 720),
                "format": "RGB888",
            },
            controls={
                "FrameRate": 15,  # OV5647 стабильнее на 15 FPS
                "AwbEnable": True,
                # "AwbMode": "auto",  # Автоматический баланс белого
                "ColourGains": (1.7, 1.4),  # Коррекция для OV5647
                "Saturation": 1.2,  # Увеличиваем насыщенность
                "Contrast": 1.1,  # Небольшой контраст
                "Brightness": 0.05,  # Подстройка яркости
                "Sharpness": 1.0,
            },
            buffer_count=4
        )
        self.quality = 85
        self.color_correction_matrix = np.array([

        [1.2, -0.2, -0.1],  # Уменьшили красное усиление
        [-0.3, 1.3, -0.1],  # Уменьшили зеленое усиление
        [0.1, -0.1, 1.2]  # Увеличили синий

        ], dtype=np.float32)

    def apply_color_correction(self, frame):
        """Применяем матрицу коррекции цвета"""
        frame_float = frame.astype(np.float32) / 255.0
        corrected = cv2.transform(frame_float, self.color_correction_matrix)
        corrected = np.clip(corrected * 255, 0, 255).astype(np.uint8)
        return corrected

    def process_frame(self, frame):
        """Обработка кадра с коррекцией цвета"""
        # Применяем коррекцию цвета
        corrected_frame = self.apply_color_correction(frame)

        # Конвертируем RGB в BGR для OpenCV
        bgr_frame = cv2.cvtColor(corrected_frame, cv2.COLOR_RGB2BGR)

        # Кодируем в JPEG с оптимальными параметрами
        _, buffer = cv2.imencode('.jpg', bgr_frame, [
            int(cv2.IMWRITE_JPEG_QUALITY), self.quality,
            int(cv2.IMWRITE_JPEG_OPTIMIZE), 1
        ])
        return buffer

    def start(self):
        try:
            self.picam2.configure(self.config)
            self.picam2.start()
            logger.info("Camera started with color correction")

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('0.0.0.0', 65432))
                s.listen()

                while True:
                    conn, addr = s.accept()
                    with self.lock:
                        self.stream_active = True

                    try:
                        while self.stream_active:
                            frame = self.picam2.capture_array("main")
                            buffer = self.process_frame(frame)
                            data = pickle.dumps(buffer)

                            try:
                                conn.sendall(len(data).to_bytes(4, 'big'))
                                conn.sendall(data)
                            except (ConnectionResetError, BrokenPipeError):
                                break
                    finally:
                        conn.close()
                        with self.lock:
                            self.stream_active = False
        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
        finally:
            self.picam2.stop()
            logger.info("Camera stopped")


if __name__ == "__main__":
    server = CameraServer()
    server.start()