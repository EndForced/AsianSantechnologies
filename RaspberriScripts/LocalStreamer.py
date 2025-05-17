from picamera2 import Picamera2
import socket
import pickle
import time
import cv2
import threading
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CameraServer:
    def __init__(self):
        self.picam2 = Picamera2()
        self.stream_active = False
        self.conn = None
        self.lock = threading.Lock()
        self.quality = 80  # Качество JPEG (0-100)

        # Оптимизированные настройки
        self.config = self.picam2.create_video_configuration(
            main={
                "size": (1280, 720),  # 720p баланс качества/производительности
                "format": "YUV420"  # Более эффективный формат
            },
            controls={
                "FrameRate": 30,  # Число, не строка!
                "AwbMode": "auto",  # Автобаланс белого
                "ExposureTime": 10000,  # Фиксированная экспозиция (микросекунды)
                "AnalogueGain": 1.0,  # Фиксированное усиление
                "NoiseReductionMode": "Fast"  # Ускоренное шумоподавление
            },
            buffer_count=6  # Больше буферов для плавности
        )
        self.picam2.configure(self.config)

    def process_frame(self, frame):
        """Оптимизированное кодирование JPEG"""
        _, buffer = cv2.imencode(
            '.jpg',
            frame,
            [
                int(cv2.IMWRITE_JPEG_QUALITY), self.quality,
                int(cv2.IMWRITE_JPEG_OPTIMIZE), 1,
                int(cv2.IMWRITE_JPEG_PROGRESSIVE), 1
            ]
        )
        return buffer

    def start(self):
        try:
            self.picam2.start()
            logger.info("Camera initialized with optimized settings")

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('0.0.0.0', 65432))
                s.listen()
                logger.info("Socket server ready on port 65432")

                while True:
                    self.conn, addr = s.accept()
                    self.conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    logger.info(f"Client connected: {addr}")
                    self.stream_active = True

                    try:
                        while self.stream_active:
                            frame = self.picam2.capture_array("main")
                            buffer = self.process_frame(frame)
                            data = pickle.dumps(buffer)

                            try:
                                self.conn.sendall(len(data).to_bytes(4, 'big'))
                                self.conn.sendall(data)
                            except (ConnectionResetError, BrokenPipeError):
                                logger.warning("Client disconnected")
                                break

                    finally:
                        self.conn.close()
                        self.stream_active = False

        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
        finally:
            self.picam2.stop()
            logger.info("Camera stopped")


if __name__ == "__main__":
    server = CameraServer()
    server.start()