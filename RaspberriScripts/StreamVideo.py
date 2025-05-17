from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
import time
from RobotAPI import RobotAPI
import serial

class Server:
    def __init__(self, robot):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'your_secret_key'
        self.socketio = SocketIO(self.app)
        self.robot = robot
        self.running = False
        self.thread = None

        # Регистрация маршрутов и обработчиков событий
        self.app.route('/')(self.index)
        self.socketio.on('uart_command')(self.handle_uart_command)

    def index(self):
        return render_template('index.html')

    def handle_uart_command(self, data):
        command = data.get('command', '')
        print(f"Received UART command: {command}")
        self.robot.handle_website_commands(command)

    def send_msg_to_website(self, message):
        while self.running:
            time.sleep(5)  # Отправка сообщения каждые 5 секунд (можно настроить)
            self.socketio.emit('uart_message', {
                'message': message,
                'type': 'received'
            })

    def start(self):
        if not self.running:
            self.running = True
            # Запуск Flask-SocketIO в отдельном потоке
            self.thread = threading.Thread(
                target=self.socketio.run,
                kwargs={
                    'app': self.app,
                    'host': '0.0.0.0',
                    'port': 5000,
                    'debug': True,
                    'allow_unsafe_werkzeug': True
                },
                daemon=True
            )
            self.thread.start()
            print("Server started!")

    def stop(self):
        if self.running:
            self.running = False
            # Остановка SocketIO (может потребоваться дополнительная логика)
            # В реальном проекте лучше использовать event для корректного завершения
            if self.thread:
                self.thread.join(timeout=1)
            print("Server stopped!")


if __name__ == '__main__':
    robot = RobotAPI((0, 0), 1)  # Инициализация робота
    server = Server(robot)
    server.start()

    try:
        while True:  # Бесконечный цикл (можно заменить на что-то полезное)
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()