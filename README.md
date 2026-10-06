# 🌱 AI Crop Disease & Yield Optimizer

An AI-powered crop health analysis and yield optimization system designed to help farmers identify crop diseases, assess disease severity, estimate disease risk, and predict crop yield.

## 🚀 Features

- 🌿 AI-based crop disease detection
- 🎯 Disease confidence score
- ⚠️ Disease severity estimation
- 🚨 Disease risk assessment
- 🩺 Treatment priority estimation
- 🌦️ Weather and location-based analysis
- 🌾 Crop yield prediction
- 📉 Estimated yield loss
- 📊 Adjusted expected yield
- 🧠 Grad-CAM AI explainability
- 📝 Scan history
- 📱 Responsive farmer dashboard
- 🔍 Low-confidence image handling
- 🌱 Supports Tomato, Potato and Pepper crops

## 🌾 Supported Crops

### Tomato

- Healthy
- Early Blight
- Late Blight
- Leaf Mold

### Potato

- Healthy
- Early Blight
- Late Blight

### Pepper

- Healthy
- Bacterial Spot

## 🧠 Machine Learning

### Disease Detection

- Model: MobileNetV3 Small
- Framework: PyTorch
- Input Size: 224 × 224
- Classes: 9
- Confidence Threshold: 60%

### Model Evaluation

- Test Accuracy: 99.41%
- Macro F1 Score: 99.48%
- Weighted F1 Score: 99.41%

### Yield Prediction

- Model: Random Forest Regressor
- Dataset: FAOSTAT crop yield data
- Features:
  - Crop
  - Country/Area
  - Year

## 🏗️ Technology Stack

### Frontend

- React
- Vite
- JavaScript
- CSS

### Backend

- FastAPI
- Python
- SQLite

### Machine Learning

- PyTorch
- TorchVision
- Scikit-learn
- OpenCV
- NumPy

### APIs

- Open-Meteo Weather API
- Open-Meteo Geocoding API

## 📂 Project Structure

```text
AI-Crop-Disease-Yield-Optimizer/
│
├── backend/
│   ├── database/
│   ├── services/
│   ├── utils/
│   ├── main.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── ml/
│   ├── dataset/
│   ├── train_mobilenet.py
│   ├── evaluate.py
│   ├── gradcam.py
│   └── train_crop_yield.py
│
├── data/
│
├── docs/
│
├── .gitignore
└── README.md