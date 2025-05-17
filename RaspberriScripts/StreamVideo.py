from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import serial


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

    def handle_website_commands(self, args):
        self.ser.reset_input_buffer()  # Для pyserial

        if args:
            res = ""
            self.send(args)

            while not res:
                res = self.read()

            socketio.emit('uart_message', {
                'message': res,
                'type': 'received'
            })


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)
robot = RobotAPI((0, 0), 1)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/raw_cameras')
def get_raw():
    robot.handle_website_commands("Reset")
    return render_template('raw_cameras.html')



@socketio.on('uart_command')
def handle_uart_command(data):
    command = data.get('command', '')
    print(f"Received UART command: {command}")
    robot.handle_website_commands(command)


if __name__ == '__main__':
    pass

socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)