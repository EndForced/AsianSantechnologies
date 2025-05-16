import cv2
import os

from flask import Flask, Response, render_template
import cv2
import threading
import time

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

app = Flask(__name__)
camera_api = CameraAPI()

class CameraStream:
    def __init__(self):
        self.frames = {}
        self.running = False

    def start(self):
        self.running = True
        thread = threading.Thread(target=self.update_frames)
        thread.daemon = True
        thread.start()

    def update_frames(self):
        while self.running:
            for cam_idx in range(camera_api.get_camera_count()):
                frame = camera_api.get_frame(cam_idx)
                ret, jpeg = cv2.imencode('.jpg', frame)
                if ret:
                    self.frames[cam_idx] = jpeg.tobytes()
            time.sleep(0.1)

    def get_frame(self, cam_idx):
        return self.frames.get(cam_idx, None)

    def stop(self):
        self.running = False


stream = CameraStream()
stream.start()


@app.route('/')
def index():
    cameras = camera_api.get_available_cameras_info()
    return render_template('index.html', cameras=cameras)


@app.route('/cameras')
def cameras():
    cameras = camera_api.get_available_cameras_info()
    return render_template('cameras.html', cameras=cameras)


def gen(cam_idx):
    while True:
        frame = stream.get_frame(cam_idx)
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        else:
            time.sleep(0.1)


@app.route('/video_feed/<int:cam_idx>')
def video_feed(cam_idx):
    return Response(gen(cam_idx),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/capture/<int:cam_idx>')
def capture(cam_idx):
    try:
        camera_api.capture_picture(cam_idx)
        return "Фото сохранено!", 200
    except Exception as e:
        return f"Ошибка: {str(e)}", 500


if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, threaded=True)
    finally:
        stream.stop()

import cv2









cam = CameraAPI(2)
print(cam.get_available_cameras_info())
cam.capture_picture(0)