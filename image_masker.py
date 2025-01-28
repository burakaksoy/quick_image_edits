import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np

class ColorMaskGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("HSV Color Masking")

        # Full-resolution original image (BGR)
        self.original_img = None

        # Full-resolution final masked image (BGR, with white background)
        self.final_masked_img = None

        # A boolean mask indicating which pixels the user wants to remove (erase).
        # Same resolution as original_img, 1-channel.
        # True means "remove" => turned white in final.
        self.user_removed_mask = None

        # For displaying (zooming on the canvas)
        self.tk_img = None            # The Tkinter image (scaled) for display
        self.scale_factor = 1.0       # How much we are zooming on the canvas

        # HSV threshold trackbar variables
        self.h_min = tk.IntVar(value=0)
        self.s_min = tk.IntVar(value=0)
        self.v_min = tk.IntVar(value=0)
        self.h_max = tk.IntVar(value=179)
        self.s_max = tk.IntVar(value=255)
        self.v_max = tk.IntVar(value=255)

        # GUI Layout ------------------------------------------------------------
        # Frame for buttons
        btn_frame = tk.Frame(self.master)
        btn_frame.pack(pady=5)

        self.open_btn = tk.Button(btn_frame, text="Open Image", command=self.open_image)
        self.open_btn.grid(row=0, column=0, padx=5)

        self.save_btn = tk.Button(btn_frame, text="Save Masked Image", 
                                  command=self.save_image, state=tk.DISABLED)
        self.save_btn.grid(row=0, column=1, padx=5)

        # Frame for sliders
        sliders_frame = tk.LabelFrame(self.master, text="HSV Thresholds")
        sliders_frame.pack(padx=5, pady=5, fill="x")

        # Row 0: HMin and HMax
        tk.Label(sliders_frame, text="HMin").grid(row=0, column=0, padx=5, pady=2)
        tk.Scale(sliders_frame, from_=0, to=179, orient=tk.HORIZONTAL, variable=self.h_min,
                 command=lambda x: self.update_image()).grid(row=0, column=1, sticky="we")

        tk.Label(sliders_frame, text="HMax").grid(row=0, column=2, padx=5, pady=2)
        tk.Scale(sliders_frame, from_=0, to=179, orient=tk.HORIZONTAL, variable=self.h_max,
                 command=lambda x: self.update_image()).grid(row=0, column=3, sticky="we")

        # Row 1: SMin and SMax
        tk.Label(sliders_frame, text="SMin").grid(row=1, column=0, padx=5, pady=2)
        tk.Scale(sliders_frame, from_=0, to=255, orient=tk.HORIZONTAL, variable=self.s_min,
                 command=lambda x: self.update_image()).grid(row=1, column=1, sticky="we")

        tk.Label(sliders_frame, text="SMax").grid(row=1, column=2, padx=5, pady=2)
        tk.Scale(sliders_frame, from_=0, to=255, orient=tk.HORIZONTAL, variable=self.s_max,
                 command=lambda x: self.update_image()).grid(row=1, column=3, sticky="we")

        # Row 2: VMin and VMax
        tk.Label(sliders_frame, text="VMin").grid(row=2, column=0, padx=5, pady=2)
        tk.Scale(sliders_frame, from_=0, to=255, orient=tk.HORIZONTAL, variable=self.v_min,
                 command=lambda x: self.update_image()).grid(row=2, column=1, sticky="we")

        tk.Label(sliders_frame, text="VMax").grid(row=2, column=2, padx=5, pady=2)
        tk.Scale(sliders_frame, from_=0, to=255, orient=tk.HORIZONTAL, variable=self.v_max,
                 command=lambda x: self.update_image()).grid(row=2, column=3, sticky="we")

        for i in range(4):
            sliders_frame.columnconfigure(i, weight=1)

        # Canvas to display the image
        self.canvas = tk.Canvas(self.master, bg="gray", width=640, height=480)
        self.canvas.pack(padx=5, pady=5)

        # Mouse bindings
        self.canvas.bind("<Button-1>", self.on_left_click)      # Pick HSV
        self.canvas.bind("<Button-3>", self.on_right_click)     # Erase undesired pixel area
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)   # Zoom with CTRL + wheel

    def open_image(self):
        """
        Let user pick an image using file dialog (full resolution).
        """
        file_types = [("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff"),
                      ("All Files", "*.*")]
        filename = filedialog.askopenfilename(title="Select an image", filetypes=file_types)
        if filename:
            self.original_img = cv2.imread(filename)  # BGR, full resolution
            if self.original_img is None:
                return

            # Initialize the user_removed_mask to same shape (single channel)
            h, w = self.original_img.shape[:2]
            self.user_removed_mask = np.zeros((h, w), dtype=bool)

            # Reset zoom
            self.scale_factor = 1.0
            # Enable saving
            self.save_btn.config(state=tk.NORMAL)

            # Apply initial threshold + display
            self.update_image()

    def save_image(self):
        """
        Save the *full-resolution* final masked image to disk.
        """
        if self.final_masked_img is None:
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        if save_path:
            cv2.imwrite(save_path, self.final_masked_img)
            print(f"Saved masked image to: {save_path}")

    def update_image(self):
        """
        1) Compute the color mask on the *full-resolution* image based on slider HSV.
        2) Apply user_removed_mask (erase) on top of that mask.
        3) Generate a final masked image with white background.
        4) Update the canvas display with a scaled version.
        """
        if self.original_img is None:
            return

        # Current HSV thresholds
        h_min = self.h_min.get()
        s_min = self.s_min.get()
        v_min = self.v_min.get()
        h_max = self.h_max.get()
        s_max = self.s_max.get()
        v_max = self.v_max.get()

        # Convert to HSV (full resolution)
        hsv = cv2.cvtColor(self.original_img, cv2.COLOR_BGR2HSV)

        # Create the mask
        lower = np.array([h_min, s_min, v_min], dtype=np.uint8)
        upper = np.array([h_max, s_max, v_max], dtype=np.uint8)
        color_mask = cv2.inRange(hsv, lower, upper)

        # Combine with user_removed_mask (any pixel the user erased is forced to 0)
        # user_removed_mask is boolean => convert to uint8 for bitwise
        user_removed_mask_uint8 = self.user_removed_mask.astype(np.uint8)
        # final_mask = color_mask & ~ (user_removed_mask_uint8)
        # But we need to invert user_removed_mask_uint8: 1 => remove, 0 => keep
        inverted_removed = cv2.bitwise_not(user_removed_mask_uint8)  # 1 => keep, 0 => remove
        final_mask = cv2.bitwise_and(color_mask, inverted_removed)

        # The masked image (BGR)
        masked_img = cv2.bitwise_and(self.original_img, self.original_img, mask=final_mask)

        # Convert any pixel not in mask to white
        white_bg = np.ones_like(self.original_img, dtype=np.uint8) * 255
        self.final_masked_img = np.where(masked_img == 0, white_bg, masked_img)

        # Show scaled version on the canvas
        self.show_on_canvas()

        # Print HSV range
        print(f"(hMin = {h_min}, sMin = {s_min}, vMin = {v_min}), "
              f"(hMax = {h_max}, sMax = {s_max}, vMax = {v_max})")

    def show_on_canvas(self):
        """
        Scale self.final_masked_img according to self.scale_factor, then display on the canvas.
        """
        if self.final_masked_img is None:
            return

        h, w = self.final_masked_img.shape[:2]
        new_w = int(w * self.scale_factor)
        new_h = int(h * self.scale_factor)

        if new_w < 1 or new_h < 1:
            return  # Avoid degenerate scaling

        # Resize the full-res final_masked_img for display
        resized_bgr = cv2.resize(self.final_masked_img, (new_w, new_h), interpolation=cv2.INTER_AREA)

        # Convert BGR -> RGB for PIL
        display_rgb = cv2.cvtColor(resized_bgr, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(display_rgb)
        self.tk_img = ImageTk.PhotoImage(image=pil_img)

        # Resize the canvas to match new display size (optional)
        self.canvas.config(width=new_w, height=new_h)
        # Clear old items
        self.canvas.delete("all")
        # Draw
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)

    def on_left_click(self, event):
        """
        Left-click => pick HSV from the clicked pixel in final_masked_img.
        We will re-threshold around the pixel's HSV (± some margin).
        """
        if self.final_masked_img is None:
            return

        # Map canvas coords back to original-image coords
        x_in_img = int(event.x / self.scale_factor)
        y_in_img = int(event.y / self.scale_factor)

        H, W = self.final_masked_img.shape[:2]
        if x_in_img < 0 or x_in_img >= W or y_in_img < 0 or y_in_img >= H:
            return  # click out of bounds

        # final_masked_img is BGR. Let's get that pixel
        b, g, r = self.final_masked_img[y_in_img, x_in_img]
        pixel_bgr = np.array([[[b, g, r]]], dtype=np.uint8)
        pixel_hsv = cv2.cvtColor(pixel_bgr, cv2.COLOR_BGR2HSV)[0][0]
        h_val, s_val, v_val = pixel_hsv

        # We pick a small range around that pixel's HSV
        dh, ds, dv = 10, 25, 25  # margins
        h_min = max(h_val - dh, 0)
        h_max = min(h_val + dh, 179)
        s_min = max(s_val - ds, 0)
        s_max = min(s_val + ds, 255)
        v_min = max(v_val - dv, 0)
        v_max = min(v_val + dv, 255)

        # Update the sliders
        self.h_min.set(h_min)
        self.h_max.set(h_max)
        self.s_min.set(s_min)
        self.s_max.set(s_max)
        self.v_min.set(v_min)
        self.v_max.set(v_max)

        # Re-apply masking with new ranges
        self.update_image()

    def on_right_click(self, event):
        """
        Right-click => erase (remove) a small region around the clicked pixel
        in the user_removed_mask. This forces the final image to show white in that region.
        """
        if self.final_masked_img is None:
            return

        # Map canvas coords back to original-image coords
        x_in_img = int(event.x / self.scale_factor)
        y_in_img = int(event.y / self.scale_factor)

        H, W = self.user_removed_mask.shape
        if x_in_img < 0 or x_in_img >= W or y_in_img < 0 or y_in_img >= H:
            return  # Out of bounds

        # Erase a small circle (radius = 5)
        erase_radius = 5
        # Draw into user_removed_mask (boolean) => True means "remove"
        # Using OpenCV circle for convenience
        # Convert mask to uint8 for cv2.circle, then convert back
        tmp_mask = (self.user_removed_mask * 255).astype(np.uint8)
        cv2.circle(tmp_mask, (x_in_img, y_in_img), erase_radius, 255, -1)
        self.user_removed_mask = (tmp_mask > 0)

        # Re-apply the mask
        self.update_image()

    def on_mouse_wheel(self, event):
        """
        Zoom in/out with CTRL + mouse wheel (Windows).
        """
        # On Windows, state & 0x0004 indicates CTRL pressed.
        is_ctrl_pressed = (event.state & 0x0004) != 0

        if is_ctrl_pressed:
            if event.delta > 0:  # scroll up
                self.scale_factor *= 1.1
            else:               # scroll down
                self.scale_factor *= 0.9

            # Clamp to a sensible range
            self.scale_factor = max(min(self.scale_factor, 10.0), 0.1)
            self.show_on_canvas()


def main():
    root = tk.Tk()
    app = ColorMaskGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
