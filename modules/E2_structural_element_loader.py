import tkinter as tk  # Used to create GUI components (buttons, listboxes, menus, entries, labels)
from tkinter import filedialog, messagebox, ttk  # To select files, create displays and layout options
from PIL import Image, ImageTk  # Allows image handling and display
import os  # Used for file and directory operations
import json  # Handles reading and writing JSON data

# Display for adjusting zone information (plan, coordinates, and structural element ID)
class ZoneApp:
    # Initialize the ZoneApp display
    def __init__(self, root):
        """
        Creates the main interface for selecting structural elements and loading construction site images.
        """
        # Set up the main window and initialize variables
        self.root = root
        self.root.title("Select Structural Element")
        self.zone_id = {}
        self.x, self.y = None, None
        self.zone_dot = None
        self.zone_text = None
        self.image_path = None
        self.max_width = 400 
        self.max_height = 400  

        # Create the main frame layout
        self.frame_main = tk.Frame(root)
        self.frame_main.pack(pady=10, padx=10, expand=True, fill=tk.BOTH)

        # Create the frame for the left side (image display)
        self.frame_left = tk.Frame(self.frame_main)
        self.frame_left.grid(row=0, column=0, padx=10, pady=10)

        # Create the frame for the right side (coordinates and listbox)
        self.frame_right = tk.Frame(self.frame_main)
        self.frame_right.grid(row=0, column=1, padx=10, pady=10)

        # Load image button
        self.load_button = tk.Button(self.frame_left, text="Load Construction Site Plan", command=self.load_image, bg="white", bd=0.5, highlightbackground="gray", width=30)
        self.load_button.pack(pady=0)

        # Canvas for displaying the image
        self.canvas = tk.Canvas(self.frame_left)
        self.canvas.pack(pady=10)

        # Listbox for displaying the structural elements ID's
        self.zone_listbox = tk.Listbox(self.frame_right, width=40, height=10)
        self.zone_listbox.grid(row=1, column=0, padx=0, pady=10)
        self.zone_listbox.bind('<<ListboxSelect>>', self.load_selected_zone)

        # Dropdown to manually select structural element ID (these are possible options)
        tk.Label(self.frame_right, text="Structural Element ID:", font=('TkDefaultFont', 9, 'bold')).grid(row=2, column=0, sticky='w')
        self.structural_element_ID_options = [
            "Wall.1", "Wall.2", "Wall.3", "Beam.1", "Beam.2", "Beam.3", "Column.1", "Column.2", "Column.3"
        ]
        self.structural_element_ID_combobox = ttk.Combobox(self.frame_right, values=self.structural_element_ID_options, state="readonly")
        self.structural_element_ID_combobox.grid(row=3, column=0, pady=5, padx=5, sticky="e")
        
        # Frame for submit and delete buttons
        self.submit_delete_frame = tk.Frame(self.frame_right)
        self.submit_delete_frame.grid(row=10, column=0, pady=10)

        # Submit button
        self.submit_button = tk.Button(self.submit_delete_frame, text="Submit Zone Details", command=self.submit_details, bg="white", bd=0.5, highlightbackground="gray")
        self.submit_button.grid(row=0, column=1, padx=6, sticky="e")

        # Delete button
        self.delete_button = tk.Button(self.submit_delete_frame, text="Delete Zone Details", command=self.delete_zone, bg="white", bd=0.5, highlightbackground="gray")
        self.delete_button.grid(row=0, column=0, padx=5, sticky="w")

        # Load existing data from JSON file
        self.load_data()

    # Load image of construction site plan
    def load_image(self, image_path=None):
        """
        Loads the construction site plan image from the local device and displays it on the canvas.
        """
        if image_path is None:  # If no path is provided, prompt the user to select an image
            self.image_path = filedialog.askopenfilename()
        else:  # Otherwise, use the given image path
            self.image_path = image_path
        
        if self.image_path:
            print(f"Image path loaded: {self.image_path}")
            self.image = Image.open(self.image_path)

            # Resize the image if it exceeds max dimensions
            self.image = self.resize_image(self.image)

            self.tk_image = ImageTk.PhotoImage(self.image)

            # Set the canvas size to match the image
            self.canvas.config(width=self.image.width, height=self.image.height)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

            # Bind the click event to get coordinates
            self.canvas.bind("<Button-1>", self.get_coordinates)

    # Resize image to fit the display area
    def resize_image(self, image):
        """
        Resizes the loaded image to fit within the defined maximum dimensions.
        """
        original_width, original_height = image.size
        aspect_ratio = original_width / original_height

        # Resize image if it exceeds max dimensions
        if original_width > self.max_width or original_height > self.max_height:
            if aspect_ratio > 1:
                self.new_width = self.max_width
                self.new_height = int(self.max_width / aspect_ratio)
            else:
                self.new_height = self.max_height
                self.new_width = int(self.max_height * aspect_ratio)

            # Calculate scaling factor
            self.scale_factor_x = original_width / self.new_width
            self.scale_factor_y = original_height / self.new_height
            return image.resize((self.new_width, self.new_height), Image.Resampling.LANCZOS)
        else:
            # No resizing needed
            self.new_width, self.new_height = original_width, original_height
            self.scale_factor_x = 1
            self.scale_factor_y = 1
            return image

    # Determine zone coordinates by clicking on the image
    def get_coordinates(self, event):
        """
        Records the coordinates of the point where the user clicks on the image.
        """
        self.x, self.y = event.x, event.y
        self.x_full = int(self.x * self.scale_factor_x)
        self.y_full = int(self.y * self.scale_factor_y)
        self.draw_zone_dot()

    # Create a dot on the image where the user clicked
    def draw_zone_dot(self):
        """
        Draws a dot on the image at the clicked coordinates.
        """
        # Remove previous dots if any
        if self.zone_dot:
            self.canvas.delete(self.zone_dot)
        if self.zone_text:
            self.canvas.delete(self.zone_text)
        radius = 5  
        self.zone_dot = self.canvas.create_oval(
            self.x - radius, self.y - radius, self.x + radius, self.y + radius,
            fill="darkred", outline="black")
        
        # Display the selected structural element ID next to the dot
        structural_element_ID = self.structural_element_ID_combobox.get()
        if structural_element_ID:
            self.zone_text = self.canvas.create_text(
                self.x, self.y + 10, text=structural_element_ID, fill="black", anchor=tk.N
            )

    # Submit the structural element ID details to the list and save
    def submit_details(self):
        """
        Submits the selected structural element ID details, including image of construction site plan & coordinates, and saves to JSON.
        """
        structural_element_ID = self.structural_element_ID_combobox.get()
        
        # Check if structural element ID is selected and coordinates are available
        if not structural_element_ID:
            messagebox.showerror("Error", "Please select a structural element ID.")
            return
        
        if self.x is None or self.y is None:
            messagebox.showwarning("Warning", "Please click on the image to select coordinates.")
            return

        # Create data entry for the selected zone
        zone_data = {
            "structural_element_ID": structural_element_ID,
            "construction_site_plan": self.image_path,
            "coordinates": [self.x_full, self.y_full],
            "crack_detected": False,
            "orientation_of_crack": "",
            "crack_length (pixels)": 0,
            "crack_width (pixels)": 0
        }

        # Add or update the zone data
        self.zone_id[structural_element_ID] = zone_data
        self.update_zone_listbox()
        self.save_data()
        self.clear_fields()

    # Delete the selected zone details
    def delete_zone(self):
        """
        Deletes the selected zone details from the list and JSON data.
        """
        selected_zone = self.zone_listbox.get(tk.ACTIVE)
        if selected_zone in self.zone_id:
            del self.zone_id[selected_zone]
            self.update_zone_listbox()
            self.save_data()
            self.clear_fields()
            messagebox.showinfo("Info", f"Zone '{selected_zone}' has been deleted.")

    # Load the selected zone details from the list
    def load_selected_zone(self, event):
        """
        Loads the details of the selected structural element id details from the listbox to display on the canvas.
        """
        selected_zone = self.zone_listbox.get(self.zone_listbox.curselection())

        if selected_zone in self.zone_id:
            zone_data = self.zone_id[selected_zone]

            # Set the selected structural element in the dropdown menu
            self.structural_element_ID_combobox.set(zone_data["structural_element_ID"])

            # Convert full-size coordinates to resized image coordinates using the scaling factor
            self.x = int(zone_data["coordinates"][0] / self.scale_factor_x)
            self.y = int(zone_data["coordinates"][1] / self.scale_factor_y)

            # Draw the dot on the resized image
            self.draw_zone_dot()

    # Update the zone listbox with the current zones
    def update_zone_listbox(self):
        """
        Updates the structural element id listbox to display the latest list.
        """
        self.zone_listbox.delete(0, tk.END)
        for zone in self.zone_id:
            self.zone_listbox.insert(tk.END, zone)

    # Save the zone data to a JSON file
    def save_data(self):
        """
        Saves the current data to a JSON file.
        """
        with open("assets/crack_information.json", "w") as json_file:
            json.dump(self.zone_id, json_file, indent=4)

    # Load data from JSON file
    def load_data(self):
        """
        Loads existing data from a JSON file, if available.
        """
        json_file_path = "assets/crack_information.json"
        if os.path.exists(json_file_path):
            with open(json_file_path, "r") as json_file:
                try:
                    self.zone_id = json.load(json_file)
                except json.JSONDecodeError:
                    self.zone_id = {}
            self.update_zone_listbox()

    # Clear the input fields
    def clear_fields(self):
        """
        Clears the input fields and resets the selected elements on the interface.
        """
        self.structural_element_ID_combobox.set('')
        self.x, self.y = None, None

        if self.zone_dot:
            self.canvas.delete(self.zone_dot)
        if self.zone_text:
            self.canvas.delete(self.zone_text)
        self.zone_dot = None
        self.zone_text = None

# Run the script correctly
if __name__ == "__main__":
    root = tk.Tk()
    zone_app = ZoneApp(root)

    root.mainloop()
