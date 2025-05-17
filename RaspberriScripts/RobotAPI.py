import serial
import time
import threading
# from StreamVideo import send_msg_to_website

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

        print(line)
        if line is not None:
            lines = line.split("*")
            return lines

    def drive_through_roadmap(self, roadmap):
        pass

    @staticmethod
    def handle_website_commands(args):
        if args:
            res = ""
            robot.send(args)

            while not res:
                res = robot.read()
            # send_msg_to_website(res)





if __name__ == "__main__":
    robot = RobotAPI((1,1), 1)
    while 1:
        result = ""
        command = input()
        robot.send(command)


        while not result:
            result = robot.read()
            print("res", result)
        # send_msg_to_website(result)





