import tkinter as tk
import subprocess

# Global variables to store the process instances
hazard_process = None
path_process = None

def import_bim():
    """Placeholder function for the Import BIM button."""
    subprocess.Popen(["python", "S.I.M.O.H./modules/P2_main_path_planning.py"])
    print()
    print("---------------------")
    print("BIM model imported...")
    print("---------------------")
    print()

def start_scripts():
    """Function to start the start.py script."""
    print()
    print("---------------------------------------")
    print("S.I.M.O.H. activated, press 'q' to stop")
    print("---------------------------------------")
    print()
    subprocess.Popen(["python", "S.I.M.O.H./modules/P3_start.py"])

# Set up the main Tkinter window
root = tk.Tk()
root.title("S.I.M.O.H. Control Panel")
root.geometry("300x150")

# Create and place the Import BIM button
import_button = tk.Button(root, text="Import BIM", command=import_bim, width=20, height=2)
import_button.pack(pady=10)

# Create and place the Start button
start_button = tk.Button(root, text="Start", command=start_scripts, width=20, height=2)
start_button.pack(pady=10)

# Run the Tkinter main loop
root.mainloop()
