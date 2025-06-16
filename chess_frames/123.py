import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import pyperclip


class PolygonDrawer:
    def __init__(self, root):
        self.root = root
        self.root.title("Polygon Selector")

        # Переменные
        self.image_path = ""
        self.points = []
        self.drawing = False
        self.current_point = None
        self.image = None
        self.display_image = None

        # Создание интерфейса
        self.create_widgets()

    def create_widgets(self):
        # Фрейм для изображения
        self.image_frame = tk.Frame(self.root)
        self.image_frame.pack(side=tk.TOP, padx=5, pady=5)

        # Canvas для отображения изображения
        self.canvas = tk.Canvas(self.image_frame, width=800, height=600, cursor="cross")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.mouse_click)
        self.canvas.bind("<Motion>", self.mouse_move)
        self.canvas.bind("<Button-3>", self.finish_polygon)

        # Фрейм для кнопок
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(side=tk.BOTTOM, padx=5, pady=5)

        # Кнопки
        self.load_button = tk.Button(self.button_frame, text="Load Image", command=self.load_image)
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = tk.Button(self.button_frame, text="Clear", command=self.clear_polygon)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        self.copy_button = tk.Button(self.button_frame, text="Copy Coords", command=self.copy_coordinates)
        self.copy_button.pack(side=tk.LEFT, padx=5)

        self.exit_button = tk.Button(self.button_frame, text="Exit", command=self.root.quit)
        self.exit_button.pack(side=tk.RIGHT, padx=5)

    def load_image(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
        if self.image_path:
            self.image = cv2.imread(self.image_path)
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            self.display_image = self.image.copy()
            self.points = []
            self.update_canvas()

    def update_canvas(self):
        if self.display_image is not None:
            img = Image.fromarray(self.display_image)
            img = ImageTk.PhotoImage(image=img)

            # Сохраняем ссылку, чтобы избежать сборки мусора
            self.canvas.image = img
            self.canvas.create_image(0, 0, anchor=tk.NW, image=img)

    def mouse_click(self, event):
        if self.image is None:
            return

        x, y = event.x, event.y
        self.points.append((x, y))
        self.drawing = True
        self.redraw_polygon()

    def mouse_move(self, event):
        if not self.drawing or self.image is None:
            return

        self.current_point = (event.x, event.y)
        self.redraw_polygon()

    def redraw_polygon(self):
        if self.image is None:
            return

        self.display_image = self.image.copy()

        # Рисуем все точки
        for point in self.points:
            cv2.circle(self.display_image, point, 5, (255, 0, 0), -1)

        # Рисуем линии между точками
        if len(self.points) > 1:
            for i in range(1, len(self.points)):
                cv2.line(self.display_image, self.points[i - 1], self.points[i], (0, 255, 0), 2)

        # Рисуем линию от последней точки к текущей позиции мыши
        if self.drawing and self.current_point and len(self.points) > 0:
            cv2.line(self.display_image, self.points[-1], self.current_point, (0, 255, 0), 2)
            cv2.circle(self.display_image, self.current_point, 5, (0, 0, 255), -1)

        self.update_canvas()

    def finish_polygon(self, event):
        if len(self.points) < 3:
            messagebox.showwarning("Warning", "Polygon must have at least 3 points")
            return

        self.drawing = False
        self.current_point = None

        # Замыкаем многоугольник
        self.display_image = self.image.copy()
        cv2.polylines(self.display_image, [np.array(self.points)], True, (0, 255, 0), 2)
        for point in self.points:
            cv2.circle(self.display_image, point, 5, (255, 0, 0), -1)

        self.update_canvas()

        # Заполняем многоугольник (полупрозрачный)
        mask = np.zeros_like(self.display_image)
        cv2.fillPoly(mask, [np.array(self.points)], (0, 255, 0, 125))
        self.display_image = cv2.addWeighted(self.display_image, 1.0, mask, 0.3, 0)
        self.update_canvas()

    def clear_polygon(self):
        self.points = []
        self.drawing = False
        self.current_point = None
        if self.image is not None:
            self.display_image = self.image.copy()
            self.update_canvas()

    def copy_coordinates(self):
        if len(self.points) < 3:
            messagebox.showwarning("Warning", "No polygon to copy")
            return

        coords_str = "[" + ", ".join([f"({x}, {y})" for x, y in self.points]) + "]"
        pyperclip.copy(coords_str)
        messagebox.showinfo("Info", "Coordinates copied to clipboard")


if __name__ == "__main__":
    root = tk.Tk()
    app = PolygonDrawer(root)
    root.mainloop()