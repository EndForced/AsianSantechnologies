# # import serial
# import time
# import threading
# # from StreamVideo import send_msg_to_website
# import cv2
# import os
#
#
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
#     @staticmethod
#     def handle_website_commands(args):
#         if args:
#             res = ""
#             robot.send(args)
#
#             while not res:
#                 res = robot.read()
#             return res
#             send_msg_to_website(res)
#
#
# class CameraAPI:
#
#
#     def __init__(self):
#         self.MaxPossibleCamNum = 3
#         self.Cameras = self.find_cameras()
#         self.pathToPhotos = "/home/pi/AsianSantechnologies/RaspberriScripts/photos"
#
#         for i in range(len(self.Cameras)):
#             self.Cameras[i] = cv2.VideoCapture(self.Cameras[i])
#
#
#     def find_cameras(self):
#         cameras = []
#
#         for i in range(self.MaxPossibleCamNum):
#             cap = cv2.VideoCapture(i)
#             if cap.read()[0]:
#                 cameras.append(i)
#                 cap.release()
#
#         return cameras
#
#
#     def get_frame(self, cam_num):
#         if cam_num >= len(self.Cameras):
#             print("Trying to get frame from non-existing camera")
#             return
#         cam_frame = self.Cameras[cam_num].read()
#         return cam_frame
#
#
#     def get_frame_encoded(self, cam_num):
#         cam_frame = self.Cameras[cam_num].read()
#         return cam_frame
#
#     def capture_picture(self, camera_index, ext="jpg"):
#         frame = self.get_frame(camera_index)
#
#         if not list(frame):
#             print("No photo cause no frame((")
#             return
#
#         if ext not in ["png", "jpg", "jpeg", "bmp"]:
#             ext = "jpg"
#
#         try:
#             if not os.path.exists(self.pathToPhotos):
#                 os.makedirs(self.pathToPhotos, exist_ok=True)  # exist_ok prevents race condition
#
#             photos_count = len(os.listdir(self.pathToPhotos))
#             filename = os.path.join(self.pathToPhotos, f'photo_{photos_count + 1}.{ext}')
#
#             cv2.imwrite(filename, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
#             print("Saved photo!", filename)
#
#         except PermissionError:
#             print(f"ERROR: Cannot write to {self.pathToPhotos}. Check permissions!")
#         except Exception as e:
#             print(f"Error saving photo: {str(e)}")
#
#
#
# if __name__ == "__main__":
#     # robot = RobotAPI((1,1), 1)
#     cam = CameraAPI()
#     cam.capture_picture(0)
#
#
#
#
#

from picamera2 import Picamera2
import time
import os

# Настройки
CAMERA_MODEL = "ov5647"
OUTPUT_DIR = "photos"
MODE = "1920x1080"  # Выберите: 640x480, 1296x972, 1920x1080, 2592x1944
DELAY_SEC = 3  # Задержка перед съёмкой (для стабилизации)


def main():
    # Создаём папку для фото, если её нет
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Инициализация камеры
    picam2 = Picamera2()

    # Конфигурация в зависимости от выбранного режима
    config = picam2.create_still_configuration(
        main={"size": tuple(map(int, MODE.split('x')))},
        buffer_count=3
    )
    picam2.configure(config)

    # Запуск камеры
    picam2.start()
    print(f"Камера {CAMERA_MODEL} запущена. Режим: {MODE}")

    # Даём камере время на стабилизацию
    time.sleep(DELAY_SEC)

    # Захват фото
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(OUTPUT_DIR, f"photo_{timestamp}.jpg")
    picam2.capture_file(output_file)
    print(f"Фото сохранено: {output_file}")

    # Остановка камеры
    picam2.stop()


if __name__ == "__main__":
    main()
