'''Это самый непонятный файл тут. Низкоуровневая работа с сокетами и обмен данными с LocalStreamer'''

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import serial
import socket
import pickle
import threading
import logging
import base64
import numpy as np
import time
import cv2

class RobotAPI:
    #по большей части тут работа с юартом, запоминание позиции, получение и отправка данных с камер



    def __init__(self, position, orientation, serial, socketio = None):
        self.telemetryQuality = 15
        self.mapQuality = 40

        self.ser = serial
        self.ser.flush()
        self.socket = socketio

        if max(position) > 15:
            raise ValueError("Robot is out of borders!", position)
        self.Position = position

        if orientation not in [1, 2, 3, 4]:
            raise ValueError("Unknown orientation!", orientation)
        self.Orientation = orientation

        self.ESPMessage = self.read()
        self.IsDoingAction = 0
        self.frames = {}

        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect(('localhost', 65432))
        self.conn.sendall(b"UNCOMPRESSED_API")

        # time.sleep(0.1)

    @staticmethod
    def recvall(conn, n):
        #крутая читалка для стабильности
        data = bytearray()
        while len(data) < n:
            packet = conn.recv(n - len(data))
            if not packet:
                # Соединение закрыто или ошибка
                return None
            data.extend(packet)
        return data

    def send(self, data):
        data_to_send = data + "\n"
        self.ser.write(data_to_send.encode('utf-8'))

    def read(self):
        line = self.ser.readline().decode('utf-8').strip()
        if line and len(line)>0:
            lines = line.split("*")
            return lines

    def drive_through_roadmap(self, commands):
        commands_dict = {"L" : "Turn Left", "R": "Turn Right", "X": "Pid Forward", "x": "Pid Backwards", "F1": "Up", "F0": "Down", "G0": "Grab", "P1": "Put"}

        for i in range(len(commands)):
            if len(commands[i]) == 2:
                if commands[i][0] not in ["F", "P", "G"]:
                    command = commands[i][0]
                    num = commands[i][1] if commands[i][1] else ""
                    commands[i] = f"{commands_dict[command]} {num}"

                elif commands[i][0] in ["F","P","G"]:
                    command = commands[i]
                    commands[i] = f"{commands_dict[command]}"

        print(commands)

        for i in commands:
            self.do(i)


    def do(self, args):
        self.ser.reset_input_buffer()
        if args.find("Pid") != -1:
            if self.Orientation == "U": self.Position = ( self.Position[0] - 1, self.Position[1] )
            elif self.Orientation == "D": self.Position = (self.Position[0] + 1, self.Position[1])
            elif self.Orientation == "R": self.Position = (self.Position[0], self.Position[1] + 1)
            elif self.Orientation == "R": self.Position = (self.Position[0], self.Position[1] - 1)



        elif args.find("Turn") != -1:

            if "2" not in args:  # Обычный поворот (не двойной)

                if "Left" in args:

                    if self.Orientation == "L":
                        self.Orientation = "D"

                    elif self.Orientation == "D":
                        self.Orientation = "R"

                    elif self.Orientation == "R":
                        self.Orientation = "U"

                    elif self.Orientation == "U":
                        self.Orientation = "L"


                elif "Right" in args:

                    if self.Orientation == "L":
                        self.Orientation = "U"

                    elif self.Orientation == "U":
                        self.Orientation = "R"

                    elif self.Orientation == "R":
                        self.Orientation = "D"

                    elif self.Orientation == "D":
                        self.Orientation = "L"


            else:

                if self.Orientation == "L":
                    self.Orientation = "R"

                elif self.Orientation == "R":
                    self.Orientation = "L"

                elif self.Orientation == "U":
                    self.Orientation = "D"

                elif self.Orientation == "D":
                    self.Orientation = "U"



        _ = 0

        if args:
            res = ""
            if args == "Reset":
                return
            self.send(args)
            print(f"doing {args} ... ")


            while not res:
                res = self.read()
                time.sleep(0.01)
                _ += 1
                if _ == 5000: break

                # print(f"\n {res}")


            if self.socket:
                self.socket.emit('uart_message', {
                    'message': res,
                    'type': 'received'
                })

            print(f"done {args}, res: {res} ... ")
            return res

    def set_frame(self, frame=None):
        if frame is None:
            print("FAIL: No image to send")
            return

        if frame.dtype == 'uint16':
            frame= (frame // 257).astype('uint8')

        quality = max(0, min(100, self.telemetryQuality))
        encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), quality]

        success, buffer = cv2.imencode('.jpg', frame, encode_params)
        if not success:
            print("FAIL: Image encoding failed")
            return

        try:
            encoded_image = base64.b64encode(buffer).decode('utf-8')
        except Exception as e:
            print(f"FAIL: Base64 encoding failed: {e}")
            return

        try:
            self.socket.emit('framee', {'frame': encoded_image})
        except Exception as e:
            print(f"FAIL: Socket emit failed: {e}")

    def get_uncompressed_frames(self, save_as_file = False):
        self.conn.sendall(b"GET_FRAMES")

        try:
            length_bytes = self.recvall(self.conn, 4)
            if not length_bytes:
                return None, None

            length = int.from_bytes(length_bytes, 'big')

            data = self.recvall(self.conn, length)
            if not data:
                return None, None

            frame_data = pickle.loads(data)

            if frame_data.get('type') == 'uncompressed_dual':
                cam1_info = frame_data['camera1']
                primary_frame = np.frombuffer(
                    cam1_info['data'],
                    dtype=np.dtype(cam1_info['dtype'])
                ).reshape(
                    (cam1_info['height'], cam1_info['width'], cam1_info['channels'])
                )

                cam2_info = frame_data['camera2']
                secondary_frame = np.frombuffer(
                    cam2_info['data'],
                    dtype=np.dtype(cam2_info['dtype'])
                ).reshape(
                    (cam2_info['height'], cam2_info['width'], cam2_info['channels'])
                )

                self.frames = {1:primary_frame, 2: secondary_frame}
                if save_as_file: cv2.imwrite("frame_1.png", primary_frame)
                if save_as_file: cv2.imwrite("frame_2.png", secondary_frame)

                return primary_frame, secondary_frame

            elif frame_data.get('type') == 'error':
                print(f"Server error: {frame_data['message']}")
                return None, None

            else:
                print("Unknown data type received")
                return None, None

        except Exception as e:
            print(f"Error receiving frames: {e}")
            return None, None

        # finally:
            # conn.close()

