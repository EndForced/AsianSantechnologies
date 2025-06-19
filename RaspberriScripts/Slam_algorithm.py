# тут типо жоски слем алгоритме
import math
import os
import platform
import sys

import numpy as np

from cv import edge_to_matrix

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append("/home/pi2/AsianSantechnologies/RaspberriScripts/CvProcessing")

from CvProcessing.CellDetector import fix_perspective, analyze_frame, tile_to_code

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
            base_x, base_y = x + 1, y - 1  # Смещаем на 1 вправо
        else:
            raise ValueError("Неправильное направление")

        # Распределение клеток по направлениям
        if direction == 'U':
            print(base_x, base_y, "bases")
            positions = [
                (base_x, base_y, 1),  # Левый верхний (индекс 1)
                (base_x - 1, base_y, 2),  # Правый верхний (индекс 2)
                (base_x, base_y - 1, 3),  # Левый нижний (индекс 3)
                (base_x - 1, base_y - 1, 4)  # Правый нижний (индекс 4)
            ]
        elif direction == 'D':
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
                (base_x, base_y, 1),
                (base_x, base_y + 1, 2),
                (base_x + 1, base_y, 3),
                (base_x + 1, base_y + 1, 4)
            ]

        for px, py, idx in positions:
            if 0 <= px < 15 and 0 <= py < 15:  # Проверяем границы
                if idx in cells and cells[idx] != 'unr':
                    new_matrix[py][px] = cells[idx]

        return new_matrix


if __name__ == "__main__":
    mat = [[0 for _ in range(17)] for _ in range(17)]
    mc = MainComputer(mat, serial)
    # res = mc.show()
    # print(mc.resizedPicture.dtype)

    if mc.OS == "Linux":
        mc.start_website()
        mc.robot.Orientation = "U"
        mc.robot.Position = (8, 8)

        time.sleep(3)
        tiles = {}
        mc._matrix[8][8] = 10 if int(mc.robot.do("MyFloor")[0]) == 1 else 20
        print("mat", mc._matrix)
        c = 0
        while 1:
            mc.floor = int(mc.robot.do("MyFloor")[0])
            frame = mc.robot.get_uncompressed_frames(0)[1]
            # frame = replace_with_nearest_color(frame)
            # a = input()
            # cv2.imwrite(f"{c}.png", frame)
            # c+=1
            frame = fix_perspective(frame)
            cv2.imwrite("Warped.png", frame)
            frame, slices, borders = analyze_frame(frame, 1)

            for key, item in slices.items():
                if str(item) != "unr":
                    tiles[key + 1] = int(tile_to_code(slices[key]))
                    cv2.imwrite(f"{key}.png", item)

                else:
                    tiles[key + 1] = "unr"

            mc._matrix = mc.insert(tiles)
            #
            # if len(borders) > 0:
            #     edge_to_matrix(mc._matrix, borders[0], mc.robot.Position, mc.robot.Orientation)

            map = mc.update_matrix()

            mc.robot.set_frame(frame)
            mc.send_map()
            # cv2.imwrite("warped.png", frame)
            # time.sleep(0.2)
            # mc.robot.set_frame(frame)
            for key, item in slices.items():
                if str(item) != "unr":
                    # print(tile_to_code(item))
                    cv2.imwrite(f"{c}.png", item)
                    c += 1
                    print(c)
            #

            print(mc.robot.Position)
            print(mc.robot.Orientation)
            print(tiles)
            print(np.array(mc._matrix))
            print("floor:", mc.floor)
            _ = input()
            mc.robot.do(_)
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
        #     # exit()
        #     # # cv2.imwrite("testing.jpg", frame)
        #     # mc.robot.set_frame(frame)
        #     pass
    else:
        # print(type(res))
        # frames = mc.robot.get_uncompressed_frames(save_in_folder = 0)
        # mc.robot.set_frame(frames[0])...
        # mc.send_map() no args!

        # print(MainComputer.__mro__)
        # while 1:
        #     pass

        # robot = mc.find_robot()
        # waves = mc.create_wave(robot)
        # mc.visualize_wave(waves)
        # res = mc.solve()
        # # print(res)
        # mc.draw_multiple_paths(res)
        # # print(mc.way_to_commands_single(res[2], "U"))
        # print(mc.way_to_commands(res, "D"))
        # mc.show()
        # unload_dict = {"R": ["P1", "R1", "X1", "L1", "P1", "R1", "X1", "L1", "P1"],
        #                "L": ["P1", "L1", "X1", "R1", "P1", "L1", "X1", "R1", "P1"],
        #                "C": ["L1", "X1", "R1", "P1", "R1", "X1", "L1", "P1", "R1", "X1", "L1", "P1"]}

        # moves =mc.solve()
        # unload_type = mc.detect_unload_type(moves[-1][-1])  # тип разгрузки, сторона с трубами
        # print("un", unload_type)
        # moves1 = mc.way_to_commands(moves, "D") #return - путь, направление робота в конце

        # print("dirs", unload_type[1], moves[1])
        # if unload_type[1] != moves1[1]:
        #     moves1[0].append(mc.get_rotation_direction(moves1[1], unload_type[1]))
        #
        # type_u = unload_type[0]
        # moves1[0].extend(unload_dict[type_u])
        # print(moves1)
        #
        # mc.draw_multiple_paths(moves)
        # m = mc.create_way((6,1),(6,5))
        # mc.draw_path(m)
        # mc.show()
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
