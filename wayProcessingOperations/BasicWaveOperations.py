from typing import List

import cv2
import numpy as np
from fontTools.unicodedata import block
from numpy.matrixlib.defmatrix import matrix
import time
import itertools
import copy

# from ClientClasses.VisualizationProcessing import VisualizeMatrix

possible_codes = [0, 10, 20, 31,32,33,34, 41,42, 51,52, 61,62,63,64, 71,72,73,74, 81,82,83,84, 91,92,93,94]

class WaveCreator:
    def __init__(self,matrix_in:list[list[int]]):
        self._matrix = matrix_in

        if not self._matrix or max(self.matrix_max_dimensions(self._matrix)) == 1:
            raise ValueError("Can't create neighbor dictionary with this matrix:" , self._matrix)

        self.Waves = []
        self.Ways = []

        self.cellsConnections = {10:{"up":[31,10, ], "left":[34,10, ], "down":[33,10, ], "right":[32,10, ]},
                                 20:{"up":[33,20, ], "left":[32,20, ], "down":[31,20, ], "right":[34,20, ]},

                                 31:{"up":[33,20], "left":[None], "down":[33,10], "right":[None]},
                                 32:{"up":[None], "left":[10], "down":[None], "right":[20, 34]},
                                 33:{"up":[31, 10], "left":[None], "down":[31,20], "right":[None]},
                                 34:{"up":[None], "left":[20,32], "down":[None], "right":[10]},

                                 71:{"up":[31,10], "left":[34,10], "down":[33,10], "right":[32,10]},
                                 72:{"up":[31,10], "left":[34,10], "down":[33,10], "right":[32,10]},
                                 73:{"up":[31,10], "left":[34,10], "down":[33,10], "right":[32,10]},
                                 74:{"up":[31,10], "left":[34,10], "down":[33,10], "right":[32,10]},

                                 81: {"up": [33, 20], "left": [32, 20], "down": [31, 20], "right": [34, 20]},
                                 82: {"up": [33, 20], "left": [32, 20], "down": [31, 20], "right": [34, 20]},
                                 83: {"up": [33, 20], "left": [32, 20], "down": [31, 20], "right": [34, 20]},
                                 84: {"up": [33, 20], "left": [32, 20], "down": [31, 20], "right": [34, 20]},

                                 61: {"up": [None], "left": [None], "down": [None], "right": [None]},
                                 62: {"up": [None], "left": [None], "down": [None], "right": [None]},
                                 63: {"up": [None], "left": [None], "down": [None], "right": [None]},
                                 64: {"up": [None], "left": [None], "down": [None], "right": [None]},

                                 41: {"up": [None], "left": [None], "down": [None], "right": [None]},
                                 42: {"up": [None], "left": [None], "down": [None], "right": [None]},

                                 51: {"up": [None], "left": [None], "down": [None], "right": [None]},
                                 52: {"up": [None], "left": [None], "down": [None], "right": [None]},

                                 0: {"up": [None], "left": [None], "down": [None], "right": [None]},

                                 94: {"up": [31, 10, 41], "left": [34, 10, 42], "down": [33, 10, 41],"right": [32, 10, 42]},
                                 }

        self.matrixConnections = self._process_cells_connections()

    def _process_cells_connections(self):
        #возвращает список вида [ {(y1,x1):[(y2,x2),(y3,x3)]}, ...]
        #где y1 и x1 - координаты клетки, а y2,x2,y3,x3 - координаты клеток в которые можно из нее пройти

        connections_dict = {}
        for i in range(len(self._matrix)):
            for j in range(len(self._matrix[i])):

                res = self.get_relative_cells((i,j))
                res = self._find_valid_connections(res[0], res[1])
                connections_dict[res[1]] = res[0]

        return connections_dict

    def _find_valid_connections(self, cell_dict, cell):
        #принимает словарь вида {"up":[], "right":[(0,1)], "down":[(1,0)], "left":[]} и координаты клетки вида (y,x)
        #исключает из исходного словаря те клетки в которые нельзя пройти по правилам в cellsConnections
        #перед return убирает направления т.к они больше не нужны
        #пример return [[(1, 0)], [(0, 1)]], (0, 0)

        mat_tmp = np.array(self._matrix)
        valid_cells = []

        if mat_tmp[cell] not in possible_codes:
            raise ValueError("Unknown cell while wave constructing:", mat_tmp[cell])

        # if cell == (6,5):
        #     print(cell_dict, 123)
        #     time.sleep(10)
        for key, value in cell_dict.items():

            if len(value) > 1:
                raise SyntaxError("Waves can't work properly cause there is more then 1 cell in one of dirs", value)

            possible_cells = self.cellsConnections[mat_tmp[cell]]
            possible_cells = possible_cells[key]
            if value and mat_tmp[value[0]] in possible_cells:
                valid_cells.append(value[0])

        return valid_cells, cell

    def get_relative_cells(self,pos, mat = None):
        #возвращает словарь из четырёх клеток расположенных вокруг какой-то клетки и саму клетку
        #пример return [{"up":[], "right":[(0,1)], "down":[(1,0)], "left":[]}, (0,0)]

        mat = mat or self._matrix
        y, x = pos

        neighbors = {
            "up": [(y - 1, x)] if y - 1 >= 0 else [],
            "down": [(y + 1, x)] if y + 1 < len(mat) else [],
            "left": [(y, x - 1)] if x - 1 >= 0 else [],
            "right": [(y, x + 1)] if x + 1 < len(mat[y]) else []
        }
        return [neighbors, pos]

    @staticmethod
    def matrix_max_dimensions(matrix):
        # возвращает максимальные измерения матрицы переданной в класс в виде
        # [макс высота, макс ширина]

        return len(matrix), max(len(row) for row in matrix) if len(matrix) > 0 else 0

    def create_wave(self, start_point):
        #делает волну с учетом рамп, нужна только стартовая точка

        def get_ramp_chain_length(start_cell, matrix, connections, used, ramp_values=[31, 32, 33, 34]):

            chain = [start_cell]
            queue = [start_cell]

            while queue:
                cell = queue.pop(0)
                for neighbor in connections[cell]:
                    if neighbor not in used and np.array(matrix)[neighbor] in ramp_values:
                        used.add(neighbor)
                        chain.append(neighbor)
                        queue.append(neighbor)
            return chain

        self.matrixConnections = self._process_cells_connections()
        y, x = start_point
        if not (0 <= y < len(self._matrix) and 0 <= x < len(self._matrix[y])):
            raise ValueError(
                f"Out of range start wave point: {start_point}. Matrix dimensions: {len(self._matrix)}x{len(self._matrix[0]) if self._matrix else 0}")

        ramp_values = {31, 32, 33, 34}
        cells_indexes = {start_point: 0}
        used = {start_point}
        added = [start_point]

        while added:
            added_prev = []
            for i in added:
                for j in self.matrixConnections[i]:
                    if j not in used:
                        cell_value = np.array(self._matrix)[j]
                        if cell_value in ramp_values:
                            used.add(j)
                            ramp_chain = get_ramp_chain_length(j, self._matrix, self.matrixConnections, used,
                                                               ramp_values)

                            for idx, ramp_cell in enumerate(ramp_chain):
                                cells_indexes[ramp_cell] = cells_indexes[i] + 3 * (idx + 1)
                                added_prev.append(ramp_cell)
                        else:
                            cells_indexes[j] = cells_indexes[i] + 1
                            used.add(j)
                            added_prev.append(j)
            added = added_prev
        waves = self.convert_to_waves(cells_indexes)
        self.Waves = waves
        return waves

    @staticmethod
    def convert_to_waves(cells_dict):
        if not cells_dict:
            return []

        max_wave = max(cells_dict.values())

        waves = [[] for i in range(max_wave + 1)]

        for coord, wave_num in cells_dict.items():
            waves[wave_num].append(coord)

        return waves

    def find_index_by_cord(self, cord):
        #возвращает индекс волны по ее элементу
        for i in self.Waves:
            if cord in i:
                return self.Waves.index(i)

    def is_in_waves(self,cord):
        for i in self.Waves:
            for j in i:
                if cord == j:
                    return True
        return False

    def find_optimal_cells(self, cord):
        optimal_cells = []
        indexes = {}
        neighbour_cells = self.get_relative_cells(cord)[0]

        for key, value in neighbour_cells.items():
            if value and (self.is_in_waves(value[0]))and value[0] in self.matrixConnections[cord]:
                indexes[value[0]] = self.find_index_by_cord(value[0])

        for key, value in indexes.items():
            if value == min(indexes.values()):
                optimal_cells.append(key)

        # print(optimal_cells)
        return optimal_cells

    def block_cords(self, coordinates):
        # print(type(self._matrix))
        matrix_copy = copy.deepcopy(self._matrix)

        for i in coordinates:
            matrix_copy[i[0]][i[1]] = 0

        return matrix_copy

    def create_way(self, start, finish):
        if start == finish:
            return [start]

        self.Waves = self.create_wave(start)
        ways = [[finish]]

        if not self.is_in_waves(finish):
            return "No way"

        while ways[0][-1] != start:
            new_ways = []
            for way in ways:
                if way:
                    variants = self.find_optimal_cells(way[-1])
                    # print(variants)

                    if len(variants) == 1:
                        new_way = way.copy()
                        new_way.append(variants[0])
                        new_ways.append(new_way)

                    elif len(variants) > 1:
                        for variant in variants:
                            new_way = way.copy()
                            new_way.append(variant)
                            new_ways.append(new_way)
            ways = new_ways
            if not ways:
                break

        #переворачиваем все пути
        for i in range(len(ways)):
            ways[i] = ways[i][::-1]

        self.Ways = ways
        return self.sort_ways(ways)

    def sort_ways(self, ways):
        res = {}
        for i in ways:
            res[len(self.way_to_commands_single(i, "U")[0])] = i

        return res[min(res.keys())]

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
        dirs = {"U": 1, "R": 2, "D": 3, "L": 4}
        start = dirs[start]
        finish = dirs[finish]

        diff = (finish - start) % 4

        if diff == 0:
            return "skip"
        elif diff == 1:
            return "R1"
        elif diff == 2:
            return "R2"
        elif diff == 3:
            return "L1"

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
                        res_prev+= "X1"
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



