import os
import shutil

# Define the source directories for train, valid, and test sets
source_dirs = {
    'train_images': r'C:\Users\tombo\Documents\BT MSc\Msc3\Safetybot\optobot.v6i.yolov8\train\images',
    'train_labels': r'C:\Users\tombo\Documents\BT MSc\Msc3\Safetybot\optobot.v6i.yolov8\train\labels',
    'valid_images': r'C:\Users\tombo\Documents\BT MSc\Msc3\Safetybot\optobot.v6i.yolov8\valid\images',
    'valid_labels': r'C:\Users\tombo\Documents\BT MSc\Msc3\Safetybot\optobot.v6i.yolov8\valid\labels',
    'test_images': r'C:\Users\tombo\Documents\BT MSc\Msc3\Safetybot\optobot.v6i.yolov8\test\images',
    'test_labels': r'C:\Users\tombo\Documents\BT MSc\Msc3\Safetybot\optobot.v6i.yolov8\test\labels',
}

# Define the destination directories for combined data
destination_dirs = {
    'train_images': r'C:\path\to\combined\dataset\images\train',
    'train_labels': r'C:\path\to\combined\dataset\labels\train',
    'valid_images': r'C:\path\to\combined\dataset\images\valid',
    'valid_labels': r'C:\path\to\combined\dataset\labels\valid',
    'test_images': r'C:\path\to\combined\dataset\images\test',
    'test_labels': r'C:\path\to\combined\dataset\labels\test',
}

# Function to move files from source to destination
def move_files(source_dir, destination_dir):
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
        
    for filename in os.listdir(source_dir):
        src_file = os.path.join(source_dir, filename)
        dst_file = os.path.join(destination_dir, filename)
        
        if os.path.isfile(src_file):
            shutil.move(src_file, dst_file)
            print(f"Moved: {src_file} -> {dst_file}")

# Move train, valid, and test images and labels to corresponding directories
move_files(source_dirs['train_images'], destination_dirs['train_images'])
move_files(source_dirs['train_labels'], destination_dirs['train_labels'])

move_files(source_dirs['valid_images'], destination_dirs['valid_images'])
move_files(source_dirs['valid_labels'], destination_dirs['valid_labels'])

move_files(source_dirs['test_images'], destination_dirs['test_images'])
move_files(source_dirs['test_labels'], destination_dirs['test_labels'])

print("All files have been moved successfully!")
