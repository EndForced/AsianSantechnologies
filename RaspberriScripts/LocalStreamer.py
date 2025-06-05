"Стримит картинку с камер в пределах распберри по запросу. Есть 2 режима"

from picamera2 import Picamera2
import socket
import pickle
import cv2
import threading
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DualCameraServer:
    def __init__(self):

        self.picam2_primary = Picamera2(0)
        self.picam2_secondary = Picamera2(1)
        self.stream_active = False
        self.conn = None
        self.lock = threading.Lock()
        self.quality = 15

        self.primary_config = self.picam2_primary.create_video_configuration(
            main={
                "size": (1280, 720),
                "format": "RGB888",
            },
            controls={
                "FrameRate": 15,
                "ExposureTime": 10000,
                "AnalogueGain": 1.0,
            },
            buffer_count=6
        )

        self.secondary_config = self.picam2_secondary.create_video_configuration(
            main={
                "size": (1280, 720),
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
        while 1:
            try:
                data = conn.recv(1024)
                if data:
                    command = data.decode('utf-8').strip()
                    if command == "GET_FRAMES":

                        primary_frame = self.picam2_primary.capture_array("main")
                        secondary_frame = self.picam2_secondary.capture_array("main")

                        primary_bytes = primary_frame.tobytes()
                        secondary_bytes = secondary_frame.tobytes()

                        data = {
                            'type': 'uncompressed_dual',
                            'camera1': {
                                'width': primary_frame.shape[1],
                                'height': primary_frame.shape[0],
                                'channels': primary_frame.shape[2] if len(primary_frame.shape) > 2 else 1,
                                'dtype': str(primary_frame.dtype),
                                'data': primary_bytes
                            },
                            'camera2': {
                                'width': secondary_frame.shape[1],
                                'height': secondary_frame.shape[0],
                                'channels': secondary_frame.shape[2] if len(secondary_frame.shape) > 2 else 1,
                                'dtype': str(secondary_frame.dtype),
                                'data': secondary_bytes
                            }
                        }


                        serialized_data = pickle.dumps(data)
                        conn.sendall(len(serialized_data).to_bytes(4, 'big'))
                        conn.sendall(serialized_data)

                        logger.info("Sent uncompressed frames from both cameras")

            except Exception as e:
                logger.error(f"Error in get_uncompressed: {e}")
                try:
                    error_data = {
                        'type': 'error',
                        'message': str(e)
                    }
                    serialized_error = pickle.dumps(error_data)
                    conn.sendall(len(serialized_error).to_bytes(4, 'big'))
                    conn.sendall(serialized_error)
                except:
                    pass

    def command_handler(self, conn):
        #eto dead code

        conn.settimeout(0.2)
        while self.stream_active:
            try:
                data = conn.recv(1024)
                if data:
                    command = data.decode('utf-8').strip()
                    logger.info(f"Received command: {command}")
                    if command == "GET_UNCOMPRESSED":
                        logger.info("getting uncompressed...")
                        self.get_uncompressed(conn)

                    elif command == "STOP":
                        self.stream_active = False
                elif not data:
                    break
            except socket.timeout:
                continue
            except (ConnectionResetError, BrokenPipeError):
                logger.warning("Client disconnected in command handler")
                break
            except Exception as e:
                logger.error(f"Command handler error: {e}")
                break

    def handle_stream(self, connection):
        try:
            while 1:
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
                    connection.sendall(len(serialized_data).to_bytes(4, 'big'))
                    connection.sendall(serialized_data)
                except (ConnectionResetError, BrokenPipeError):
                    logger.warning("Client disconnected during streaming")
                    break

        finally:
            connection.close()
            self.stream_active = False
            logger.info("Connection closed")


    def start(self):
        try:
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
                    logger.info(f"Client connected: {addr}, waiting for connection type")

                    conn_type = b""
                    while not conn_type:
                        conn_type = conn.recv(1024)

                    conn_type = conn_type.decode().strip().replace("'", "")
                    logger.info(f"Connection type: {conn_type}")

                    if conn_type == "WEBSITE_STREAMING":
                        logger.info("Starting website stream...")
                        threading.Thread(
                            target=self.handle_stream,
                            args=(conn,),
                            daemon=True
                        ).start()

                    elif conn_type == "UNCOMPRESSED_API":
                        logger.info("Starting robot's API...")
                        threading.Thread(
                            target=self.get_uncompressed,
                            args=(conn,),
                            daemon=True
                        ).start()



        except Exception as e:
            logger.error(f"Error in start(): {e}")
            raise



        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
        finally:
            self.picam2_primary.stop()
            self.picam2_secondary.stop()
            logger.info("Both cameras stopped")


if __name__ == "__main__":
    server = DualCameraServer()
    server.start()