from numpy.f2py.symbolic import replace_parenthesis
from collections import deque
import numpy as np
import copy


def prepare_to_insert(cells, direction):
    print("cells start", cells)
    if direction == "U":
        return cells

    elif direction == "D":
        replacements = {31: 33, 32: 34, 33: 31, 34: 32, 61: 63, 62: 64, 63: 61, 64: 62}
        for i in range(len((cells))):
            if cells[i] in replacements.keys():
                cells[i] = replacements[cells[i]]
        print("cells finish")
        return cells

    elif direction == "L":
        replacements = {41: 42, 51: 52, 42: 41, 52: 51, 32: 31, 34: 33, 31: 34,
                        33: 32, 61: 64, 62: 61, 63: 62, 64: 63}  # idktbh 61:63, 62:64, 63:61, 64:62
        for i in range(len((cells))):
            if cells[i] in replacements.keys():
                cells[i] = replacements[cells[i]]
        print("cells finish")
        return cells

    elif direction == "R":  # not sure
        replacements = {41: 42, 51: 52, 42: 41, 52: 51, 32: 31, 34: 33, 31: 34,
                        33: 32, 61: 62, 62: 63, 63: 64, 64: 61}  # idktbh 61:63, 62:64, 63:61, 64:62
        for i in range(len((cells))):
            if cells[i] in replacements.keys():
                cells[i] = replacements[cells[i]]
        print("cells finish")
        return cells


def line_in_matrix(line_of, cord_type, cord, mat17x17):
    length = mat17x17.shape[0] if cord_type == 'x' else mat17x17.shape[1]
    if length != 17 or sum(mat17x17.shape[:2]) != 17 * 2:
        print(
            f"you are using some strange matrix?\nnormal one should be 17x17 not {mat17x17.shape[0]}x{mat17x17.shape[1]}")
    if cord < 0 or cord >= sum(mat17x17.shape[:2]) - length:
        print(f"cord {cord} is outside of map bound")
        return

    for c in range(length):
        if cord_type == "x":
            mat17x17[c][cord] = line_of
        elif cord_type == "y":
            mat17x17[cord][c] = line_of
        else:
            print(f"unknown cord type - {cord_type}")
            return


def edge_to_matrix(mat17x17, edge_type, cords_yx, orientation):
    def same_dir(dir):
        return "x" if dir == "R" or dir == "L" else "y"

    def opposite_dir(dir):
        return "y" if dir == "R" or dir == "L" else "x"

    edge_types = ['fc', 'ff', 'sc', 'sf']
    oris = 'URDL'

    if not edge_type in edge_types:
        print(f"unknown edge type - {edge_type}")
        return

    if cords_yx[0] > mat17x17.shape[0] or cords_yx[0] < 0:
        print(f"cord y is outside of map bound")
        return
    if cords_yx[1] > mat17x17.shape[1] or cords_yx[1] < 0:
        print(f"cord x is outside of map bound")
        return

    if not orientation in oris:
        print(f"unknown orientation - {orientation}")
        return

    delta = 1
    direction_of_line_normale = ''
    if edge_type[1] == "f":
        delta = 2

    if orientation == "U" or orientation == "L":
        delta *= -1

    if edge_type[0] == 'f':
        direction_of_line_normale = same_dir(orientation)
    else:
        direction_of_line_normale = opposite_dir(orientation)

    cord = cords_yx[0] if direction_of_line_normale == 'y' else cords_yx[1]
    cord = cord + delta
    # край ближний к нам

    if cord > 8:
        for i in range(cord, 17 + 1):
            line_in_matrix(99, direction_of_line_normale, i, mat17x17)
        cord = cord - 9
        for i in range(0, cord + 1):
            line_in_matrix(99, direction_of_line_normale, i, mat17x17)
    else:
        for i in range(0, cord + 1):
            line_in_matrix(99, direction_of_line_normale, i, mat17x17)
        cord = cord + 9
        for i in range(cord, 17 + 1):
            line_in_matrix(99, direction_of_line_normale, i, mat17x17)

    return mat17x17


def cell_interest(cell, direction, mat, used_cells):
    # адаптировать под вторую камеру будет не сложно
    used_cells = used_cells.copy()
    y, x = cell
    mat = np.array(mat)
    ymax, xmax = mat.shape
    banned_indexes = []

    cords_of_interest = {
        "U": [(y - 1, x + 1), (y - 1, x), (y - 1, x - 1), (y - 2, x + 1), (y - 2, x), (y - 2, x - 1)],
        "D": [(y + 1, x - 1), (y + 1, x), (y + 1, x + 1), (y + 2, x - 1), (y + 2, x), (y + 2, x + 1)],
        "R": [(y + 1, x + 1), (y, x + 1), (y - 1, x + 1), (y + 1, x + 2), (y, x + 2), (y - 1, x + 2)],
        "L": [(y - 1, x - 1), (y, x - 1), (y + 1, x - 1), (y - 1, x - 2), (y, x - 2), (y + 1, x - 2)]
    }

    if direction not in ["U", "D", "R", "L"]:
        print("Strange direction while interest calculation!!!1", direction)
        return

    interest = 0
    for cord in cords_of_interest[direction]:
        yc, xc = cord

        if -1 < yc <= ymax - 1 and -1 < xc <= xmax - 1:  # in matrix range

            if cords_of_interest[direction].index(cord) == 0:  # cant read behind 2 floor
                if mat[cord] in [20, 51, 52, 32, 33, 34]:
                    banned_indexes.append(3)

            if cords_of_interest[direction].index(cord) == 1:
                if mat[cord] in [20, 51, 52, 32, 33, 34]:
                    banned_indexes.append(4)

            if cords_of_interest[direction].index(cord) == 2:
                if mat[cord] in [20, 51, 52, 32, 33, 34]:
                    banned_indexes.append(5)

            flag = 0 if mat[cord] != 0 or cord in used_cells or cords_of_interest[direction].index(
                cord) in banned_indexes else 1

            if min(cord) > -1 and flag:
                used_cells.append(cord)

            if mat[cord] == 0 and cords_of_interest[direction].index(cord) not in banned_indexes and flag and min(
                    cord) > -1:
                interest += 1

    return interest, used_cells


