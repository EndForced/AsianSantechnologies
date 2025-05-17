from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
import time
from RobotAPI import RobotAPI

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)
robot = RobotAPI((0,0), 0)

def send_msg_to_website(message):
    while True:
        time.sleep(5)
        # Автоматическая отправка сообщения от "устройства"
        socketio.emit('uart_message', {
            'message': message,
            'type': 'received'
        })


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('uart_command')
def handle_uart_command(data):
    command = data.get('command', '')
    print(f"Received UART command: {command}")

    robot.handle_website_commands(command)

    # # Отправляем подтверждение обратно клиенту
    # emit('uart_message', {
    #     'message': f"Processed: {command}",
    #     'type': 'received'
    # })


if __name__ == '__main__':
    pass

socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)