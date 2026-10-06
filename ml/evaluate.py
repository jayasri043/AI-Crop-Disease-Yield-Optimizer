from pathlib import Path

import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from torchvision.models import MobileNet_V3_Small_Weights

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)


# ==========================================
# 1. Paths
# ==========================================

DATA_DIR = Path("ml/dataset/crop_disease")
MODEL_PATH = Path(
    "backend/models/disease_model/best_model.pth"
)


# ==========================================
# 2. Device
# ==========================================

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("Device:", device)


# ==========================================
# 3. Transform
# ==========================================

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# ==========================================
# 4. Test dataset
# ==========================================

test_dataset = datasets.ImageFolder(
    DATA_DIR / "test",
    transform=transform
)

test_loader = DataLoader(
    test_dataset,
    batch_size=32,
    shuffle=False,
    num_workers=0
)


print("\nTest images:", len(test_dataset))

print("\nClasses:")

for index, class_name in enumerate(
    test_dataset.classes
):
    print(index, "->", class_name)


# ==========================================
# 5. Load MobileNetV3
# ==========================================

print("\nLoading model...")

model = models.mobilenet_v3_small(
    weights=None
)

model.classifier[3] = torch.nn.Linear(
    model.classifier[3].in_features,
    len(test_dataset.classes)
)


# ==========================================
# 6. Load trained weights
# ==========================================

checkpoint = torch.load(
    MODEL_PATH,
    map_location=device
)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model = model.to(device)

model.eval()


print("Model loaded successfully!")


# ==========================================
# 7. Prediction
# ==========================================

all_labels = []
all_predictions = []

print("\nEvaluating test dataset...\n")


with torch.no_grad():

    for images, labels in test_loader:

        images = images.to(device)

        outputs = model(images)

        predictions = outputs.argmax(
            dim=1
        )

        all_labels.extend(
            labels.numpy()
        )

        all_predictions.extend(
            predictions.cpu().numpy()
        )


# ==========================================
# 8. Accuracy
# ==========================================

accuracy = accuracy_score(
    all_labels,
    all_predictions
)

print("===================================")
print(
    f"Test Accuracy: {accuracy * 100:.2f}%"
)
print("===================================")


# ==========================================
# 9. Classification report
# ==========================================

print("\nClassification Report:\n")

print(
    classification_report(
        all_labels,
        all_predictions,
        target_names=test_dataset.classes,
        digits=4
    )
)


# ==========================================
# 10. Confusion Matrix
# ==========================================

matrix = confusion_matrix(
    all_labels,
    all_predictions
)

print("\nConfusion Matrix:\n")

print(matrix)


# ==========================================
# 11. Completed
# ==========================================

print("\n===================================")
print("Evaluation completed successfully!")
print("===================================")