from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import serial
import socket
import pickle
import threading
import logging
import base64
import cv2
import numpy as np
import sys
import os
import time
import struct

serial = serial.Serial('/dev/ttyAMA0', 115200, timeout=1)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
socketio = SocketIO(app,
                   async_mode='threading',
                   engineio_logger=False,
                   ping_timeout=60,
                   max_http_buffer_size=50*1024*1024)


camera_configs = {
    'low': {'size': (640, 480), 'fps': 30},
    'medium': {'size': (1296, 972), 'fps': 20},
    'high': {'size': (1920, 1080), 'fps': 15},
    'max': {'size': (2592, 1944), 'fps': 10}
}
current_quality = 'medium'
stream_active = False

class RobotAPI:
    def __init__(self, position, orientation, serial):
        self.ser = serial
        self.ser.flush()

        if max(position) > 15:
            raise ValueError("Robot is out of borders!", position)
        self.RobotPosition = position

        if orientation not in [1, 2, 3, 4]:
            raise ValueError("Unknown orientation!", orientation)
        self.RobotOrientation = orientation

        self.ESPMessage = self.read()
        self.IsDoingAction = 0

    def send(self, data):
        data_to_send = data + "\n"
        self.ser.write(data_to_send.encode('utf-8'))

    def read(self):
        line = self.ser.readline().decode('utf-8').strip()
        print(line)
        if line is not None:
            lines = line.split("*")
            return lines

    def drive_through_roadmap(self, roadmap):
        pass

    def handle_website_commands(self, args):
        self.ser.reset_input_buffer()
        if args:
            res = ""
            self.send(args)
            while not res:
                res = self.read()
            socketio.emit('uart_message', {
                'message': res,
                'type': 'received'
            })

class CameraClient:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.stream_active = False
        self.lock = threading.Lock()
        self.map_image = None

    def connect(self):
        try:
            self.client_socket.connect(('localhost', 65432))
            with self.lock:
                self.stream_active = True

            self.client_socket.sendall(b"WEBSITE_STREAMING")
            logger.info("Connected to dual camera server")

            while self.stream_active:
                try:
                    # Получаем длину данных
                    length_bytes = self.client_socket.recv(4)
                    if not length_bytes:
                        break

                    length = int.from_bytes(length_bytes, 'big')

                    # Получаем данные
                    data = b''
                    while len(data) < length:
                        packet = self.client_socket.recv(length - len(data))
                        if not packet:
                            break
                        data += packet

                    if data:
                        frames = pickle.loads(data)

                        if 'camera1' in frames:
                            encoded1 = base64.b64encode(frames['camera1']).decode('utf-8')
                            socketio.emit('video_frame', {
                                'camera': 1,
                                'frame': encoded1
                            })

                        if 'camera2' in frames:
                            encoded2 = base64.b64encode(frames['camera2']).decode('utf-8')
                            socketio.emit('video_frame', {
                                'camera': 2,
                                'frame': encoded2
                            })

                        if self.map_image is not None:
                            _, buffer = cv2.imencode('.jpg', self.map_image)
                            map_encoded = base64.b64encode(buffer).decode('utf-8')
                            socketio.emit('video_frame', {
                                'camera': 3,
                                'frame': map_encoded
                            })

                except (ConnectionResetError, BrokenPipeError) as e:
                    logger.error(f"Connection error: {str(e)}")
                    break
                except pickle.UnpicklingError as e:
                    logger.error(f"Data unpacking error: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
        finally:
            self.client_socket.close()
            with self.lock:
                self.stream_active = False

class WebsiteHolder:
    def __init__(self, uart_port):
        # Настройка логгера
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Инициализация Flask и SocketIO
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app,
                                 async_mode='threading',
                                 engineio_logger=False,
                                 ping_timeout=60,
                                 max_http_buffer_size=50 * 1024 * 1024)

        self.camera_configs = {
            'low': {'size': (640, 480), 'fps': 30},
            'medium': {'size': (1296, 972), 'fps': 20},
            'high': {'size': (1920, 1080), 'fps': 15},
            'max': {'size': (2592, 1944), 'fps': 10}
        }
        self.current_quality = 'medium'
        self.stream_active = False

        # Инициализация робота и клиента камеры (предполагается, что классы определены)
        self.robot = RobotAPI((0, 0), 1, uart_port)
        self.camera_client = CameraClient()

        # Установка маршрутов и обработчиков SocketIO
        self._set_routes()
        self._set_socketio_handlers()

    def _set_routes(self):
        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/raw_cameras')
        def get_raw():
            self.robot.handle_website_commands("Reset")
            return render_template('raw_cameras.html',
                                   qualities=['low', 'medium', 'high', 'max'])

    def _set_socketio_handlers(self):
        @self.socketio.on('uart_command')
        def handle_uart_command(data):
            command = data.get('command', '')
            self.logger.info(f"Received UART command: {command}")
            self.robot.handle_website_commands(command)

        @self.socketio.on('start_stream')
        def handle_start_stream(data=None):
            if data is None:
                camera = 1
                quality = 'medium'
            else:
                camera = data.get('camera', 1)
                quality = data.get('quality', 'medium')

            if camera == 3:
                self.socketio.emit('video_frame', {
                    'camera': 3,
                    'frame': ''
                })
            else:
                with self.camera_client.lock:
                    if not self.camera_client.stream_active:
                        client_thread = threading.Thread(target=self.camera_client.connect)
                        client_thread.daemon = True
                        client_thread.start()

        @self.socketio.on('stop_stream')
        def handle_stop_stream(data=None):
            if data is None:
                camera = 1
            else:
                camera = data.get('camera', 1)

            if camera == 3:
                black_img = np.zeros((480, 640, 3), dtype=np.uint8)
                encoded = base64.b64encode(black_img.tobytes()).decode('utf-8')
                self.socketio.emit('video_frame', {
                    'camera': 3,
                    'frame': encoded
                })
            else:
                with self.camera_client.lock:
                    self.camera_client.stream_active = False

    def start_website(self):
        self.socketio.run(self.app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)




