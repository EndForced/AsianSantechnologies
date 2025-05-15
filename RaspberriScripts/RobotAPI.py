import serial
import time

class RobotAPI:
    def __init__(self, position, orientation):
        self.ser = serial.Serial('/dev/AMA0', 9600)
        self.ser.flush()  # очищаем буфер

        if max(position) > 15:
            raise ValueError("Robot is out of borders!", position)
        self.RobotPosition = position

        if orientation not in [1,2,3,4]:
            raise  ValueError("Unknown orientation!", orientation)
        self.RobotOrientation = orientation

        self.ArduinoMessage = self.read()

    def send(self, data):
        data_to_send = data + "\n"  # Data to send (must be bytes)
        self.ser.write(data_to_send.encode('utf-8'))

    def read(self):
        line = self.ser.readline().decode('utf-8').strip()
        return line



robot = RobotAPI((1,1), 1)
while 1:
    print(robot.read())
    robot.send("hehehaha")
    time.sleep(1)





