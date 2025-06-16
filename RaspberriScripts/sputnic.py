from flask import Flask, request, jsonify
from Slam_algorithm import  MainComputer
import serial
serial = serial.Serial('/dev/ttyAMA0', 115200, timeout=1)

app = Flask(__name__)


@app.route('/data', methods=['POST'])
def handle_data():
    # Получаем данные из POST-запроса
    mat = request.get_json()  # для JSON данных
    # или data = request.form  # для form-data

    # Проверяем, есть ли данные
    if not mat:
        return jsonify({'error': 'No data received'}), 400

    # Выводим полученные данные в консоль (для отладки)
    print("Received data:", mat)

    # Отправляем ответ
    response = {
        'status': 'success',
        'message': 'Data received successfully',
        'received_data': mat
    }

    mc = MainComputer(serial, mat)
    while mc.robot.read() != "Activated":
        pass
    mc.robot.do("Beep")

    floor = mc.robot.do("MyFloor")
    cord = mc.find_robot()
    mc._matrix[cord[0]][cord[1]] = 71 if floor == 1 else 81
    print(mc._matrix)
    mc.qualifiction()



if __name__ == '__main__':
    app.run(debug=True)