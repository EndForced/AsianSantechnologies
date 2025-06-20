from numpy.f2py.symbolic import replace_parenthesis


def prepare_to_insert(cells, direction):
    print("cells start", cells)
    if direction == "U":
        return cells

    elif direction == "D":
        replacements = {31:33, 32:34, 33:31, 34:32, 61:63, 62:64, 63:61, 64:62}
        for i in cells.keys():
            if cells[i] in replacements.keys():
                cells[i] = replacements[cells[i]]
        print("cells finish")
        return cells

    elif direction == "L":
        replacements = {41:42, 51:52, 42:41, 52:51, 32:31, 34:33, 31:32, 33:34}#idktbh 61:63, 62:64, 63:61, 64:62
        for i in cells.keys():
            if cells[i] in replacements.keys():
                cells[i] = replacements[cells[i]]
        print("cells finish")
        return cells

    elif direction == "R": #not sure
        replacements = {41:42, 51:52, 42:41, 52:51, 32:31, 34:33, 31:32, 33:34}#idktbh 61:63, 62:64, 63:61, 64:62
        for i in cells.keys():
            if cells[i] in replacements.keys():
                cells[i] = replacements[cells[i]]
        print("cells finish")
        return cells



def line_in_matrix(line_of, cord_type, cord, mat17x17):
    length = mat17x17.shape[0] if cord_type == 'x' else mat17x17.shape[1]
    if length != 17 or sum(mat17x17.shape[:2]) != 17 * 2:
        print(f"you are using some strange matrix?\nnormal one should be 17x17 not {mat17x17.shape[0]}x{mat17x17.shape[1]}")
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

    if cords_yx[0] > mat17x17.shape[0] or cords_yx[0] < 0 :
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

    if orientation == "U" or orientation=="L":
        delta*=-1

    if edge_type[0] == 'f':
        direction_of_line_normale = same_dir(orientation)
    else:
        direction_of_line_normale = opposite_dir(orientation)


    cord = cords_yx[0] if direction_of_line_normale=='y' else cords_yx[1]
    cord = cord + delta
    # край ближний к нам
    line_in_matrix(99,direction_of_line_normale,cord,mat17x17)

    if cord > 8:
        cord = cord - 9
    else:
        cord = cord + 9
    # второй край через поле от него
    line_in_matrix(99,direction_of_line_normale,cord,mat17x17)







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

