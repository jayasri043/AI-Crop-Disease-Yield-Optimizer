from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.services.disease_detector import predict_disease
from backend.services.severity import estimate_severity
from backend.services.gradcam_service import generate_gradcam
from backend.services.weather import get_weather
from backend.services.location import get_coordinates
from backend.services.recommendation import get_recommendation
from backend.services.yield_predictor import predict_yield
from backend.services.yield_loss import calculate_yield_loss
from backend.services.disease_risk import calculate_disease_risk
from backend.services.treatment_priority import calculate_treatment_priority

# Database
from backend.database.database import (
    initialize_database,
    save_scan_history,
    get_scan_history
)


# ==========================================
# 1. Create FastAPI app
# ==========================================

app = FastAPI(
    title="AI Crop Disease & Yield Optimizer"
)


# ==========================================
# 2. Initialize database
# ==========================================

initialize_database()


# ==========================================
# 3. Crop name mapping
# ==========================================

def get_crop_name(disease_name):

    if not disease_name:
        return None

    disease_lower = disease_name.lower()

    if "tomato" in disease_lower:
        return "Tomato"

    elif "potato" in disease_lower:
        return "Potato"

    elif "pepper" in disease_lower:
        return "Pepper"

    return None


# ==========================================
# 4. Yield Area Validation
# ==========================================

# The yield model was trained using FAOSTAT
# area/country names rather than individual
# city names.

SUPPORTED_YIELD_AREAS = {
    "India",
    "United States of America",
    "Brazil",
    "China",
    "Mexico",
    "Indonesia",
    "Bangladesh",
    "Pakistan",
    "Nepal",
    "Sri Lanka",
    "Thailand",
    "Vietnam",
    "Philippines",
    "Türkiye",
    "Egypt",
    "Italy",
    "Spain",
    "France",
    "Germany",
    "United Kingdom",
    "Australia",
    "Canada",
    "Argentina",
    "Chile",
    "Colombia",
    "Peru",
    "South Africa",
    "Nigeria",
    "Kenya"
}


def validate_yield_area(area):

    if not area:
        raise HTTPException(
            status_code=400,
            detail="Yield prediction requires a valid FAOSTAT area/country."
        )

    area_clean = area.strip()

    if not area_clean:
        raise HTTPException(
            status_code=400,
            detail="Yield prediction requires a valid FAOSTAT area/country."
        )

    if area_clean not in SUPPORTED_YIELD_AREAS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"'{area_clean}' is not configured as a supported "
                "FAOSTAT yield area. Please enter a supported "
                "country/area name such as 'India'."
            )
        )

    return area_clean


# ==========================================
# 5. Grad-CAM image folder
# ==========================================

app.mount(
    "/gradcam",
    StaticFiles(
        directory="backend/models/disease_model"
    ),
    name="gradcam"
)


# ==========================================
# 6. CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# 7. Home route
# ==========================================

@app.get("/")
def home():

    return {
        "message": "AI Crop Disease API is running!"
    }


# ==========================================
# 8. Disease prediction
# ==========================================

