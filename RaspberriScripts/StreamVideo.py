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
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ClientClasses.VisualizationProcessing import VisualizePaths

app = Flask(__name__)
socketio = SocketIO(app,
                  async_mode='threading',
                  engineio_logger=False,
                  ping_timeout=60,
                  max_http_buffer_size=50*1024*1024)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CameraClient:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.stream_active = False
        self.lock = threading.Lock()
        self.map_image = None  # Для хранения изображения карты

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

                    # Получаем данные
                    data = b''
                    while len(data) < length:
                        packet = self.client_socket.recv(length - len(data))
                        if not packet:
                            break
                        data += packet

                    if data:
                        # Декодируем и отправляем в base64
                        frame = pickle.loads(data)
                        encoded = base64.b64encode(frame.tobytes()).decode('utf-8')

                        # Отправляем основной кадр для камер 1 и 2
                        socketio.emit('video_frame', {
                            'camera': 1,  # Или 2, в зависимости от источника
                            'frame': encoded
                        })

                        # Если есть изображение карты, отправляем его для камеры 3
                        if self.map_image is not None:
                            map_encoded = base64.b64encode(self.map_image.tobytes()).decode('utf-8')
                            socketio.emit('video_frame', {
                                'camera': 3,
                                'frame': map_encoded
                            })

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
        """Устанавливает изображение для третьей камеры (карты)"""
        with self.lock:
            self.map_image = img
            if img is not None:
                # Немедленно отправляем обновленное изображение карты
                map_encoded = base64.b64encode(img.tobytes()).decode('utf-8')
                socketio.emit('video_frame', {
                    'camera': 3,
                    'frame': map_encoded
                })


camera_client = CameraClient()


@app.route('/')
def index():
    return render_template('raw_cameras.html',
                           qualities=['low', 'medium', 'high', 'max'])


@socketio.on('start_stream')
def handle_start_stream(data):
    camera = data.get('camera', 1)
    quality = data.get('quality', 'medium')

    if camera == 3:
        # Для камеры 3 (карты) просто активируем поток
        socketio.emit('video_frame', {
            'camera': 3,
            'frame': ''  # Пустой кадр, если нет изображения
        })
    else:
        with camera_client.lock:
            if not camera_client.stream_active:
                client_thread = threading.Thread(target=camera_client.connect)
                client_thread.daemon = True
                client_thread.start()


@socketio.on('stop_stream')
def handle_stop_stream(data):
    camera = data.get('camera', 1)
    if camera == 3:
        # Для камеры 3 просто отправляем черный кадр
        black_img = np.zeros((480, 640, 3), dtype=np.uint8)
        encoded = base64.b64encode(black_img.tobytes()).decode('utf-8')
        socketio.emit('video_frame', {
            'camera': 3,
            'frame': encoded
        })
    else:
        with camera_client.lock:
            camera_client.stream_active = False


@socketio.on('set_map_image')
def handle_set_map_image(data):
    """Обработчик для установки изображения карты через WebSocket"""
    try:
        # Декодируем изображение из base64
        img_data = base64.b64decode(data['image'])
        # Преобразуем в numpy array
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        camera_client.set_map_image(img)
    except Exception as e:
        logger.error(f"Error setting map image: {str(e)}")


def main():
    mat = [[10, 31, 10, 10, 42, 10, 10, 62], [10, 20, 10, 10, 20, 20, 10, 62], [20, 20, 20, 10, 32, 34, 10, 62], [20, 20, 20, 10, 20, 10, 20, 10], [20, 33, 33, 10, 71, 10, 10, 41], [33, 41, 20, 20, 34, 10, 10, 10], [10, 20, 10, 10, 32, 20, 20, 34], [10, 10, 10, 20, 20, 34, 10, 10]]
    obj = VisualizePaths(mat)
    while True:
        time.sleep(3)
        obj.show()
        img = obj.resizedPicture

        # Добавьте проверку изображения
        if img is not None and isinstance(img, np.ndarray):
            print(f"Image shape: {img.shape}, dtype: {img.dtype}")  # Для отладки
            camera_client.set_map_image(img)
        else:
            print("Invalid image!")

if __name__ == "__main__":
    main_code = threading.Thread(target = main)
    main_code.start()

    time.sleep(1)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)

