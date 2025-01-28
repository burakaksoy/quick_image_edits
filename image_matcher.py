import cv2
import numpy as np

# Global variables to store selected points
points_img1 = []
points_img2 = []

# Mouse callback function for selecting points on an image
def select_points(event, x, y, flags, param):
    """
    When the left mouse button is clicked, record the (x, y) coordinates.
    """
    if event == cv2.EVENT_LBUTTONDOWN:
        param.append((x, y))
        print(f"Point selected at: ({x}, {y})")

def get_points_from_image(image_path, window_name):
    """
    Opens an image in a named window and lets the user select points by left-clicking.
    Press 'q' to close the window once you've selected all desired points.
    Returns a list of (x, y) points.
    """
    # Read the image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not load image: {image_path}")

    # Create a clone to draw selected points for visual feedback
    img_clone = img.copy()

    # A local list to store the points for this specific image
    local_points = []

    # Create a window and set the mouse callback
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, select_points, local_points)

    print(f"\n[INFO] Select points on '{window_name}' (left-click).")
    print("[INFO] Press 'q' when finished.")

    while True:
        # Show the updated image with drawn points
        for i, pt in enumerate(local_points):
            cv2.circle(img_clone, pt, 5, (0, 0, 255), -1)
            cv2.putText(img_clone, str(i + 1), (pt[0] + 5, pt[1] - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)

        cv2.imshow(window_name, img_clone)
        key = cv2.waitKey(20) & 0xFF

        # If the user presses 'q', break from the loop
        if key == ord('q'):
            break

        # Reset the drawing if 'r' is pressed (optional)
        if key == ord('r'):
            local_points.clear()
            img_clone = img.copy()
            print("[INFO] Points reset.")

    cv2.destroyWindow(window_name)
    return local_points

def main():
    # Paths to your two images
    image_path_1 = "DLO-narrow-corridor-exec-snapshots-06.png"  # Replace with your first image path
    image_path_2 = "DLO-narrow-corridor-exec-snapshots-07.png"  # Replace with your first image path

    # Step 1: Select points on the first image
    points_img1 = get_points_from_image(image_path_1, "Image 1")

    # Step 2: Select points on the second image
    points_img2 = get_points_from_image(image_path_2, "Image 2")

    # Make sure both lists have the same length
    if len(points_img1) != len(points_img2):
        raise ValueError("Number of points selected in Image 1 and Image 2 do not match!")

    # Convert to NumPy arrays of shape (N, 1, 2)
    pts1 = np.array(points_img1, dtype=np.float32).reshape(-1, 1, 2)
    pts2 = np.array(points_img2, dtype=np.float32).reshape(-1, 1, 2)

    # Compute the Homography matrix
    # Method could be 0 (least-squares) or cv2.RANSAC or cv2.LMEDS
    H, mask = cv2.findHomography(pts1, pts2, cv2.RANSAC, 5.0)

    print("\n[RESULT] Homography Matrix (3x3):")
    print(H)

    # If you want to see how the first image looks warped onto the second, you can do:
    # (Optional visualization)
    # Load the images again
    img1 = cv2.imread(image_path_1)
    img2 = cv2.imread(image_path_2)
    # Warp the first image to align with the second
    height, width, _ = img2.shape
    warped_img1 = cv2.warpPerspective(img1, H, (width, height))
    # Show side by side
    cv2.imshow("Warped Image 1", warped_img1)
    cv2.imshow("Original Image 2", img2)
    print("[INFO] Press any key to close.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
