import os
import shutil
import random

# Define paths
annotations_dir = r'C:\Users\tombo\Documents\BT MSc\Msc3\Safetybot\archive\annotations'  # The folder where all labels are
train_dir = r'C:\Users\tombo\Documents\BT MSc\Msc3\Safetybot\data\images\train'
val_dir = r'C:\Users\tombo\Documents\BT MSc\Msc3\Safetybot\data\images\val'
test_dir = r'C:\Users\tombo\Documents\BT MSc\Msc3\Safetybot\data\images\test'

# Create label directories if they don't exist
train_labels_dir = r'C:\Users\tombo\Documents\BT MSc\Msc3\Safetybot\data\labels\train'
val_labels_dir = r'C:\Users\tombo\Documents\BT MSc\Msc3\Safetybot\data\labels\val'
test_labels_dir = r'C:\Users\tombo\Documents\BT MSc\Msc3\Safetybot\data\labels\test'

os.makedirs(train_labels_dir, exist_ok=True)
os.makedirs(val_labels_dir, exist_ok=True)
os.makedirs(test_labels_dir, exist_ok=True)

# Get a list of all training, validation, and test images
train_images = [f for f in os.listdir(train_dir) if f.endswith('.png')]
val_images = [f for f in os.listdir(val_dir) if f.endswith('.png')]
test_images = [f for f in os.listdir(test_dir) if f.endswith('.png')]

# Move labels for training images
for img in train_images:
    label_filename = img.replace('.png', '.xml')  # Assuming label has same name as image
    shutil.move(os.path.join(annotations_dir, label_filename), os.path.join(train_labels_dir, label_filename))

# Move labels for validation images
for img in val_images:
    label_filename = img.replace('.png', '.xml')
    shutil.move(os.path.join(annotations_dir, label_filename), os.path.join(val_labels_dir, label_filename))

# Move labels for test images
for img in test_images:
    label_filename = img.replace('.png', '.xml')
    shutil.move(os.path.join(annotations_dir, label_filename), os.path.join(test_labels_dir, label_filename))

print("Labels moved to their respective directories.")
