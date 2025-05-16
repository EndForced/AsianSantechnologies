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

from flask import Flask, Response, render_template
import cv2
import threading
import time

app = Flask(__name__)

class VideoCamera:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.video = cv2.VideoCapture(camera_index)
        self.success, self.frame = self.video.read()
        self.running = True
        self.thread = threading.Thread(target=self.update)
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        while self.running:
            self.success, self.frame = self.video.read()
            if not self.success:
                break
            time.sleep(0.05)

    def get_frame(self):
        if self.success and self.frame is not None:
            ret, jpeg = cv2.imencode('.jpg', self.frame)
            if ret:
                return jpeg.tobytes()
        return None

    def __del__(self):
        self.running = False
        if hasattr(self, 'thread'):
            self.thread.join()
        self.video.release()

def gen(camera):
    while True:
        frame = camera.get_frame()
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        else:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' +
                   cv2.imencode('.jpg', cv2.imread('error.jpg'))[1].tobytes() +
                   b'\r\n\r\n')
            break

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)