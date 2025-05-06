from flask import Flask, Response, jsonify, request
import sys
import os
import cv2
import threading
import time
from collections import defaultdict
from ClientClasses.VisualizationProcessing import VisualizeMatrix
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


app = Flask(__name__)

# Глобальные переменные для управления камерами
cameras = defaultdict(dict)
active_cameras = set()
main_camera_id = None
manual_image = None


class CameraStream:
    def __init__(self, camera_id, src=0):
        self.camera_id = camera_id
        self.src = src
        self.frame = None
        self.running = False
        self.thread = None

    def start(self):
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        cap = cv2.VideoCapture(self.src)
        while self.running:
            ret, frame = cap.read()
            if ret:
                self.frame = frame
            time.sleep(0.01)
        cap.release()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def get_frame(self):
        return self.frame


def generate_frames(camera_id):
    while True:
        frame = None

        # Проверяем ручное изображение
        if manual_image is not None and camera_id == main_camera_id:
            frame = manual_image
        # Проверяем активные камеры
        elif camera_id in active_cameras and camera_id in cameras:
            frame = cameras[camera_id]['stream'].get_frame()

        if frame is not None:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            # Черный кадр если камера не активна
            black_frame = np.zeros((480, 640, 3), np.uint8)
            ret, buffer = cv2.imencode('.jpg', black_frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed/<int:camera_id>')
def video_feed(camera_id):
    return Response(generate_frames(camera_id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


# API методы
@app.route('/api/add_camera', methods=['POST'])
def add_camera():
    data = request.json
    camera_id = data.get('camera_id')
    src = data.get('src', 0)

    if camera_id in cameras:
        return jsonify({'error': 'Camera already exists'}), 400

    stream = CameraStream(camera_id, src)
    stream.start()
    cameras[camera_id] = {'stream': stream, 'src': src}
    return jsonify({'message': f'Camera {camera_id} added'})


@app.route('/api/remove_camera', methods=['POST'])
def remove_camera():
    data = request.json
    camera_id = data.get('camera_id')

    if camera_id not in cameras:
        return jsonify({'error': 'Camera not found'}), 404

    cameras[camera_id]['stream'].stop()
    del cameras[camera_id]
    if camera_id in active_cameras:
        active_cameras.remove(camera_id)
    if camera_id == main_camera_id:
        main_camera_id = None
    return jsonify({'message': f'Camera {camera_id} removed'})


@app.route('/api/set_main_camera', methods=['POST'])
def set_main_camera():
    global main_camera_id
    data = request.json
    camera_id = data.get('camera_id')

    if camera_id not in cameras:
        return jsonify({'error': 'Camera not found'}), 404

    main_camera_id = camera_id
    return jsonify({'message': f'Camera {camera_id} set as main'})


@app.route('/api/enable_camera', methods=['POST'])
def enable_camera():
    data = request.json
    camera_id = data.get('camera_id')

    if camera_id not in cameras:
        return jsonify({'error': 'Camera not found'}), 404

    active_cameras.add(camera_id)
    return jsonify({'message': f'Camera {camera_id} enabled'})


@app.route('/api/disable_camera', methods=['POST'])
def disable_camera():
    data = request.json
    camera_id = data.get('camera_id')

    if camera_id not in cameras:
        return jsonify({'error': 'Camera not found'}), 404

    if camera_id in active_cameras:
        active_cameras.remove(camera_id)
    return jsonify({'message': f'Camera {camera_id} disabled'})


def set_manual_image(img):
    global manual_image
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']
    img_bytes = file.read()
    nparr = np.frombuffer(img_bytes, np.uint8)
    manual_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return jsonify({'message': 'Manual image set'})


@app.route('/api/clear_manual_image', methods=['POST'])
def clear_manual_image():
    global manual_image
    manual_image = None
    return jsonify({'message': 'Manual image cleared'})


@app.route('/api/status')
def get_status():
    return jsonify({
        'active_cameras': list(active_cameras),
        'main_camera': main_camera_id,
        'all_cameras': list(cameras.keys()),
        'manual_image_set': manual_image is not None
    })


# HTML страница для просмотра
@app.route('/')
def index():
    return """
    <html>
    <head>
        <title>Multi-Camera Streaming</title>
    </head>
    <body>
        <h1>Multi-Camera Streaming</h1>
        <div id="streams"></div>
        <script>
            function loadStream(cameraId) {
                const div = document.createElement('div');
                div.innerHTML = `<h2>Camera ${cameraId}</h2>
                                <img src="/video_feed/${cameraId}">`;
                document.getElementById('streams').appendChild(div);
            }

            // Загружаем список камер и создаем потоки
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    data.all_cameras.forEach(camId => loadStream(camId));
                });
        </script>
    </body>
    </html>
    """


if __name__ == '__main__':
    # Пример добавления камер по умолчанию
    cameras[0] = {'stream': CameraStream(0, 0), 'src': 0}
    cameras[0]['stream'].start()
    active_cameras.add(0)
    main_camera_id = 0

    app.run(host='0.0.0.0', port=5000, threaded=True)




