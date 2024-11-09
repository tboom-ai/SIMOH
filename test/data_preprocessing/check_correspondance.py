import os

# Define paths
train_dir = r'C:\Users\tombo\Documents\BT MSc\Msc3\Safetybot\data\images\train'
val_dir = r'C:\Users\tombo\Documents\BT MSc\Msc3\Safetybot\data\images\val'
test_dir = r'C:\Users\tombo\Documents\BT MSc\Msc3\Safetybot\data\images\test'

train_labels_dir = r'C:\Users\tombo\Documents\BT MSc\Msc3\Safetybot\data\labels\train'
val_labels_dir = r'C:\Users\tombo\Documents\BT MSc\Msc3\Safetybot\data\labels\val'
test_labels_dir = r'C:\Users\tombo\Documents\BT MSc\Msc3\Safetybot\data\labels\test'

# Function to check correspondence
def check_correspondence(images_dir, labels_dir):
    images = [f for f in os.listdir(images_dir) if f.endswith('.png')]
    labels = [f for f in os.listdir(labels_dir) if f.endswith('.txt')]

    missing_labels = [img for img in images if img.replace('.png', '.txt') not in labels]
    missing_images = [label for label in labels if label.replace('.txt', '.png') not in images]

    if not missing_labels and not missing_images:
        print(f"All images and labels in '{images_dir}' and '{labels_dir}' match.")
    else:
        if missing_labels:
            print(f"Missing labels for images: {missing_labels}")
        if missing_images:
            print(f"Missing images for labels: {missing_images}")

# Check each set
check_correspondence(train_dir, train_labels_dir)
check_correspondence(val_dir, val_labels_dir)
check_correspondence(test_dir, test_labels_dir)
