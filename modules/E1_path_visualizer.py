import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.animation import FuncAnimation
from multiprocessing import Queue
# Import from other scripts
from E1_robot_path import simulate_robot_path
from E1_hazard_detection import load_json
import P1_BIM as BIM

# Get wall coordinates from BIM (ultimately)
wall_coordinates = BIM.plan

def get_boundary_points(zone):
    """Extract boundary points from the zone data"""
    
    # Retrieve the boundary points directly as a list of tuples
    boundary = zone.get('boundary', [])

    # Ensure the boundary is a list of points, otherwise empty list
    return boundary if isinstance(boundary, list) else []

def plot_zones(ax, zones):
    """Plot all zones"""

    for zone_name, zone_info in zones.items():
        boundary_points = get_boundary_points(zone_info)
        if not boundary_points:
            print(f"Warning: No boundary points found for {zone_name}. Skipping.")
            continue
        
        # Create a polygon for the zone
        polygon = Polygon(boundary_points, color='red', closed=True, fill=True, alpha=0.3)
        ax.add_patch(polygon)
        
        # Calculate the centre for placing the text
        xs, ys = zip(*boundary_points)
        centroid_x = sum(xs) / len(xs)
        centroid_y = sum(ys) / len(ys)
        
        # Prepare the label with zone name and required PPE
        required_PPE = zone_info.get('required_PPE', 'None')
        label = f"{zone_name}\nPPE: {required_PPE}"
        
        # Add the label to the plot
        ax.text(centroid_x, centroid_y, label, horizontalalignment='center', verticalalignment='center', fontsize=4, bbox=dict(color='white', alpha=0.6))
        
def plot_walls(ax, wall_coordinates, color='lightgrey', alpha=0.8):
    """Plot the walls"""

    for wall in wall_coordinates:
        # Extract x and y coordinates
        polygon = Polygon(wall, closed=True, color=color, alpha=alpha)
        ax.add_patch(polygon)

def plot_robot_path(ax, path, color='blue', linewidth=2, label='Robot Path'):
    """Plot the robot path on the given axis."""

    # Extract x and y coordinates, adjusting y to account for image coordinate inversion
    x_coords = [position[0] for position in path]
    y_coords = [position[1] for position in path]  # Invert path on y axis
    
    # Plot the path and scatter the points
    ax.plot(x_coords, y_coords, color=color, linewidth=linewidth, label=label)
    ax.legend()  # Optional: add a legend to identify the path

def main(position_queue):
    """Main function to visualize zones and robot path."""

    # Path to the JSON file containing zone information
    BIM_DATA = 'assets/BIM.json'  # Update this path if necessary

    # Load zone data
    zones = load_json(BIM_DATA)

    # Initialize the plot
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_title('Building Site Visualization')
    ax.set_xlabel('x coordinate')
    ax.set_ylabel('y coordinate')
    
    # Plot walls
    plot_walls(ax,wall_coordinates)

    # Plot zones
    plot_zones(ax, zones)

    # Simulate and plot robot path live
    robot_path = list(simulate_robot_path())
    plot_robot_path(ax, robot_path)
    
    # Initialize moving dot
    moving_dot, = ax.plot([], [], 'ro', label='Current Position') # ro = red dot
    ax.legend()

    # Customize the plot
    ax.set_aspect('equal', 'box')

    def init():
        moving_dot.set_data([], [])
        return moving_dot,

    def update(frame):
        while not position_queue.empty():
            current_position = position_queue.get()
            moving_dot.set_data([current_position[0]], [current_position[1]])
        return moving_dot,

    ani = FuncAnimation(fig, update, init_func=init, blit=True, interval=50)
    plt.show()

if __name__ == "__main__":
   position_queue = Queue()
   main(position_queue)
    
