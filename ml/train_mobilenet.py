from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms
from torchvision.models import MobileNet_V3_Small_Weights


# ==========================================
# 1. Paths
# ==========================================

DATA_DIR = Path("ml/dataset/crop_disease")
MODEL_DIR = Path("backend/models/disease_model")

MODEL_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================
# 2. Device
# ==========================================

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print("Device:", device)


# ==========================================
# 3. Image transformations
# ==========================================

weights = MobileNet_V3_Small_Weights.DEFAULT

train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.ColorJitter(
        brightness=0.2,
        contrast=0.2,
        saturation=0.2
    ),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


val_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# ==========================================
# 4. Load datasets
# ==========================================

train_dataset = datasets.ImageFolder(
    DATA_DIR / "train",
    transform=train_transform
)

val_dataset = datasets.ImageFolder(
    DATA_DIR / "val",
    transform=val_transform
)


print("\nClasses:")
for index, class_name in enumerate(train_dataset.classes):
    print(index, "->", class_name)


print("\nTraining images:", len(train_dataset))
print("Validation images:", len(val_dataset))


# ==========================================
# 5. Data loaders
# ==========================================

train_loader = DataLoader(
    train_dataset,
    batch_size=32,
    shuffle=True,
    num_workers=0
)

val_loader = DataLoader(
    val_dataset,
    batch_size=32,
    shuffle=False,
    num_workers=0
)


# ==========================================
# 6. Class weights
# ==========================================

class_counts = [0] * len(train_dataset.classes)

for _, label in train_dataset.samples:
    class_counts[label] += 1


total_samples = sum(class_counts)

class_weights = [
    total_samples / (len(class_counts) * count)
    for count in class_counts
]

class_weights = torch.tensor(
    class_weights,
    dtype=torch.float32
).to(device)


print("\nClass weights:")
for class_name, weight in zip(
    train_dataset.classes,
    class_weights
):
    print(f"{class_name}: {weight.item():.3f}")


# ==========================================
# 7. Load pretrained MobileNetV3 Small
# ==========================================

print("\nLoading MobileNetV3 Small...")

model = models.mobilenet_v3_small(
    weights=weights
)


# ==========================================
# 8. Replace classifier
# ==========================================

number_of_classes = len(train_dataset.classes)

model.classifier[3] = nn.Linear(
    model.classifier[3].in_features,
    number_of_classes
)

model = model.to(device)


# ==========================================
# 9. Loss and optimizer
# ==========================================

criterion = nn.CrossEntropyLoss(
    weight=class_weights
)

optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=0.0001,
    weight_decay=0.0001
)


# ==========================================
# 10. Training settings
# ==========================================

EPOCHS = 10

best_val_accuracy = 0.0


# ==========================================
# 11. Training loop
# ==========================================

print("\nStarting training...\n")


for epoch in range(EPOCHS):

    # -------------------------
    # Training
    # -------------------------

    model.train()

    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in train_loader:

        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()

        outputs = model(images)

        loss = criterion(
            outputs,
            labels
        )

        loss.backward()

        optimizer.step()

        running_loss += loss.item()

        predictions = outputs.argmax(
            dim=1
        )

        total += labels.size(0)

        correct += (
            predictions == labels
        ).sum().item()


    train_accuracy = (
        100.0 * correct / total
    )

    train_loss = (
        running_loss / len(train_loader)
    )


    # -------------------------
    # Validation
    # -------------------------

    model.eval()

    val_correct = 0
    val_total = 0

    with torch.no_grad():

        for images, labels in val_loader:

            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)

            predictions = outputs.argmax(
                dim=1
            )

            val_total += labels.size(0)

            val_correct += (
                predictions == labels
            ).sum().item()


    val_accuracy = (
        100.0 * val_correct / val_total
    )


    print(
        f"Epoch [{epoch + 1}/{EPOCHS}] "
        f"Loss: {train_loss:.4f} "
        f"Train Acc: {train_accuracy:.2f}% "
        f"Val Acc: {val_accuracy:.2f}%"
    )


    # -------------------------
    # Save best model
    # -------------------------

    if val_accuracy > best_val_accuracy:

        best_val_accuracy = val_accuracy

        torch.save(
            {
                "model_state_dict": model.state_dict(),
                "classes": train_dataset.classes,
                "image_size": 224
            },
            MODEL_DIR / "best_model.pth"
        )

        print(
            f"  ✓ Best model saved "
            f"(Val Acc: {val_accuracy:.2f}%)"
        )


# ==========================================
# 12. Training completed
# ==========================================

print("\n===================================")
print("Training completed!")
print("===================================")

print(
    f"Best Validation Accuracy: "
    f"{best_val_accuracy:.2f}%"
)

print(
    "Model saved at:",
    MODEL_DIR / "best_model.pth"
)