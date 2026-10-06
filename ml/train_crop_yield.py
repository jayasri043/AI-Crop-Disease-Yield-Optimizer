import csv
from pathlib import Path

import joblib

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ==========================================
# Paths
# ==========================================

DATA_PATH = Path(
    "ml/dataset/yield/crop_yield_faostat.csv"
)

MODEL_DIR = Path(
    "backend/models/yield_model"
)

MODEL_PATH = MODEL_DIR / "crop_yield_model.pkl"


# ==========================================
# Read dataset
# ==========================================

print("Reading FAOSTAT 3-crop yield dataset...")

rows = []

with open(
    DATA_PATH,
    "r",
    encoding="utf-8"
) as f:

    reader = csv.DictReader(f)

    for row in reader:

        rows.append([
            row["crop"],
            row["area"],
            float(row["year"]),
            float(row["yield_kg_ha"])
        ])


print("Total records:", len(rows))


# ==========================================
# Prepare features
# ==========================================

X = [
    [
        row[0],  # crop
        row[1],  # area
        row[2]   # year
    ]
    for row in rows
]

y = [
    row[3]
    for row in rows
]


# ==========================================
# Train / Test split
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)


print("Training records:", len(X_train))
print("Testing records :", len(X_test))


# ==========================================
# Preprocessing
# ==========================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            [0, 1]
        )
    ],
    remainder="passthrough"
)


X_train_encoded = preprocessor.fit_transform(
    X_train
)

X_test_encoded = preprocessor.transform(
    X_test
)


# ==========================================
# Random Forest
# ==========================================

print("\nTraining 3-crop Random Forest model...")

model = RandomForestRegressor(
    n_estimators=300,
    random_state=42,
    n_jobs=-1,
    max_features="sqrt"
)

model.fit(
    X_train_encoded,
    y_train
)


# ==========================================
# Evaluation
# ==========================================

predictions = model.predict(
    X_test_encoded
)

mae = mean_absolute_error(
    y_test,
    predictions
)

rmse = mean_squared_error(
    y_test,
    predictions
) ** 0.5

r2 = r2_score(
    y_test,
    predictions
)


print("\n===================================")
print("3-Crop Yield Model Evaluation")
print("===================================")

print("MAE  :", round(mae, 2))
print("RMSE :", round(rmse, 2))
print("R2   :", round(r2, 4))


# ==========================================
# Save model
# ==========================================

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)

joblib.dump(
    {
        "model": model,
        "preprocessor": preprocessor,
        "crops": [
            "Potato",
            "Tomato",
            "Pepper"
        ]
    },
    MODEL_PATH
)


print("\nModel saved successfully!")
print("Path:", MODEL_PATH)