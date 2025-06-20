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

