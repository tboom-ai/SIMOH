import json
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np
import matplotlib as mpl

class BIMinterpreter:
    # Initialize zone data & set up the plot
    def __init__(self):
        self.json_file = "assets/BIM.json" 
        self.wall_coordinates = self.load_wall_data()
        self.zone_data = self.load_zone_data()
        self.max_hazards = self.get_max_hazards()
        self.fig, self.ax1 = plt.subplots(1, 1, figsize=(10, 5)) 
        self.ax_text = None 
        self.cid = None

    # Load walls 
    def load_wall_data(self):
        import P1_BIM as BIM
        return BIM.plan

    # Load zones
    def load_zone_data(self):
        with open(self.json_file, 'r') as f:
            return json.load(f)

    # Get the max. number of hazards to scale the colors
    def get_max_hazards(self):
        return max(round(info['amount_of_hazards']) for info in self.zone_data.values())

    # Generate shades of color based on hazard count
    def get_red_color(self, hazard_count):
        normalized_value = hazard_count / self.max_hazards if self.max_hazards > 0 else 0
        r = 1 - (normalized_value * 0.5)  # Value decreases slightly
        g = 0.5 - (normalized_value * 0.5)
        b = 0.5 - (normalized_value * 0.5)
        return (r, g, b, 0.6)  # Adding transparency 

    # Display a text message under the image
    def display_message(self, zone_name, helmet_hazard_count):
        if self.ax_text:
            self.ax_text.remove()  # Remove the old text

        # Create the new message based on helmet_hazard_count
        if helmet_hazard_count == 0:
            message = f'No persons without helmets detected in {zone_name}.'
        elif helmet_hazard_count == 1:
            message = f'1 person without helmet detected in {zone_name}.'
        else:
            message = f'{helmet_hazard_count} persons without helmets detected in {zone_name}.'

        # Add the new text message below the heatmap
        self.ax_text = self.fig.text(0.5, 0.05, message, ha='center', va='bottom', fontsize=11, color='black')
        plt.draw()  

    # Clicking on a zone in the heatmap
    def on_click(self, event):
        if event.inaxes == self.ax1:
            x_click, y_click = event.xdata, event.ydata
            for zone_name, info in self.zone_data.items():
                x_zone, y_zone = info['location']
                if np.hypot(x_click - x_zone, y_click - y_zone) < 50: 
                    # Use 'amount_of_hazards' for helmet hazard count
                    helmet_hazard_count = info['amount_of_hazards']
                    
                    # Display message based on the hazard count
                    self.display_message(zone_name, helmet_hazard_count)

    # Plot walls using boundary points
    def plot_walls(self):
        for wall in self.wall_coordinates:
            # Extract x and y coordinates
            polygon = Polygon(wall, closed=True, color='darkgrey')
            self.ax1.add_patch(polygon)

    # Plot zones and hazards
    def plot_zones(self):
        for zone_name, zone_info in self.zone_data.items():
            boundary_points = zone_info.get('boundary', [])
            if not boundary_points:
                continue

            # Create a polygon for the zone
            polygon = Polygon(boundary_points, color='lightgrey', closed=True, fill=True, alpha=0.3)
            self.ax1.add_patch(polygon)

            # Calculate the center for placing the text
            xs, ys = zip(*boundary_points)
            centroid_x = sum(xs) / len(xs)
            centroid_y = sum(ys) / len(ys)

            # Add the label to the plot
            self.ax1.text(centroid_x, centroid_y-60, f'{zone_name}', horizontalalignment='center', verticalalignment='center', fontsize=8)

    # Draw the initial visualizations
    def draw(self):
        # Subplot 1: Walls and zones
        self.plot_walls()  # Plot the walls
        self.plot_zones()  # Plot the zones

        # Plot hazard markers
        for zone, info in self.zone_data.items():
            x, y = info['location']
            hazards = round(info['amount_of_hazards'])

            if hazards > 0:  # Only plot zones with 1 or more hazards
                color = self.get_red_color(hazards)
                size = 100 + hazards * 300
                self.ax1.scatter(x, y, s=size, c=[color])

            # Plot the black dot and add text labels
            self.ax1.scatter(x, y, s=30, c='black')

        # Create the color legend for the heatmap
        cmap = mpl.colors.LinearSegmentedColormap.from_list("", ["lightcoral", "darkred"])
        norm = mpl.colors.Normalize(vmin=1, vmax=self.max_hazards)
        cbar = plt.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), ax=self.ax1, shrink=0.5)

        # Calculate evenly spaced ticks
        num_ticks = 5  
        ticks = np.linspace(1, self.max_hazards, num_ticks).astype(int) 

        # Set ticks and labels
        cbar.set_ticks(ticks)
        cbar.set_ticklabels([str(i) for i in ticks])

        cbar.set_label('Amount of Hazards', fontsize=10, rotation=90, labelpad=1)
        cbar.ax.yaxis.set_label_position('left')

        self.ax1.set_title('Hazard Heatmap per Zone')
        self.ax1.axis('off')

        # Connect the click event to the heatmap
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.on_click)

        # Avoid overlapping and ensure equal sizing
        plt.subplots_adjust(left=0.05, right=0.95, wspace=0.3)

        plt.show()

    # Disconnect the click event if needed
    def disconnect_click_event(self):
        if self.cid is not None:
            self.fig.canvas.mpl_disconnect(self.cid)
            self.cid = None

# Check the script and create heatmap
if __name__ == "__main__":
    visualizer = BIMinterpreter()
    visualizer.draw()
