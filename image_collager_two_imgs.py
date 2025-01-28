import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image

class TwoImageCollageApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Two-Image Collage Maker")
        self.geometry("300x300")

        # ========== Variables ==========

        # Paths to the two selected images
        self.img1_path = None
        self.img2_path = None

        # Layout: "horizontal" (side by side) or "vertical" (top to bottom)
        self.layout_var = tk.StringVar(value="horizontal")

        # Spacing (in pixels) between the two images
        self.spacing_var = tk.IntVar(value=0)  # default is 0

        # Output format: "PNG" or "JPEG"
        self.format_var = tk.StringVar(value="PNG")  # default is PNG

        # ========== Widgets ==========

        # 1. Buttons to select images
        self.select_img1_btn = tk.Button(self, text="Select First Image", command=self.select_first_image)
        self.select_img1_btn.pack(pady=(10, 5))

        self.select_img2_btn = tk.Button(self, text="Select Second Image", command=self.select_second_image)
        self.select_img2_btn.pack(pady=5)

        # 2. Radio buttons for layout
        layout_frame = tk.LabelFrame(self, text="Layout")
        layout_frame.pack(pady=5, fill="x", padx=20)

        self.horizontal_rb = tk.Radiobutton(
            layout_frame, text="Side by Side",
            variable=self.layout_var, value="horizontal"
        )
        self.vertical_rb = tk.Radiobutton(
            layout_frame, text="Top to Bottom",
            variable=self.layout_var, value="vertical"
        )
        self.horizontal_rb.pack(anchor="w")
        self.vertical_rb.pack(anchor="w")

        # 3. Entry (Spinbox) for spacing
        spacing_frame = tk.LabelFrame(self, text="Spacing (px)")
        spacing_frame.pack(pady=5, fill="x", padx=20)
        
        self.spacing_entry = tk.Spinbox(
            spacing_frame, from_=0, to=9999,
            textvariable=self.spacing_var, width=5
        )
        self.spacing_entry.pack(pady=5)

        # 4. Radio buttons for save format
        format_frame = tk.LabelFrame(self, text="Save Format")
        format_frame.pack(pady=5, fill="x", padx=20)

        self.png_rb = tk.Radiobutton(
            format_frame, text="PNG",
            variable=self.format_var, value="PNG"
        )
        self.jpg_rb = tk.Radiobutton(
            format_frame, text="JPG",
            variable=self.format_var, value="JPEG"
        )
        self.png_rb.pack(anchor="w")
        self.jpg_rb.pack(anchor="w")

        # 5. Button to create collage
        self.create_collage_btn = tk.Button(self, text="Create Collage", command=self.create_collage)
        self.create_collage_btn.pack(pady=(5, 10))

    # ========== Methods ==========

    def select_first_image(self):
        """Select the first image."""
        path = filedialog.askopenfilename(
            title="Select First Image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.tiff;*.bmp;*.gif")]
        )
        if path:
            self.img1_path = path
            messagebox.showinfo("First Image Selected", f"First image:\n{path}")

    def select_second_image(self):
        """Select the second image."""
        path = filedialog.askopenfilename(
            title="Select Second Image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.tiff;*.bmp;*.gif")]
        )
        if path:
            self.img2_path = path
            messagebox.showinfo("Second Image Selected", f"Second image:\n{path}")

    def create_collage(self):
        """Create a collage of the two selected images."""
        # Check that both images have been selected
        if not self.img1_path or not self.img2_path:
            messagebox.showwarning("Images Not Selected", "Please select two images first.")
            return

        # Try to open both images
        try:
            with Image.open(self.img1_path) as im1:
                img1 = im1.convert("RGB")  # Convert to RGB to avoid mode conflicts
            with Image.open(self.img2_path) as im2:
                img2 = im2.convert("RGB")
        except Exception as e:
            messagebox.showerror("Error Opening Images", f"Could not open images:\n{e}")
            return

        layout = self.layout_var.get()
        spacing = self.spacing_var.get()
        save_format = self.format_var.get()  # "PNG" or "JPEG"

        # Helper function to scale an image proportionally
        def scale_image(image, target_width=None, target_height=None):
            """Scale 'image' proportionally to match target_width or target_height."""
            orig_w, orig_h = image.size

            if target_width and target_height:
                # If both are given, scale exactly
                # new_im = image.resize((target_width, target_height), Image.ANTIALIAS)
                new_im = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
                return new_im
            elif target_width:
                # Scale by width, preserve aspect ratio
                ratio = target_width / float(orig_w)
                new_h = int(orig_h * ratio)
                # new_im = image.resize((target_width, new_h), Image.ANTIALIAS)
                new_im = image.resize((target_width, new_h), Image.Resampling.LANCZOS)
                return new_im
            elif target_height:
                # Scale by height, preserve aspect ratio
                ratio = target_height / float(orig_h)
                new_w = int(orig_w * ratio)
                # new_im = image.resize((new_w, target_height), Image.ANTIALIAS)
                new_im = image.resize((new_w, target_height), Image.Resampling.LANCZOS)
                return new_im
            else:
                return image  # No scaling

        # Collage logic
        if layout == "horizontal":
            # SIDE BY SIDE: match heights
            h1, h2 = img1.height, img2.height
            min_height = min(h1, h2)

            # Scale both images to the smaller height
            scaled_img1 = scale_image(img1, target_height=min_height)
            scaled_img2 = scale_image(img2, target_height=min_height)

            total_width = scaled_img1.width + scaled_img2.width + spacing
            final_height = min_height
            collage = Image.new("RGB", (total_width, final_height), color=(255, 255, 255))

            x_offset = 0
            collage.paste(scaled_img1, (x_offset, 0))
            x_offset += scaled_img1.width + spacing
            collage.paste(scaled_img2, (x_offset, 0))

        else:
            # VERTICAL: match widths
            w1, w2 = img1.width, img2.width
            min_width = min(w1, w2)

            # Scale both images to the smaller width
            scaled_img1 = scale_image(img1, target_width=min_width)
            scaled_img2 = scale_image(img2, target_width=min_width)

            total_height = scaled_img1.height + scaled_img2.height + spacing
            final_width = min_width
            collage = Image.new("RGB", (final_width, total_height), color=(255, 255, 255))

            y_offset = 0
            collage.paste(scaled_img1, (0, y_offset))
            y_offset += scaled_img1.height + spacing
            collage.paste(scaled_img2, (0, y_offset))

        # Save the collage in the same folder as the first image
        output_dir = os.path.dirname(self.img1_path)

        # Use correct file extension based on format
        if save_format == "PNG":
            extension = ".png"
        else:
            extension = ".jpg"  # for "JPEG"

        output_path = os.path.join(output_dir, f"two_image_collage{extension}")
        try:
            collage.save(output_path, save_format)
            messagebox.showinfo("Collage Created",
                                f"Collage saved as:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save collage:\n{e}")

def main():
    app = TwoImageCollageApp()
    app.mainloop()

if __name__ == "__main__":
    main()
