import cv2
from ultralytics import YOLO
import json
from datetime import datetime
from matplotlib.path import Path
from screeninfo import get_monitors
from multiprocessing import Queue
# Import from other scripts
from E1_robot_path import simulate_robot_path

# Constants 
BIM_FILE = 'assets/BIM.json' 

# Load trained YOLO model
model = YOLO('assets/best_helmet.pt')  # Path to the trained model

# Window name
WINDOW_NAME = "Hazard Detection S.I.M.O.H."

# Functions
def load_json(path):
    """Load JSON data from the given file path"""
    with open(path, 'r') as f:
        return json.load(f)
        
def save_json(path, data):
    """Save JSON data to the given file path"""
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

def calculate_overlap(box1, box2):
    """Calculate overlap ratio between two bounding boxes"""
    x1_max = max(box1[0], box2[0])
    y1_max = max(box1[1], box2[1])
    x2_min = min(box1[2], box2[2])
    y2_min = min(box1[3], box2[3])
    overlap_area = max(0, x2_min - x1_max) * max(0, y2_min - y1_max)

    # Calculate the area of each bounding box
    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])

    # Determine the overlap ratio
    if box1_area == 0 or box2_area == 0:
        return 0
    return overlap_area / min(box1_area, box2_area)

def initialize_detected_hazards():
    """Initialize dictionary to keep track of detected hazards in this run"""
    return {"no_helmet": {}}

def process_detections(results, detected_hazards, helmet_boxes):
    """Process detection results and update the list of hazards"""
    # List to store hazards
    hazards = []

    # Process results from model if applicable
    if results:
        for box in results[0].boxes:
            class_name = model.names[int(box.cls[0])]   # Get the class name ('helmet' or 'no_helmet')
            x1, y1, x2, y2 = map(int, box.xyxy[0])      # Extract bounding box coordinates 

            # Check if detection ID is valid
            if box.id is not None:
                detection_id = str(int(box.id[0]))      # Extract unique ID

                if class_name == 'helmet':
                    helmet_boxes.append((x1, y1, x2, y2))   # Store helmet boxes

                elif class_name == 'no_helmet':
                    head_is_hazard = True   # Assume the head is a hazard until proven otherwise
                    # Check if the head overlaps with any helmet
                    for helmet_box in helmet_boxes:
                        overlap_ratio = calculate_overlap((x1, y1, x2, y2), helmet_box)
                        if overlap_ratio > 0.8:  # More than 80% overlap means person is wearing a helmet
                            head_is_hazard = False  # Proven otherwise
                            break

                    # If no helmet overlaps, log the hazard if it hasn't been logged yet
                    if head_is_hazard and detection_id not in detected_hazards["no_helmet"]:
                        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        hazard_warning = f"WARNING: Person without helmet detected, ID: {detection_id}, at {current_time}"

                        # Add to detected hazards dictionary to prevent re-logging in this run
                        detected_hazards["no_helmet"][detection_id] = current_time

                        # Append the hazard warning to update JSON
                        hazards.append(hazard_warning)
    return hazards

def update_zone_data(zone_data, zone_name, hazards):
    """Update the zone data with new hazards"""
    hazard_count = len(hazards)
    if hazard_count > 0:
        zone = zone_data.get(zone_name, {}) # Provides empy dictionary if the zone is not found

        # Update the amount of hazards
        zone["amount_of_hazards"] = zone.get("amount_of_hazards", 0) + hazard_count

        # Update the hazard types
        zone.setdefault("hazard_type", []).extend(hazards)

        # Save the updated zone data back into the main data
        zone_data[zone_name] = zone

        return True     # Indicates that the zone data was updated
    return False        # No updates made

def detect_hazards(frame, model, detected_hazards):
    """Perfrom hazard detection on the given frame
    Returns a list of detected hazards."""
    # Make a list to store helmet boudning boxes
    helmet_boxes = []

    # Yolo detection and tracking
    results = model.track(
        source = frame,
        conf = 0.6,
        persist = True,
        save = False,
        tracker = 'assets/bytetrack_helmet.yaml',
        verbose = False
    )

    hazards = process_detections(results, detected_hazards, helmet_boxes)
    return hazards, results

def get_current_zone(robot_pose, zone_data):
    """Determine the current zone based on the robots position
    Returns a tuple: (zone_name, required_PPE)
    """
    # initialize robot position
    x, y = robot_pose

    for zone_name, zone_info in zone_data.items():
        # assume each zone has a boundary field defining its area i 
        boundary = zone_info.get('boundary') 

        if boundary:
            # Create a Path object from the boundary points
            polygon_path = Path(boundary)

            # Check if the robots (x,y) position is inside the boundary of the polygon
            if polygon_path.contains_point((x,y)):
                # Get the required PPE as a list (split on commas and delete space)
                required_PPE = [p.strip() for p in zone_info.get('required_PPE', '').split('.')]
                return zone_name, required_PPE
    
    # After checking all the zones       
    return None, None 

