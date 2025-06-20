from numpy.f2py.symbolic import replace_parenthesis


def prepare_to_insert(cells, direction):
    if direction == "U":
        return cells
    elif direction == "D":
        replacements = {31:33, 32:34, 33:31, 34:32, 61:63, 62:64, 63:61, 64:62}
        for i in range(len(cells)):
            if cells[i] in replacements.keys():
                cells[i] = replacements[i]