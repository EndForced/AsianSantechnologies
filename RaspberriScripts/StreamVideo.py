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

app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CameraClient:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.stream_active = False

    def connect(self):
        try:
            self.client_socket.connect(('localhost', 65432))
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
                        socketio.emit('video_frame', {'data': data.hex()})

                except (ConnectionResetError, BrokenPipeError) as e:
                    logger.error(f"Connection error: {str(e)}")
                    break

        except Exception as e:
            logger.error(f"Error: {str(e)}")
        finally:
            self.client_socket.close()
            self.stream_active = False


camera_client = CameraClient()


@app.route('/')
def index():
    return render_template('raw_cameras.html',
                           qualities=['low', 'medium', 'high', 'max'])


@socketio.on('start_stream')
def handle_start_stream(quality):
    if not camera_client.stream_active:
        client_thread = threading.Thread(target=camera_client.connect)
        client_thread.daemon = True
        client_thread.start()


@socketio.on('stop_stream')
def handle_stop_stream():
    camera_client.stream_active = False


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