def processing_robot_position(robot_pose, zone_data, hazard_detection_active, active_zone, detected_hazards):
    """Process the robot position to determine zone and update the hazard detection status"""

    x, y = robot_pose

    print(f"Robot Position: x={x}, y={y}")

    # Step 1: Determine current zone and required PPE
    current_zone, required_PPE = get_current_zone(robot_pose, zone_data)
    print(f"Current Zone: {current_zone}")
    print(f"Required PPE: {required_PPE}")
    print()

    # Step 2: Check if helmet PPE is required
    helmet_required = 'Helmet' in required_PPE if required_PPE else False

    # Step 3: Start or stop hazard detection based on the zone and PPE requirement
    if current_zone and helmet_required:
        if not hazard_detection_active:
            print(f"S.I.M.O.H. entered {current_zone}. Starting hazard detection")
            print()
            hazard_detection_active = True
            active_zone = current_zone # Store the current zone as active
            # Initialize directory to keep track of hazards detected in zone run
            detected_hazards = initialize_detected_hazards()
    else:
        if hazard_detection_active:
            print(f"S.I.M.O.H. left {active_zone}. Stopping hazard detection")
            print()
            hazard_detection_active = False     # Reset
            active_zone = None                  # Reset

    # Return updated variables
    return hazard_detection_active, active_zone, detected_hazards

def get_screen_dimensions():
    """Get the dimensions of the primary screen."""
    monitor = get_monitors()[0]
    return monitor.width, monitor.height

def setup_window(frame):
    """Resize the frame to fit the right side of the screen and display the OpenCV window."""

    # Get screen dimensions
    screen_width, screen_height = get_screen_dimensions()

    # Calculate available space for the window on the right half of the screen
    window_width = screen_width // 2
    window_height = screen_height

    # Calculate the scaling factors for width and height to fit the frame
    scale_x = window_width / frame.shape[1]
    scale_y = window_height / frame.shape[0]
    scale_factor = min(scale_x, scale_y)  # Choose the smaller scale to fit within the available space

    # Resize the frame based on the calculated scale factor
    resized_frame = cv2.resize(frame, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_LINEAR)

    # Calculate position to place the window on the right side of the screen
    x_position = screen_width - resized_frame.shape[1]
    y_position = 0  # Position at the top of the screen

    # Set up and display the window
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, resized_frame.shape[1], resized_frame.shape[0])
    cv2.moveWindow(WINDOW_NAME, x_position, y_position)

    # Show the resized frame in the positioned window
    cv2.imshow(WINDOW_NAME, resized_frame)

# MAIN LOOP
def main(position_queue):
    """Main loop to perform hazard detection based on simulated robot position."""

    # Initialize the camera 
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Cannot open camera")
        return

    # Load the zone data from JSON
    zone_data = load_json(BIM_FILE)

    # Initialize variables
    hazard_detection_active = False
    detected_hazards = None     
    active_zone = None          # To store the zone where hazard detection is active
    window_open = False         # Track if window is open

    # Simulate robot movement
    robot_positions = simulate_robot_path()

    for robot_pose in robot_positions:
        # Put the currunt robot position into the queue for path_visualizer.py
        position_queue.put(robot_pose)

        # Store previous hazard detection status
        prev_hazard_detection_active = hazard_detection_active

        # Process the robot position per step and update the hazard detection status
        hazard_detection_active, active_zone, detected_hazards, = processing_robot_position(robot_pose, zone_data, hazard_detection_active, active_zone, detected_hazards)
        
        # Check if hazard_detection_active has changed
        if hazard_detection_active and not prev_hazard_detection_active:
            # Just entered the zone, open camera window
            print("Starting camera for hazard detection")
            print()
            window_open = True
        
        elif not hazard_detection_active and prev_hazard_detection_active:
            # Just left the zone, close window
            print("Stopping camera for hazard detection")
            print()
            if window_open:
                cv2.destroyWindow('Hazard Detection S.I.M.O.H.')
                window_open = False

        # If hazard detection is active, perform hazard tracking
        if hazard_detection_active:
            # Capture frame-by-frame
            ret, frame = cap.read()
            if not ret:
                print("Error: failed to grab frame")
                break

            # Pass frame to setup_window() function for resizing and correct display
            setup_window(frame)

            # Perform hezard detection
            hazards, results = detect_hazards(frame, model, detected_hazards)

            # Update zone data if new hazards are detected
            data_updated = update_zone_data(zone_data, active_zone, hazards)

            # Save the JSON data only if there were updates
            if data_updated:
                save_json(BIM_FILE, zone_data)

            # Get the annotated image
            if results:
                annotated_image = results[0].plot()
                setup_window(annotated_image)

            # Add a small waiting time for less lag
            cv2.waitKey(2)

        else:
            # If the window is open but hazard detection is not active, destroy the window
            if window_open:
                cv2.destroyWindow(WINDOW_NAME)
                window_open = False
        
        # Exit the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


    # Cleanup
    cap.release()
    cv2.destroyAllWindows()

    print("-----------------------------------")
    print("S.I.M.O.H. finished it's cycle")
    print("Detected hazards are logged to BIM")
    print("Charging...")
    print("-----------------------------------")
    print()

if __name__ == "__main__":
    position_queue = Queue()
    main(position_queue)