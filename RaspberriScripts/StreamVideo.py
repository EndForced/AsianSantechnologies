import cv2
import os

# class WebsiteHolder:
#     def __init__(self):
#         pass
#
#     def set_frame(self, cam_num):
#         pass
#
#     def get_frame(self,cam_num):
#         pass
#
#     def start_hosting(self):
#         pass
#
#     def show_in_chat(self, name, message):
#         pass
#
#     def get_current_website_requests(self):
#         pass
#
#     def stop_hosting(self):
#         pass

import cv2


class CameraAPI:
    def __init__(self, max_cameras_to_check=3):
        self.cameras = self._find_available_cameras(max_cameras_to_check)
        self.pathToPhotos = "/photos/"

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

        if frame:

            if ext not in ["png", "jpg", "jpeg", "bmp"]:
                ext = "jpg"

            if not os.path.exists(self.pathToPhotos):
                os.makedirs(self.pathToPhotos)

            photos_count = len(os.listdir(self.pathToPhotos))
            filename = os.path.join(self.pathToPhotos, f'photo_{photos_count+1}.{ext}')

            cv2.imwrite(filename, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
            print("Saved photo!", filename)

        else: print("No photo cause no frame((")








cam = CameraAPI(2)
print(cam.get_available_cameras_info())
cam.capture_picture(0)