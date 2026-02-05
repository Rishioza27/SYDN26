import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import cv2
import numpy as np
import os
 
# small state holder
 
class ImageState:
    def __init__(self):
        self.currentImage = None   # PIL Image
        self.filePath = None
        self.history = []          # undo stack (PIL images)
        self.future = []           # redo stack
        self.maxHistory = 20

    def loadImage(self, path):
        img = Image.open(path).convert("RGB")
        self.currentImage = img
        self.filePath = path
        self.history = [img.copy()]
        self.future = []

    def setImage(self, pilImg):
        if self.currentImage is not None:
            self.history.append(pilImg.copy())
            if len(self.history) > self.maxHistory:
                self.history.pop(0)
            self.future = []
        else:
            self.history = [pilImg.copy()]
        self.currentImage = pilImg

    def canUndo(self):
        return len(self.history) > 1

    def undo(self):
        if self.canUndo():
            last = self.history.pop()
            self.future.append(last)
            self.currentImage = self.history[-1].copy()
            return True
        return False

    def canRedo(self):
        return len(self.future) > 0

    def redo(self):
        if self.canRedo():
            nxt = self.future.pop()
            self.history.append(nxt.copy())
            self.currentImage = nxt.copy()
            return True
        return False

    def getCurrentImage(self):
        return self.currentImage

    def clear(self):
        self.currentImage = None
        self.filePath = None
        self.history = []
        self.future = []


# 
# small processing helpers

class ImageProcessor:
    @staticmethod
    def pilToCv(pilImg):
        arr = np.array(pilImg)
        return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

    @staticmethod
    def cvToPil(cvImg):
        rgb = cv2.cvtColor(cvImg, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb)

    @staticmethod
    def toGrayscale(pilImg):
        cvImg = ImageProcessor.pilToCv(pilImg)
        gray = cv2.cvtColor(cvImg, cv2.COLOR_BGR2GRAY)
        rgb = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        return ImageProcessor.cvToPil(rgb)

    @staticmethod
    def blur(pilImg, ksize):
        try:
            k = int(ksize)
        except Exception:
            k = 1
        if k <= 0:
            return pilImg
        if k % 2 == 0:
            k += 1
        k = min(k, 31)  # avoid huge kernel
        cvImg = ImageProcessor.pilToCv(pilImg)
        blurred = cv2.GaussianBlur(cvImg, (k, k), 0)
        return ImageProcessor.cvToPil(blurred)

    @staticmethod
    def cannyEdges(pilImg, low=100, high=200):
        cvImg = ImageProcessor.pilToCv(pilImg)
        gray = cv2.cvtColor(cvImg, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, low, high)
        rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        return ImageProcessor.cvToPil(rgb)

    @staticmethod
    def adjustBrightnessContrast(pilImg, brightness=0, contrast=1.0):
        # keep simple clamping
        b = max(-200, min(200, int(brightness)))
        c = max(0.2, min(3.0, float(contrast)))
        cvImg = ImageProcessor.pilToCv(pilImg).astype(np.float32)
        out = cvImg * c + b
        out = np.clip(out, 0, 255).astype(np.uint8)
        return ImageProcessor.cvToPil(out)

    @staticmethod
    def rotate(pilImg, deg):
        if deg % 360 == 0:
            return pilImg
        return pilImg.rotate(deg, expand=True)

    @staticmethod
    def flipHorizontal(pilImg):
        return pilImg.transpose(Image.FLIP_LEFT_RIGHT)

    @staticmethod
    def flipVertical(pilImg):
        return pilImg.transpose(Image.FLIP_TOP_BOTTOM)

    @staticmethod
    def resize(pilImg, newW, newH):
        try:
            w = int(newW); h = int(newH)
        except Exception:
            return pilImg
        if w <= 0 or h <= 0:
            return pilImg
        # protect from absurd values
        w = min(w, 10000); h = min(h, 10000)
        return pilImg.resize((w, h))


# main GUI
 
