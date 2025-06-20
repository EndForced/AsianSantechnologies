import cv2
import numpy as np
from typing import List,Tuple

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wayProcessingOperations import BasicWaveOperations as WaveProcessing
from wayProcessingOperations.BasicWaveOperations import PattersSolver
import platform
possible_codes = [0, 10, 20, 31,32,33,34, 41,42, 51,52, 61,62,63,64, 71,72,73,74, 81,82,83,84, 91,92,93,94, 99]


class VisualizeMatrix:
    import cv2
    from typing import List, AnyStr
    import numpy as np

    def __init__(self, matrix:list[list[int]]):
        # super().__init__(matrix)
        self.pathToPics = "field_pictures/"

        self._possibleCodes = possible_codes
        #ждём текстуры для 81,82,83,84(робот на втором этаже) 91,92,93,94 - (робот на рампах)
        self._matrix = matrix

        self.OS = platform.system()

        self._matrixMaxHeight, self._matrixMaxWeight = WaveProcessing.WaveCreator.matrix_max_dimensions(self._matrix)
        self.picture = self.image_by_matrix_size()

        self._codesInMatrix = self.find_included_codes()
        self._cached_images =  self.cache_images()
        self.visualize_matrix()

        self.resizedPicture = self.smart_resize()

    def find_included_codes(self):
        codes = []
        for i in range(len(self._matrix)):
            for j in range(len(self._matrix[i])):

                code = self._matrix[i][j]
                if code in self._possibleCodes and code not in codes:
                    codes.append(code)

                if code not in self._possibleCodes:
                    raise ValueError("Impossible code found:",code)
        return codes

    def image_by_matrix_size(self):
        #создает картинку согласно максимальным измерениям матрицы

        if self._matrixMaxHeight > 0 and self._matrixMaxWeight > 0:
            picture = np.ones((100*self._matrixMaxHeight, 100*self._matrixMaxWeight,3), dtype=np.uint16)
        else: raise ValueError("Matrix dimensions can't equal zero", self._matrix)

        return picture


    def cache_images(self):
        pic_dictionary = {}
        for i in self._codesInMatrix:
            pic_dictionary[i] = np.uint16(cv2.imread(f"{self.pathToPics}{i}.png") * (65535 / 255))

        return pic_dictionary

    def visualize_matrix(self):
        # print(self.picture.shape)
        for i in range(self._matrixMaxHeight):
            for j in range(len(self._matrix[i])):
                code = self._matrix[i][j]
                y = i*100, (i+1)*100
                x = j*100, (j+1)*100
                # print(self._picture.dtype)
                # print(self._cached_images[code].dtype)
                self.picture[y[0]:y[1],x[0]:x[1]] = self._cached_images[code]

        if max(self.picture.shape) > 600:
            return self.smart_resize()

        return self.picture

    def update_matrix(self):
        self.picture = self.image_by_matrix_size()

        self._codesInMatrix = self.find_included_codes()
        self._cached_images = self.cache_images()
        self.visualize_matrix()

        self.resizedPicture = self.smart_resize()
        return self.resizedPicture

    def smart_resize(self, target_size=600, keep_aspect_ratio=True, interpolation=cv2.INTER_AREA):

        if self.picture is None:
            raise ValueError("Input image is None")

        h, w = self.picture.shape[:2]

        # Если изображение уже меньше целевого размера, не изменяем его
        if h <= target_size and w <= target_size:
            return self.picture

        # Ваш оригинальный подход с автоматическим расчетом коэффициента
        max_dim = max(h, w)
        scale_factor = target_size / max_dim

        # Рассчитываем новые размеры с сохранением пропорций
        if keep_aspect_ratio:
            new_h = int(h * scale_factor)
            new_w = int(w * scale_factor)
        else:
            new_h = target_size
            new_w = target_size

        # Применяем ресайз с выбранной интерполяцией
        resized = picture = cv2.resize(
            self.picture,
            (new_w, new_h),
            interpolation=interpolation
        )

        # Опционально: добавляем логгирование
        # print(f"Resized from {w}x{h} to {new_w}x{new_h} (scale factor: {scale_factor:.2f})")
        return resized

    def show(self):
        # print(self.OS)
        self.resizedPicture = self.smart_resize()
        if self.OS == "Windows":
            cv2.imshow("map", self.resizedPicture)
            cv2.waitKey(0)
        else:
            #smth for frame updating
            # print("Cant imshow on rp")
            return self.resizedPicture

