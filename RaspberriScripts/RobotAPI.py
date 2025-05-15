import serial
import time
import threading

class RobotAPI:
    def __init__(self, position, orientation):
        self.ser = serial.Serial('/dev/ttyAMA0', 115200, timeout = 1)
        self.ser.flush()  # очищаем буфер

        if max(position) > 15:
            raise ValueError("Robot is out of borders!", position)
        self.RobotPosition = position

        if orientation not in [1,2,3,4]:
            raise  ValueError("Unknown orientation!", orientation)
        self.RobotOrientation = orientation

        self.ESPMessage = self.read()
        self.IsDoingAction = 0

    def send(self, data):
        data_to_send = data + "\n"  # Data to send (must be bytes)
        self.ser.write(data_to_send.encode('utf-8'))

    def read(self):
        line = self.ser.readline().decode('utf-8').strip()

        if line is not None:
            lines = line.strip("*")
            self.ESPMessage = lines
            self.process_esp_responses()

    def process_esp_responses(self):
        if self.ESPMessage[0] == "Doing":
            self.IsDoingAction = 1
            return

        elif self.ESPMessage[0] == "Done":
            self.IsDoingAction = 0

        else:
            print(self.ESPMessage)






robot = RobotAPI((1,1), 1)
while 1:
    robot.read()
    robot.send("hehehaha")
    time.sleep(1)





