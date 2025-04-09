import os
import cv2
import numpy as np


def preprocess_image(image_path, output_path, target_size=(224, 224)):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Failed to load image: {image_path}")

    # Resize and normalize to [0, 1]
    img = cv2.resize(img, target_size)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype(np.float32) / 255.0

    img_uint8 = (img * 255).astype(np.uint8)
    cv2.imwrite(image_path, cv2.cvtColor(img_uint8, cv2.COLOR_RGB2BGR))  # Convert back to [0,255] for saving


# Process all images in the dataset
input_dir = './dataset'
for label in os.listdir(input_dir):
    label_dir = os.path.join(input_dir, label)
    if not os.path.isdir(label_dir):
        continue

    for img_name in os.listdir(label_dir):
        if img_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            img_path = os.path.join(label_dir, img_name)
            preprocess_image(img_path, img_path)  # Overwrite original

print(" Preprocessing complete (images resized to 224x224 and normalized).")