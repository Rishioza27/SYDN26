import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

class ImageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Viewer")

        self.canvas = tk.Canvas(root, bg="grey")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        menu = tk.Menu(root)
        fileMenu = tk.Menu(menu, tearoff=0)
        fileMenu.add_command(label="Open", command=self.openImage)
        menu.add_cascade(label="File", menu=fileMenu)
        root.config(menu=menu)

        self.imgTk = None

    def openImage(self):
        path = filedialog.askopenfilename()
        if path:
            img = Image.open(path)
            self.imgTk = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, image=self.imgTk, anchor=tk.NW)

root = tk.Tk()
app = ImageApp(root)
root.mainloop()
