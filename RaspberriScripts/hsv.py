import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk


class HSVAreaSelector:
    def __init__(self, root):
        self.root = root
        self.root.title("HSV Area Selector")

        # Переменные
        self.image_path = ""
        self.image = None
        self.display_image = None
        self.selection_start = None
        self.selection_end = None
        self.selecting = False
        self.hsv_values = tk.StringVar()

        # Создание интерфейса
        self.create_widgets()

    def create_widgets(self):
        # Фрейм для изображения
        self.image_frame = tk.Frame(self.root)
        self.image_frame.pack(side=tk.TOP, padx=5, pady=5)

        # Canvas для отображения изображения
        self.canvas = tk.Canvas(self.image_frame, width=800, height=600, cursor="cross")
        self.canvas.pack()
        self.canvas.bind("<ButtonPress-1>", self.start_selection)
        self.canvas.bind("<B1-Motion>", self.update_selection)
        self.canvas.bind("<ButtonRelease-1>", self.end_selection)

        # Фрейм для кнопок и информации
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(side=tk.BOTTOM, padx=5, pady=5)

        # Кнопки
        self.load_button = tk.Button(self.control_frame, text="Load Image", command=self.load_image)
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = tk.Button(self.control_frame, text="Clear", command=self.clear_selection)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        # Поле для вывода HSV значений
        self.hsv_label = tk.Label(self.control_frame, text="Average HSV:")
        self.hsv_label.pack(side=tk.LEFT, padx=5)

        self.hsv_entry = tk.Entry(self.control_frame, textvariable=self.hsv_values, width=30, state='readonly')
        self.hsv_entry.pack(side=tk.LEFT, padx=5)

    def load_image(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
        if self.image_path:
            self.image = cv2.imread(self.image_path)
            if self.image is not None:
                self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
                self.display_image = self.image.copy()
                self.update_canvas()
                self.clear_selection()

    def update_canvas(self):
        if self.display_image is not None:
            # Масштабирование изображения для отображения
            h, w = self.display_image.shape[:2]
            ratio = min(800 / w, 600 / h)
            new_w, new_h = int(w * ratio), int(h * ratio)
            resized_img = cv2.resize(self.display_image, (new_w, new_h))

            img = Image.fromarray(resized_img)
            img = ImageTk.PhotoImage(image=img)

            # Сохраняем ссылку, чтобы избежать сборки мусора
            self.canvas.image = img
            self.canvas.config(width=new_w, height=new_h)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=img)

    def start_selection(self, event):
        if self.image is None:
            return

        self.selecting = True
        self.selection_start = (event.x, event.y)
        self.selection_end = None

    def update_selection(self, event):
        if not self.selecting or self.image is None:
            return

        self.selection_end = (event.x, event.y)
        self.redraw_image_with_selection()

    def end_selection(self, event):
        if not self.selecting or self.image is None:
            return

        self.selection_end = (event.x, event.y)
        self.selecting = False

        if self.selection_start and self.selection_end:
            # Получаем координаты выделенной области в масштабе исходного изображения
            h, w = self.image.shape[:2]
            canvas_w = self.canvas.winfo_width()
            canvas_h = self.canvas.winfo_height()
            ratio = min(canvas_w / w, canvas_h / h)

            x1 = int(min(self.selection_start[0], self.selection_end[0]) / ratio)
            y1 = int(min(self.selection_start[1], self.selection_end[1]) / ratio)
            x2 = int(max(self.selection_start[0], self.selection_end[0]) / ratio)
            y2 = int(max(self.selection_start[1], self.selection_end[1]) / ratio)

            # Обрезаем координаты, если они выходят за границы изображения
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)

            # Проверяем, что область выделения валидна
            if x2 > x1 and y2 > y1:
                # Получаем выделенную область из исходного изображения
                selected_area = self.image[y1:y2, x1:x2]

                # Конвертируем в HSV и вычисляем среднее значение
                hsv_area = cv2.cvtColor(selected_area, cv2.COLOR_RGB2HSV)
                avg_hsv = np.mean(hsv_area, axis=(0, 1))

                # Форматируем вывод
                self.hsv_values.set(f"H: {avg_hsv[0]:.2f}, S: {avg_hsv[1]:.2f}, V: {avg_hsv[2]:.2f}")
            else:
                self.clear_selection()

    def redraw_image_with_selection(self):
        if self.image is None:
            return

        self.display_image = self.image.copy()

        # Масштабирование изображения для отображения
        h, w = self.display_image.shape[:2]
        ratio = min(800 / w, 600 / h)
        new_w, new_h = int(w * ratio), int(h * ratio)
        resized_img = cv2.resize(self.display_image, (new_w, new_h))

        # Рисуем прямоугольник выделения
        if self.selection_start and self.selection_end:
            x1, y1 = self.selection_start
            x2, y2 = self.selection_end
            cv2.rectangle(resized_img, (x1, y1), (x2, y2), (0, 255, 0), 2)

        img = Image.fromarray(resized_img)
        img = ImageTk.PhotoImage(image=img)

        # Сохраняем ссылку, чтобы избежать сборки мусора
        self.canvas.image = img
        self.canvas.create_image(0, 0, anchor=tk.NW, image=img)

    def clear_selection(self):
        self.selection_start = None
        self.selection_end = None
        self.selecting = False
        self.hsv_values.set("")

        if self.image is not None:
            self.display_image = self.image.copy()
            self.update_canvas()


if __name__ == "__main__":
    root = tk.Tk()
    app = HSVAreaSelector(root)
    root.mainloop()