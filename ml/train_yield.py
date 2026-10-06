import csv
from pathlib import Path

import joblib

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder


# ==========================================
# 1. File paths
# ==========================================

DATA_FILE = Path(
    "ml/dataset/yield/potato_yield.csv"
)

MODEL_DIR = Path(
    "backend/models/yield_model"
)

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)

MODEL_FILE = MODEL_DIR / "potato_yield_model.pkl"


# ==========================================
# 2. Read dataset
# ==========================================

print("Reading potato yield dataset...")

rows = []

with open(
    DATA_FILE,
    "r",
    encoding="utf-8"
) as file:

    reader = csv.DictReader(file)

    for row in reader:

        rows.append({
            "area": row["area"],
            "year": float(row["year"]),
            "rainfall": float(
                row["average_rain_fall_mm_per_year"]
            ),
            "pesticides": float(
                row["pesticides_tonnes"]
            ),
            "temperature": float(
                row["avg_temp"]
            ),
            "yield": float(
                row["yield_hg_ha"]
            )
        })


print(f"Total records: {len(rows)}")


# ==========================================
# 3. Prepare features
# ==========================================

X = [
    [
        row["area"],
        row["year"],
        row["rainfall"],
        row["pesticides"],
        row["temperature"]
    ]
    for row in rows
]

y = [
    row["yield"]
    for row in rows
]


# ==========================================
# 4. Train / test split
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)


print(f"Training records: {len(X_train)}")
print(f"Testing records : {len(X_test)}")


# ==========================================
# 5. Encode area
# ==========================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "area",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            [0]
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
# 6. Create Random Forest model
# ==========================================

print()
print("Training Random Forest model...")

model = RandomForestRegressor(
    n_estimators=200,
    random_state=42,
    n_jobs=-1
)


model.fit(
    X_train_encoded,
    y_train
)


# ==========================================
# 7. Predictions
# ==========================================

predictions = model.predict(
    X_test_encoded
)


# ==========================================
# 8. Evaluation
# ==========================================

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


print()
print("===================================")
print("Yield Model Evaluation")
print("===================================")

print(f"MAE  : {mae:.2f}")
print(f"RMSE : {rmse:.2f}")
print(f"R2   : {r2:.4f}")


# ==========================================
# 9. Save model + preprocessor
# ==========================================

model_data = {
    "model": model,
    "preprocessor": preprocessor
}

joblib.dump(
    model_data,
    MODEL_FILE
)


print()
print("===================================")
print("Yield model saved successfully!")
print("===================================")
print(f"Model: {MODEL_FILE}")