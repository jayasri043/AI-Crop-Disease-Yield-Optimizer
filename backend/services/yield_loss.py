def calculate_yield_loss(
    predicted_yield,
    disease,
    severity
):
    """
    Estimate yield loss based on disease and severity.

    Returns:
        base yield
        estimated loss percentage
        estimated loss amount
        adjusted expected yield
    """

    # ------------------------------------------
    # Healthy crop → no yield loss
    # ------------------------------------------

    if (
        not disease
        or "healthy" in disease.lower()
        or disease.lower() == "none"
    ):
        loss_percentage = 0.0

    # ------------------------------------------
    # Disease + severity based loss
    # ------------------------------------------

    else:

        severity_lower = severity.lower()

        if severity_lower == "low":
            loss_percentage = 5.0

        elif severity_lower == "moderate":
            loss_percentage = 15.0

        elif severity_lower == "high":
            loss_percentage = 25.0

        else:
            loss_percentage = 10.0

    # ------------------------------------------
    # Calculate yield loss
    # ------------------------------------------

    estimated_loss = (
        predicted_yield *
        loss_percentage /
        100
    )

    adjusted_yield = (
        predicted_yield -
        estimated_loss
    )

    return {
        "base_predicted_yield_kg_ha": round(
            predicted_yield,
            2
        ),

        "estimated_yield_loss_percentage": round(
            loss_percentage,
            2
        ),

        "estimated_yield_loss_kg_ha": round(
            estimated_loss,
            2
        ),

        "adjusted_expected_yield_kg_ha": round(
            adjusted_yield,
            2
        )
    }