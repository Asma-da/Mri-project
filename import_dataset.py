import os
from datasets import load_dataset
from PIL import Image

# Load the dataset
ds = load_dataset("Hemg/Brain-Tumor-MRI-Dataset")

# Define the base directory for saving images
base_dir = './dataset'

# Tumor types (from the dataset feature)
labels = ds['train'].features['label'].names

# Create a subfolder for each tumor type if it doesn't exist
for label in labels:
    os.makedirs(os.path.join(base_dir, label), exist_ok=True)

# Loop through the dataset and save images in respective tumor type folders
for i in range(len(ds['train'])):
    image = ds['train'][i]['image']
    label = ds['train'][i]['label']
    label_text = labels[label]  # Get tumor type name

    # Create the path for saving the image in the appropriate folder
    save_path = os.path.join('./dataset', label_text, f'image_{i}_{label_text}.png')

    # Save the image
    image.save(save_path)

print(f"Saved {len(ds['train'])} images to their respective tumor type folders.")
