import os
import cv2
from flask import Flask, Response, render_template
import threading
import time

app = Flask(__name__)


class CameraStreamer:
    def __init__(self):
        self.cameras = {
            0: None,  # Первая камера
            1: None  # Вторая камера
            2: None #user input
        }
        self.lock = threading.Lock()
        self.stop_event = threading.Event()

        # Инициализация камер
        for cam_id in self.cameras.keys():
            self.start_camera(cam_id)

        # Запуск потока для обновления кадров
        self.update_thread = threading.Thread(target=self.update_frames)
        self.update_thread.daemon = True
        self.update_thread.start()

    def start_camera(self, cam_id):
        """Инициализирует камеру"""
        cap = cv2.VideoCapture(cam_id)
        if cap.isOpened():
            self.cameras[cam_id] = cap
            print(f"Camera {cam_id} started successfully")
        else:
            print(f"Failed to start camera {cam_id}")

    def stop_cameras(self):
        """Останавливает все камеры"""
        self.stop_event.set()
        for cam_id, cap in self.cameras.items():
            if cap is not None:
                cap.release()
        self.cameras = {}

    def get_frame(self, cam_id):
        """Возвращает текущий кадр с указанной камеры"""
        with self.lock:
            if cam_id in self.cameras and self.cameras[cam_id] is not None:
                ret, frame = self.cameras[cam_id].read()
                if ret:
                    _, jpeg = cv2.imencode('.jpg', frame)
                    return jpeg.tobytes()
        return None

    def update_frames(self):
        """Обновляет кадры в отдельном потоке"""
        while not self.stop_event.is_set():
            with self.lock:
                for cam_id, cap in self.cameras.items():
                    if cap is not None:
                        cap.grab()  # Захватываем кадр, но не декодируем его здесь
            time.sleep(0.03)  # Небольшая задержка для уменьшения нагрузки на CPU


# Создаем экземпляр стримера
streamer = CameraStreamer()


@app.route('/')
def index():
    """Главная страница со всеми камерами"""
    return render_template('index.html', cameras=streamer.cameras.keys())


@app.route('/camera/<int:cam_id>')
def single_camera(cam_id):
    """Страница с одной камерой"""
    if cam_id in streamer.cameras:
        return render_template('single_camera.html', cam_id=cam_id)
    return "Camera not found", 404


@app.route('/video_feed/<int:cam_id>')
def video_feed(cam_id):
    """Генератор видеопотока для указанной камеры"""

    def generate():
        while True:
            frame = streamer.get_frame(cam_id)
            if frame is not None:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                # Если кадр не получен, отправляем черное изображение
                black_frame = cv2.imencode('.jpg', cv2.imread('static/black.jpg') if os.path.exists(
                    'static/black.jpg') else cv2.imread('black.jpg'))[1].tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + black_frame + b'\r\n')

    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    try:
        # Создаем черное изображение, если его нет
        if not os.path.exists('static/black.jpg'):
            os.makedirs('static', exist_ok=True)
            cv2.imwrite('static/black.jpg',
                        cv2.imread('black.jpg') if os.path.exists('black.jpg') else cv2.imread('black.jpg',
                                                                                               cv2.IMREAD_COLOR))

        # Запускаем Flask с поддержкой многопоточности
        app.run(host='0.0.0.0', port=5000, threaded=True)
    finally:
        streamer.stop_cameras()