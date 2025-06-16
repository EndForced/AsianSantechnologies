from flask import Flask, request, jsonify
from Slam_algorithm import  MainComputer
import serial
import ast
serial = serial.Serial('/dev/ttyAMA0', 115200, timeout=1)

app = Flask(__name__)
import ast


def string2list(matrix_string):
    try:
        # Используем ast.literal_eval для безопасного преобразования строки в список
        result = ast.literal_eval(matrix_string)
        if isinstance(result, list):
            return result
        else:
            raise ValueError("Input string is not a list representation")
    except (SyntaxError, ValueError) as e:
        print(f"Error converting string to list: {e}")
        return []

@app.route('/data', methods=['POST'])
def handle_data():
    # Получаем данные из POST-запроса
    mat = request.get_json()["mat"]  # для JSON данных
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
    mat = string2list(mat)
    mc = MainComputer(mat, serial)
    while mc.robot.read() != "Activated":
        pass
    mc.robot.do("Beep")

    floor = mc.robot.do("MyFloor")
    cord = mc.find_robot()
    mc._matrix[cord[0]][cord[1]] = 71 if floor == 1 else 81
    print(mc._matrix)
    mc.qualifiction()



if __name__ == '__main__':
    print("starting...")
    app.run(debug=True,host='0.0.0.0', port=5000)