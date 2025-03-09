import cv2
import numpy as np

def preprocess_image(image_data, target_size=(224, 224)):
    """
    Preprocess the MRI image in memory.
    - Resizes the image to the target size.
    - Normalizes the image by dividing pixel values by 255.

    Args:
    - image_data: The image as a NumPy array (grayscale or color).
    - target_size: The target size for resizing the image (default is 224x224).

    Returns:
    - normalized_image: The preprocessed image (resized and normalized).
    """
    if image_data is None:
        raise ValueError("Image could not be loaded or is empty")

    # Resize the image to the target size
    resized_image = cv2.resize(image_data, target_size)

    # Normalize the image by dividing pixel values by 255.0
    normalized_image = resized_image / 255.0

    return normalized_image
