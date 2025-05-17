import socket
import pickle
import os
import time
from datetime import datetime


def test_client_save_frames(save_dir="test_frames", max_frames=10, frame_interval=1.0):
    """
    Тестовый клиент, который сохраняет кадры в файлы

    :param save_dir: Директория для сохранения кадров
    :param max_frames: Максимальное количество кадров для сохранения
    :param frame_interval: Интервал между кадрами (секунды)
    """
    # Создаем директорию для теста
    os.makedirs(save_dir, exist_ok=True)
    print(f"Сохранение тестовых кадров в директорию: {save_dir}")

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('localhost', 65432))  # Подключаемся к серверу

        frame_count = 0
        last_save_time = time.time()

        while frame_count < max_frames:
            # Получаем длину данных
            length_bytes = s.recv(4)
            if not length_bytes:
                break
            length = int.from_bytes(length_bytes, 'big')

            # Получаем данные кадра
            data = b''
            while len(data) < length:
                packet = s.recv(length - len(data))
                if not packet:
                    break
                data += packet

            if data and time.time() - last_save_time >= frame_interval:
                # Сохраняем кадр только если прошел нужный интервал
                frame = pickle.loads(data)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                filename = os.path.join(save_dir, f"frame_{timestamp}.jpg")

                with open(filename, 'wb') as f:
                    f.write(frame.tobytes())

                print(f"Сохранен кадр: {filename}")
                frame_count += 1
                last_save_time = time.time()

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        s.close()
        print(f"Тест завершен. Сохранено кадров: {frame_count}/{max_frames}")


if __name__ == "__main__":
    # Тестируем с сохранением 5 кадров с интервалом 2 секунды
    test_client_save_frames(save_dir="server_test_frames",
                            max_frames=5,
                            frame_interval=2.0)