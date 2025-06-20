# тут типо жоски слем алгоритме
import sys, os, platform, math

import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append("/home/pi2/AsianSantechnologies/RaspberriScripts/CvProcessing")

from CvProcessing.CellDetector import fix_perspective, analyze_frame, tile_to_code
from SlamLogic.SlamLogic import prepare_to_insert, edge_to_matrix
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


# ты ему клетки со фрейма, а он тебе все остальное
class MainComputer(VisualizePaths, WebsiteHolder):
    def __init__(self, matrix, serial_p):

        if not matrix:
            matrix = [[0] * 15] * 15

        VisualizePaths.__init__(self, matrix)

        if self.OS == "Linux":
            WebsiteHolder.__init__(self, serial_p)

        self.coefficient_mat = np.array([[0, 1, 1, 1, 0],
                            [1, 1, 1, 1, 1],
                            [1, 1, 0, 1, 1],
                            [1, 1, 1, 1, 1],
                            [0, 1, 1, 1, 0]])

    def send_map(self):
        # pozdno pozdno pozdno noch'u
        if self.resizedPicture is None:
            print("FAIL: No image to send")
            return

        if self.resizedPicture.dtype == 'uint16':
            self.resizedPicture = (self.resizedPicture // 257).astype('uint8')

        quality = max(0, min(100, self.robot.mapQuality))
        encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), quality]

        success, buffer = cv2.imencode('.jpg', self.resizedPicture, encode_params)
        if not success:
            print("FAIL: Image encoding failed")
            return

        try:
            encoded_image = base64.b64encode(buffer).decode('utf-8')
        except Exception as e:
            print(f"FAIL: Base64 encoding failed: {e}")
            return

        try:
            self.robot.socket.emit('field_map', {'frame': encoded_image})
        except Exception as e:
            print(f"FAIL: Socket emit failed: {e}")

    def way_to_commands(self, path, dir):
        used_tubes = []
        rob_dir = dir
        res = []
        cell_with_tube = []

        tubes_cords = list(self.pick_tubes_cords().keys())

        for i in range(len(path)):
            if len(path[i]) > 1:
                s_way = self.way_to_commands_single(path[i], rob_dir)

                res += s_way[0]
                rob_dir = s_way[1]

            if i != len(path) - 1:

                for j in tubes_cords:
                    # if math.dist(j, path[i][-1]) <= 1 and j not in used_tubes: print(123)
                    if math.dist(j, path[i][-1]) <= 1 and j not in used_tubes and ((np.array(self._matrix)[
                                                                                        path[i][-1]] in [20, 31, 32, 33,
                                                                                                         34] and
                                                                                    np.array(self._matrix)[j] in [51,
                                                                                                                  52]) or (
                                                                                           np.array(self._matrix)[
                                                                                               path[i][-1]] in [10, 31,
                                                                                                                32, 33,
                                                                                                                34] and
                                                                                           np.array(self._matrix)[
                                                                                               j] in [41, 42])):
                        cell_with_tube = j
                        used_tubes.append(j)
                        break

                rel_pos = self.get_relative_direction(path[i][-1], cell_with_tube)
                move_to_pick = self.get_rotation_direction(rob_dir, rel_pos)

                if move_to_pick != "skip":
                    res.append(move_to_pick)
                res.append("G0")

                rob_dir = rel_pos

        return res, rob_dir

    def qualifiction(self):
        print("Starting qualification...")

        res = str(self.robot.read())

        while res != "Activated":
            if res: print(res)
            res = self.robot.read()
            if res: res = str(res[0])

        self.robot.do("OK")
        time.sleep(0.1)
        self.robot.do("Beep")

        unload_dict = {"R": ["P1", "R1", "X1", "L1", "P1", "R1", "X1", "L1", "P1"],
                       "L": ["P1", "L1", "X1", "R1", "P1", "L1", "X1", "R1", "P1"],
                       "C": ["L1", "X1", "R1", "P1", "R1", "X1", "L1", "P1", "R1", "X1", "L1", "P1"]}

        moves = self.solve()
        unload_type = self.detect_unload_type(moves[-1][-1])  # тип разгрузки, сторона с трубами
        moves = self.way_to_commands(moves, "U")

        if unload_type[1] != moves[1]:
            moves[0].append(self.get_rotation_direction(moves[1], unload_type[1]))

        type_u = unload_type[0]
        moves[0].extend(unload_dict[type_u])

        # _ = input()
        self.robot.do("Direction 1")
        self.robot.do(f"Elevation {self.floor}")
        self.robot.drive_through_roadmap(moves[0])

    def insert(self, cells):
        # josko insert
        cells = prepare_to_insert(cells, self.robot.Orientation)
        matrix = self._matrix
        y, x = self.robot.Position
        direction = self.robot.Orientation

        new_matrix = [row.copy() for row in matrix]

        # Сначала вычисляем базовые координаты с учетом смещения вверх
        if direction == 'U':
            base_x, base_y = x, y - 1  # Смещаем на 1 вверх и влево
        elif direction == 'D':
            base_x, base_y = x, y + 1  # Смещаем на 1 вниз
        elif direction == 'L':
            base_x, base_y = x - 1, y  # Смещаем на 1 влево
        elif direction == 'R':
            base_x, base_y = x + 1, y - 1   # Смещаем на 1 вправо
        else:
            raise ValueError("Неправильное направление")

        # Распределение клеток по направлениям
        if direction == 'U':
            positions = [
                (base_x, base_y, 1),  # Левый верхний (индекс 1)
                (base_x - 1, base_y, 2),  # Правый верхний (индекс 2)
                (base_x, base_y - 1, 3),  # Левый нижний (индекс 3)
                (base_x - 1, base_y - 1, 4)  # Правый нижний (индекс 4)
            ]
        elif direction == 'D':
            print(base_x, base_y, "bases")
            positions = [
                (base_x, base_y, 1),
                (base_x + 1, base_y, 2),
                (base_x, base_y + 1, 3),
                (base_x + 1, base_y + 1, 4)
            ]
        elif direction == 'L':
            positions = [
                (base_x, base_y, 1),
                (base_x, base_y + 1, 2),
                (base_x - 1, base_y, 3),
                (base_x - 1, base_y + 1, 4)
            ]
        elif direction == 'R':
            positions = [
                (base_x, base_y, 2),
                (base_x, base_y + 1, 1),
                (base_x + 1, base_y, 4),
                (base_x + 1, base_y + 1, 3)
            ]

        for px, py, idx in positions:
            if 0 <= px < 15 and 0 <= py < 15:  # Проверяем границы
                if idx in cells and cells[idx] != 'unr':
                    if self._matrix [py][px] != 99:
                        new_matrix[py][px] = cells[idx]

        return new_matrix

    def slam_parameters_init(self):
        self.robot.Orientation = "U"
        self.robot.Position = (8, 8)

        self._matrix[8][8] = 10 if int(mc.robot.do("MyFloor")[0]) == 1 else 20
        self.floor = int(mc.robot.do("MyFloor")[0])
        self.robot.do(f"Elevation {self.floor}")
        self.robot.do("Direction -1")

    def capture_to_map(self):
        self.floor = int(mc.robot.do("MyFloor")[0])
        frame = self.robot.get_uncompressed_frames(0)[1]
        frame = fix_perspective(frame)
        # cv2.imwrite("Warped.png", frame)
        frame, slices, borders = analyze_frame(frame, self.floor)

        if borders:
            mc._matrix = list(edge_to_matrix(np.array(mc._matrix), borders[0], self.robot.Position, self.robot.Orientation))

        for key, item in slices.items():
            if str(item) != "unr":
                tiles[key + 1] = int(tile_to_code(slices[key]))
                cv2.imwrite(f"{key}.png", item)

            else:
                tiles[key + 1] = "unr"

        self._matrix = self.insert(tiles)
        self.update_matrix()
        self.robot.set_frame(frame)
        self.send_map()

    def drive_and_capture(self, cell):
        commands = self.create_way(self.robot.Position, cell)
        commands = self.way_to_commands_single(commands, self.robot.Orientation, 0 )[0]
        print(commands)
        # command_prev = []

        print(commands)
        _ = input()

        commands_dict = {"L": "Turn Left", "R": "Turn Right", "X": "Pid Forward", "x": "Pid Backwards", "F1": "Up",
                         "F0": "Down", "G0": "Grab", "P1": "Put"}

        for i in range(len(commands)):
            if len(commands[i]) == 2:
                if commands[i][0] not in ["F", "P", "G"]:
                    command = commands[i][0]
                    num = commands[i][1] if commands[i][1] else ""
                    commands[i] = f"{commands_dict[command]} {num}"

                elif commands[i][0] in ["F", "P", "G"]:
                    command = commands[i]
                    commands[i] = f"{commands_dict[command]}"

        print(commands)

        for i in commands:
            self.capture_to_map()
            i = i.replace("Forward", "Backwards")
            self.robot.do(i)


    def sort_matrix_coordinates(self, matrix):
        # Создаем список кортежей (значение, y, x)
        coordinates = []
        for y in range(len(matrix)):
            for x in range(len(matrix[y])):
                value = matrix[y][x]
                if value != 0:  # Игнорируем нули
                    coordinates.append((value, y, x))  # Порядок: значение, y, x

        # Сортируем по убыванию значения, затем по y (возрастание), затем по x (возрастание)
        coordinates.sort(key=lambda item: (-item[0], item[1], item[2]))

        # Возвращаем список кортежей (y, x) только для координат из waves
        sorted_coordinates = [(y, x) for value, y, x in coordinates if self.is_in_waves((y, x))]
        return sorted_coordinates

    def interest_calculation(self, matrix):
        mat = np.array(matrix)
        revealed = np.array([[0 if cell == 0 else 1 for cell in row] for row in matrix])
        rows, cols = mat.shape[:2]
        k_rows, k_cols = self.coefficient_mat.shape[:2]
        offset_r, offset_c = k_rows // 2, k_cols // 2  # Центр маски

        result = np.array([[0] * cols] * rows)

        for r in range(rows):
            for c in range(cols):
                total = 0
                for kr in range(k_rows):
                    for kc in range(k_cols):
                        nr, nc = r + kr - offset_r, c + kc - offset_c
                        if 0 <= nr < rows and 0 <= nc < cols:  # Проверка границ
                            total += revealed[nr][nc] * self.coefficient_mat[kr][kc]
                result[r][c] = total

        return result

    def interesting_coords(self):
        unrevealed = np.array([[0 if cell == 0 or cell == 99 else 1 for cell in row] for row in self._matrix])
        self.Waves = self.create_wave(self.robot.Position)
        interest_mat = self.interest_calculation(unrevealed)
        interest_sorted = self.sort_matrix_coordinates(interest_mat)
        return interest_sorted



