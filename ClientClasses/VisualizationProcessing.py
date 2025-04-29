import cv2
import numpy as np


class VisualizeMatrix:
    import cv2
    from typing import List
    import numpy as np

    def __init__(self, matrix:list[list[int]]):
        if np.array(matrix).ndim != 2:
            raise ValueError("Matrix dimension error!11!!1! mat:", matrix)

        self.pathToPics = "field_pictures/"
        self._possibleCodes = [0, 10, 20, 31,32,33,34, 41,42, 51,52, 61,62,63,64, 71,72,73,74]
        #ждём текстуры для 81,82,83,84(робот на втором этаже) 91,92,93,94 - (робот на рампах)
        self._matrix = matrix

        self._matrixMaxHeight, self._matrixMaxWeight = self._matrix_max_dimensions()
        self._picture = self._image_by_matrix_size()

        self._codesInMatrix = self._find_included_codes()
        self._cached_images =  self._cache_images()
        self.visualize_matrix()

    def _find_included_codes(self):
        codes = []
        for i in range(len(self._matrix)):
            for j in range(len(self._matrix[i])):

                code = self._matrix[i][j]
                if code in self._possibleCodes and code not in codes:
                    codes.append(code)

                if code not in self._possibleCodes:
                    raise ValueError("Impossible code found:",code)
        return codes

    def _image_by_matrix_size(self):
        #создает картинку согласно максимальным измерениям матрицы

        if self._matrixMaxHeight > 0 and self._matrixMaxWeight > 0:
            picture = np.ones((100*self._matrixMaxHeight, 100*self._matrixMaxWeight,3), dtype=np.uint16)
        else: raise ValueError("Matrix dimensions can't equal zero", self._matrix)

        return picture

    def _matrix_max_dimensions(self):
        #возвращает максимальные измерения матрицы переданной в класс в виде
        #[макс высота, макс ширина]

        return len(self._matrix), max(len(row) for row in self._matrix) if len(self._matrix) > 0 else 0

    def _cache_images(self):
        pic_dictionary = {}
        for i in self._codesInMatrix:
            pic_dictionary[i] = np.uint16(cv2.imread(f"{self.pathToPics}{i}.png") * (65535 / 255))

        return pic_dictionary

    def visualize_matrix(self):
        print(self._picture.shape)
        for i in range(self._matrixMaxHeight):
            for j in range(len(self._matrix[i])):
                code = self._matrix[i][j]
                y = i*100, (i+1)*100
                x = j*100, (j+1)*100
                # print(self._picture.dtype)
                # print(self._cached_images[code].dtype)
                self._picture[y[0]:y[1],x[0]:x[1]] = self._cached_images[code]

        if max(self._picture.shape) > 600:
            return self._smart_resize()

        return self._picture

    def _smart_resize(self, target_size=600, keep_aspect_ratio=True, interpolation=cv2.INTER_AREA):
        """
        Улучшенный ресайз изображения с автоматическим подбором коэффициента масштабирования
        и сохранением качества.

        Параметры:
            target_size (int): максимальный размер по любой из сторон (по умолчанию 600)
            keep_aspect_ratio (bool): сохранять соотношение сторон (True по умолчанию)
            interpolation: метод интерполяции (по умолчанию INTER_AREA для уменьшения)

        Возвращает:
            None (изменяет self._picture напрямую)
        """
        if self._picture is None:
            raise ValueError("Input image is None")

        h, w = self._picture.shape[:2]

        # Если изображение уже меньше целевого размера, не изменяем его
        if h <= target_size and w <= target_size:
            return

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
            self._picture,
            (new_w, new_h),
            interpolation=interpolation
        )

        # Опционально: добавляем логгирование
        print(f"Resized from {w}x{h} to {new_w}x{new_h} (scale factor: {scale_factor:.2f})")
        return resized




mat = [[10]*15]*15
       # print(mat)

c = VisualizeMatrix(mat)
pic = c.visualize_matrix()
# print(pic)
cv2.imshow("pic",pic)
cv2.waitKey(0)
c.__init__(mat)

cv2.imshow("pic",c._picture)
cv2.waitKey(0)
#tsttst