@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    area: str = Form("Chennai")
):

    # ------------------------------------------
    # Read uploaded image
    # ------------------------------------------

    file_bytes = await file.read()

    temporary_file = "temp_leaf.jpg"

    with open(
        temporary_file,
        "wb"
    ) as f:

        f.write(file_bytes)


    # ------------------------------------------
    # Disease prediction
    # ------------------------------------------

    result = predict_disease(
        temporary_file
    )


    # ==========================================
    # LOW-CONFIDENCE SAFETY HANDLING
    # ==========================================
    #
    # If the AI cannot confidently identify the
    # uploaded image as one of the supported crop
    # disease classes, do not calculate:
    #
    # - severity
    # - disease risk
    # - treatment priority
    # - recommendation
    # - crop yield
    # - yield loss
    #
    # This prevents meaningless values from being
    # shown or stored for an unknown image.
    # ==========================================

    if (
        result["disease"] == "Unable to identify"
        or result["confidence"] < 60
    ):

        save_scan_history(
            crop="Unknown",
            disease="Unable to identify",
            confidence=result["confidence"],
            severity=None,
            affected_area=None,
            risk_level=None,
            risk_score=None,
            treatment_priority=None,
            treatment_priority_score=None,
            temperature=None,
            humidity=None,
            rainfall=None,
            location=area,
            base_yield=None,
            yield_loss_percentage=None,
            adjusted_yield=None
        )

        return {

            "filename": file.filename,

            "prediction": "Unable to identify",

            "confidence": result["confidence"],

            "severity": None,

            "severity_score": None,

            "affected_area": None,

            "area": area,

            "weather": None,

            "disease_risk": None,

            "treatment_priority": None,

            "recommendation": None,

            "yield_loss": None,

            "gradcam_path": None

        }


    # ------------------------------------------
    # Severity estimation
    # ------------------------------------------

    severity_result = estimate_severity(
        temporary_file,
        result["confidence"],
        result["disease"]
    )


    # ------------------------------------------
    # Get location coordinates
    # ------------------------------------------

    location = get_coordinates(area)

    if location:

        weather = get_weather(
            latitude=location["latitude"],
            longitude=location["longitude"]
        )

    else:

        # Fallback to Chennai
        weather = get_weather(
            latitude=13.0827,
            longitude=80.2707
        )


    # ==========================================
    # Disease Risk / Early Warning
    # ==========================================

    disease_risk = calculate_disease_risk(
        disease=result["disease"],
        severity=severity_result["severity"],
        temperature=weather["temperature"],
        humidity=weather["humidity"],
        rainfall=weather["rainfall"]
    )


    # ==========================================
    # Treatment Priority
    # ==========================================

    treatment_priority = calculate_treatment_priority(
        confidence=result["confidence"],
        severity=severity_result["severity"],
        affected_area=severity_result["affected_area"],
        risk_score=disease_risk["risk_score"]
    )


    # ------------------------------------------
    # Treatment recommendation
    # ------------------------------------------

    recommendation = get_recommendation(
        result["disease"],
        severity_result["severity"],
        weather
    )


    # ------------------------------------------
    # Grad-CAM
    # ------------------------------------------

    gradcam_output = (
        "backend/models/disease_model/gradcam_result.jpg"
    )

    gradcam_result = generate_gradcam(
        temporary_file,
        gradcam_output
    )


    # ==========================================
    # Yield Prediction + Yield Loss
    # ==========================================

    crop_name = get_crop_name(
        result["disease"]
    )

    yield_loss_result = None

    if crop_name:

        # Current prediction year
        prediction_year = 2026

        # --------------------------------------
        # Base yield prediction
        # --------------------------------------
        #
        # IMPORTANT:
        # The disease scan location may be a city
        # such as Chennai.
        #
        # The current yield model, however, was
        # trained using FAOSTAT area/country data.
        #
        # Until the frontend supplies a separate
        # yield area, we use India as the model area.
        # This keeps the prediction consistent with
        # the training data.

        yield_area = "India"

        base_yield_result = predict_yield(
            crop=crop_name,
            area=yield_area,
            year=prediction_year
        )

        base_yield = base_yield_result[
            "predicted_yield_kg_ha"
        ]

        # --------------------------------------
        # Disease-based yield loss
        # --------------------------------------

        yield_loss_result = calculate_yield_loss(
            predicted_yield=base_yield,
            disease=result["disease"],
            severity=severity_result["severity"]
        )

        # Add extra information
        yield_loss_result["crop"] = crop_name
        yield_loss_result["area"] = yield_area
        yield_loss_result["year"] = prediction_year


    # ==========================================
    # Save Scan History
    # ==========================================

    base_yield = None
    yield_loss_percentage = None
    adjusted_yield = None

    if yield_loss_result:

        base_yield = yield_loss_result[
            "base_predicted_yield_kg_ha"
        ]

        yield_loss_percentage = yield_loss_result[
            "estimated_yield_loss_percentage"
        ]

        adjusted_yield = yield_loss_result[
            "adjusted_expected_yield_kg_ha"
        ]


    save_scan_history(
        crop=crop_name or "Unknown",
        disease=result["disease"],
        confidence=result["confidence"],
        severity=severity_result["severity"],
        affected_area=severity_result["affected_area"],
        risk_level=disease_risk["risk_level"],
        risk_score=disease_risk["risk_score"],
        treatment_priority=treatment_priority["priority_level"],
        treatment_priority_score=treatment_priority["priority_score"],
        temperature=weather["temperature"],
        humidity=weather["humidity"],
        rainfall=weather["rainfall"],
        location=area,
        base_yield=base_yield,
        yield_loss_percentage=yield_loss_percentage,
        adjusted_yield=adjusted_yield
    )


    # ==========================================
    # Final response
    # ==========================================

    return {

        "filename": file.filename,

        "prediction": result["disease"],

        "confidence": result["confidence"],

        "severity": severity_result["severity"],

        "severity_score": severity_result["score"],

        "affected_area": severity_result["affected_area"],

        "area": area,

        "weather": weather,

        "disease_risk": disease_risk,

        "treatment_priority": treatment_priority,

        "recommendation": recommendation,

        "yield_loss": yield_loss_result,

        "gradcam_path": gradcam_result["gradcam_path"]

    }


# ==========================================
# 9. Yield prediction
# ==========================================

@app.post("/predict-yield")
async def predict_yield_api(
    crop: str,
    area: str,
    year: int
):

    # ------------------------------------------
    # Validate crop
    # ------------------------------------------

    allowed_crops = {
        "Tomato",
        "Potato",
        "Pepper"
    }

    if crop not in allowed_crops:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported crop. Choose Tomato, Potato or Pepper."
            )
        )


    # ------------------------------------------
    # Validate yield area
    # ------------------------------------------

    validated_area = validate_yield_area(area)


    # ------------------------------------------
    # Validate year
    # ------------------------------------------

    if year < 1961 or year > 2100:

        raise HTTPException(
            status_code=400,
            detail="Please enter a valid year between 1961 and 2100."
        )


    # ------------------------------------------
    # Predict yield
    # ------------------------------------------

    result = predict_yield(
        crop=crop,
        area=validated_area,
        year=year
    )

    return result


# ==========================================
# 10. Scan History
# ==========================================

@app.get("/scan-history")
def scan_history():

    history = get_scan_history()

    return {
        "count": len(history),
        "scans": history
    }