if __name__ == "__main__":
    mat = [[0 for _ in range(17)] for _ in range(17)]
    mc = MainComputer(mat, serial)
    if mc.OS == "Linux":
        mc.slam_parameters_init()

        mc.start_website()
        tiles = {}
        mc.capture_to_map()

        while 1:
            cords = mc.interesting_coords()
            for i in cords:
                if mc.is_in_waves(i):
                    mc.drive_and_capture(i)
                    for _ in range(4):
                        mc.robot.do("Turn Right")
                        mc.capture_to_map()
                    # print(mc.robot.Position)
                    # print(mc.robot.Orientation)
                    # print(tiles)
                    # print(np.array(mc._matrix))
                    # print("floor:", mc.floor)
                    # _ = input()





            # _ = input()
            # mc.robot.do(_)
        # mc.qualifiction()
        # time.sleep(1000)
        # while 1:
        #     # frame = mc.robot.get_uncompressed_frames(1)[1].copy()
        #     # frame, slices = update_frame_smart(frame)
        #     # for i in range(len(slices)):
        #     #     print(i)
        #     #     cv2.imwrite(f"{i}.jpg", slices[i])
        #     #
        #     # print("upd!!")
        #     # exit()git
        #     # # cv2.imwrite("testing.jpg", frame)
        #     # mc.robot.set_frame(frame)
        #     pass
    else:
        print(MainComputer.__mro__)
        mc.robot.Orientation = "U"
        mat = [[0] * 15] * 15
        cells = {1: 20, 2: 20, 3: "unr", 4: "unr"}
        mat = mc.insert(cells)
        pos = mc.robot.Position
        mc._matrix[pos[0]][pos[1]] = 71
        mc._matrix = mat
        mc.update_matrix()
        mc.show()