class VisualizeWaves(PattersSolver,VisualizeMatrix):
    def __init__(self, matrix:list[list[int]]):
        PattersSolver.__init__(self,matrix)
        VisualizeMatrix.__init__(self,matrix)
        self.frameWeight = 7
        self.fontSize = 0.7
        self.fontThickness = 2
        self.maxWavesNum = 0

    def put_frame(self, cords: tuple[int, int], base_color: tuple[int, int, int]):
        """Рисует рамку вокруг клетки с автоматическим подбором контрастного цвета.

        Args:
            cords: Координаты клетки (y, x)
            base_color: Базовый цвет рамки в формате (B, G, R) [0-65535]
        """
        # Получаем область клетки
        y_start, y_end = cords[0] * 100, (cords[0] + 1) * 100
        x_start, x_end = cords[1] * 100, (cords[1] + 1) * 100

        # Корректировка границ для крайних клеток
        if cords[0] == 0: y_start += self.frameWeight
        if cords[1] == 0: x_start += self.frameWeight

        # Получаем средний цвет клетки (BGR)
        cell_area = self.picture[y_start:y_end, x_start:x_end]
        mean_color = np.mean(cell_area, axis=(0, 1))

        # Вычисляем яркость (формула восприятия)
        brightness = 0.299 * mean_color[2] + 0.587 * mean_color[1] + 0.114 * mean_color[0]

        # Преобразуем базовый цвет в numpy array для операций
        base_color_np = np.array(base_color, dtype=np.float32)

        # Выбираем контрастный цвет
        if brightness > 32768:  # Светлая клетка
            frame_color = base_color_np * 0.7  # Темнее
        else:  # Темная клетка
            frame_color = base_color_np * 1.3  # Светлее

        # Ограничиваем диапазон и преобразуем
        frame_color = np.clip(frame_color, 0, 65535).astype(np.uint16)

        # Рисуем рамку
        weight = self.frameWeight
        self.picture[y_start - weight:y_start, x_start:x_end] = frame_color  # Верх
        self.picture[y_end - weight:y_end, x_start:x_end] = frame_color  # Низ
        self.picture[y_start:y_end, x_start - weight:x_start] = frame_color  # Лево
        self.picture[y_start:y_end, x_end - weight:x_end] = frame_color  # Право

    def put_text(self, cords: tuple, text: str, color=(65535/2, 65535/2, 65535/2)):
        #Максимум - 3 символа !!!11!!11!
        if type(text) != "str":
            text = str(text)

        if cords[0] >= len(self._matrix) or cords[1] >= len(self._matrix[cords[0]]):
            raise ValueError("Trying to display text out of matrix range:", cords, "matrix:", self._matrix)
        temp_img = np.zeros(self.picture.shape[:2], dtype=np.uint8)

        x = int((cords[1] + 1) * 100 - 99 + 5 * abs(3 - len(text)))
        y = int(cords[0] * 100 + 84)

        cv2.putText(
            temp_img,
            text,
            org=(x, y),
            fontScale=self.fontSize,
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            color=255,
            thickness=self.fontThickness,
            lineType=cv2.LINE_8
        )

        mask = temp_img > 0

        for c in range(3):
            self.picture[:, :, c][mask] = color[c]

    def visualize_wave(self,waves:dict = None):
        waves = waves or self.Waves
        self.maxWavesNum = len(waves)
        self.visualize_matrix()

        for wave in waves:
            for cell in wave:
                current_number = waves.index(wave)
                color_temp = self.scale_value_waves(current_number)
                color = self._interpolate_color(color_temp)
                self.put_text(cell,current_number)
                self.put_frame(cell,color)

    @staticmethod
    def _interpolate_color(t):
        if (t < 1 or t == 1) and (t > 0 or t == 0):
            # переводит значение от нуля до единицы в цвет от красного до синего, думаю мне не нужно это объяснять
            light_blue = (75, 120, 230)
            bright_red = (255, 0, 0)
            t = t - 0.05
            red = int(light_blue[0] + (bright_red[0] - light_blue[0]) * t)
            green = 0
            blue = int(light_blue[2] + (bright_red[2] - light_blue[2]) * t)

            return blue*257, green*257, red*257
        else:
            print("Fail during colour interpolation! arg can't be > 1 or < 0 !  \n arg:", t)
            return None

    def scale_value_waves(self,value):
        from_min, to_min = 0, 0
        from_max = self.maxWavesNum
        to_max = 1

        normalized_value = (value - from_min) / (from_max - from_min)  # map() из ардуино но в питоне

        scaled_value = to_min + normalized_value * (to_max - to_min)

        return scaled_value

