from multiprocessing import set_start_method, Process
import os

def run_hazard_detection():
    """Run the hazard detection script, which opens cv2 windows."""
    os.system("python SIMOH/modules/E1_hazard_detection.py")

def run_path_visualizer():
    """Run the path visualizer script, which opens a matplotlib plot."""
    os.system("python SIMOH/modules/E1_path_visualizer.py")

if __name__ == "__main__":
    set_start_method("spawn", force=True)

    # Create processes for each script
    hazard_process = Process(target=run_hazard_detection)
    path_process = Process(target=run_path_visualizer)

    # Start both processes
    hazard_process.start()
    path_process.start()

    # Wait for both processes to complete
    hazard_process.join()
    path_process.join()

