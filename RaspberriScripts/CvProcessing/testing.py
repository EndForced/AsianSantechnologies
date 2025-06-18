def insert_cells_into_matrix(matrix, cells, x, y, direction):
    # Создаем копию матрицы
    new_matrix = [row.copy() for row in matrix]

    # Определяем порядок вставки в зависимости от направления
    if direction == 'D':  # Вниз (вертикальная вставка)
        # Порядок: сначала верхняя строка (индексы 1,2), потом нижняя (3,4)
        positions = [
            (x, y + 1, 1),  # Правая верхняя (индекс 1)
            (x + 1, y + 1, 2),  # Левая верхняя (индекс 2)
            (x, y + 2, 3),  # Правая нижняя (индекс 3)
            (x + 1, y + 2, 4)  # Левая нижняя (индекс 4)
        ]
    elif direction == 'U':  # Вверх
        positions = [
            (x, y - 1, 1),
            (x + 1, y - 1, 2),
            (x, y - 2, 3),
            (x + 1, y - 2, 4)
        ]
    elif direction == 'L':  # Влево
        positions = [
            (x - 1, y, 1),
            (x - 1, y + 1, 2),
            (x - 2, y, 3),
            (x - 2, y + 1, 4)
        ]
    elif direction == 'R':  # Вправо
        positions = [
            (x + 1, y, 1),
            (x + 1, y + 1, 2),
            (x + 2, y, 3),
            (x + 2, y + 1, 4)
        ]
    else:
        raise ValueError("Неправильное направление. Допустимые значения: 'D', 'U', 'L', 'R'")

    # Вставляем клетки
    for px, py, idx in positions:
        if 0 <= px < 15 and 0 <= py < 15:  # Проверяем границы матрицы
            if idx in cells and cells[idx] != 'unr':  # Проверяем наличие значения
                new_matrix[py][px] = cells[idx]

    return new_matrix


import numpy as np

# Создаем пустую матрицу 15x15
matrix = np.zeros((15, 15), dtype=int).tolist()


pos = (8,8)
orientation = "U"
mat = [[0]*15]*15
cells = {1:20, 2:20, 3:30, 4:30}
mat = insert_cells_into_matrix(mat, cells, pos[0], pos[1], "U")
mat = np.array(mat)
print(mat)
