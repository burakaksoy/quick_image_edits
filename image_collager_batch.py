import os
import math
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image

class CollageApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Collage Maker")
        self.geometry("350x300")
        
        # Variables
        self.folder_path = None
        # layout_var can be: "horizontal", "vertical", or "grid"
        self.layout_var = tk.StringVar(value="horizontal")
        self.spacing_var = tk.IntVar(value=0)        # Default spacing is 0 px
        self.format_var = tk.StringVar(value="PNG")  # "PNG" or "JPEG", default PNG
        
        # Number of columns for the grid layout
        self.columns_var = tk.IntVar(value=2)        # Default 2 columns if grid mode

        # 1. Button to select folder
        self.select_folder_btn = tk.Button(self, text="Select Folder", command=self.select_folder)
        self.select_folder_btn.pack(pady=(10, 5))
        
        # 2. Radio buttons for layout
        layout_frame = tk.LabelFrame(self, text="Layout")
        layout_frame.pack(pady=5, fill="x", padx=20)
        
        self.horizontal_rb = tk.Radiobutton(layout_frame, text="Side by Side",
                                            variable=self.layout_var, value="horizontal")
        self.vertical_rb = tk.Radiobutton(layout_frame, text="Top to Bottom",
                                          variable=self.layout_var, value="vertical")
        self.grid_rb = tk.Radiobutton(layout_frame, text="Grid",
                                      variable=self.layout_var, value="grid")

        self.horizontal_rb.pack(anchor="w")
        self.vertical_rb.pack(anchor="w")
        self.grid_rb.pack(anchor="w")
        
        # 3. Entry (Spinbox) for spacing
        spacing_frame = tk.LabelFrame(self, text="Spacing (px)")
        spacing_frame.pack(pady=5, fill="x", padx=20)
        
        self.spacing_entry = tk.Spinbox(spacing_frame, from_=0, to=9999,
                                        textvariable=self.spacing_var, width=5)
        self.spacing_entry.pack(pady=5)
        
        # 4. Radio buttons for output format
        format_frame = tk.LabelFrame(self, text="Save Format")
        format_frame.pack(pady=5, fill="x", padx=20)
        self.png_rb = tk.Radiobutton(format_frame, text="PNG",
                                     variable=self.format_var, value="PNG")
        self.jpg_rb = tk.Radiobutton(format_frame, text="JPG",
                                     variable=self.format_var, value="JPEG")
        self.png_rb.pack(anchor="w")
        self.jpg_rb.pack(anchor="w")

        # 5. Spinbox for number of columns (used only if layout=grid)
        columns_frame = tk.LabelFrame(self, text="Number of Columns (Grid Mode)")
        columns_frame.pack(pady=5, fill="x", padx=20)
        self.columns_entry = tk.Spinbox(columns_frame, from_=1, to=100,
                                        textvariable=self.columns_var, width=5)
        self.columns_entry.pack(pady=5)

        # 6. Button to create collage
        self.create_collage_btn = tk.Button(self, text="Create Collage", command=self.create_collage)
        self.create_collage_btn.pack(pady=(5, 10))

    def select_folder(self):
        """Prompt the user to select a folder containing images."""
        folder_selected = filedialog.askdirectory(title="Select Folder Containing Images")
        if folder_selected:
            self.folder_path = folder_selected
            messagebox.showinfo("Folder Selected", f"Images will be loaded from:\n{folder_selected}")

    def create_collage(self):
        """Create and save the collage based on user selections."""
        if not self.folder_path:
            messagebox.showwarning("No Folder Selected", "Please select a folder first.")
            return

        # Gather all images in the folder
        image_files = [
            f for f in os.listdir(self.folder_path)
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif"))
        ]
        if not image_files:
            messagebox.showwarning("No Images Found", "No valid images in the selected folder.")
            return
        
        # Open all images with Pillow
        images = []
        for img_file in image_files:
            img_path = os.path.join(self.folder_path, img_file)
            try:
                with Image.open(img_path) as im:
                    # Convert to RGB (avoid issues with RGBA, P mode, etc.)
                    images.append(im.convert("RGB"))
            except Exception as e:
                print(f"Skipping file '{img_file}' due to error: {e}")

        if not images:
            messagebox.showwarning("No Valid Images", "Could not open any images from this folder.")
            return
        
        layout = self.layout_var.get()         # "horizontal", "vertical", or "grid"
        spacing = self.spacing_var.get()
        save_format = self.format_var.get()    # "PNG" or "JPEG"

        if layout == "horizontal":
            # SIDE-BY-SIDE
            total_width = sum(img.width for img in images) + spacing * (len(images) - 1)
            max_height = max(img.height for img in images)
            
            collage = Image.new("RGB", (total_width, max_height), color=(255, 255, 255))
            
            x_offset = 0
            for img in images:
                collage.paste(img, (x_offset, 0))
                x_offset += img.width + spacing

        elif layout == "vertical":
            # TOP-TO-BOTTOM
            total_height = sum(img.height for img in images) + spacing * (len(images) - 1)
            max_width = max(img.width for img in images)
            
            collage = Image.new("RGB", (max_width, total_height), color=(255, 255, 255))
            
            y_offset = 0
            for img in images:
                collage.paste(img, (0, y_offset))
                y_offset += img.height + spacing

        else:
            # GRID LAYOUT
            columns = self.columns_var.get()
            if columns < 1:
                messagebox.showwarning("Invalid Columns", "Number of columns must be >= 1.")
                return

            # Calculate how many rows we need
            total_images = len(images)
            rows = math.ceil(total_images / columns)

            # We need to find:
            #  - max width of each column
            #  - max height of each row
            # so we can position images in a table-like layout.
            col_widths = [0] * columns
            row_heights = [0] * rows

            # Assign each image to a row, col in row-major order
            for idx, img in enumerate(images):
                r = idx // columns
                c = idx % columns
                # Update max col width
                if img.width > col_widths[c]:
                    col_widths[c] = img.width
                # Update max row height
                if img.height > row_heights[r]:
                    row_heights[r] = img.height

            # Compute total collage size
            total_width = sum(col_widths) + spacing * (columns - 1)
            total_height = sum(row_heights) + spacing * (rows - 1)

            collage = Image.new("RGB", (total_width, total_height), color=(255, 255, 255))

            # Now paste images row by row
            y_offset = 0
            for r in range(rows):
                x_offset = 0
                for c in range(columns):
                    idx = r * columns + c
                    if idx < total_images:
                        img = images[idx]
                        # Paste image at (x_offset, y_offset)
                        collage.paste(img, (x_offset, y_offset))
                    x_offset += col_widths[c] + spacing
                y_offset += row_heights[r] + spacing

        # Determine file extension from format
        extension = ".png" if save_format == "PNG" else ".jpg"
        output_path = os.path.join(self.folder_path, f"collage_output{extension}")

        # Save the collage
        try:
            collage.save(output_path, save_format)
            messagebox.showinfo("Collage Created", f"Collage saved as:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save collage:\n{e}")

def main():
    app = CollageApp()
    app.mainloop()

if __name__ == "__main__":
    main()