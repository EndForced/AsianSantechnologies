# from flask import Flask, render_template
# from flask_socketio import SocketIO, emit
# import serial
# import threading
# import base64
# import time
# import cv2
# import os
# class RobotAPI:
#     def __init__(self, position, orientation):
#         self.ser = serial.Serial('/dev/ttyAMA0', 115200, timeout = 1)
#         self.ser.flush()  # очищаем буфер
#
#         if max(position) > 15:
#             raise ValueError("Robot is out of borders!", position)
#         self.RobotPosition = position
#
#         if orientation not in [1,2,3,4]:
#             raise  ValueError("Unknown orientation!", orientation)
#         self.RobotOrientation = orientation
#
#         self.ESPMessage = self.read()
#         self.IsDoingAction = 0
#
#     def send(self, data):
#         data_to_send = data + "\n"  # Data to send (must be bytes)
#         self.ser.write(data_to_send.encode('utf-8'))
#
#     def read(self):
#         line = self.ser.readline().decode('utf-8').strip()
#
#         print(line)
#         if line is not None:
#             lines = line.split("*")
#             return lines
#
#     def drive_through_roadmap(self, roadmap):
#         pass
#
#     def handle_website_commands(self, args):
#         self.ser.reset_input_buffer()  # Для pyserial
#
#         if args:
#             res = ""
#             self.send(args)
#
#             while not res:
#                 res = self.read()
#
#             socketio.emit('uart_message', {
#                 'message': res,
#                 'type': 'received'
#             })
#
#
# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'your_secret_key'
# socketio = SocketIO(app)
# robot = RobotAPI((0, 0), 1)
#
# camera_configs = {
#     'low': {'size': (640, 480), 'fps': 30},
#     'medium': {'size': (1296, 972), 'fps': 20},
#     'high': {'size': (1920, 1080), 'fps': 15},
#     'max': {'size': (2592, 1944), 'fps': 10}
# }
# current_quality = 'medium'
# stream_active = False
#
# os.environ['LD_LIBRARY_PATH'] = '/usr/lib/aarch64-linux-gnu:' + os.environ.get('LD_LIBRARY_PATH', '')
# import os
# import cv2
# import base64
# import time
#
#
# def get_frame_from_service():
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         s.connect(('localhost', 65432))
#         while True:
#             # Получаем длину данных
#             length_bytes = s.recv(4)
#             if not length_bytes:
#                 break
#             length = int.from_bytes(length_bytes, 'big')
#
#             # Получаем сами данные
#             data = b''
#             while len(data) < length:
#                 packet = s.recv(length - len(data))
#                 if not packet:
#                     break
#                 data += packet
#
#             frame = pickle.loads(data)
#             yield base64.b64encode(frame).decode('utf-8')
#
# @app.route('/')
# def index():
#     return render_template('index.html')
#
# @app.route('/raw_cameras')
# def get_raw():
#     robot.handle_website_commands("Reset")
#     return render_template('raw_cameras.html')
#
#
#
# @socketio.on('uart_command')
# def handle_uart_command(data):
#     command = data.get('command', '')
#     print(f"Received UART command: {command}")
#     robot.handle_website_commands(command)
#
# @socketio.on('start_stream')
# def handle_connect():
#     for frame in get_frame_from_service():
#         socketio.emit('video_frame', {'data': frame})
#
# @socketio.on('stop_stream')
# def handle_stop_stream():
#     global stream_active
#     stream_active = False
#
#
# if __name__ == '__main__':
#     pass
#
# socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)


from flask import Flask, render_template
from flask_socketio import SocketIO
import socket
import pickle
import threading
import logging
import base64
import cv2
import numpy as np
import time

app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading', engineio_logger=False)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DualCameraClient:
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
            logger.info("Connected to camera server")

            while self.stream_active:
                try:
                    # Получаем длину данных
                    length_bytes = self.client_socket.recv(4)
                    if not length_bytes:
                        break

                    length = int.from_bytes(length_bytes, 'big')
                    data = b''
                    while len(data) < length:
                        packet = self.client_socket.recv(length - len(data))
                        if not packet:
                            break
                        data += packet

                    if data:
                        # Декодируем данные с сервера
                        frames = pickle.loads(data)

                        # Отправляем кадры на клиент
                        if 'camera1' in frames:
                            encoded1 = base64.b64encode(frames['camera1']).decode('utf-8')
                            socketio.emit('video_frame', {'camera': 1, 'frame': encoded1})

                        if 'camera2' in frames:
                            encoded2 = base64.b64encode(frames['camera2']).decode('utf-8')
                            socketio.emit('video_frame', {'camera': 2, 'frame': encoded2})

                        # Отправляем карту если есть
                        if self.map_image is not None:
                            _, buffer = cv2.imencode('.jpg', self.map_image)
                            map_encoded = base64.b64encode(buffer).decode('utf-8')
                            socketio.emit('video_frame', {'camera': 3, 'frame': map_encoded})

                except (ConnectionResetError, BrokenPipeError) as e:
                    logger.error(f"Connection error: {str(e)}")
                    break

        except Exception as e:
            logger.error(f"Error: {str(e)}")
        finally:
            self.client_socket.close()
            with self.lock:
                self.stream_active = False

    def set_map_image(self, img):
        with self.lock:
            self.map_image = img
            if img is not None:
                _, buffer = cv2.imencode('.jpg', img)
                map_encoded = base64.b64encode(buffer).decode('utf-8')
                socketio.emit('video_frame', {'camera': 3, 'frame': map_encoded})


camera_client = DualCameraClient()


@app.route('/')
def index():
    return render_template('raw_cameras.html',
                           qualities=['low', 'medium', 'high', 'max'])


@app.route('/map_control')
def map_control():
    return render_template('map_control.html')


@socketio.on('start_stream')
def handle_start_stream(data):
    camera = data.get('camera')
    quality = data.get('quality', 'medium')

    if camera in [1, 2]:
        with camera_client.lock:
            if not camera_client.stream_active:
                client_thread = threading.Thread(target=camera_client.connect)
                client_thread.daemon = True
                client_thread.start()
    elif camera == 3:
        # Активируем поток карты
        black_img = np.zeros((480, 640, 3), dtype=np.uint8)
        camera_client.set_map_image(black_img)


@socketio.on('stop_stream')
def handle_stop_stream(data):
    camera = data.get('camera')
    if camera in [1, 2]:
        with camera_client.lock:
            camera_client.stream_active = False
    elif camera == 3:
        camera_client.set_map_image(None)


@socketio.on('set_map_image')
def handle_set_map_image(data):
    try:
        img_data = base64.b64decode(data['image'])
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        camera_client.set_map_image(img)
    except Exception as e:
        logger.error(f"Error setting map image: {str(e)}")


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)