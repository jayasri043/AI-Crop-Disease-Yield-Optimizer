from pathlib import Path
import random
import shutil

# Source dataset
SOURCE = Path(
    "data/disease/PlantVillage-Dataset/raw/color"
)

# Output dataset
OUTPUT = Path(
    "ml/dataset/crop_disease"
)

# 9 target classes
CLASSES = [
    "Pepper,_bell___Bacterial_spot",
    "Pepper,_bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___healthy",
]

# Split ratios
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

random.seed(42)

# Create output folders
for split in ["train", "val", "test"]:
    for class_name in CLASSES:
        (OUTPUT / split / class_name).mkdir(
            parents=True,
            exist_ok=True
        )

print("Starting dataset split...\n")

for class_name in CLASSES:

    source_folder = SOURCE / class_name

    if not source_folder.exists():
        print(f"ERROR: Class folder not found: {class_name}")
        continue

    images = [
        file for file in source_folder.iterdir()
        if file.is_file()
    ]

    random.shuffle(images)

    total = len(images)

    train_end = int(total * TRAIN_RATIO)
    val_end = train_end + int(total * VAL_RATIO)

    train_images = images[:train_end]
    val_images = images[train_end:val_end]
    test_images = images[val_end:]

    splits = {
        "train": train_images,
        "val": val_images,
        "test": test_images
    }

    print(f"{class_name}")
    print(f"  Total : {total}")
    print(f"  Train : {len(train_images)}")
    print(f"  Val   : {len(val_images)}")
    print(f"  Test  : {len(test_images)}")

    for split_name, split_images in splits.items():

        destination = OUTPUT / split_name / class_name

        for image_file in split_images:
            shutil.copy2(
                image_file,
                destination / image_file.name
            )

    print()

print("===================================")
print("Dataset split completed successfully!")
print("===================================")