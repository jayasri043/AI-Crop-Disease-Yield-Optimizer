from pathlib import Path

import cv2
import numpy as np
import torch
from PIL import Image
from torchvision import models, transforms


# ==========================================
# Model path
# ==========================================

MODEL_PATH = Path(
    "backend/models/disease_model/best_model.pth"
)


# ==========================================
# Device
# ==========================================

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ==========================================
# Load trained model
# ==========================================

checkpoint = torch.load(
    MODEL_PATH,
    map_location=device
)

CLASSES = checkpoint["classes"]

model = models.mobilenet_v3_small(
    weights=None
)

model.classifier[3] = torch.nn.Linear(
    model.classifier[3].in_features,
    len(CLASSES)
)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model = model.to(device)
model.eval()


# ==========================================
# Image preprocessing
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
# Grad-CAM function
# ==========================================

def generate_gradcam(image_path, output_path):

    activations = None
    gradients = None

    # --------------------------------------
    # Hooks
    # --------------------------------------

    def forward_hook(module, input, output):
        nonlocal activations
        activations = output

    def backward_hook(module, grad_input, grad_output):
        nonlocal gradients
        gradients = grad_output[0]

    target_layer = model.features[-1]

    forward_handle = target_layer.register_forward_hook(
        forward_hook
    )

    backward_handle = target_layer.register_full_backward_hook(
        backward_hook
    )

    try:

        # ----------------------------------
        # Load image
        # ----------------------------------

        original_image = Image.open(
            image_path
        ).convert("RGB")

        input_tensor = transform(
            original_image
        ).unsqueeze(0).to(device)


        # ----------------------------------
        # Forward pass
        # ----------------------------------

        model.zero_grad()

        output = model(input_tensor)

        probabilities = torch.softmax(
            output,
            dim=1
        )

        confidence, predicted_index = torch.max(
            probabilities,
            dim=1
        )

        predicted_class = CLASSES[
            predicted_index.item()
        ]


        # ----------------------------------
        # Backward pass
        # ----------------------------------

        target_score = output[
            0,
            predicted_index.item()
        ]

        target_score.backward()


        # ----------------------------------
        # Generate CAM
        # ----------------------------------

        feature_maps = activations.detach()
        grads = gradients.detach()

        weights = torch.mean(
            grads,
            dim=(2, 3),
            keepdim=True
        )

        cam = torch.sum(
            weights * feature_maps,
            dim=1
        )

        cam = torch.relu(cam)

        cam = cam.squeeze().cpu().numpy()

        cam = cv2.resize(
            cam,
            (224, 224)
        )

        cam -= cam.min()

        if cam.max() != 0:
            cam /= cam.max()


        # ----------------------------------
        # Create heatmap
        # ----------------------------------

        heatmap = np.uint8(
            255 * cam
        )

        heatmap = cv2.applyColorMap(
            heatmap,
            cv2.COLORMAP_JET
        )


        # ----------------------------------
        # Prepare original image
        # ----------------------------------

        original = np.array(
            original_image.resize((224, 224))
        )

        original = cv2.cvtColor(
            original,
            cv2.COLOR_RGB2BGR
        )


        # ----------------------------------
        # Overlay
        # ----------------------------------

        overlay = cv2.addWeighted(
            original,
            0.6,
            heatmap,
            0.4,
            0
        )


        # ----------------------------------
        # Save result
        # ----------------------------------

        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        cv2.imwrite(
            str(output_path),
            overlay
        )


        return {
            "prediction": predicted_class,
            "confidence": round(
                confidence.item() * 100,
                2
            ),
            "gradcam_path": str(output_path)
        }

    finally:

        forward_handle.remove()
        backward_handle.remove()