# # Инициализация объектов
# robot = RobotAPI((0, 0), 1, serial)
# camera_client = CameraClient()
#
# @app.route('/')
# def index():
#     return render_template('index.html')
#
# @app.route('/raw_cameras')
# def get_raw():
#     robot.handle_website_commands("Reset")
#     return render_template('raw_cameras.html',
#                          qualities=['low', 'medium', 'high', 'max'])
#
# @socketio.on('uart_command')
# def handle_uart_command(data):
#     command = data.get('command', '')
#     print(f"Received UART command: {command}")
#     robot.handle_website_commands(command)
#
# @socketio.on('start_stream')
# def handle_start_stream(data=None):
#     if data is None:
#         # Режим совместимости со старым кодом
#         camera = 1
#         quality = 'medium'
#     else:
#         camera = data.get('camera', 1)
#         quality = data.get('quality', 'medium')
#
#     if camera == 3:
#         socketio.emit('video_frame', {
#             'camera': 3,
#             'frame': ''
#         })
#     else:
#         with camera_client.lock:
#             if not camera_client.stream_active:
#                 client_thread = threading.Thread(target=camera_client.connect)
#                 client_thread.daemon = True
#                 client_thread.start()
#
# @socketio.on('stop_stream')
# def handle_stop_stream(data=None):
#     if data is None:
#         # Режим совместимости со старым кодом
#         camera = 1
#     else:
#         camera = data.get('camera', 1)
#
#     if camera == 3:
#         black_img = np.zeros((480, 640, 3), dtype=np.uint8)
#         encoded = base64.b64encode(black_img.tobytes()).decode('utf-8')
#         socketio.emit('video_frame', {
#             'camera': 3,
#             'frame': encoded
#         })
#     else:
#         with camera_client.lock:
#             camera_client.stream_active = False
# #
# if __name__ == "__main__":
#     time.sleep(1)
#     socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)

s = WebsiteHolder(serial)
s.start_website()