def dirs_summ(dir1, dir2):
    if dir1 == "U":
        if dir2 == "R":
            return "R"
        if dir2 == "L":
            return "L"

    if dir1 == "D":
        if dir2 == "R":
            return "L"
        if dir2 == "L":
            return "R"

    if dir1 == "R":
        if dir2 == "R":
            return "D"
        if dir2 == "L":
            return "U"

    if dir1 == "L":
        if dir2 == "R":
            return "U"
        if dir2 == "L":
            return "D"


def route_to_dirs(route, commands, dir_start):
    # heart of the slam
    dir_d = {}
    dir_d[route[0]] = [dir_start]
    dir_prev = dir_start
    curr_dir = dir_start
    c = 0

    for i in range(len(commands)):
        if commands[i][0] not in ["F", "X"]:
            curr_dir = dirs_summ(dir_prev, commands[i][0])

            if route[c] in dir_d.keys():
                dir_d[route[c]].append(curr_dir)

            else:
                dir_d[route[c]] = [curr_dir]

            dir_prev = copy.copy(curr_dir)


        else:
            c += 1
            if route[c] not in dir_d.keys():
                dir_d[route[c]] = [curr_dir]

    return dir_d


def coolest_route(mc):
    cells_interests = {}
    cord_r = mc.robot.Position
    wave = mc.create_wave(cord_r)
    used_cells_d = {}

    for i in wave:
        for j in i:
            cords_roadmap = mc.create_way(cord_r, j)

            if len(cords_roadmap) > 1 and np.array(mc._matrix)[j] not in [31, 32, 33, 34]:
                used_cells = []

                roadmap, end_dir = mc.way_to_commands_single(cords_roadmap, mc.robot.Orientation, 0)
                if roadmap[0] == "R2":
                    roadmap.pop(0)
                    roadmap = roadmap[::-1]
                    roadmap.append("R1")
                    roadmap.append("R1")
                    roadmap = roadmap[::-1]

                cords_to_pos = route_to_dirs(cords_roadmap, roadmap, mc.robot.Orientation)
                # print(cords_roadmap, cords_to_pos)
                route_interest = 0
                counter = 0
                for cord, dirs in cords_to_pos.items():
                    for dir in dirs:
                        cell_int, used_cells = cell_interest(cord, dir, mc._matrix, used_cells)
                        route_interest += cell_int
                        route_interest -= 0.01 * counter ** 0.5
                        counter += 1

                cells_interests[route_interest] = cords_roadmap[-1]
                used_cells_d[route_interest] = used_cells

    print(
        f"Now going to {cells_interests[max(cells_interests.keys())]} with route interest {max(cells_interests.keys())}")
    return cells_interests[max(cells_interests.keys())], [used_cells_d[max(cells_interests.keys())]]


def choose_by_border(cell, mc, dir):
    pass


def choose_by_interest(interest, cell, mc, dir):
    pass


def find_optimal_orientation(cell, mc, dir):
    pass


def optimal_cell_scanning(mc, cell, dir, used_cells):
    dirs = ["U", "R", "D", "L"]
    # print(used_cells)
    interest_dirs = []
    for i in dirs:
        interest = cell_interest(cell, i, mc._matrix, used_cells[0])[0]
        if interest:
            # print(interest, i)
            interest_dirs.append(i)

    if 99 in np.array(mc._matrix):
        return choose_by_border(cell, mc, dir)

    elif interest_dirs.count(max(interest_dirs)) == 1:
        return choose_by_interest(cell, mc, dir)

    else:
        return find_optimal_orientation(cell, mc, dir)

    # print(interest_dirs)


mat = [[0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0],
       [0, 0, 10, 0, 0],
       [0, 20, 20, 20, 0],
       [0, 0, 0, 0, 0],
       ]
used_cells = []
print(cell_interest((2, 2), "D", mat, used_cells))
print(used_cells)

# mat = np.full((17,17),10)
# cords = (8,8)
# dir = "R"
# edge = 'fc'
# mat[cords[0]][cords[1]] = 71
# print(mat)
# edge_to_matrix(mat,edge,cords,dir)
# print(mat)
# cords = (8,8)
# dir = "U"
# edge = 'fc'
# mat[cords[0]][cords[1]] = 71
# edge_to_matrix(mat,edge,cords,dir)
# print(mat)
#
# # mat = np.full((8,4),10)
# # line_in_matrix(99,'y',8,mat)
# # print(mat)
