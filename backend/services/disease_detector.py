from pathlib import Path

import torch
from PIL import Image
from torchvision import models, transforms


# ==========================================
# 1. Model path
# ==========================================

MODEL_PATH = Path(
    "backend/models/disease_model/best_model.pth"
)


# ==========================================
# 2. Confidence threshold
# ==========================================

CONFIDENCE_THRESHOLD = 60.0


# ==========================================
# 3. Device
# ==========================================

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ==========================================
# 4. Load checkpoint
# ==========================================

checkpoint = torch.load(
    MODEL_PATH,
    map_location=device
)

CLASSES = checkpoint["classes"]


# ==========================================
# 5. Create model
# ==========================================

model = models.mobilenet_v3_small(
    weights=None
)

model.classifier[3] = torch.nn.Linear(
    model.classifier[3].in_features,
    len(CLASSES)
)


# ==========================================
# 6. Load trained weights
# ==========================================

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model = model.to(device)

model.eval()


# ==========================================
# 7. Image preprocessing
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
# 8. Disease prediction function
# ==========================================

def predict_disease(image_path):

    image = Image.open(
        image_path
    ).convert("RGB")

    image_tensor = transform(
        image
    )

    image_tensor = image_tensor.unsqueeze(
        0
    )

    image_tensor = image_tensor.to(
        device
    )


    # --------------------------------------
    # Model prediction
    # --------------------------------------

    with torch.no_grad():

        outputs = model(
            image_tensor
        )

        probabilities = torch.softmax(
            outputs,
            dim=1
        )

        confidence, predicted_index = torch.max(
            probabilities,
            dim=1
        )


    predicted_class = CLASSES[
        predicted_index.item()
    ]

    confidence_percentage = (
        confidence.item() * 100
    )

    confidence_percentage = round(
        confidence_percentage,
        2
    )


    # --------------------------------------
    # Low-confidence rejection
    # --------------------------------------

    if confidence_percentage < CONFIDENCE_THRESHOLD:

        return {
            "disease": "Unable to identify",
            "confidence": confidence_percentage
        }


    # --------------------------------------
    # Normal prediction
    # --------------------------------------

    return {
        "disease": predicted_class,
        "confidence": confidence_percentage
    }