class PattersSolver(WaveCreator):
    def __init__(self, matrix_for_solving):
        self.matrix = matrix_for_solving
        super().__init__(self.matrix)
        self.tubes = self.find_tubes()
        self.holders = self.find_holders()
        self.pick_up = self.pick_tubes_cords()
        self.floor = 1
        self.robot_cord = (8,8)
        # print(tubes)


    def find_tubes(self):
        #возвращает словарь вида {(yt, xt): []}
        tubes = []

        for i in range(len(self.matrix)):
            for j in range(len(self.matrix[i])):
                if str(self.matrix[i][j])[0] in ["4", "5"]:
                    tubes.append((i,j))

        return tubes

    def pick_tubes_cords(self):
        #возвращает координаты с которых можно забрать трубы вида {(yt,xt):[(yp,xp)...]}

        tubes_out = {}
        for i in self.tubes:
            tube = self._matrix[i[0]][i[1]]
            cells = self.get_relative_cells(i)[0]

            if tube == 41:
                res = []
                if cells["down"] and np.array(self._matrix)[cells["down"][0]] in [10, 33]:
                    res.append(cells["down"][0])

                if cells["up"] and np.array(self._matrix)[cells["up"][0]] in [10, 31]:
                    res.append(cells["up"][0])

                tubes_out[i] = res

            if tube == 42:
                res = []
                if cells["left"] and np.array(self._matrix)[cells["left"][0]] in [10, 34]:
                    res.append(cells["left"][0])

                if cells["right"] and np.array(self._matrix)[cells["right"][0]] in [10, 32]:
                    res.append(cells["right"][0])


                tubes_out[i] = res

            if tube == 51:
                res = []
                if cells["down"] and np.array(self._matrix)[cells["down"][0]] in [20, 31]:
                    res.append(cells["down"][0])

                if cells["up"] and np.array(self._matrix)[cells["up"][0]] in [20, 33]:
                    res.append(cells["up"][0])

                tubes_out[i] = res

            if tube == 52:
                res = []
                if cells["left"] and np.array(self._matrix)[cells["left"][0]] in [20, 32]:
                    res.append(cells["left"][0])

                if cells["right"] and np.array(self._matrix)[cells["right"][0]] in [20, 34]:
                    res.append(cells["right"][0])


                tubes_out[i] = res

        return tubes_out

    def get_unload_type(self):
        mat = []

        for i in self._matrix:
            mat += i

        if mat.count(61): return "up"
        elif mat.count(62): return "right"
        elif mat.count(63): return "down"
        elif mat.count(64):return "left"

        print("no holders")

    def find_holders(self):
        holders = []
        #база
        type_u = self.get_unload_type()

        if type_u == "right": type_u = "left"
        elif type_u == "left": type_u = "right"
        elif type_u == "down": type_u = "up"
        elif type_u == "up": type_u = "down"

        for i in range(len(self.matrix)):
            for j in range(len(self.matrix[i])):
                if str(self.matrix[i][j])[0] == "6":
                    holders.append((i,j))

        holders = [self.get_relative_cells(i)[0][type_u][0] for i in holders]

        return holders

    def find_robot(self):
        for i in range(len(self.matrix)):
            for j in range(len(self.matrix[i])):
                if str(self.matrix[i][j])[0] in ["7","8"]:
                    robot_cord = (i,j)
                    self.floor = 1 if str(self.matrix[i][j])[0] == "7" else 2
                    return robot_cord

    def generate_combinations(self,start):
        if not start:
            raise ValueError("Can't solve: no robot \n", np.array(self._matrix))


        tube_permutations = list(itertools.permutations(self.tubes, len(self.tubes)))
        combinations = [[start] + list(perm) for perm in tube_permutations]

        full_combinations = []


        for holder in self.holders:
            for comb in combinations:
                new_comb = comb.copy()
                new_comb.append(holder)
                full_combinations.append(new_comb)

        return full_combinations

    def weight_calculator(self, way):

        if len(way) == 1:
            return 0

        # print(way)
        weight = 0
        for i in way:
            if np.array(self._matrix)[i] not in [31,32,33,34]:
                weight += 1
            else: weight += 3

        return weight

    def choose_tube(self, cord, start):

        if cord not in self.tubes:
            return cord

        # print(self.pick_up, cord)
        index = 100
        cord_p = {}
        # print(self.pick_up[cord])
        for i in self.pick_up[cord]:

            if self.create_way(start, i) != "No way":
                index = self.weight_calculator(self.create_way(start,i))
                cord_p[index] = i

        return cord_p[min(cord_p.keys())]

    def process_combinations(self, combs):
        combins = {}

        for comb in combs:
            weight = 0
            way = []
            way_single = []
            for cell_num in range(len(comb)-1):
                add = 1
                if cell_num == 0:
                    add = 0

                if add == 0:
                    start = comb[0]
                else:
                    start = way_single[-1]

                way_single = self.create_way(start, self.choose_tube(comb[cell_num+1], start))


                if way_single == "No way":
                    print("Unsolvable")
                    return "No solution"

                weight += self.weight_calculator(way_single)
                way.append(way_single)
            combins[weight] = way
        return  combins[min(combins.keys())]

    def solve(self):
        start = self.find_robot()
        self.robot_cord = start
        self._matrix[start[0]][start[1]] = 10 if self._matrix[start[0]][start[1]] in [71,72,73,74] else 20
        self.tubes = self.find_tubes()
        self.holders = self.find_holders()
        self.pick_up = self.pick_tubes_cords()


        combs = self.generate_combinations(start)
        d = self.process_combinations(combs)
        return d

    def detect_unload_type(self, cord):
        cells = self.get_relative_cells(cord)
        unload_direction = []
        cord_to_detect = []
        dummy_dict = {"left":"L", "right":"R", "up":"U", "down":"D",}

        for key, item in cells[0].items():
            if np.array(self._matrix)[item[0]] in [61, 62, 63, 64]:
                unload_direction = dummy_dict[key]
                cord_to_detect = item[0]
                break

        # Получаем соседние клетки для текущей позиции держателя
        neighbor_cells = self.get_relative_cells(cord_to_detect)[0]

        # Проверяем правую сторону
        right_cell = neighbor_cells["right"]
        if right_cell and np.array(self._matrix)[right_cell[0]] not in [61, 62, 63, 64]:
            return "R", unload_direction  # Разгрузка справа

        # Проверяем левую сторону
        left_cell = neighbor_cells["left"]
        if left_cell and np.array(self._matrix)[left_cell[0]] not in [61, 62, 63, 64]:
            return "L", unload_direction  # Разгрузка слева

        # Если обе стороны заняты держателями
        if (right_cell and left_cell and
                np.array(self._matrix)[right_cell[0]] in [61, 62, 63, 64] and
                np.array(self._matrix)[left_cell[0]] in [61, 62, 63, 64]):
            return "C", unload_direction  # Разгрузка по центру

        # Если ни один вариант не подошел
        else: return "idktbh"




