import cv2
import os

import cv2
import threading
import time
from flask import Flask, render_template, send_file, Response
import cv2

class CameraAPI:
    def __init__(self, max_cameras_to_check=3):
        self.cameras = self._find_available_cameras(max_cameras_to_check)
        self.pathToPhotos = "/home/pi/AsianSantechnologies/RaspberriScripts/photos"

    @staticmethod
    def _find_available_cameras(max_to_check):

        available = []
        for i in range(max_to_check):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available.append(i)
                cap.release()
        return available

    def get_camera_count(self):
        return len(self.cameras)

    def get_frame(self, camera_index):
        if camera_index >= len(self.cameras):
            raise ValueError(f"Camera index {camera_index} is out of range")

        cap = cv2.VideoCapture(self.cameras[camera_index])
        if not cap.isOpened():
            raise RuntimeError(f"Failed to open camera {camera_index}")

        ret, frame = cap.read()
        cap.release()

        if not ret:
            raise RuntimeError(f"Failed to capture frame from camera {camera_index}")

        return frame

    def get_frame_encoded(self, camera_index, format='.jpg', quality=95):
        frame = self.get_frame(camera_index)
        params = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        success, encoded = cv2.imencode(format, frame, params)

        if not success:
            raise RuntimeError("Failed to encode frame")

        return encoded

    def get_available_cameras_info(self):
        info = []
        for idx, cam_idx in enumerate(self.cameras):
            cap = cv2.VideoCapture(cam_idx)
            if cap.isOpened():
                info.append({
                    'system_index': cam_idx,
                    'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                    'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                    'fps': cap.get(cv2.CAP_PROP_FPS)
                })
                cap.release()
        return info

    def capture_picture(self, camera_index, ext = "jpg"):
        frame = self.get_frame(camera_index)

        if list(frame):

            if ext not in ["png", "jpg", "jpeg", "bmp"]:
                ext = "jpg"

            if not os.path.exists(self.pathToPhotos):
                os.makedirs(self.pathToPhotos)

            photos_count = len(os.listdir(self.pathToPhotos))
            filename = os.path.join(self.pathToPhotos, f'photo_{photos_count+1}.{ext}')

            cv2.imwrite(filename, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
            print("Saved photo!", filename)

        else: print("No photo cause no frame((")


from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import cv2
import base64
import threading

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')

def capture_and_emit(camera_id):
    cap = cv2.VideoCapture(camera_id)
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        _, buffer = cv2.imencode('.jpg', frame)
        img_str = base64.b64encode(buffer).decode('utf-8')
        socketio.emit(f'video_frame_{camera_id}', img_str)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    for i in [0, 1]:  # Запуск потоков для двух камер
        threading.Thread(target=capture_and_emit, args=(i,), daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=5000)