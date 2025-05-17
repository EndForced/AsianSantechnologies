from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import serial
import threading
from picamera2 import Picamera2
import base64
import time
import cv2

class RobotAPI:
    def __init__(self, position, orientation):
        self.ser = serial.Serial('/dev/ttyAMA0', 115200, timeout = 1)
        self.ser.flush()  # очищаем буфер

        if max(position) > 15:
            raise ValueError("Robot is out of borders!", position)
        self.RobotPosition = position

        if orientation not in [1,2,3,4]:
            raise  ValueError("Unknown orientation!", orientation)
        self.RobotOrientation = orientation

        self.ESPMessage = self.read()
        self.IsDoingAction = 0

    def send(self, data):
        data_to_send = data + "\n"  # Data to send (must be bytes)
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
        self.ser.reset_input_buffer()  # Для pyserial

        if args:
            res = ""
            self.send(args)

            while not res:
                res = self.read()

            socketio.emit('uart_message', {
                'message': res,
                'type': 'received'
            })


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)
robot = RobotAPI((0, 0), 1)

picam2 = Picamera2()
camera_configs = {
    'low': {'size': (640, 480), 'fps': 30},
    'medium': {'size': (1296, 972), 'fps': 20},
    'high': {'size': (1920, 1080), 'fps': 15},
    'max': {'size': (2592, 1944), 'fps': 10}
}
current_quality = 'medium'
stream_active = False

import os
import cv2
import base64
import time
from picamera2 import Picamera2


def generate_frames():
    global stream_active

    # Явно указываем пути к системным библиотекам libcamera
    os.environ['LD_LIBRARY_PATH'] = '/usr/lib/aarch64-linux-gnu:' + os.environ.get('LD_LIBRARY_PATH', '')

    try:
        picam2 = Picamera2()
        config = picam2.create_video_configuration(
            main={"size": camera_configs[current_quality]['size']},
            buffer_count=4
        )
        picam2.configure(config)
        picam2.start()

        while stream_active:
            frame = picam2.capture_array("main")
            # Конвертируем в JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = base64.b64encode(buffer).decode('utf-8')
            socketio.emit('video_frame', {'data': frame_bytes})
            time.sleep(1 / camera_configs[current_quality]['fps'])

    except Exception as e:
        print(f"Camera error: {str(e)}")
        socketio.emit('camera_error', {'message': str(e)})
    finally:
        if 'picam2' in locals():
            picam2.stop()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/raw_cameras')
def get_raw():
    robot.handle_website_commands("Reset")
    return render_template('raw_cameras.html')



@socketio.on('uart_command')
def handle_uart_command(data):
    command = data.get('command', '')
    print(f"Received UART command: {command}")
    robot.handle_website_commands(command)

@socketio.on('start_stream')
def handle_start_stream(quality):
    global stream_active, current_quality
    if not stream_active:
        current_quality = quality
        stream_active = True
        threading.Thread(target=generate_frames).start()

@socketio.on('stop_stream')
def handle_stop_stream():
    global stream_active
    stream_active = False


if __name__ == '__main__':
    pass

socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)