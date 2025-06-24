from flask import Flask, request, jsonify
from Slam_algorithm import MainComputer
import serial
import ast
import threading
import time

app = Flask(__name__)

try:
    serial_conn = serial.Serial('/dev/ttyAMA0', 115200, timeout=1)
    print("Serial port initialized successfully")
except serial.SerialException as e:
    print(f"Failed to initialize serial port: {e}")
    serial_conn = None


def string2list(matrix_string):
    try:
        result = ast.literal_eval(matrix_string)
        if isinstance(result, list):
            return result
        raise ValueError("Input string is not a list representation")
    except (SyntaxError, ValueError) as e:
        print(f"Error converting string to list: {e}")
        return []


def process_matrix_in_background(mat, serial_conn):
    try:
        print("Background processing started")
        mc = MainComputer(mat, serial_conn)

        # mc.robot.do("OK")
        mc.robot.do("Beep")
        floor = int(mc.robot.do("MyFloor")[0])
        cord = mc.find_robot()
        mc._matrix[cord[0]][cord[1]] = 71 if floor == 1 else 81

        print("Current matrix:", mc._matrix)
        mc.qualification()
        print("Background processing completed")
    except Exception as e:
        print(f"Error in background processing: {e}")


@app.route('/data', methods=['POST'])
def handle_data():
    try:
        data = request.get_json()
        if not data or 'mat' not in data:
            return jsonify({'error': 'No data received or invalid format'}), 400

        mat_str = data['mat']
        print("Received data:", mat_str)

        mat = string2list(mat_str)
        if not mat:
            return jsonify({'error': 'Invalid matrix format'}), 400

        thread = threading.Thread(
            target=process_matrix_in_background,
            args=(mat, serial_conn)
        )
        thread.daemon = True
        thread.start()

        response = {
            'status': 'success',
            'message': 'Data received and processing started',
            'received_data': mat_str
        }
        return jsonify(response), 200

    except Exception as e:
        print(f"Server error: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("Starting server...")
    app.run(debug=True, host='0.0.0.0', port=5000)