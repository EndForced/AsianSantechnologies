#тут типо жоски слем алгоритме
import sys, os, platform
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
        if self.resizedPicture is not None:
            encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), self.robot.telemetryQuality]
            buffer1 = cv2.imencode('.jpg', self.resizedPicture, encode_params)

            _, buffer = cv2.imencode('.jpg', self.resizedPicture)
            encoded_image = base64.b64encode(buffer).decode('utf-8')
        else:
            print("FAIL")
            exit()

        self.robot.socket.emit('field_map', {
            'fieldMap': encoded_image
        })


mat = [[20]*10]*10
mc = MainComputer(mat, serial)
res = mc.show()

if list(res):
    mc.start_website()
    time.sleep(5)
    mc.send_map()
    print("sent")

print(MainComputer.__mro__)
while 1:
    pass




