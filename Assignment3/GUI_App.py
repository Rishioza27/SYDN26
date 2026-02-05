import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np


class ImageState:
    def __init__(self):
        self.currentImage = None
        self.history = []

    def loadImage(self, path):
        img = Image.open(path).convert("RGB")
        self.currentImage = img
        self.history = [img.copy()]


class ImageEditorApp:
    def __init__(self, root):
        self.root = root
        root.title("Simple Image Editor")
        root.geometry("1000x700")

        self.state = ImageState()
        self.displayImg = None

        self.left = tk.Frame(root)
        self.left.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.canvas = tk.Canvas(self.left, bg="grey")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.right = tk.Frame(root, width=250)
        self.right.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Button(self.right, text="Open Image", command=self.openFile).pack(padx=10, pady=10)

    def openFile(self):
        path = filedialog.askopenfilename()
        if path:
            self.state.loadImage(path)
            self.showImage()

    def showImage(self):
        img = self.state.currentImage
        if not img:
            return
        disp = img.resize((600, 400))
        self.displayImg = ImageTk.PhotoImage(disp)
        self.canvas.create_image(300, 200, image=self.displayImg)


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditorApp(root)
    root.mainloop()
