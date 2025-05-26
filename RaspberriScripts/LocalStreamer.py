from picamera2 import Picamera2
import socket
import pickle
import time
import cv2
import threading
import logging
import select

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
        try:
            # ... ваш код обработки ...

            # Отправка подтверждения
            conn.send(b"accepted")
            print("Sent acceptance confirmation")

        except Exception as e:
            print(f"Error sending acceptance: {e}")

    def handle_command(self, command, conn):
        try:
            # Пытаемся декодировать команду
            decoded_command = command.decode('utf-8')
            logger.info(f"Received command: {decoded_command}")

            if decoded_command == "GET_UNCOMPRESSED":
                # Отправляем подтверждение
                conn.sendall(b"accepted")

                # Получаем номер камеры (следующие данные)
                camera_id = conn.recv(1024).decode('utf-8').strip()

                # Получаем кадр с нужной камеры
                frame = self.picam2_primary.capture_array(
                    "main") if camera_id == "1" else self.picam2_secondary.capture_array("main")

                # Отправляем несжатый кадр
                _, img_encoded = cv2.imencode('.jpg', frame)
                img_bytes = img_encoded.tobytes()
                response = {
                    'type': 'uncompressed',
                    'uncompressed': img_bytes
                }
                serialized_response = pickle.dumps(response)
                conn.sendall(len(serialized_response).to_bytes(4, 'big'))
                conn.sendall(serialized_response)

            elif decoded_command == "STOP":
                self.stream_active = False

        except UnicodeDecodeError:
            logger.warning("Received binary command that couldn't be decoded")

    def start(self):
        self.picam2_primary.start()
        self.picam2_secondary.start()
        logger.info("Both cameras initialized")

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('0.0.0.0', 65432))
            s.listen()
            logger.info("Socket server ready on port 65432")

            while True:
                conn, addr = s.accept()
                conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                logger.info(f"Client connected: {addr}")

                self.conn = conn  # Сохраняем соединение
                self.stream_active = True


                try:
                    while self.stream_active:
                        # Основной поток только отправляет видео
                        primary_frame = self.picam2_primary.capture_array("main")
                        secondary_frame = self.picam2_secondary.capture_array("main")

                        primary_buffer, _ = self.process_frame(primary_frame, 1)
                        secondary_buffer, _ = self.process_frame(secondary_frame, 2)

                        data = {
                            'camera1': primary_buffer,
                            'camera2': secondary_buffer
                        }

                        serialized_data = pickle.dumps(data)
                        try:
                            conn.sendall(len(serialized_data).to_bytes(4, 'big'))
                            conn.sendall(serialized_data)

                            # Проверка входящих команд
                            ready = select.select([conn], [], [], 0.01)  # Небольшой таймаут
                            if ready[0]:
                                command = conn.recv(1024).strip()
                                if not command:
                                    raise ConnectionResetError("Client disconnected")

                                self.handle_command(command, conn)

                        except (ConnectionResetError, BrokenPipeError):
                            logger.warning("Client disconnected during streaming")
                            break

                finally:
                    conn.close()
                    self.stream_active = False
                    logger.info("Connection closed")





if __name__ == "__main__":
    server = DualCameraServer()
    server.start()