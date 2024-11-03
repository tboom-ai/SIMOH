import tkinter as tk  # Used to create GUI components (buttons, listboxes, menus, entries, labels)
import modules.E2_structural_element_loader as SEL  # Load E2_structural_element_loader.py script
import subprocess  # To run external Python scripts

# Custom button class with rounded edges
class RoundedButton(tk.Canvas):
    """
    A custom class for creating rounded buttons using a Canvas widget.
    """
    def __init__(self, parent, text, command=None, width=250, **kwargs):
        """
        Initializes a RoundedButton with specified text, command, and size.
        """
        tk.Canvas.__init__(self, parent, width=width, height=50, **kwargs)
        self.command = command
        self.text = text
        self.rect = self.create_rounded_rectangle(5, 5, width - 5, 45, radius=20, fill="#7296bd", outline="#252526")
        self.label = self.create_text(width / 2, 25, text=self.text, fill="#252526", font=("Arial", 12, "bold"))

        # Bind events for button actions
        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
        """
        Creates a rounded rectangle shape on the Canvas.
        """
        points = [
            x1 + radius, y1,
            x1 + radius, y1,
            x2 - radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def on_click(self, event):
        """
        Handles the button click event.
        """
        if self.command:
            self.command()

    def on_enter(self, event):
        """
        Changes button color when the mouse enters and  reverts button color when the mouse leaves.
        """
        self.itemconfig(self.rect, fill="#86b0de")
    def on_leave(self, event):
        self.itemconfig(self.rect, fill="#7296bd")

# Main application class
class RobotApp:
    """
    A class representing the main interface for the "robot" control application.
    """
    def __init__(self, root):
        """
        Initializes the main application window and creates the interface components with layout options.
        """
        self.root = root
        self.root.title("")
        self.root.geometry("600x300")
        self.root.config(bg="#f3f3f3")
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.label = tk.Label(root, text="Crack Detection Panel", font=("Arial", 16), fg="#252526", bg="#f3f3f3")
        self.label.grid(row=0, column=0, columnspan=2, pady=20)
        self.create_buttons()

    def create_buttons(self):
        """
        Creates the buttons for opening external python scripts as E2_structural_element_loader.py, E2_crack_dashboard.py, and E2_crack_detection.py.
        """
        button_width = 280  

        # Button to run E2_structural_element_loader.py
        button_import_plan = RoundedButton(self.root, text="Structural Element Information", command=self.import_BIM_model, width=button_width, highlightthickness=0)
        button_import_plan.grid(row=1, column=0, padx=10, pady=10)

        # Button to run E2_crack_dashboard.py
        button_show_info = RoundedButton(self.root, text="Dashboard", command=self.show_dashboard, width=button_width, highlightthickness=0)
        button_show_info.grid(row=1, column=1, padx=10, pady=10)

        # Button to run E2_crack_detection.py
        button_start = RoundedButton(self.root, text="Start Crack Detection", command=self.start_detection, width=(button_width * 2) + 20, highlightthickness=0)
        button_start.grid(row=3, column=0, columnspan=2, padx=10, pady=20)

    def show_dashboard(self):
        """
        Opens the E2_crack_dashboard.py file to display the analysis dashboard.
        """
        try:
            subprocess.Popen(["python", "modules/E2_crack_dashboard.py"])
            print("Dashboard opened successfully!")
        except Exception as e:
            print(f"Error opening dashboard: {e}")

    def import_BIM_model(self):
        """
        Opens a new window for structural element information using the ZoneApp Class from SEL module.
        """
        new_window = tk.Toplevel(self.root)
        app = SEL.ZoneApp(new_window)

    def start_detection(self):
        """
        Starts the crack detection by running the E2_crack_detection.py script.
        """
        try:
            subprocess.Popen(["python", "modules/E2_crack_detection.py"])
            print("Detection started successfully!")
        except Exception as e:
            print(f"Error starting detection: {e}")

# Create the main window and run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = RobotApp(root)
    root.mainloop()
