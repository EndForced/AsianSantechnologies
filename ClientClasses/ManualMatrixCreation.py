import cv2
import numpy as np
from tkinter import *
from tkinter import messagebox, simpledialog, filedialog
import json
import os

class MatrixEditor:
    def __init__(self):
        # Initialize with default empty matrix
        self.matrix = []
        self.cell_size = 100
        self.selected_code = 10  # Default cell code
        self.available_codes = [
            10, 20, 31, 32, 33, 34, 41,42,51,52,61,62,63,64, 71  # Add all your possible codes here
        ]
        self.code_descriptions = {
            10: "1 floor",
            20: "2 floor",
            31: "ramp up",
            32: "ramp right",
            33: "ramp down",
            34: "ramp left",
            41: "tube horizon 1f",
            42: "tube vertical 1f",
            51: "tube horizon 2f",
            52: "tube vertical 2f",
            61: "place up",
            62: "place right",
            63: "place down",
            64: "place left",
            71: "Robot Start"
        }

        self.scale_x = 1.0  # Коэффициент масштабирования по X
        self.scale_y = 1.0  # Коэффициент масштабирования по Y

        # Path to images
        self.image_path = "field_pictures/"
        self.cell_images = {}  # Cache for cell images

        # Load cell images
        self.load_cell_images()

        # Create main window
        self.root = Tk()
        self.root.title("Matrix Editor")

        # Create controls frame
        self.controls_frame = Frame(self.root)
        self.controls_frame.pack(side=TOP, fill=X)

        # Dimension controls
        Label(self.controls_frame, text="Rows:").grid(row=0, column=0)
        self.rows_entry = Entry(self.controls_frame, width=5)
        self.rows_entry.grid(row=0, column=1)
        self.rows_entry.insert(0, "8")

        Label(self.controls_frame, text="Cols:").grid(row=0, column=2)
        self.cols_entry = Entry(self.controls_frame, width=5)
        self.cols_entry.grid(row=0, column=3)
        self.cols_entry.insert(0, "8")

        Button(self.controls_frame, text="Create Matrix", command=self.create_matrix).grid(row=0, column=4)

        # Cell type selection
        Label(self.controls_frame, text="Cell Type:").grid(row=0, column=5)
        self.cell_type_var = StringVar()
        self.cell_type_var.set("10 - Empty")
        self.cell_type_menu = OptionMenu(
            self.controls_frame,
            self.cell_type_var,
            *[f"{code} - {self.code_descriptions.get(code, 'Unknown')}" for code in self.available_codes]
        )
        self.cell_type_menu.grid(row=0, column=6)

        # File operations
        Button(self.controls_frame, text="Save", command=self.save_matrix).grid(row=0, column=7)
        Button(self.controls_frame, text="Load", command=self.load_matrix).grid(row=0, column=8)

        # Create canvas for matrix display
        self.canvas_frame = Frame(self.root)
        self.canvas_frame.pack(side=TOP, fill=BOTH, expand=True)

        self.canvas = Canvas(self.canvas_frame)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)

        # Scrollbars
        self.scroll_y = Scrollbar(self.canvas_frame, orient=VERTICAL, command=self.canvas.yview)
        self.scroll_y.pack(side=RIGHT, fill=Y)
        self.scroll_x = Scrollbar(self.root, orient=HORIZONTAL, command=self.canvas.xview)
        self.scroll_x.pack(side=BOTTOM, fill=X)

        self.canvas.configure(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)
        self.canvas.bind('<Configure>', self.on_canvas_configure)

        # Initialize with default matrix
        self.create_matrix()

        # Bind mouse events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)

        # Bind cell type selection change
        self.cell_type_var.trace("w", self.on_cell_type_change)
        self.root.state('zoomed')

    def smart_resize(self, image, target_size=600):
        if image is None:
            raise ValueError("Input image is None")

        h, w = image.shape[:2]

        if h <= target_size and w <= target_size:
            return image.copy()

        scale = min(target_size / w, target_size / h)
        new_w = int(w * scale)
        new_h = int(h * scale)

        return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

    def load_cell_images(self):
        """Load all cell images from field_pictures directory"""
        for code in self.available_codes:
            image_path = os.path.join(self.image_path, f"{code}.png")
            if os.path.exists(image_path):
                try:
                    img = cv2.imread(image_path)
                    if img is not None:
                        # Convert from BGR to RGB for correct color display
                        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        # Resize if needed
                        if img.shape[0] != self.cell_size or img.shape[1] != self.cell_size:
                            img = cv2.resize(img, (self.cell_size, self.cell_size))
                        self.cell_images[code] = img
                    else:
                        print(f"Failed to load image: {image_path}")
                        self.create_default_image(code)
                except Exception as e:
                    print(f"Error loading image {image_path}: {e}")
                    self.create_default_image(code)
            else:
                print(f"Image not found: {image_path}")
                self.create_default_image(code)

    def create_default_image(self, code):
        """Create a default image when the proper image is not found"""
        img = np.zeros((self.cell_size, self.cell_size, 3), dtype=np.uint8)

        # Fill with color based on code (note: we're using RGB order here)
        if code == 10:  # Empty
            color = (200, 200, 200)
        elif code == 20:  # Wall
            color = (100, 100, 100)
        elif code == 31:  # Ramp North
            color = (255, 150, 150)
        elif code == 32:  # Ramp East
            color = (150, 255, 150)
        elif code == 33:  # Ramp South
            color = (150, 150, 255)
        elif code == 34:  # Ramp West
            color = (255, 255, 150)
        elif code == 41:  # Elevator
            color = (255, 150, 255)
        elif code == 62:  # Pit
            color = (50, 50, 50)
        elif code == 71:  # Robot Start
            color = (150, 255, 255)
        else:  # Unknown
            color = (255, 255, 255)

        img[:, :] = color

        # Add code number
        cv2.putText(img, str(code),
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (0, 0, 0), 2)

        # Add border
        cv2.rectangle(img, (0, 0), (self.cell_size - 1, self.cell_size - 1), (0, 0, 0), 2)

        self.cell_images[code] = img

    def on_cell_type_change(self, *args):
        # Update selected code when dropdown changes
        selected = self.cell_type_var.get()
        self.selected_code = int(selected.split(" - ")[0])

    def create_matrix(self):
        try:
            rows = int(self.rows_entry.get())
            cols = int(self.cols_entry.get())

            if rows <= 0 or cols <= 0:
                raise ValueError("Dimensions must be positive")

            # Create empty matrix filled with default code (10)
            self.matrix = [[10 for _ in range(cols)] for _ in range(rows)]
            self.draw_matrix()

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid dimensions: {e}")

    def draw_matrix(self):
        self.canvas.delete("all")

        rows = len(self.matrix)
        if rows == 0:
            return

        cols = len(self.matrix[0])

        total_width = cols * self.cell_size
        total_height = rows * self.cell_size

        # Создаем оригинальное изображение (уже в RGB)
        original_image = np.zeros((total_height, total_width, 3), dtype=np.uint8)

        for i in range(rows):
            for j in range(cols):
                code = self.matrix[i][j]
                cell_img = self.cell_images.get(code, self.cell_images[10])
                y1, y2 = i * self.cell_size, (i + 1) * self.cell_size
                x1, x2 = j * self.cell_size, (j + 1) * self.cell_size
                original_image[y1:y2, x1:x2] = cell_img

        # Масштабируем изображение и сохраняем коэффициенты
        self.display_image = self.smart_resize(original_image)
        h, w = original_image.shape[:2]
        resized_h, resized_w = self.display_image.shape[:2]
        self.scale_x = w / resized_w
        self.scale_y = h / resized_h

        self.photo_image = self.np_to_photo(self.display_image)
        self.canvas.create_image(0, 0, anchor=NW, image=self.photo_image)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def np_to_photo(self, image):
        """Convert numpy array to PhotoImage (image is already in RGB format)"""
        # Convert to PIL Image format
        from PIL import Image, ImageTk
        pil_image = Image.fromarray(image)
        return ImageTk.PhotoImage(image=pil_image)

    def on_canvas_configure(self, event):
        """Handle canvas resize"""
        if hasattr(self, 'photo_image'):
            self.canvas.itemconfig("all", image=self.photo_image)

    def on_canvas_click(self, event):
        if not self.matrix:
            return

        # Корректируем координаты с учетом масштабирования
        x = int(event.x * self.scale_x)
        y = int(event.y * self.scale_y)

        col = x // self.cell_size
        row = y // self.cell_size

        if 0 <= row < len(self.matrix) and 0 <= col < len(self.matrix[0]):
            self.matrix[row][col] = self.selected_code
            self.draw_matrix()

    def on_canvas_drag(self, event):
        self.on_canvas_click(event)

    def save_matrix(self):
        """Save matrix to JSON file"""
        try:
            filename = simpledialog.askstring("Save Matrix", "Enter filename (without extension):")
            if not filename:
                return

            filename += ".json"

            with open(filename, 'w') as f:
                json.dump(self.matrix, f)

            messagebox.showinfo("Success", f"Matrix saved to {filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save matrix: {e}")

    def load_matrix(self):
        """Load matrix from JSON file"""
        try:
            filename = filedialog.askopenfilename(
                title="Select Matrix File",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )

            if not filename:
                return

            with open(filename, 'r') as f:
                self.matrix = json.load(f)

            # Update UI
            self.rows_entry.delete(0, END)
            self.rows_entry.insert(0, str(len(self.matrix)))

            self.cols_entry.delete(0, END)
            self.cols_entry.insert(0, str(len(self.matrix[0]) if self.matrix else "0"))

            self.draw_matrix()
            messagebox.showinfo("Success", f"Matrix loaded from {filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load matrix: {e}")

    def run(self):
        self.root.mainloop()


# Run the editor
if __name__ == "__main__":
    editor = MatrixEditor()
    editor.run()