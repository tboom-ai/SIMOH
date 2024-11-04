
from multiprocessing import set_start_method, Process, Queue
import E1_hazard_detection
import E1_path_visualizer

def run_hazard_detection(position_queue):
    """Run the hazard detection script."""
    E1_hazard_detection.main(position_queue)

def run_path_visualizer(position_queue):
    """Run the path visualizer script."""
    E1_path_visualizer.main(position_queue)

if __name__ == "__main__":
    set_start_method("spawn", force=True)

    # Create a Queue to be able to get current [x,y] position 
    position_queue = Queue()

    # Create processes for each script
    hazard_process = Process(target=run_hazard_detection, args=(position_queue,))
    path_process = Process(target=run_path_visualizer, args=(position_queue,))

    # Start both processes
    hazard_process.start()
    path_process.start()

    # Wait for both processes to complete
    hazard_process.join()
    path_process.join()

