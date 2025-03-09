import os
import random
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import time


train_dir = 'C:/Users/da3bess/Downloads/archive (3)/data2/Training'
test_dir = 'C:/Users/da3bess/Downloads/archive (3)/data2/Testing'


output_folder = "eda_output"
os.makedirs(output_folder, exist_ok=True)



def load_image_paths(directory):
    paths = []
    labels = []
    for label in os.listdir(directory):
        label_dir = os.path.join(directory, label)
        if os.path.isdir(label_dir):
            for image_name in os.listdir(label_dir):
                image_path = os.path.join(label_dir, image_name)
                paths.append(image_path)
                labels.append(label)
    return paths, labels



train_paths, train_labels = load_image_paths(train_dir)
test_paths, test_labels = load_image_paths(test_dir)

print(f"Number of training images: {len(train_paths)}")
print(f"Number of testing images: {len(test_paths)}")
print(f"Training classes: {set(train_labels)}")
print(f"Testing classes: {set(test_labels)}")


def count_images_class(paths, labels):
    class_counts = {}
    for label in set(labels):
        class_counts[label] = labels.count(label)
    return class_counts


train_class_counts = count_images_class(train_paths, train_labels)
test_class_counts = count_images_class(test_paths, test_labels)



def plot_class_distribution(class_counts, title, filename):
    plt.bar(class_counts.keys(), class_counts.values())
    plt.xlabel("Class")
    plt.ylabel("Number of Images")
    plt.title(title)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, filename))
    plt.close()


print("Plotting class distribution for training data...")
plot_class_distribution(train_class_counts, "Class Distribution in Training Data", "class_distribution_train.png")
time.sleep(2)

print("Plotting class distribution for testing data...")
plot_class_distribution(test_class_counts, "Class Distribution in Testing Data", "class_distribution_test.png")
time.sleep(2)



def display_sample_images(paths, labels, num_samples=5, filename="sample_images.png"):
    unique_labels = set(labels)
    plt.figure(figsize=(15, 10))
    for i, label in enumerate(unique_labels):
        label_paths = [path for path, lbl in zip(paths, labels) if lbl == label]
        sample_paths = random.sample(label_paths, min(num_samples, len(label_paths)))
        for j, path in enumerate(sample_paths):
            img = Image.open(path)
            plt.subplot(len(unique_labels), num_samples, i * num_samples + j + 1)
            plt.imshow(img , cmap='gray')
            plt.title(f"{label}\n{img.size}")
            plt.axis('off')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, filename))
    plt.close()


print("Displaying sample images from training data...")
display_sample_images(train_paths, train_labels, filename="sample_images_train.png")
time.sleep(2)

print("Displaying sample images from testing data...")
display_sample_images(test_paths, test_labels, filename="sample_images_test.png")
time.sleep(2)


def analyze_image_size(paths):
    sizes = []
    for path in paths:
        img = Image.open(path)
        sizes.append(img.size)
    sizes = np.array(sizes)
    print(
        f"Image sizes (width, height):\nMin: {sizes.min(axis=0)}\nMax: {sizes.max(axis=0)}\nMean: {sizes.mean(axis=0)}")
    return sizes


def image_size_distribution(sizes, title, filename):

    widths, heights = sizes[:, 0], sizes[:, 1]
    plt.figure(figsize=(12, 6))

    plt.subplot(1, 2, 1)
    plt.hist(widths, bins=30, color='blue', alpha=0.7)
    plt.xlabel("Width")
    plt.ylabel("Frequency")
    plt.title(f"{title} - Width Distribution")


    plt.subplot(1, 2, 2)
    plt.hist(heights, bins=30, color='green', alpha=0.7)
    plt.xlabel("Height")
    plt.ylabel("Frequency")
    plt.title(f"{title} - Height Distribution")

    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, filename))
    plt.close()


print("Plotting image size distribution for training data...")
train_sizes = analyze_image_size(train_paths)
image_size_distribution(train_sizes, "Training Data", "image_size_distribution_train.png")
time.sleep(2)

print("Plotting image size distribution for testing data...")
test_sizes = analyze_image_size(test_paths)
image_size_distribution(test_sizes, "Testing Data", "image_size_distribution_test.png")
time.sleep(2)



def analyze_pixel_intensity(paths, batch_size=100):

    min_val, max_val, mean_val, std_val = None, None, None, None
    pixel_count = 0
    pixel_sum = 0
    pixel_squared_sum = 0

    for i in range(0, len(paths), batch_size):
        batch_paths = paths[i:i + batch_size]
        batch_pixels = []
        for path in batch_paths:
            img = Image.open(path)
            img_array = np.array(img) / 255.0  # Normalize to [0, 1]
            batch_pixels.extend(img_array.flatten())

        batch_pixels = np.array(batch_pixels)
        if min_val is None:
            min_val = batch_pixels.min()
            max_val = batch_pixels.max()
        else:
            min_val = min(min_val, batch_pixels.min())
            max_val = max(max_val, batch_pixels.max())

        pixel_count += len(batch_pixels)
        pixel_sum += batch_pixels.sum()
        pixel_squared_sum += np.square(batch_pixels).sum()

    mean_val = pixel_sum / pixel_count
    std_val = np.sqrt((pixel_squared_sum / pixel_count) - (mean_val ** 2))

    print(f"Pixel intensity statistics:\nMin: {min_val}\nMax: {max_val}\nMean: {mean_val}\nStd: {std_val}")


def pixel_intensity_distribution(paths, title, filename, batch_size=100, num_bins=50):


    bin_edges = np.linspace(0, 1, num_bins + 1)
    histogram = np.zeros(num_bins, dtype=int)

    for i in range(0, len(paths), batch_size):
        batch_paths = paths[i:i + batch_size]
        batch_pixels = []
        for path in batch_paths:
            img = Image.open(path)
            img_array = np.array(img) / 255.0
            batch_pixels.extend(img_array.flatten())


        batch_hist, _ = np.histogram(batch_pixels, bins=bin_edges)
        histogram += batch_hist


    plt.figure(figsize=(12, 6))
    plt.bar(bin_edges[:-1], histogram, width=np.diff(bin_edges), color='red', alpha=0.7)
    plt.xlabel("Pixel Intensity")
    plt.ylabel("Frequency")
    plt.title(f"{title} - Pixel Intensity Distribution")
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, filename))
    plt.close()


print("Analyzing pixel intensity for training data...")
analyze_pixel_intensity(train_paths, batch_size=100)
pixel_intensity_distribution(train_paths, "Training Data", "pixel_intensity_distribution_train.png", batch_size=100)
time.sleep(2)

print("Analyzing pixel intensity for testing data...")
analyze_pixel_intensity(test_paths, batch_size=100)
pixel_intensity_distribution(test_paths, "Testing Data", "pixel_intensity_distribution_test.png", batch_size=100)
time.sleep(2)

