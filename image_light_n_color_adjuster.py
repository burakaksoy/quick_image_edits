import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageEnhance
import math

class PhotoEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simple Photo Editor")
        self.geometry("900x600")  # Adjust window size as needed
        
        # ===================== State Variables =====================
        self.img_path = None
        self.original_image = None  # Will hold the original PIL.Image
        self.preview_image = None   # Will hold the processed PIL.Image for preview
        self.tk_preview = None      # The ImageTk version to display
        
        # Output format (PNG or JPEG)
        self.format_var = tk.StringVar(value="PNG")  # default PNG
        
        # Sliders values: we store them as tkinter DoubleVars
        # Ranges are chosen somewhat arbitrarily for demonstration
        self.brightness_var = tk.DoubleVar(value=1.0)   # 0.0 to 2.0
        self.exposure_var   = tk.DoubleVar(value=1.0)   # 0.1 to 2.0 (gamma)
        self.contrast_var   = tk.DoubleVar(value=1.0)   # 0.0 to 2.0
        self.highlights_var = tk.DoubleVar(value=1.0)   # 0.5 to 1.5
        self.shadows_var    = tk.DoubleVar(value=1.0)   # 0.5 to 1.5
        self.saturation_var = tk.DoubleVar(value=1.0)   # 0.0 to 2.0 (ImageEnhance.Color)
        self.warmth_var     = tk.DoubleVar(value=0.0)   # -1.0 to 1.0
        self.tint_var       = tk.DoubleVar(value=0.0)   # -1.0 to 1.0
        self.sharpness_var  = tk.DoubleVar(value=1.0)   # 0.0 to 3.0 (for demonstration)

        # ===================== Layout Frames =====================
        # Left pane: controls
        control_frame = tk.Frame(self)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Right pane: preview
        preview_frame = tk.Frame(self, bd=2, relief=tk.SUNKEN)
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(preview_frame, bg="gray")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # ===================== Controls =====================
        # 1) Button to open an image
        open_btn = tk.Button(control_frame, text="Open Image", command=self.open_image)
        open_btn.pack(pady=3, fill=tk.X)

        # 2) Sliders for various adjustments
        # We'll create a helper function for each labeled Scale
        self.make_slider(control_frame, "Brightness", self.brightness_var,
                         from_=0.0, to=2.0, resolution=0.01)
        self.make_slider(control_frame, "Exposure (Gamma)", self.exposure_var,
                         from_=0.1, to=2.0, resolution=0.01)
        self.make_slider(control_frame, "Contrast", self.contrast_var,
                         from_=0.0, to=2.0, resolution=0.01)
        self.make_slider(control_frame, "Highlights", self.highlights_var,
                         from_=0.5, to=1.5, resolution=0.01)
        self.make_slider(control_frame, "Shadows", self.shadows_var,
                         from_=0.5, to=1.5, resolution=0.01)
        self.make_slider(control_frame, "Saturation", self.saturation_var,
                         from_=0.0, to=2.0, resolution=0.01)
        self.make_slider(control_frame, "Warmth", self.warmth_var,
                         from_=-1.0, to=1.0, resolution=0.01)
        self.make_slider(control_frame, "Tint", self.tint_var,
                         from_=-1.0, to=1.0, resolution=0.01)
        self.make_slider(control_frame, "Sharpness", self.sharpness_var,
                         from_=0.0, to=3.0, resolution=0.1)

        # Radio buttons for output format
        format_frame = tk.LabelFrame(control_frame, text="Save Format")
        format_frame.pack(pady=5, fill=tk.X)
        rb_png = tk.Radiobutton(format_frame, text="PNG", variable=self.format_var, value="PNG")
        rb_jpg = tk.Radiobutton(format_frame, text="JPG", variable=self.format_var, value="JPEG")
        rb_png.pack(anchor="w")
        rb_jpg.pack(anchor="w")
        
        # 3) Button to save
        save_btn = tk.Button(control_frame, text="Save Image", command=self.save_image)
        save_btn.pack(pady=3, fill=tk.X)

    def make_slider(self, parent, label_text, var, from_, to, resolution):
        """Helper to create a labeled Scale widget that calls update_preview on change."""
        frame = tk.Frame(parent)
        frame.pack(pady=2, fill=tk.X)
        
        label = tk.Label(frame, text=label_text)
        label.pack(anchor="w")

        scale = tk.Scale(frame, variable=var,
                         orient=tk.HORIZONTAL, from_=from_, to=to,
                         resolution=resolution,
                         command=lambda x: self.update_preview())  # update preview on drag
        scale.pack(fill=tk.X)
        # We intentionally re-run self.update_preview() each time slider changes

    def open_image(self):
        """Open an image file from disk."""
        path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.tiff;*.bmp;*.gif")]
        )
        if path:
            self.img_path = path
            try:
                self.original_image = Image.open(path).convert("RGB")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open image:\n{e}")
                return
            self.update_preview()

    def update_preview(self):
        """Apply all adjustments to the original image and show the result on the canvas."""
        if not self.original_image:
            return
        
        # Start with the original
        edited = self.original_image.copy()
        
        # 1) Brightness
        brightness_factor = self.brightness_var.get()
        if brightness_factor != 1.0:
            enhancer = ImageEnhance.Brightness(edited)
            edited = enhancer.enhance(brightness_factor)
        
        # 2) Exposure (Gamma Correction)
        # gamma < 1 => lighten midtones, gamma > 1 => darken midtones
        gamma = self.exposure_var.get()
        if abs(gamma - 1.0) > 0.001:
            edited = self.apply_gamma(edited, gamma)

        # 3) Contrast
        contrast_factor = self.contrast_var.get()
        if contrast_factor != 1.0:
            enhancer = ImageEnhance.Contrast(edited)
            edited = enhancer.enhance(contrast_factor)

        # 4) Highlights
        highlights_factor = self.highlights_var.get()
        if abs(highlights_factor - 1.0) > 0.001:
            edited = self.apply_highlights(edited, highlights_factor)

        # 5) Shadows
        shadows_factor = self.shadows_var.get()
        if abs(shadows_factor - 1.0) > 0.001:
            edited = self.apply_shadows(edited, shadows_factor)

        # 6) Saturation
        sat_factor = self.saturation_var.get()
        if sat_factor != 1.0:
            enhancer = ImageEnhance.Color(edited)
            edited = enhancer.enhance(sat_factor)

        # 7) Warmth
        warmth_factor = self.warmth_var.get()
        if abs(warmth_factor) > 0.001:
            edited = self.apply_warmth(edited, warmth_factor)

        # 8) Tint
        tint_factor = self.tint_var.get()
        if abs(tint_factor) > 0.001:
            edited = self.apply_tint(edited, tint_factor)

        # 9) Sharpness
        sharp_factor = self.sharpness_var.get()
        if sharp_factor != 1.0:
            enhancer = ImageEnhance.Sharpness(edited)
            edited = enhancer.enhance(sharp_factor)
        
        # Convert to ImageTk to display
        self.preview_image = edited
        self.display_image(self.preview_image)

    def display_image(self, pil_image):
        """Display the given PIL image on the canvas (resizing if needed)."""
        # Fit to the canvas size if needed
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        if canvas_w < 10 or canvas_h < 10:
            # The window might not be drawn yet, skip
            return
        
        # We'll do a simple fit if it's bigger than the canvas
        img_w, img_h = pil_image.size
        scale = min(canvas_w / img_w, canvas_h / img_h, 1.0)
        if scale < 1.0:
            new_w = int(img_w * scale)
            new_h = int(img_h * scale)
            display_img = pil_image.resize((new_w, new_h), Image.LANCZOS)
        else:
            display_img = pil_image
        
        self.tk_preview = ImageTk.PhotoImage(display_img)
        self.canvas.delete("all")
        # Center the image on the canvas
        cx = canvas_w // 2
        cy = canvas_h // 2
        self.canvas.create_image(cx, cy, image=self.tk_preview, anchor="center")

    # =============== Custom Adjustment Helpers ===============

    @staticmethod
    def apply_gamma(image, gamma):
        """Apply gamma correction to a PIL image. gamma < 1 => lighten, gamma > 1 => darken."""
        # Build a lookup table
        lut = []
        for i in range(256):
            # normalized value = i/255
            # gamma correction => out = (normalized**(1/gamma))*255
            v = int((i / 255.0) ** (1.0 / gamma) * 255.0)
            lut.append(v)
        return image.point(lut*3)  # for R, G, B

    @staticmethod
    def apply_highlights(image, factor):
        """
        Simplistic highlight compression/expansion:
        For bright pixels, push them toward or away from white.
        
        factor > 1 => we are brightening highlights
        factor < 1 => we are darkening highlights
        This is a naive approach using a 'curve'.
        """
        # Let "threshold" define what we consider "highlights." 
        # For a 0-255 range, let's say above ~180 is highlight.
        threshold = 180
        
        lut = []
        for i in range(256):
            if i < threshold:
                # below threshold, leave as is
                lut.append(i)
            else:
                # above threshold, move i toward white or toward threshold
                # new_i = threshold + (i - threshold)*factor
                # But let's clamp to 255
                new_i = threshold + (i - threshold) * factor
                new_i = max(0, min(255, new_i))
                lut.append(int(new_i))
        
        return image.point(lut*3)

    @staticmethod
    def apply_shadows(image, factor):
        """
        Simplistic shadow lift/crush:
        For dark pixels, push them up or down.
        
        factor > 1 => lighten shadows
        factor < 1 => darken shadows
        """
        # Let's define shadow range below 75
        threshold = 75
        
        lut = []
        for i in range(256):
            if i > threshold:
                # above threshold, leave as is
                lut.append(i)
            else:
                # below threshold, move i toward 0 or up
                # new_i = i * factor if factor < 1 => crush
                # or i + (threshold - i)*(factor-1) if factor>1 => lift
                # For simplicity:
                new_i = i * factor
                new_i = max(0, min(255, new_i))
                lut.append(int(new_i))
        
        return image.point(lut*3)

    @staticmethod
    def apply_warmth(image, factor):
        """
        Shift color balance to add more red/yellow or reduce them. 
        factor > 0 => warmer (slightly raise R, lower B)
        factor < 0 => cooler (lower R, raise B)
        This is an approximation.
        """
        # We'll do a direct pixel iteration. For speed, we could do .point,
        # but let's illustrate a simple approach. This can be slow for large images.
        # A factor ~ +1 means strong warmth, -1 means strong cool.
        # We'll clamp factor to about ±1 for demonstration.

        import numpy as np
        
        arr = np.array(image, dtype=np.float32)
        # arr.shape => (h, w, 3)
        
        # We'll do a simple approach:
        # R' = R + factor*X
        # B' = B - factor*X
        # where X is some portion of the original channel or a constant
        # Let's base it on the original average intensity:
        # Something small so as not to blow out the image.
        X = 30.0  # tweak as you like
        # If factor = 1 => add 30 to R channel, subtract 30 from B channel
        # If factor = -1 => subtract 30 from R channel, add 30 to B channel
        
        arr[..., 0] += factor * X    # R channel
        arr[..., 2] -= factor * X    # B channel
        
        # clamp
        arr = np.clip(arr, 0, 255)
        return Image.fromarray(arr.astype(np.uint8), mode="RGB")

    @staticmethod
    def apply_tint(image, factor):
        """
        Shift color balance to add green/magenta.
        factor > 0 => more green
        factor < 0 => more magenta
        Another naive approach.
        """
        import numpy as np
        
        arr = np.array(image, dtype=np.float32)
        
        X = 30.0
        # G' = G + factor*X
        # R'/B' = R/B - factor*(X/2) maybe, to shift color distinctly
        arr[..., 1] += factor * X   # G channel
        arr[..., 0] -= factor * (X/2)  # R
        arr[..., 2] -= factor * (X/2)  # B
        
        arr = np.clip(arr, 0, 255)
        return Image.fromarray(arr.astype(np.uint8), mode="RGB")

    def save_image(self):
        """Save the edited image to disk in the selected format (PNG or JPEG)."""
        if not self.preview_image:
            messagebox.showwarning("No Image", "Please open and adjust an image first.")
            return
        
        # Ask the user for a save location
        extension = ".png" if self.format_var.get() == "PNG" else ".jpg"
        filetypes = [("PNG File", "*.png")] if extension == ".png" else [("JPEG File", "*.jpg")]
        save_path = filedialog.asksaveasfilename(
            defaultextension=extension,
            filetypes=filetypes,
            title="Save Edited Image"
        )
        if not save_path:
            return  # user canceled
        
        try:
            # PIL wants "PNG" or "JPEG" as format
            self.preview_image.save(save_path, self.format_var.get())
            messagebox.showinfo("Success", f"Image saved as:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save image:\n{e}")

def main():
    app = PhotoEditor()
    app.mainloop()

if __name__ == "__main__":
    main()
