import cv2

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

class CameraAPI:
    def __init__(self):
        self.MaxPossibleCamNum = 3
        self.Cameras = self.find_cameras()

        for i in range(len(self.Cameras)):
            self.Cameras[i] = cv2.VideoCapture(self.Cameras[i])
            

    def find_cameras(self):
        cameras = []

        for i in range(self.MaxPossibleCamNum):
            cap = cv2.VideoCapture(i)
            if cap.read()[0]:
                cameras.append(i)
                cap.release()

        return cameras

    def get_frame(self, cam_num):
        frame = self.Cameras[cam_num].read()
        return frame

    def get_frame_encoded(self, cam_num):
        frame = self.Cameras[cam_num].read()
        return frame


cam = CameraAPI()
print(cam.Cameras)
frame = cam.get_frame(0)
print(frame)