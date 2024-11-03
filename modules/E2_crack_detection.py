import cv2  # Allows loading and processing images
from ultralytics import YOLO  # Loads YOLO model for crack detection
import matplotlib.pyplot as plt  # Visualizes results (bbox on image)
from PIL import Image, ImageDraw, ImageFont  # Enhances image annotation
import numpy as np  # Convert PIL image to make it compatible with OpenCV
import json  # Handles reading and writing JSON data
import tkinter as tk # Used to create GUI components (buttons, listboxes, menus, entries, labels)
from tkinter import filedialog, messagebox, ttk # To select files, create displays and layout options

# Creates display that opens when the code is runned
root = tk.Tk()
root.withdraw()  # Hide the main window initially

# Load YOLO model
model = YOLO('assets/best_cracks.pt')  # Trained model to detect crack / no-crack

# Load JSON data if the file exists otherwise create an empty dictionary
json_output_path = "assets/crack_information.json"
try:
    with open(json_output_path, 'r') as json_file:
        json_data = json.load(json_file)
except (FileNotFoundError, json.JSONDecodeError):
    json_data = {}

# Function to merge overlapping bounding boxes for cracks
def merge_boxes(boxes):
    """
    Merges overlapping bounding boxes by combining close or overlapping rectangles into single boxes.
    Returns a list of merged boxes.
    """
    if not boxes:
        return []
    boxes = sorted(boxes, key=lambda x: x[0])
    merged_boxes = [boxes[0]]
    for current_box in boxes[1:]:
        x1, y1, x2, y2 = current_box
        last_x1, last_y1, last_x2, last_y2 = merged_boxes[-1]
        if x1 <= last_x2:
            merged_boxes[-1] = (min(last_x1, x1), min(last_y1, y1), max(last_x2, x2), max(last_y2, y2))
        else:
            merged_boxes.append(current_box)
    return merged_boxes

# Function to calculate crack dimensions within bounding boxes
def calculate_crack_dimensions(cropped_image):
    """
    Detects crack length and width by finding contours within the bounding box.
    Returns crack length and width in pixels.
    """
    gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        longest_contour = max(contours, key=lambda c: cv2.arcLength(c, closed=False))
        crack_length = round(cv2.arcLength(longest_contour, closed=False), 2)
        y_coords = [point[0][1] for point in longest_contour]
        crack_width = round(max(y_coords) - min(y_coords), 2) if y_coords else 0
        return crack_length, crack_width
    return 0, 0

# Function to process the uploaded image and detect cracks
def process_image(image_path):
    """
    Loads an image, applies the YOLO model to detect cracks, and calculates crack dimensions and orientation.
    Updates the JSON data with results and saves an annotated image if a crack is found.
    """
    element_id = f"{element_type.get()}.{element_number.get()}"
    
    # Create a new JSON entry for the structural element if none exists
    if element_id not in json_data:
        json_data[element_id] = {
            "structural_element_ID": element_id,
            "coordinates": [0, 0],  
            "crack_detected": False,
            "orientation_of_crack": "",
            "crack_length (pixels)": 0,
            "crack_width (pixels)": 0,
            "crack_detected_image": ""
        }

    # Load and process the image using YOLO model
    image = cv2.imread(image_path)
    results = model(image, conf=0.2)
    has_detected_crack = False

    # Check for bounding boxes in YOLO results
    if results[0].boxes:
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_image)
        font = ImageFont.load_default()
        detected_boxes = []

        # Determine orientation of bouding box (horizontal / vertical crack) 
        for box in results[0].boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            box_width = abs(x2 - x1)
            box_height = abs(y2 - y1)
            orientation = "Horizontal" if box_width > box_height else "Vertical"
            detected_boxes.append((x1, y1, x2, y2, orientation))

        # Merge overlapping bounding boxes
        merged_boxes = merge_boxes([(x1, y1, x2, y2) for x1, y1, x2, y2, _ in detected_boxes])
        
        # Annotate image with "crack" with layout options
        for box, orientation in zip(merged_boxes, [orientation for _, _, _, _, orientation in detected_boxes]):
            x1, y1, x2, y2 = box
            draw.rectangle([x1, y1, x2, y2], outline="red", width=4)
            crack_region = image[y1:y2, x1:x2]
            crack_length, crack_width = calculate_crack_dimensions(crack_region)
            text = f"Crack"
            text_bbox = draw.textbbox((x1, y1), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            draw.rectangle([x1, y1 - text_height, x1 + text_width, y1], fill="red")
            draw.text((x1, y1 - text_height), text, fill="white", font=font)
            has_detected_crack = True

            # Update JSON data with detected crack details
            json_data[element_id]["crack_detected"] = True
            json_data[element_id]["orientation_of_crack"] = orientation
            json_data[element_id]["crack_length (pixels)"] = int(crack_length)
            json_data[element_id]["crack_width (pixels)"] = int(crack_width)

        # Save the annotated image if crack is detected and update JSON with this image path
        image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        plt.axis('off')
        plt.show()
        output_path = f"crack_detected_{element_id}.jpg" 
        cv2.imwrite(output_path, image)
        print(f"Image with detected crack saved as: {output_path}")
        json_data[element_id]["crack_detected_image"] = output_path
    else:
        print(f"No cracks detected on {element_id}")
        json_data[element_id]["crack_detected"] = False 

    # Save updated JSON data
    with open(json_output_path, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)
    print(f"Detection results saved in: {json_output_path}")

    # Close the display
    root.destroy()

# Function to open the Tkinter selection window for structural element and image upload
def open_selection_window():
    """
    Opens a display allowing the user to select a Structural Element ID and an image file of that structural element for crack detection.
    Initiates the detection process once the image is uploaded.
    """
    selection_window = tk.Toplevel(root)
    selection_window.title("Select Structural Element and Upload Image")

    # Dropdown menu for structural element types (e.g. wall, beam & column)
    tk.Label(selection_window, text="Select Structural Element:").pack()
    element_type.set("")
    element_type_menu = ttk.Combobox(selection_window, textvariable=element_type, values=["Wall", "Beam", "Column"])
    element_type_menu.pack()

    # Dropdown menu for element number (e.g. ID numbers 1 to 3)
    tk.Label(selection_window, text="Select Element ID Number:").pack()
    element_number.set("")
    element_number_menu = ttk.Combobox(selection_window, textvariable=element_number, values=[str(i) for i in range(1, 4)])
    element_number_menu.pack()

    # Function to upload image and start detection
    def upload_image():
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if not file_path:
            messagebox.showerror("Input Error", "Please upload an image.")
        else:
            selection_window.destroy()
            process_image(file_path)

    # Button to trigger image upload
    upload_button = tk.Button(selection_window, text="Upload Image", command=upload_image)
    upload_button.pack()

    selection_window.mainloop()

# Initialize variables for dropdown selections
element_type = tk.StringVar()
element_number = tk.StringVar()

# Open the selection window and start the Tkinter main loop
open_selection_window()
root.mainloop()
