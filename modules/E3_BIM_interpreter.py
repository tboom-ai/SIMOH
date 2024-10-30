import json
import cv2
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl

# Heatmap with amount of hazards per zone
class ConstructionHazardVisualizer:
    # Determine hazard visualization, load zone data & set up the plot
    def __init__(self):
        self.json_file = "assets/BIM.json" 
        self.zone_data = self.load_zone_data()
        self.max_hazards = self.get_max_hazards()
        self.fig, self.ax1 = plt.subplots(1, 1, figsize=(12, 6))  #
        self.ax_text = None 
        self.construction_site = self.load_image()
        self.cid = None

    # Load zone data from the JSON file
    def load_zone_data(self):
        with open(self.json_file, 'r') as f:
            return json.load(f)

    # Get the max. number of hazards to scale the colors
    def get_max_hazards(self):
        return max(round(info['amount_of_hazards']) for info in self.zone_data.values())

    # Load the image using the floorplan path from the JSON
    def load_image(self):
        first_zone = list(self.zone_data.values())[0]  # Get the first zone's data
        construction_site = first_zone["floorplan"]  # Extract the floorplan path from the JSON
        img = cv2.imread(construction_site)
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

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

    # Draw the initial visualizations
    def draw(self):
        # Subplot 1: Heatmap on construction site plan
        self.ax1.imshow(self.construction_site)

        # Plot the heatmap markers
        for zone, info in self.zone_data.items():
            x, y = info['location']
            hazards = round(info['amount_of_hazards'])

            if hazards > 0:  # Only plot zones with 1 or more hazards
                color = self.get_red_color(hazards)
                size = 100 + hazards * 300
                self.ax1.scatter(x, y, s=size, c=[color])

            # Plot the black dot and add text labels
            self.ax1.scatter(x, y, s=30, c='black')
            self.ax1.text(x + 40, y + 40, f'{zone}', color='black', fontsize=10, ha='center')

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

        cbar.set_label('Amount of Hazards', fontsize=10, rotation=90, labelpad=1)
        cbar.ax.yaxis.set_label_position('left')

        self.ax1.set_title('Amount of Hazards per Zone')
        self.ax1.axis('off')

        # Invert the y axis to match coordiante system
        # self.ax1.invert_yaxis()

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
    visualizer = ConstructionHazardVisualizer()
    visualizer.draw()
