from multiprocessing import set_start_method, Process, Event
import os
import time
import signal
import sys

def run_hazard_detection(finish_event):
    """Run the hazard detection script, which opens cv2 windows."""
    os.system("python modules/E1_hazard_detection.py")
    # After the hazard detection is done, set the event
    finish_event.set()

def run_path_visualizer(finish_event):
    """Run the path visualizer script, which opens a matplotlib plot."""
    import matplotlib.pyplot as plt
    from modules.E1_path_visualizer import main  # Assuming your visualization script has a main function

    # Run the visualization script
    main()

    # Wait for the hazard detection process to finish
    while not finish_event.is_set():
        plt.pause(1)  # Keep updating the plot periodically to keep it responsive

    # Close the matplotlib plot once the hazard detection finishes
    plt.close('all')

if __name__ == "__main__":
    set_start_method("spawn", force=True)

    # Create an event for communication between processes
    finish_event = Event()

    # Create processes for each script
    hazard_process = Process(target=run_hazard_detection, args=(finish_event,))
    path_process = Process(target=run_path_visualizer, args=(finish_event,))

    # Start both processes
    hazard_process.start()
    path_process.start()

    # Wait for both processes to complete
    hazard_process.join()
    path_process.join()
