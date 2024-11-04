import tkinter as tk  # Used to create GUI components (buttons, listboxes, menus, entries, labels)
from PIL import Image, ImageTk # Allows image handling and display
import json  # Handles reading and writing JSON data

# Load the JSON file with structural element information
def load_zone_data(json_path):
    """
    Loads zone information from the provided JSON file.
    """
    with open(json_path, 'r') as file:
        data = json.load(file)
    return data

# Main application class for the dashboard
class DashboardApp:
    def __init__(self, root, json_path):
        """
        Initializes the Dashboard application and loads the data.
        """
        self.root = root
        self.root.title("Dashboard")

        # Load zone data from JSON file
        self.zone_data = load_zone_data(json_path)

        # Load the image using PIL
        self.image_path = list(self.zone_data.values())[0]["construction_site_plan"]  # Get path to image from the loaded data
        self.image = Image.open(self.image_path)
        self.max_width = 800  # Set max width for the displayed image
        self.max_height = 600  # Set max height for the displayed image
        self.image = self.resize_image(self.image)
        self.photo = ImageTk.PhotoImage(self.image)  # Convert image to PhotoImage for Tkinter

        # Create a canvas to display the image
        self.canvas = tk.Canvas(root, width=self.new_width, height=self.new_height)  # Set the canvas size
        self.canvas.pack(side=tk.LEFT)  # Position the canvas on the left side of the window

        # Add the image to the canvas
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

        # Draw points for each set of coordinates from the JSON file
        self.draw_coordinatess()

        # Create a text widget to display crack information
        self.info_text = tk.Text(root, width=40, height=10, wrap=tk.WORD)  
        self.info_text.pack(side=tk.TOP, padx=10, pady=10)

        # Create a label to display the crack image
        self.crack_image_label = tk.Label(root)
        self.crack_image_label.pack(side=tk.BOTTOM, padx=10, pady=10)

    # Resize image to fit within defined dimensions
    def resize_image(self, image):
        """
        Resizes the loaded image to fit within the defined maximum dimensions.
        """
        original_width, original_height = image.size
        aspect_ratio = original_width / original_height

        # Adjust size based on aspect ratio and maximum allowed dimensions
        if original_width > self.max_width or original_height > self.max_height:
            if aspect_ratio > 1:  # If image is wider than its tall
                self.new_width = self.max_width
                self.new_height = int(self.max_width / aspect_ratio)
            else:  # If image is taller than its wide
                self.new_height = self.max_height
                self.new_width = int(self.max_height * aspect_ratio)

            # Set scale factors for resizing
            self.scale_factor_x = original_width / self.new_width
            self.scale_factor_y = original_height / self.new_height
            return image.resize((self.new_width, self.new_height), Image.Resampling.LANCZOS)
        else:
            # Keep the original dimensions if resizing is not needed
            self.new_width, self.new_height = original_width, original_height
            self.scale_factor_x = 1
            self.scale_factor_y = 1
            return image

    # Draw coordinates of zones on the image
    def draw_coordinatess(self):
        """
        Draws points on the image to represent the location (coordinates) of each structural element on the construction site.
        """
        for element_id, element_data in self.zone_data.items():
            x, y = element_data["coordinates"]  # Extract x, y coordinates from the data
            x = int(x / self.scale_factor_x)  
            y = int(y / self.scale_factor_y)
            self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="red", outline="black", width=2)
            self.canvas.create_text(x + 10, y, text=element_id, anchor=tk.W, fill="black", font=("Arial", 10, "bold"))
            self.canvas.tag_bind(self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="red", outline="black", width=2), "<Button-1>", lambda e, el_id=element_id: self.show_crack_info(el_id))

    # Display information about the selected crack
    def show_crack_info(self, element_id):
        """
        Displays detailed information about the selected element, including crack detection data. Data imported from the JSON file.
        """
        element_data = self.zone_data[element_id]
        # Compile crack information into a text block
        crack_info = f"Element ID: {element_data['structural_element_ID']}\n"
        crack_info += f"Crack Detected: {element_data['crack_detected']}\n"
        crack_info += f"Orientation of Crack: {element_data['orientation_of_crack']}\n"
        crack_info += f"Crack Length (pixels): {element_data['crack_length (pixels)']}\n"
        crack_info += f"Crack Width (pixels): {element_data['crack_width (pixels)']}\n"

        # Display the information in the text widget
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, crack_info)

        # Load and display crack image if available
        if "crack_detected_image" in element_data:
            crack_image = Image.open(element_data["crack_detected_image"])
            crack_image = crack_image.resize((200, 200), Image.Resampling.LANCZOS)  # Resize the crack image
            self.crack_photo = ImageTk.PhotoImage(crack_image)
            self.crack_image_label.config(image=self.crack_photo)
        else:
            self.crack_image_label.config(image='')

# Create the main window and run the application
if __name__ == "__main__":
    root = tk.Tk()  # Create main application window
    json_path = "assets/crack_information.json"  # Path to the JSON data file
    app = DashboardApp(root, json_path)  # Instantiate the dashboard application
    root.mainloop()  # Run the main event loop
