def calculate_disease_risk(
    disease,
    severity,
    temperature,
    humidity,
    rainfall
):
    """
    Calculate disease risk using disease status,
    severity and current weather conditions.
    """

    if not disease:
        return {
            "risk_level": "Unknown",
            "risk_score": 0,
            "reason": "Disease information is unavailable."
        }

    disease_lower = disease.lower()

    # Healthy crop
    if "healthy" in disease_lower:
        return {
            "risk_level": "Low",
            "risk_score": 0,
            "reason": "No disease was detected."
        }

    score = 0
    reasons = []

    # -----------------------------
    # Disease severity
    # -----------------------------
    severity_lower = severity.lower()

    if severity_lower == "high":
        score += 40
        reasons.append("Disease severity is high.")
    elif severity_lower == "moderate":
        score += 25
        reasons.append("Disease severity is moderate.")
    elif severity_lower == "low":
        score += 10
        reasons.append("Disease severity is low.")

    # -----------------------------
    # Humidity
    # -----------------------------
    if humidity >= 90:
        score += 30
        reasons.append("Very high humidity may favor disease development.")
    elif humidity >= 80:
        score += 20
        reasons.append("High humidity may favor disease development.")
    elif humidity >= 70:
        score += 10
        reasons.append("Moderate humidity may support disease development.")

    # -----------------------------
    # Temperature
    # -----------------------------
    if 20 <= temperature <= 30:
        score += 20
        reasons.append("Temperature is favorable for disease development.")
    elif 15 <= temperature < 20 or 30 < temperature <= 35:
        score += 10
        reasons.append("Temperature may support disease development.")

    # -----------------------------
    # Rainfall
    # -----------------------------
    if rainfall > 10:
        score += 10
        reasons.append("Recent rainfall may increase disease risk.")
    elif rainfall > 0:
        score += 5
        reasons.append("Rainfall may increase leaf moisture.")

    # Maximum score = 100
    score = min(score, 100)

    # -----------------------------
    # Risk level
    # -----------------------------
    if score >= 75:
        risk_level = "Very High"
    elif score >= 50:
        risk_level = "High"
    elif score >= 25:
        risk_level = "Moderate"
    else:
        risk_level = "Low"

    return {
        "risk_level": risk_level,
        "risk_score": score,
        "reason": " ".join(reasons)
    }