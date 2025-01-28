import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

class CropTool(tk.Tk):
    SCROLL_MARGIN = 20  # Pixels from edge at which auto-scroll should trigger
    SCROLL_SPEED = 1    # How many "units" to scroll each step

    def __init__(self, folder_path):
        super().__init__()
        self.title("Image Crop Tool")

        self.folder_path = folder_path
        
        # Get list of image files from the folder
        self.image_files = [
            f for f in os.listdir(folder_path)
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'))
        ]
        if not self.image_files:
            print("No image files found in the specified folder.")
            self.destroy()
            return

        # Create a subfolder to save cropped images
        self.cropped_folder = os.path.join(folder_path, "cropped")
        os.makedirs(self.cropped_folder, exist_ok=True)

        # We'll display the first image so that user can pick a region
        self.current_image_path = os.path.join(folder_path, self.image_files[0])
        self.load_image()

        # Variables to store selection box coordinates
        self.start_x = None
        self.start_y = None
        self.rect_id = None  # ID of the rectangle drawn on Canvas

        # ============= BUILD GUI WITH SCROLLBARS =============
        container = tk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True)

        # Scrollbars
        self.v_scroll = tk.Scrollbar(container, orient=tk.VERTICAL)
        self.h_scroll = tk.Scrollbar(container, orient=tk.HORIZONTAL)

        # Canvas
        self.canvas = tk.Canvas(
            container,
            cursor="cross",
            xscrollcommand=self.h_scroll.set,
            yscrollcommand=self.v_scroll.set
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.h_scroll.grid(row=1, column=0, sticky="ew")

        self.v_scroll.config(command=self.canvas.yview)
        self.h_scroll.config(command=self.canvas.xview)

        # Make the canvas expandable in grid
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        # Confirm selection button
        self.confirm_button = tk.Button(self, text="Confirm Selection", command=self.confirm_selection)
        self.confirm_button.pack(pady=5)

        # Render the image on the canvas
        self.draw_image_on_canvas()

    def load_image(self):
        self.original_image = Image.open(self.current_image_path)
        self.tk_image = ImageTk.PhotoImage(self.original_image)

    def draw_image_on_canvas(self):
        """Draws the current image on the canvas and sets the scroll region."""
        self.canvas_image_id = self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
        # Set scroll region to the size of the image
        w, h = self.tk_image.width(), self.tk_image.height()
        self.canvas.config(scrollregion=(0, 0, w, h))

    def on_button_press(self, event):
        """Record the starting point of the selection rectangle in canvas coordinates."""
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

        # If there's an old rectangle, remove it
        if self.rect_id:
            self.canvas.delete(self.rect_id)
            self.rect_id = None

    def on_move_press(self, event):
        """Draw/update the selection rectangle, and auto-scroll if near edges."""
        # Auto-scroll if near edges
        self.auto_scroll_if_needed(event)

        # Now get the current mouse position in canvas coords
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)

        # Remove any existing rectangle
        if self.rect_id:
            self.canvas.delete(self.rect_id)

        # Draw a new rectangle
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, cur_x, cur_y,
            outline='red', width=2, dash=(2, 2)
        )

    def on_button_release(self, event):
        """Finalize the selection rectangle."""
        pass

    def auto_scroll_if_needed(self, event):
        """
        Auto-scroll the canvas if the mouse is near any edge (while dragging).
        This allows selecting regions that extend beyond the currently visible area.
        """
        # The current mouse position in widget coordinates (not scrolled)
        widget_x, widget_y = event.x, event.y

        # Canvas visible width/height
        visible_width = self.canvas.winfo_width()
        visible_height = self.canvas.winfo_height()

        # Scroll horizontally if near left/right
        if widget_x < self.SCROLL_MARGIN:
            # scroll left
            self.canvas.xview_scroll(-self.SCROLL_SPEED, "units")
        elif widget_x > (visible_width - self.SCROLL_MARGIN):
            # scroll right
            self.canvas.xview_scroll(self.SCROLL_SPEED, "units")

        # Scroll vertically if near top/bottom
        if widget_y < self.SCROLL_MARGIN:
            # scroll up
            self.canvas.yview_scroll(-self.SCROLL_SPEED, "units")
        elif widget_y > (visible_height - self.SCROLL_MARGIN):
            # scroll down
            self.canvas.yview_scroll(self.SCROLL_SPEED, "units")

    def confirm_selection(self):
        # Make sure we actually have a drawn rectangle
        if not self.rect_id:
            print("No selection rectangle found!")
            return
        
        coords = self.canvas.coords(self.rect_id)
        if len(coords) != 4:
            print("No valid rectangle drawn. Please click and drag to draw a rectangle.")
            return
        
        x1, y1, x2, y2 = coords
        
        # Sort the x and y coordinates to get a proper bounding box
        left, right = sorted([x1, x2])
        upper, lower = sorted([y1, y2])
        bounding_box = (left, upper, right, lower)
        
        print(f"Selected region: {bounding_box}")

        # Crop all images in the folder to this bounding box
        for img_file in self.image_files:
            path = os.path.join(self.folder_path, img_file)
            try:
                with Image.open(path) as im:
                    cropped_im = im.crop(bounding_box)
                    
                    # Save in the cropped folder
                    cropped_path = os.path.join(self.cropped_folder, img_file)
                    cropped_im.save(cropped_path)
                    print(f"Cropped and saved: {cropped_path}")
            except Exception as e:
                print(f"Failed to process {path}: {e}")

        print("Cropping done for all images!")
        self.quit()

def main():
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title="Select Folder Containing Images")
    root.destroy()
    
    if not folder_path:
        print("No folder selected.")
        return

    app = CropTool(folder_path)
    app.mainloop()

if __name__ == "__main__":
    main()