if __name__ == "__main__":
    mat = [[42, 10, 10, 10, 10, 20, 10, 10], [10, 10, 32, 20, 20, 34, 41, 20], [10, 10, 71, 20, 20, 34, 10, 20],
     [20, 20, 20, 34, 20, 10, 10, 33], [10, 10, 31, 10, 10, 10, 10, 62], [10, 10, 33, 10, 20, 20, 10, 62],
     [10, 20, 20, 20, 34, 10, 10, 62], [10, 20, 32, 20, 20, 20, 34, 10]]
    mat = [[10, 10, 42, 10, 20, 10, 10, 41], [10, 10, 20, 20, 34, 10, 20, 10], [10, 10, 10, 10, 10, 10, 10, 10], [31, 20, 10, 32, 20, 20, 34, 10], [20, 20, 20, 20, 20, 20, 34, 10], [20, 20, 10, 20, 52, 20, 34, 71], [20, 20, 10, 10, 10, 32, 34, 10], [33, 33, 63, 63, 63, 10, 10, 10]]
    mat = [[64, 10, 10, 10, 42, 10, 20, 10], [64, 10, 20, 20, 20, 34, 71, 10], [64, 10, 32, 20, 20, 20, 34, 10], [42, 10, 10, 10, 10, 10, 10, 20], [20, 20, 34, 10, 20, 10, 20, 20], [10, 10, 10, 10, 10, 10, 20, 20], [31, 20, 10, 32, 20, 20, 34, 33], [33, 10, 10, 10, 20, 20, 34, 42]]

    w = PattersSolver(mat)
    # w.create_wave((0,0))
    # print(w.Waves)
    # print(np.array(w._matrix))
    # w.create_way((0,6),(2,6))
    # print(w.Way)
    # print(w.tubes, w.holders)
    # w = PattersSolver(mat)
    res = w.solve()
    print(res)



