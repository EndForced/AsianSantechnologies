from picamera2 import Picamera2
import socket
import pickle
import time
import cv2
import threading
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DualCameraServer:
    def __init__(self):
        # Инициализация двух камер
        self.picam2_primary = Picamera2(0)  # Основная камера
        self.picam2_secondary = Picamera2(1)  # Вторая камера
        self.stream_active = False
        self.conn = None
        self.lock = threading.Lock()
        self.quality = 30

        # Конфигурация для основной камеры
        self.primary_config = self.picam2_primary.create_video_configuration(
            main={
                "size": (1080, 720),
                "format": "RGB888",
            },
            controls={
                "FrameRate": 15,
                "ExposureTime": 10000,
                "AnalogueGain": 1.0,
            },
            buffer_count=6
        )

        # Конфигурация для второй камеры (может отличаться)
        self.secondary_config = self.picam2_secondary.create_video_configuration(
            main={
                "size": (1080, 720),
                "format": "RGB888",
            },
            controls={
                "FrameRate": 15,
                "ExposureTime": 10000,
                "AnalogueGain": 1.0,
            },
            buffer_count=6
        )

        self.picam2_primary.configure(self.primary_config)
        self.picam2_secondary.configure(self.secondary_config)

    def process_frame(self, frame, camera_id):
        """Обработка кадра с указанием камеры"""
        # Здесь можно добавить специфичную обработку для каждой камеры
        _, buffer = cv2.imencode(
            '.jpg',
            frame,
            [
                int(cv2.IMWRITE_JPEG_QUALITY), self.quality,
                int(cv2.IMWRITE_JPEG_OPTIMIZE), 1
            ]
        )
        return buffer, camera_id

    def get_uncompressed(self, conn):
        print("Getting uncompressed")

    def start(self):
        try:
            # Запускаем обе камеры
            self.picam2_primary.start()
            self.picam2_secondary.start()
            logger.info("Both cameras initialized")

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('0.0.0.0', 65432))
                s.listen()
                logger.info("Socket server ready on port 65432")

                while True:
                    self.conn, addr = s.accept()
                    self.conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    logger.info(f"Client connected: {addr}")

                    self.conn.settimeout(1.0)  # 0.1 сек таймаут
                    try:
                        data = self.conn.recv(1024)
                        if data:
                            command = data.decode('utf-8').strip()
                            if command == "GET_UNCOMPRESSED":
                                print("command: ", command)
                                self.get_uncompressed(self.conn)
                    except socket.timeout:
                        pass  # Таймаут, данных нет
                    except Exception as e:
                        print("Ошибка:", e)

                    self.stream_active = True

                    try:
                        while self.stream_active:
                            # Получаем кадры с обеих камер
                            primary_frame = self.picam2_primary.capture_array("main")
                            secondary_frame = self.picam2_secondary.capture_array("main")

                            # Обрабатываем кадры
                            primary_buffer, _ = self.process_frame(primary_frame, 1)
                            secondary_buffer, _ = self.process_frame(secondary_frame, 2)

                            # Упаковываем данные в словарь
                            data = {
                                'camera1': primary_buffer,
                                'camera2': secondary_buffer
                            }

                            # Сериализуем и отправляем
                            serialized_data = pickle.dumps(data)
                            try:
                                self.conn.sendall(len(serialized_data).to_bytes(4, 'big'))
                                self.conn.sendall(serialized_data)
                            except (ConnectionResetError, BrokenPipeError):
                                logger.warning("Client disconnected")
                                break

                    finally:
                        self.conn.close()
                        self.stream_active = False

        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
        finally:
            self.picam2_primary.stop()
            self.picam2_secondary.stop()
            logger.info("Both cameras stopped")


if __name__ == "__main__":
    server = DualCameraServer()
    server.start()