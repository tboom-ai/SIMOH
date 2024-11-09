import os

# Define the path to the hammer dataset (labels directory)
labels_path = r"C:\Users\tombo\Documents\BT MSc\Msc3\Safetybot\optobot.v6i.yolov8\train\labels"  # Update this path

# Function to update class index from 3 to 0
def update_hammer_class(label_path):
    with open(label_path, 'r') as file:
        lines = file.readlines()

    # Rewrite the labels with updated class index
    with open(label_path, 'w') as file:
        for line in lines:
            class_id, *bbox = line.split()
            if class_id == '3':  # Update hammer class from 3 to 0
                class_id = '0'
            file.write(f"{class_id} {' '.join(bbox)}\n")

# Iterate over all label files and update class indices
for label_file in os.listdir(labels_path):
    if label_file.endswith('.txt'):
        label_path = os.path.join(labels_path, label_file)
        update_hammer_class(label_path)

print("Class indices updated from 3 to 0 for hammer class.")