class ImageEditorApp:
    def __init__(self, root):
        self.root = root
        root.title("Simple Image Editor")
        root.geometry("1000x700")

        self.state = ImageState()
        self.displayImageTk = None

        self.setMenu()
        self.setMainArea()
        self.setControls()
        self.setStatusBar()

    def setMenu(self):
        menubar = tk.Menu(self.root)
        fileMenu = tk.Menu(menubar, tearoff=0)
        fileMenu.add_command(label="Open", command=self.openFile)
        fileMenu.add_command(label="Save", command=self.saveFile)
        fileMenu.add_command(label="Save As...", command=self.saveAsFile)
        fileMenu.add_separator()
        fileMenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=fileMenu)

        editMenu = tk.Menu(menubar, tearoff=0)
        editMenu.add_command(label="Undo", command=self.doUndo)
        editMenu.add_command(label="Redo", command=self.doRedo)
        menubar.add_cascade(label="Edit", menu=editMenu)

        self.root.config(menu=menubar)

    def setMainArea(self):
        left = tk.Frame(self.root, width=700, height=600)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(left, bg="grey")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda e: self.updateDisplay())

    def setControls(self):
        right = tk.Frame(self.root, width=280)
        right.pack(side=tk.RIGHT, fill=tk.Y)

        # grayscale
        tk.Button(right, text="Grayscale", command=self.applyGrayscale).pack(fill=tk.X, padx=8, pady=4)

        # blur controls
        tk.Label(right, text="Blur (odd kernel)").pack(anchor="w", padx=8)
        self.blurScale = tk.Scale(right, from_=0, to=31, orient=tk.HORIZONTAL)
        self.blurScale.set(1)
        self.blurScale.pack(fill=tk.X, padx=8)
        tk.Button(right, text="Apply Blur", command=self.applyBlur).pack(fill=tk.X, padx=8, pady=4)

        # edges
        tk.Button(right, text="Edges (Canny)", command=self.applyEdges).pack(fill=tk.X, padx=8, pady=4)

        # brightness/contrast
        tk.Label(right, text="Brightness (-200..200)").pack(anchor="w", padx=8)
        self.brightScale = tk.Scale(right, from_=-200, to=200, orient=tk.HORIZONTAL)
        self.brightScale.set(0)
        self.brightScale.pack(fill=tk.X, padx=8)

        tk.Label(right, text="Contrast (50..300%)").pack(anchor="w", padx=8)
        self.contrastScale = tk.Scale(right, from_=50, to=300, orient=tk.HORIZONTAL)
        self.contrastScale.set(100)
        self.contrastScale.pack(fill=tk.X, padx=8)

        tk.Button(right, text="Apply Bright/Contrast", command=self.applyBrightContrast).pack(fill=tk.X, padx=8, pady=4)

        # rotate
        tk.Label(right, text="Rotate").pack(anchor="w", padx=8)
        rotFrame = tk.Frame(right)
        rotFrame.pack(fill=tk.X, padx=8)
        tk.Button(rotFrame, text="90", command=lambda: self.applyRotate(90)).pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Button(rotFrame, text="180", command=lambda: self.applyRotate(180)).pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Button(rotFrame, text="270", command=lambda: self.applyRotate(270)).pack(side=tk.LEFT, expand=True, fill=tk.X)

        # flip
        tk.Label(right, text="Flip").pack(anchor="w", padx=8)
        flipFrame = tk.Frame(right)
        flipFrame.pack(fill=tk.X, padx=8)
        tk.Button(flipFrame, text="Horizontal", command=self.applyFlipH).pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Button(flipFrame, text="Vertical", command=self.applyFlipV).pack(side=tk.LEFT, expand=True, fill=tk.X)

        # resize
        tk.Button(right, text="Resize", command=self.applyResize).pack(fill=tk.X, padx=8, pady=6)

        # undo/redo quick
        tk.Button(right, text="Undo", command=self.doUndo).pack(fill=tk.X, padx=8, pady=4)
        tk.Button(right, text="Redo", command=self.doRedo).pack(fill=tk.X, padx=8)

    def setStatusBar(self):
        self.status = tk.Label(self.root, text="No image loaded", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    #  file ops 
    def openFile(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp"), ("All files", "*.*")])
        if not path:
            return
        # simple check
        ext = os.path.splitext(path)[1].lower()
        if ext not in [".jpg", ".jpeg", ".png", ".bmp"]:
            messagebox.showwarning("Warning", "File may not be a supported image type.")
        try:
            self.state.loadImage(path)
            self.updateDisplay()
            self.setStatus()
        except Exception as e:
            messagebox.showerror("Open Error", f"Could not open file:\n{e}")

    def saveFile(self):
        img = self.state.getCurrentImage()
        if img is None:
            messagebox.showinfo("No image", "No image to save.")
            return
        path = self.state.filePath
        if not path:
            self.saveAsFile()
            return
        try:
            img.save(path)
            messagebox.showinfo("Saved", f"Saved to {path}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def saveAsFile(self):
        img = self.state.getCurrentImage()
        if img is None:
            messagebox.showinfo("No image", "No image to save.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".png",
                                            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg *.jpeg"), ("BMP", "*.bmp")])
        if not path:
            return
        try:
            img.save(path)
            self.state.filePath = path
            messagebox.showinfo("Saved", f"Saved to {path}")
            self.setStatus()
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    #  actions 
    def applyGrayscale(self):
        img = self.state.getCurrentImage()
        if img is None:
            messagebox.showinfo("No image", "Open an image first.")
            return
        newImg = ImageProcessor.toGrayscale(img)
        self.state.setImage(newImg)
        self.updateDisplay()
        self.setStatus()

    def applyBlur(self):
        img = self.state.getCurrentImage()
        k = self.blurScale.get()
        if img is None:
            messagebox.showinfo("No image", "Open an image first.")
            return
        newImg = ImageProcessor.blur(img, k)
        self.state.setImage(newImg)
        self.updateDisplay()
        self.setStatus()

    def applyEdges(self):
        img = self.state.getCurrentImage()
        if img is None:
            messagebox.showinfo("No image", "Open an image first.")
            return
        newImg = ImageProcessor.cannyEdges(img)
        self.state.setImage(newImg)
        self.updateDisplay()
        self.setStatus()

    def applyBrightContrast(self):
        img = self.state.getCurrentImage()
        if img is None:
            messagebox.showinfo("No image", "Open an image first.")
            return
        b = self.brightScale.get()
        c = self.contrastScale.get() / 100.0
        newImg = ImageProcessor.adjustBrightnessContrast(img, brightness=b, contrast=c)
        self.state.setImage(newImg)
        self.updateDisplay()
        self.setStatus()

    def applyRotate(self, deg):
        img = self.state.getCurrentImage()
        if img is None:
            messagebox.showinfo("No image", "Open an image first.")
            return
        newImg = ImageProcessor.rotate(img, deg)
        self.state.setImage(newImg)
        self.updateDisplay()
        self.setStatus()

    def applyFlipH(self):
        img = self.state.getCurrentImage()
        if img is None:
            messagebox.showinfo("No image", "Open an image first.")
            return
        newImg = ImageProcessor.flipHorizontal(img)
        self.state.setImage(newImg)
        self.updateDisplay()
        self.setStatus()

    def applyFlipV(self):
        img = self.state.getCurrentImage()
        if img is None:
            messagebox.showinfo("No image", "Open an image first.")
            return
        newImg = ImageProcessor.flipVertical(img)
        self.state.setImage(newImg)
        self.updateDisplay()
        self.setStatus()

    def applyResize(self):
        img = self.state.getCurrentImage()
        if img is None:
            messagebox.showinfo("No image", "Open an image first.")
            return
        w = simpledialog.askinteger("Width", "Enter new width (pixels)", initialvalue=img.width)
        if w is None:
            return
        h = simpledialog.askinteger("Height", "Enter new height (pixels)", initialvalue=img.height)
        if h is None:
            return
        newImg = ImageProcessor.resize(img, w, h)
        self.state.setImage(newImg)
        self.updateDisplay()
        self.setStatus()

    #  undo/redo 
    def doUndo(self):
        if self.state.undo():
            self.updateDisplay()
            self.setStatus()
        else:
            messagebox.showinfo("Undo", "Nothing to undo.")

    def doRedo(self):
        if self.state.redo():
            self.updateDisplay()
            self.setStatus()
        else:
            messagebox.showinfo("Redo", "Nothing to redo.")

    #  display 
    def updateDisplay(self):
        img = self.state.getCurrentImage()
        if img is None:
            self.canvas.delete("all")
            return
        canvasW = self.canvas.winfo_width() or 700
        canvasH = self.canvas.winfo_height() or 600
        imgW, imgH = img.size
        scale = min(canvasW / imgW, canvasH / imgH, 1.0)
        displaySize = (int(imgW * scale), int(imgH * scale))
        disp = img.resize(displaySize, Image.LANCZOS)
        self.displayImageTk = ImageTk.PhotoImage(disp)
        self.canvas.delete("all")
        self.canvas.create_image(canvasW//2, canvasH//2, image=self.displayImageTk, anchor=tk.CENTER)

    def setStatus(self):
        img = self.state.getCurrentImage()
        if img is None:
            self.status.config(text="No image loaded")
            return
        name = os.path.basename(self.state.filePath) if self.state.filePath else "Untitled"
        self.status.config(text=f"{name} — {img.width}x{img.height} px")


# run
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditorApp(root)
    root.mainloop()