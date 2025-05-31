#тут типо жоски слем алгоритме
import sys, os, platform

import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ClientClasses.VisualizationProcessing import VisualizePaths, VisualizeMatrix
import time
import cv2
import base64

if platform.system() == "Windows":
    class WebsiteHolder:
        pass
    serial = None

if platform.system() == "Linux":
    from StreamVideo import WebsiteHolder
    import serial
    serial = serial.Serial('/dev/ttyAMA0', 115200, timeout=1)

#ты ему клетки со фрейма, а он тебе все остальное
class MainComputer(VisualizePaths, WebsiteHolder):
    def __init__(self, matrix, serial_p):

        if not matrix:
            matrix = [[0]*15]*15

        VisualizePaths.__init__(self,matrix)

        if self.OS == "Linux":
            WebsiteHolder.__init__(self,serial_p)

    def send_map(self):
        if self.resizedPicture is None:
            print("FAIL: No image to send")
            return

        if self.resizedPicture.dtype == 'uint16':
            self.resizedPicture = (self.resizedPicture // 257).astype('uint8')


        quality = max(0, min(100, self.robot.mapQuality))
        encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), quality]

        success, buffer = cv2.imencode('.jpg', self.resizedPicture, encode_params)
        if not success:
            print("FAIL: Image encoding failed")
            return

        try:
            encoded_image = base64.b64encode(buffer).decode('utf-8')
        except Exception as e:
            print(f"FAIL: Base64 encoding failed: {e}")
            return

        try:
            self.robot.socket.emit('field_map', {'frame': encoded_image})
        except Exception as e:
            print(f"FAIL: Socket emit failed: {e}")


# mat = [[20, 20, 20, 34, 10, 10, 10, 31], [20, 51, 20, 10, 10, 10, 41, 20], [20, 10, 10, 10, 10, 10, 10, 20], [20, 20, 20, 34, 10, 20, 10, 33], [33, 10, 10, 71, 10, 20, 10, 62], [20, 10, 10, 20, 10, 33, 10, 62], [10, 10, 10, 20, 10, 42, 10, 62], [10, 32, 34, 32, 20, 20, 20, 34]]
mat = [[10]*15]*15
mc = MainComputer(mat, serial)
res = mc.show()
print(mc.resizedPicture.dtype)

if mc.OS == "Linux":
    # mc.start_website()
    frames = mc.robot.get_uncompressed_frames(1)
    time.sleep(1)
    mc.send_map()
    mc.robot.set_frame(frames[0])
    print(np.median(frames[0]))

else:
    print(type(res))
    #frames = mc.robot.get_uncompressed_frames(save_in_folder = 0)
    #mc.robot.set_frame(frames[0])...
    #mc.send_map() no args!

    print(MainComputer.__mro__)
    while 1:
        pass