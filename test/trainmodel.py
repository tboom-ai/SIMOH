from ultralytics import YOLO

# Load the model
model = YOLO('yolov8s.pt')  

# Train the model
results = model.train(
    data='/Users/tombo/Documents/CORE/Safetybot/helmet_nohelmet.yaml',
    epochs=50,  # Adjust based on the dataset size and complexity
    imgsz=640,  # Image size for training 
    batch=16,  # Batch size
    workers=8,  # Number of workers for parallel data loading.
    device='mps',  # For apple: Use MPS to leverage the Apple GPU
    cache=True,  # Cache dataset in RAM for faster loading during training
    optimizer='AdamW',  # AdamW optimizer is a good balance for training speed and performance
    project='/Users/tombo/Documents/CORE/Safetybot/runs/train',  
    name='helmet_nohelmet',  
    exist_ok=True,  # Allow overwriting of previous runs with the same name
    patience=5,  # Early stopping when model is not improving
    resume=True
)
