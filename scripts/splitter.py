import os
import shutil
import random

# Your main dataset folder where images are currently stored
original_dataset_dir = "data"  # Change this to your actual raw folder name
base_dir = "dataset"  # This will have 'train' and 'val'

labels = ["Hello","I Love You", "No","Ok","Please","Yes"]
split_ratio = 0.8  # 80% training, 20% validation

for label in labels:
    images = os.listdir(os.path.join(original_dataset_dir, label))
    random.shuffle(images)

    split_point = int(len(images) * split_ratio)
    train_images = images[:split_point]
    val_images = images[split_point:]

    for split in ['train', 'val']:
        split_dir = os.path.join(base_dir, split, label)
        os.makedirs(split_dir, exist_ok=True)

    for img in train_images:
        src = os.path.join(original_dataset_dir, label, img)
        dst = os.path.join(base_dir, 'train', label, img)
        shutil.copy2(src, dst)

    for img in val_images:
        src = os.path.join(original_dataset_dir, label, img)
        dst = os.path.join(base_dir, 'val', label, img)
        shutil.copy2(src, dst)

print("Dataset split complete.")