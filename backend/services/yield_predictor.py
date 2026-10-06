from pathlib import Path

import joblib


MODEL_PATH = Path(
    "backend/models/yield_model/crop_yield_model.pkl"
)


# Load trained 3-crop model
model_data = joblib.load(MODEL_PATH)

model = model_data["model"]
preprocessor = model_data["preprocessor"]


def predict_yield(
    crop,
    area,
    year
):
    """
    Predict crop yield for Potato, Tomato, or Pepper.

    Returns yield in kg/ha.
    """

    input_data = [
        [
            crop,
            area,
            float(year)
        ]
    ]

    # Apply the same preprocessing used during training
    input_encoded = preprocessor.transform(
        input_data
    )

    # Predict yield
    prediction = model.predict(
        input_encoded
    )

    predicted_yield = float(
        prediction[0]
    )

    return {
        "crop": crop,
        "area": area,
        "predicted_yield_kg_ha": round(
            predicted_yield,
            2
        )
    }