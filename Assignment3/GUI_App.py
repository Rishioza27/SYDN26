import tkinter as tk
from PIL import Image
import cv2
import numpy as np


class ImageState:
    def __init__(self):
        self.currentImage = None
        self.filePath = None
        self.history = []
        self.future = []

    def loadImage(self, path):
        img = Image.open(path).convert("RGB")
        self.currentImage = img
        self.filePath = path
        self.history = [img.copy()]
        self.future = []

    def setImage(self, img):
        if self.currentImage:
            self.history.append(img.copy())
            self.future = []
        self.currentImage = img


class ImageProcessor:
    """
    Handles image processing using OpenCV.
    """

    @staticmethod
    def pilToCv(pilImg):
        return cv2.cvtColor(np.array(pilImg), cv2.COLOR_RGB2BGR)

    @staticmethod
    def cvToPil(cvImg):
        return Image.fromarray(cv2.cvtColor(cvImg, cv2.COLOR_BGR2RGB))

    @staticmethod
    def toGrayscale(pilImg):
        cvImg = ImageProcessor.pilToCv(pilImg)
        gray = cv2.cvtColor(cvImg, cv2.COLOR_BGR2GRAY)
        rgb = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        return ImageProcessor.cvToPil(rgb)

    @staticmethod
    def blur(pilImg, k):
        if k <= 0:
            return pilImg
        if k % 2 == 0:
            k += 1
        cvImg = ImageProcessor.pilToCv(pilImg)
        blurred = cv2.GaussianBlur(cvImg, (k, k), 0)
        return ImageProcessor.cvToPil(blurred)


class ImageEditorApp:
    def __init__(self, root):
        self.root = root
        root.title("Simple Image Editor")
        root.geometry("900x600")

        self.state = ImageState()
        tk.Label(root, text="Processing logic added").pack(pady=20)


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditorApp(root)
    root.mainloop()
