import os
import xml.etree.ElementTree as ET
import cv2

# Define paths for training, validation, and test datasets
datasets = {
    'train': {
        'images_dir': r'C:\Users\tombo\Documents\BT MSc\Msc3\Safetybot\data\images\train',
        'annotations_dir': r'C:\Users\tombo\Documents\BT MSc\Msc3\Safetybot\data\labels\train',
        'yolo_labels_dir': r'C:\Users\tombo\Documents\BT MSc\Msc3\Safetybot\data\labels_yolo\train'
    },
    'val': {
        'images_dir': r'C:\Users\tombo\Documents\BT MSc\Msc3\Safetybot\data\images\val',
        'annotations_dir': r'C:\Users\tombo\Documents\BT MSc\Msc3\Safetybot\data\labels\val',
        'yolo_labels_dir': r'C:\Users\tombo\Documents\BT MSc\Msc3\Safetybot\data\labels_yolo\val'
    },
    'test': {
        'images_dir': r'C:\Users\tombo\Documents\BT MSc\Msc3\Safetybot\data\images\test',
        'annotations_dir': r'C:\Users\tombo\Documents\BT MSc\Msc3\Safetybot\data\labels\test',
        'yolo_labels_dir': r'C:\Users\tombo\Documents\BT MSc\Msc3\Safetybot\data\labels_yolo\test'
    }
}

# Define a mapping of classes
class_mapping = {
    'helmet': 0,
    'head': 1,
    'person': 2
}

# Function to convert Pascal VOC bbox format to YOLO format
def convert_bbox_to_yolo_format(xmin, ymin, xmax, ymax, img_width, img_height):
    x_center = (xmin + xmax) / 2 / img_width
    y_center = (ymin + ymax) / 2 / img_height
    width = (xmax - xmin) / img_width
    height = (ymax - ymin) / img_height
    return x_center, y_center, width, height

# Iterate over datasets
for dataset, paths in datasets.items():
    images_dir = paths['images_dir']
    annotations_dir = paths['annotations_dir']
    yolo_labels_dir = paths['yolo_labels_dir']

    # Create the YOLO labels directory if it doesn't exist
    os.makedirs(yolo_labels_dir, exist_ok=True)

    # Iterate over all XML files in your annotations directory
    for xml_file in os.listdir(annotations_dir):
        if not xml_file.endswith('.xml'):
            continue
        
        # Parse the XML file
        tree = ET.parse(os.path.join(annotations_dir, xml_file))
        root = tree.getroot()

        # Get the corresponding image file
        img_filename = root.find('filename').text
        img_path = os.path.join(images_dir, img_filename)
        img = cv2.imread(img_path)

        if img is None:
            print(f"Warning: Image {img_path} not found.")
            continue

        img_height, img_width = img.shape[:2]

        # Open the corresponding YOLO format annotation file
        txt_filename = os.path.splitext(img_filename)[0] + '.txt'
        with open(os.path.join(yolo_labels_dir, txt_filename), 'w') as f:
            # Iterate through all object elements in the XML
            for obj in root.findall('object'):
                class_name = obj.find('name').text
                if class_name not in class_mapping:
                    continue  # Skip if class is not in the defined class_mapping

                # Get class ID
                class_id = class_mapping[class_name]

                # Get bounding box coordinates (Pascal VOC format)
                bbox = obj.find('bndbox')
                xmin = int(bbox.find('xmin').text)
                ymin = int(bbox.find('ymin').text)
                xmax = int(bbox.find('xmax').text)
                ymax = int(bbox.find('ymax').text)

                # Convert bounding box to YOLO format
                x_center, y_center, width, height = convert_bbox_to_yolo_format(xmin, ymin, xmax, ymax, img_width, img_height)

                # Write to the YOLO format annotation file
                f.write(f"{class_id} {x_center} {y_center} {width} {height}\n")

print("Annotations converted to YOLO format for all datasets.")
