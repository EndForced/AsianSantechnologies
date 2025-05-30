from typing import List

import numpy as np
from numpy.matrixlib.defmatrix import matrix
import time

possible_codes = [0, 10, 20, 31,32,33,34, 41,42, 51,52, 61,62,63,64, 71,72,73,74]

class WaveCreator:
    def __init__(self,matrix_in:list[list[int]]):
        self._matrix = matrix_in

        if not self._matrix or max(self.matrix_max_dimensions(self._matrix)) == 1:
            raise ValueError("Can't create neighbor dictionary with this matrix:" , self._matrix)

        self.Waves = []
        self.Ways = []

        self.cellsConnections = {10:{"up":[31,10, 41], "left":[34,10, 42], "down":[33,10, 41], "right":[32,10, 42]},
                                 20:{"up":[33,20, 51], "left":[32,20, 52], "down":[31,20, 51], "right":[34,20, 52]},

                                 31:{"up":[33,20, 51], "left":[None], "down":[33,10, 41], "right":[None]},
                                 32:{"up":[None], "left":[10,34, 42], "down":[None], "right":[20, 51]},
                                 33:{"up":[31, 41], "left":[None], "down":[31,20, 51], "right":[None]},
                                 34:{"up":[None], "left":[20,32, 52], "down":[None], "right":[10, 42]},

                                 71:{"up":[31,10, 41], "left":[34,10, 42], "down":[33,10, 41], "right":[32,10, 42]},
                                 72:{"up":[31,10, 41], "left":[34,10, 42], "down":[33,10, 41], "right":[32,10, 42]},
                                 73:{"up":[31,10, 41], "left":[34,10, 42], "down":[33,10, 41], "right":[32,10, 42]},
                                 74:{"up":[31,10, 41], "left":[34,10, 42], "down":[33,10, 41], "right":[32,10, 42]},

                                 61: {"up": [None], "left": [None], "down": [None], "right": [None]},
                                 62: {"up": [None], "left": [None], "down": [None], "right": [None]},
                                 63: {"up": [None], "left": [None], "down": [None], "right": [None]},
                                 64: {"up": [None], "left": [None], "down": [None], "right": [None]},

                                 41: {"up": [None], "left": [None], "down": [None], "right": [None]},
                                 42: {"up": [None], "left": [None], "down": [None], "right": [None]},

                                 51: {"up": [None], "left": [None], "down": [None], "right": [None]},
                                 52: {"up": [None], "left": [None], "down": [None], "right": [None]},

                                 0: {"up": [None], "left": [None], "down": [None], "right": [None]},
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
        y, x = start_point
        if not (-1 < y < len(self._matrix) - 1 and -1 < x < len(self._matrix[y])):
            raise ValueError("Out of range start wave point:", start_point, self._matrix)

        waves = [[start_point]]
        visited = set(waves[0])

        while waves[-1]: #пока в прошлой волне что-то есть
            next_wave = []

            for element in waves[-1]:
                for neighbour in self.matrixConnections[element]:
                    if neighbour not in visited:
                        next_wave.append(neighbour)
                        visited.add(neighbour)

            waves.append(next_wave)

        self.Waves = waves[:-1]
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
            if value and (self.is_in_waves(value[0])):
                indexes[value[0]] = self.find_index_by_cord(value[0])

        for key, value in indexes.items():
            if value == min(indexes.values()):
                optimal_cells.append(key)

        return optimal_cells

    def create_way(self, start, finish):
        self.Waves = self.create_wave(start)
        ways = [[finish]]

        if start == finish:
            return [[]]

        while ways[0][-1] != start:
            new_ways = []
            for way in ways:
                if way:
                    variants = self.find_optimal_cells(way[-1])
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
            last_cell = np.array(self._matrix)[ways[i][-1]]

            if last_cell in [41,42, 51,52]:
                ways[i].pop(-1)

        if not ways:
            return "No way"

        self.Ways = ways
        return ways

    def sort_ways(self, ways):
        res = {}
        count = 0
        prev_conn = ""

        if len(ways) == 1:
            return ways[0]

        for i in range(len(ways)):
            for j in range(len(ways[i])):

                if j+1 == len(ways[i]):
                    break

                cells = self.get_relative_cells(ways[i][j+1])[0]
                for key, item in cells.items():
                    if item == ways[i][j]:
                        if key != prev_conn:
                            count += 1
                            prev_conn = key

            res[count] = ways[i]

        return res[min(res.keys())]

class PattersSolver(WaveCreator):
    def __init__(self, matrix_for_solving):
        self.matrix = matrix_for_solving
        super().__init__(self.matrix)
        tubes = self.find_tubes()
        # print(tubes)


    def find_tubes(self):
        #возвращает словарь вида {(yt, xt): []}
        tubes = []

        for i in range(len(self.matrix)):
            for j in range(len(self.matrix[i])):
                if str(self.matrix[i][j])[0] in ["4", "5"]:
                    tubes.append((i,j))

        return tubes


if __name__ == "__main__":
    mat = [[10, 31, 10, 10, 42, 10, 10, 62], [10, 20, 10, 10, 20, 20, 10, 62], [20, 20, 20, 10, 32, 34, 10, 62], [20, 20, 20, 10, 20, 10, 20, 10], [20, 33, 33, 10, 71, 10, 10, 41], [33, 41, 20, 20, 34, 10, 10, 10], [10, 20, 10, 10, 32, 20, 20, 34], [10, 10, 10, 20, 20, 34, 10, 10]]

    w = WaveCreator(mat)
    w.create_wave((0,0))
    print(w.Waves)
    print(np.array(w._matrix))
    w.create_way((0,6),(2,6))
    print(w.Way)
    # w = PattersSolver(mat)


