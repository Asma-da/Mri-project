import os
import matplotlib.pyplot as plt
from PIL import Image

base_dir = './dataset'
tumor_types = os.listdir(base_dir)

# Count images per class
counts = {}
for tumor in tumor_types:
    tumor_folder = os.path.join(base_dir, tumor)
    counts[tumor] = len([img for img in os.listdir(tumor_folder) if img.endswith('.png')])

# Bar plot
plt.figure(figsize=(8, 5))
plt.bar(counts.keys(), counts.values(), color='skyblue')
plt.title('Number of Images per Tumor Type')
plt.xlabel('Tumor Type')
plt.ylabel('Image Count')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Show sample image from each class
for tumor in tumor_types:
    tumor_folder = os.path.join(base_dir, tumor)
    sample_image = Image.open(os.path.join(tumor_folder, os.listdir(tumor_folder)[0]))
    plt.imshow(sample_image)
    plt.title(f"Sample - {tumor}")
    plt.axis("off")
    plt.show()