class VisualizePaths(VisualizeWaves):
    def __init__(self, matrix: List[List[int]]):
        super().__init__(matrix)
        # Цвета для путей (BGR в диапазоне 0-65535)
        self.path_colors = [
            (0, 65535, 0),  # Зеленый
            (65535, 0, 0),  # Синий
            (0, 0, 65535),  # Красный
            (65535, 65535, 0),  # Голубой
            (0, 65535, 65535),  # Желтый
            (65535, 0, 65535)  # Пурпурный
        ]
        self.path_thickness = 9
        self.arrow_thickness = 3
        self.path_offset = 9 # Смещение для параллельных путей
        self.temp_canvas = None
        self.route_number_font = cv2.FONT_HERSHEY_SIMPLEX
        self.route_number_scale = 0.8
        self.route_number_thickness = 2

    def draw_path(self, path: List[Tuple[int, int]], color_index: int = 0, route_num: int = 0):
        """Рисует один путь на изображении сплошной линией с номером маршрута"""
        if not path or len(path) < 2:
            return

        color = self.path_colors[color_index % len(self.path_colors)]

        # Вычисляем смещение для текущего маршрута
        offset_x = (color_index % 3 - 1) * self.path_offset
        offset_y = ((color_index // 3) % 2) * self.path_offset

        # Подготавливаем массив точек для сплошной линии
        points = []
        for cell in path:
            center = self._get_center_coords(cell, offset_x, offset_y)
            points.append(center)

        # Преобразуем в numpy массив и рисуем сплошную линию
        points = np.array(points, dtype=np.int32)
        cv2.polylines(self.picture, [points], False, color, self.path_thickness)

        # # Добавляем стрелки направления
        # for i in range(len(points) - 1):
        #     cv2.arrowedLine(self.picture, points[i], points[i + 1], (0, 0, 0),
        #                     self.arrow_thickness, tipLength=0.3)

        # Добавляем номер маршрута в верхний правый угол последней клетки
        if route_num > 0:
            self._draw_route_number(path[-1], route_num, color)

    def _get_center_coords(self, cell: Tuple[int, int], offset_x: int = 0, offset_y: int = 0) -> Tuple[int, int]:
        """Возвращает координаты центра клетки в пикселях с учетом смещения"""
        y, x = cell
        center_x = x * 100 + 50 + offset_x
        center_y = y * 100 + 50 + offset_y
        return (center_x, center_y)

    def _draw_route_number(self, cell: Tuple[int, int], route_num: int, color: Tuple[int, int, int]):
        """Рисует номер маршрута в верхнем правом углу клетки"""
        y, x = cell
        text = str(route_num)

        # Позиция текста (верхний правый угол клетки)
        text_x = x * 100 + 80
        text_y = y * 100 + 30

        # Размер текста
        text_size = cv2.getTextSize(text, self.route_number_font,
                                    self.route_number_scale,
                                    self.route_number_thickness)[0]

        # Рисуем текст с контуром для лучшей видимости
        cv2.putText(self.picture, text, (text_x - text_size[0], text_y),
                    self.route_number_font, self.route_number_scale,
                    (65535, 65535, 65535), self.route_number_thickness + 2)

        cv2.putText(self.picture, text, (text_x - text_size[0], text_y),
                    self.route_number_font, self.route_number_scale,
                    color, self.route_number_thickness)

    def draw_multiple_paths(self, paths: List[List[Tuple[int, int]]]):
        """Рисует несколько путей разными цветами с номерами"""
        # Рисуем все пути
        for i, path in enumerate(paths):
            if len(path) == 1:
                self._draw_route_number(path[0], i+1 , self.path_colors[1])
            self.draw_path(path, i, i + 1)  # i+1 - номер маршрута

    def visualize(self, paths: List[List[Tuple[int, int]]], waves: List[List[Tuple[int, int]]] = None):
        """Основной метод визуализации"""
        # Сначала рисуем волны (если нужно)
        if waves:
            self.visualize_wave(waves)

        # Затем рисуем пути с номерами
        self.draw_multiple_paths(paths)

        # Возвращаем изображение в формате BGR
        return cv2.cvtColor(self.picture, cv2.COLOR_RGB2BGR)

if __name__ == "__main__":
    # mat = [[10, 31, 10, 10, 42, 10, 10, 62], [10, 20, 10, 10, 20, 20, 10, 62], [20, 20, 20, 10, 32, 34, 10, 62], [20, 20, 20, 10, 20, 10, 20, 10], [20, 33, 33, 10, 71, 10, 10, 41], [33, 41, 20, 20, 34, 10, 10, 10], [10, 20, 10, 10, 32, 20, 20, 34], [10, 10, 10, 20, 20, 34, 10, 10]]
    mat = [[0, 0, 10, 10, 10, 61, 61, 61],
           [10, 10, 10, 10, 10, 10, 10, 10],
           [10, 10, 10, 10, 10, 10, 10, 10],
           [10, 10, 0, 0, 0, 41, 10, 10],
           [10, 33, 10, 42, 10, 10, 10, 10],
           [10, 31, 10, 10, 41, 10, 10, 10],
           [10, 33, 10, 10, 10, 71, 10, 10],
           [10, 10, 10, 10, 10, 10, 10, 10],]

    # mat = [[64, 10, 10, 10, 42, 10, 20, 10], [64, 10, 20, 20, 20, 34, 10, 10], [64, 10, 32, 20, 81, 52, 34, 10], [42, 10, 10, 10, 10, 10, 10, 20], [20, 20, 34, 10, 20, 10, 20, 20], [10, 10, 10, 10, 10, 10, 20, 20], [31, 20, 10, 32, 20, 20, 34, 33], [33, 10, 10, 10, 20, 20, 34, 42]]
    mat = [[10, 10, 20, 20, 20, 34, 10, 62], [10, 52, 20, 20, 34, 20, 10, 62], [10, 20, 20, 20, 34, 10, 10, 62], [32, 20, 20, 20, 34, 10, 10, 20], [20, 10, 10, 10, 10, 10, 31, 20], [20, 32, 20, 20, 34, 10, 33, 20], [33, 10, 10, 10, 10, 10, 10, 10], [42, 10, 10, 71, 10, 10, 42, 10]]
    obj = VisualizePaths(mat)

    robot = obj.find_robot()
    obj.create_wave(robot)
    obj.visualize_wave(obj.Waves)
    # d = obj.solve()
    # print(d)
    # obj.draw_multiple_paths(d)
    # res = obj.create_way((5,5),(6,4))

    # print(res)
    # obj.draw_path(res)
    obj.show()





