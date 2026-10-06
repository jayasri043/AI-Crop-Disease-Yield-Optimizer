def calculate_treatment_priority(
    confidence,
    severity,
    affected_area,
    risk_score
):
    """
    Estimate treatment priority using:
    - AI confidence
    - disease severity
    - affected leaf area
    - disease risk

    This is a heuristic priority score,
    not an agricultural ground-truth measurement.
    """

    # --------------------------------
    # Confidence contribution
    # --------------------------------

    confidence_score = min(max(confidence, 0), 100) * 0.20

    # --------------------------------
    # Severity contribution
    # --------------------------------

    severity_lower = severity.lower()

    if severity_lower == "high":
        severity_score = 100
    elif severity_lower == "moderate":
        severity_score = 60
    elif severity_lower == "low":
        severity_score = 30
    else:
        severity_score = 0

    severity_contribution = severity_score * 0.30

    # --------------------------------
    # Affected area contribution
    # --------------------------------

    affected_area_score = min(max(affected_area, 0), 100)

    affected_area_contribution = affected_area_score * 0.20

    # --------------------------------
    # Disease risk contribution
    # --------------------------------

    risk_score = min(max(risk_score, 0), 100)

    risk_contribution = risk_score * 0.30

    # --------------------------------
    # Final priority score
    # --------------------------------

    priority_score = (
        confidence_score
        + severity_contribution
        + affected_area_contribution
        + risk_contribution
    )

    priority_score = round(
        min(max(priority_score, 0), 100),
        2
    )

    # --------------------------------
    # Priority level
    # --------------------------------

    if priority_score >= 75:
        priority_level = "Urgent"
    elif priority_score >= 50:
        priority_level = "High"
    elif priority_score >= 25:
        priority_level = "Moderate"
    else:
        priority_level = "Low"

    # --------------------------------
    # Action message
    # --------------------------------

    if priority_level == "Urgent":
        action = (
            "Immediate attention is recommended. "
            "Inspect affected plants and begin appropriate "
            "disease management measures."
        )
    elif priority_level == "High":
        action = (
            "Prompt attention is recommended. "
            "Monitor the affected area closely and follow "
            "appropriate disease management practices."
        )
    elif priority_level == "Moderate":
        action = (
            "Continue monitoring the crop and take preventive "
            "disease management measures."
        )
    else:
        action = (
            "Continue regular crop monitoring and maintain "
            "good crop management practices."
        )

    return {
        "priority_level": priority_level,
        "priority_score": priority_score,
        "action": action
    }