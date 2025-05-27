import socket
import pickle
import cv2
import numpy as np
import time

def get_uncompressed_frames():
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect(('localhost', 65432))
        conn.sendall(b"UNCOMPRESSED_API")
        time.sleep(0.05)

        try:
            # Получаем данные
            length_bytes = conn.recv(4)
            if not length_bytes:
                return None, None

            length = int.from_bytes(length_bytes, 'big')
            data = conn.recv(length)

            frame_data = pickle.loads(data)

            if frame_data.get('type') == 'uncompressed_dual':
                # Восстанавливаем кадр первой камеры
                cam1_info = frame_data['camera1']
                primary_frame = np.frombuffer(
                    cam1_info['data'],
                    dtype=np.dtype(cam1_info['dtype'])
                ).reshape(
                    (cam1_info['height'], cam1_info['width'], cam1_info['channels'])
                )

                # Восстанавливаем кадр второй камеры
                cam2_info = frame_data['camera2']
                secondary_frame = np.frombuffer(
                    cam2_info['data'],
                    dtype=np.dtype(cam2_info['dtype'])
                ).reshape(
                    (cam2_info['height'], cam2_info['width'], cam2_info['channels'])
                )

                return primary_frame, secondary_frame

            elif frame_data.get('type') == 'error':
                print(f"Server error: {frame_data['message']}")
                return None, None

        except Exception as e:
            print(f"Error receiving frames: {e}")
            return None, None



frames = get_uncompressed_frames()
if frames[0]:
    print("LETS GO")
