import os

# Define the path to your dataset labels
label_dir = r"C:\Users\tombo\Documents\BT MSc\Msc3\Safetybot\data_helmetheadperson\labels\val"  # Change to your actual label path

# Loop over all label files in the directory
for label_file in os.listdir(label_dir):
    label_path = os.path.join(label_dir, label_file)

    # Read the content of the label file
    with open(label_path, 'r') as f:
        lines = f.readlines()

    # Filter out any lines where the class_id is 2 (person)
    new_lines = [line for line in lines if line.startswith('0') or line.startswith('1')]

    # Write the filtered annotations back to the file
    with open(label_path, 'w') as f:
        f.writelines(new_lines)

print("Finished filtering out class 2 (person) annotations.")
