import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os


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

    def undo(self):
        if len(self.history) > 1:
            last = self.history.pop()
            self.future.append(last)
            self.currentImage = self.history[-1].copy()
            return True
        return False

    def redo(self):
        if self.future:
            img = self.future.pop()
            self.history.append(img)
            self.currentImage = img.copy()
            return True
        return False


class ImageEditorApp:
    def __init__(self, root):
        self.root = root
        root.title("Simple Image Editor")

        self.state = ImageState()
        self.status = tk.Label(root, text="No image loaded", anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

        tk.Button(root, text="Open", command=self.openFile).pack()
        tk.Button(root, text="Undo", command=self.undo).pack()
        tk.Button(root, text="Redo", command=self.redo).pack()

    def openFile(self):
        path = filedialog.askopenfilename()
        if not path:
            return
        try:
            self.state.loadImage(path)
            self.status.config(text=os.path.basename(path))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def undo(self):
        if self.state.undo():
            self.status.config(text="Undo")
        else:
            messagebox.showinfo("Undo", "Nothing to undo")

    def redo(self):
        if self.state.redo():
            self.status.config(text="Redo")
        else:
            messagebox.showinfo("Redo", "Nothing to redo")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditorApp(root)
    root.mainloop()
