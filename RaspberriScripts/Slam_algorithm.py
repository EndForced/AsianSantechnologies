#тут типо жоски слем алгоритме
import sys, os, platform, math

import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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

#ты ему клетки со фрейма, а он тебе все остальное
class MainComputer(VisualizePaths, WebsiteHolder):
    def __init__(self, matrix, serial_p):

        if not matrix:
            matrix = [[0]*15]*15

        VisualizePaths.__init__(self,matrix)

        if self.OS == "Linux":
            WebsiteHolder.__init__(self,serial_p)

    def send_map(self):

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

    @staticmethod
    def optimize_commands(res):

        seen = ""
        count = 1
        res_optimized = []
        for i in range(len(res)):
            if seen == "":
                seen = res[i]
            elif res[i] == seen:
                count += 1
            else:
                seen = seen.replace('1', str(count))
                res_optimized.append(seen)
                seen = res[i]
                count = 1
        seen = seen.replace('1', str(count))
        res_optimized.append(seen)

        return res_optimized

    @staticmethod
    def get_rotation_direction(start, finish):
        dirs = {"U": 1, "R": 2, "D": 3, "L":4}
        start = dirs[start]
        finish = dirs[finish]

        diff = (finish - start)%4

        if diff == 0: return "skip"
        elif diff == 1: return "R1"
        elif diff == 2: return "R2"
        elif diff == 3: return "L1"

    def way_to_commands_single(self, path, my_dir):
        mat = np.array(self._matrix)
        res = []
        floor = 1 if mat[path[0]] == 10 else 2

        for i in range(len(path)):

            res_prev = ""
            current_cell = mat[path[i]]
            if i + 1 < len(path):
                next_cell = mat[path[i + 1]]

                if current_cell == 10:
                    if next_cell == 10:
                        res_prev += "X1"
                    elif next_cell // 10 == 3:
                        res_prev += "F1"
                        floor = 2

                    else:
                        print("ERROR", current_cell, next_cell)

                if current_cell == 20:
                    if next_cell == current_cell:
                        res_prev += "X1"
                    elif next_cell // 10 == 3:
                        res_prev += "F0"
                        floor = 1
                    else:
                        print("ERROR", current_cell, next_cell)

                if current_cell // 10 == 3:
                    if next_cell // 10 == 3:
                        res_prev += f'F{2 - floor}'
                        floor = 3 - floor
                    else:
                        # pass
                        res_prev += "X1"

                if path[i][1] == path[i + 1][1] + 1:  # если некст клетка слева, то едем налево
                    res_prev += "L"
                elif path[i][1] == path[i + 1][1] - 1:
                    res_prev += "R"
                elif path[i][0] == path[i + 1][0] + 1:
                    res_prev += "U"
                elif path[i][0] == path[i + 1][0] - 1:
                    res_prev += "D"

            if res_prev != "" and res_prev:
                res.append(res_prev)

        res_optimized = self.optimize_commands(res)
        # print(res_optimized)

        res_relative = []
        for i in res_optimized:
            if i[-1] != my_dir:
                res_relative.append(self.get_rotation_direction(my_dir, i[-1]))
                # print(self.get_rotation_direction(my_dir, i[-1]), my_dir, i[-1])
                my_dir = i[-1]

                i = i[0:2]
                res_relative.append(i)

            else:
                i = i[0:2]
                res_relative.append(i)

        return res_relative, my_dir

    @staticmethod
    def get_relative_direction(pos1, pos2):
        x1, y1 = pos1
        x2, y2 = pos2

        if abs(x1 - x2) + abs(y1 - y2) != 1:
            return None

        if x1 == x2:
            return "R" if y2 > y1 else "L"
        else:
            return "D" if x2 > x1 else "U"

    def way_to_commands(self, path, dir):
        used_tubes = []
        rob_dir = dir
        res = []
        cell_with_tube = []

        tubes_cords = list(self.pick_tubes_cords().keys())

        for i in range(len(path)):
            if len(path[i]) > 1:
                s_way = self.way_to_commands_single(path[i],rob_dir)

                res += s_way[0]
                rob_dir = s_way[1]

            if i != len(path) - 1:

                for j in tubes_cords:
                    if math.dist(j, path[i][-1]) <= 1 and j not in used_tubes:
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


mat = [[64, 10, 10, 10, 42, 10, 20, 10], [64, 10, 20, 20, 20, 34, 10, 10], [64, 10, 32, 20, 81, 52, 34, 10], [42, 10, 10, 10, 10, 10, 10, 20], [20, 20, 34, 10, 20, 10, 20, 20], [10, 10, 10, 10, 10, 10, 20, 20], [31, 20, 10, 32, 20, 20, 34, 33], [33, 10, 10, 10, 20, 20, 34, 42]]


# mat = [[10]*15]*15
mc = MainComputer(mat, serial)
# res = mc.show()
# print(mc.resizedPicture.dtype)

if mc.OS == "Linux":
    mc.start_website()
    # frames = mc.robot.get_uncompressed_frames(0)
    # frame = cv2.resize(frames[0], (600,600))
    # # time.sleep(1)
    # mc.send_map()
    # mc.robot.set_frame(frames[0])
    # print(np.median(frames[0]))
    # print(mc.robot.read())
    # while 1:
        # msg = input()
        # mc.robot.do(msg)
    # print("starting roadmap")
    msg = input()
    # commands = ["X3", "R1", "X1", "F0", "X1", "R2", "X1", "F1", "L1", "X3"]
    commands = ["X3", "R1", "X1", "F0", "X1"]
    mc.robot.drive_through_roadmap(commands)
    time.sleep(1000)
else:
    # print(type(res))
    #frames = mc.robot.get_uncompressed_frames(save_in_folder = 0)
    #mc.robot.set_frame(frames[0])...
    #mc.send_map() no args!

    # print(MainComputer.__mro__)
    # while 1:
    #     pass

    robot = mc.find_robot()
    waves = mc.create_wave(robot)
    mc.visualize_wave(waves)
    res = mc.solve()
    # print(res)
    mc.draw_multiple_paths(res)
    # print(mc.way_to_commands_single(res[2], "U"))
    print(mc.way_to_commands(res, "U"))
    mc.show()