class CameraClient:
    def __init__(self, sock, logg):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.stream_active = False
        self.lock = threading.Lock()
        self.map_image = None
        self.socketio = sock
        self.logger = logg

    def connect(self):
        try:
            self.client_socket.connect(('localhost', 65432))
            with self.lock:
                self.stream_active = True

            self.client_socket.sendall(b"WEBSITE_STREAMING")
            self.logger.info("Connected to dual camera server")

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
                            self.socketio.emit('video_frame', {
                                'camera': 1,
                                'frame': encoded1
                            })

                        if 'camera2' in frames:
                            encoded2 = base64.b64encode(frames['camera2']).decode('utf-8')
                            self.socketio.emit('video_frame', {
                                'camera': 2,
                                'frame': encoded2
                            })


                except (ConnectionResetError, BrokenPipeError) as e:
                    self.logger.error(f"Connection error: {str(e)}")
                    break
                except pickle.UnpicklingError as e:
                    self.logger.error(f"Data unpacking error: {str(e)}")
                    continue

        except Exception as e:
            self.logger.error(f"Error: {str(e)}", exc_info=True)
        finally:
            self.client_socket.close()
            with self.lock:
                self.stream_active = False

class WebsiteHolder:
    #не лезь сюда (хотя-бы пока работает)
    def __init__(self, uart_port):

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

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


        self.camera_client = CameraClient(self.socketio, self.logger)
        self.robot = RobotAPI((8, 8), 1, uart_port, self.socketio)


        self._set_routes()
        self._set_socketio_handlers()


    def _set_routes(self):
        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/raw_cameras')
        def get_raw():
            self.robot.do("Reset")
            return render_template('raw_cameras.html',
                                   qualities=['low', 'medium', 'high', 'max'])

        @self.app.route('/manual_control')
        def manual_control():
            return render_template('manual_control.html')

        @self.app.route('/telemetry_cameras')
        def telemetry_cameras():
            return render_template('telemetry.html')

    def _set_socketio_handlers(self):
        @self.socketio.on('uart_command')
        def handle_uart_command(data):
            command = data.get('command', '')
            self.logger.info(f"Received UART command: {command}")
            self.robot.do(command)

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

        server_thread = threading.Thread(target=self._run_server)
        server_thread.daemon = True
        server_thread.start()

    def _run_server(self):
        #я больше никогда не буду тыкать сокеты
        self.socketio.run(self.app, host='0.0.0.0', port=5000, debug=True, use_reloader=False,
                          allow_unsafe_werkzeug=True)

if __name__ == "__main__":
    pass
    # serial = serial.Serial('/dev/ttyAMA0', 115200, timeout=1)
    # s = WebsiteHolder(serial)
    # s.start_website()
    # c = 0
    # while 1:
        # time.sleep(5)
        # print("saving")
        # frames = s.robot.get_uncompressed_frames(0)
        # s.robot.set_frame(frames[(c%2)-1])
        # print(c)
        # time.sleep(0.15)
        # c += 1