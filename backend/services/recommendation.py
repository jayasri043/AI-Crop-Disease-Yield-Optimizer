def get_recommendation(disease, severity, weather):
    """
    Structured crop-disease recommendation engine.

    Recommendations are general crop-management guidance.
    They are not a substitute for local agricultural advice,
    pesticide labels, or professional diagnosis.
    """

    disease_key = (disease or "").lower().strip()
    severity_key = (severity or "").lower().strip()

    # ==========================================
    # Disease Recommendation Knowledge Base
    # ==========================================

    recommendations = {

        # --------------------------------------
        # Tomato
        # --------------------------------------

        "tomato___early_blight": {
            "actions": [
                "Remove and safely dispose of severely infected leaves.",
                "Improve air circulation between tomato plants.",
                "Avoid overhead irrigation and keep foliage dry.",
                "Monitor nearby plants for new symptoms."
            ],
            "prevention": [
                "Maintain adequate spacing between plants.",
                "Remove infected plant debris after harvest.",
                "Use clean tools when pruning.",
                "Practice appropriate crop rotation."
            ]
        },

        "tomato___late_blight": {
            "actions": [
                "Remove severely affected plant material promptly.",
                "Inspect nearby tomato plants because late blight can spread quickly.",
                "Improve airflow around the crop.",
                "Avoid prolonged leaf wetness."
            ],
            "prevention": [
                "Avoid overhead irrigation where practical.",
                "Remove infected plant debris promptly.",
                "Maintain good field sanitation.",
                "Follow locally recommended late-blight management practices."
            ]
        },

        "tomato,_bell___leaf_mold": {
            "actions": [
                "Remove heavily affected leaves where practical.",
                "Improve ventilation around the tomato crop.",
                "Reduce prolonged humidity around foliage.",
                "Avoid unnecessary leaf wetness."
            ],
            "prevention": [
                "Provide adequate plant spacing.",
                "Use proper greenhouse ventilation where applicable.",
                "Remove infected plant debris.",
                "Monitor plants regularly for new symptoms."
            ]
        },

        "tomato___healthy": {
            "actions": [
                "No disease-specific treatment is recommended.",
                "Continue regular crop monitoring.",
                "Maintain appropriate irrigation and balanced nutrition."
            ],
            "prevention": [
                "Keep the growing area clean.",
                "Maintain good airflow around plants.",
                "Inspect leaves regularly for early symptoms."
            ]
        },

        # --------------------------------------
        # Potato
        # --------------------------------------

        "potato___early_blight": {
            "actions": [
                "Remove severely affected foliage where practical.",
                "Maintain good airflow around potato plants.",
                "Avoid prolonged leaf wetness.",
                "Monitor the crop regularly for disease progression."
            ],
            "prevention": [
                "Remove infected crop debris.",
                "Maintain balanced crop nutrition.",
                "Practice appropriate crop rotation.",
                "Avoid unnecessary overhead irrigation."
            ]
        },

        "potato___late_blight": {
            "actions": [
                "Remove severely infected plant material where practical.",
                "Monitor surrounding potato plants closely.",
                "Reduce prolonged leaf wetness.",
                "Take prompt disease-management action because late blight can spread rapidly."
            ],
            "prevention": [
                "Avoid overhead irrigation where possible.",
                "Maintain good field ventilation.",
                "Remove infected crop debris.",
                "Follow locally recommended late-blight management practices."
            ]
        },

        "potato___healthy": {
            "actions": [
                "No disease-specific treatment is recommended.",
                "Continue regular potato crop monitoring.",
                "Maintain appropriate irrigation and balanced nutrition."
            ],
            "prevention": [
                "Keep the field clean.",
                "Maintain good plant spacing and airflow.",
                "Inspect plants regularly for early symptoms."
            ]
        },

        # --------------------------------------
        # Pepper
        # --------------------------------------

        "pepper,_bell___bacterial_spot": {
            "actions": [
                "Remove severely affected leaves where practical.",
                "Avoid handling pepper plants when foliage is wet.",
                "Improve airflow between plants.",
                "Monitor nearby plants for new lesions."
            ],
            "prevention": [
                "Use clean planting material.",
                "Sanitize tools regularly.",
                "Avoid unnecessary overhead irrigation.",
                "Remove infected crop debris."
            ]
        },

        "pepper,_bell___healthy": {
            "actions": [
                "No disease-specific treatment is recommended.",
                "Continue regular pepper crop monitoring.",
                "Maintain appropriate irrigation and balanced nutrition."
            ],
            "prevention": [
                "Keep the growing area clean.",
                "Maintain good airflow.",
                "Inspect leaves regularly for early symptoms."
            ]
        }
    }

    # ==========================================
    # Find Disease Recommendation
    # ==========================================

    recommendation = recommendations.get(disease_key)

    # ==========================================
    # Healthy Fallback
    # ==========================================

    if recommendation is None and "healthy" in disease_key:

        recommendation = {
            "actions": [
                "No disease-specific treatment is recommended.",
                "Continue regular crop monitoring.",
                "Maintain appropriate irrigation and balanced nutrition."
            ],
            "prevention": [
                "Keep the growing area clean.",
                "Maintain good airflow.",
                "Inspect leaves regularly for early symptoms."
            ]
        }

    # ==========================================
    # Unknown Disease Fallback
    # ==========================================

    if recommendation is None:

        recommendation = {
            "actions": [
                "Monitor the affected plant closely.",
                "Remove severely damaged plant material where appropriate.",
                "Maintain good airflow and avoid prolonged leaf wetness."
            ],
            "prevention": [
                "Keep the crop area clean.",
                "Inspect nearby plants regularly.",
                "Follow locally approved agricultural guidance."
            ]
        }

    # ==========================================
    # Severity-Based Priority
    # ==========================================

    # Healthy crops should NEVER receive a
    # disease-treatment priority based on severity.

    if "healthy" in disease_key:

        priority = "Low"

        urgency = (
            "No disease-specific treatment is required. "
            "Continue regular crop monitoring."
        )

    elif severity_key == "high":

        priority = "High"

        urgency = (
            "Take action promptly and monitor the crop closely."
        )

    elif severity_key == "moderate":

        priority = "Medium"

        urgency = (
            "Begin appropriate management measures and "
            "monitor disease progression."
        )

    elif severity_key == "low":

        priority = "Low"

        urgency = (
            "Continue monitoring and preventive crop management."
        )

    else:

        priority = "Low"

        urgency = (
            "Continue regular crop monitoring and "
            "preventive management."
        )

    # ==========================================
    # Weather-Based Advice
    # ==========================================

    weather_advice = []

    if weather:

        humidity = float(
            weather.get("humidity", 0) or 0
        )

        rainfall = float(
            weather.get("rainfall", 0) or 0
        )

        temperature = float(
            weather.get("temperature", 0) or 0
        )

        # --------------------------------------
        # Healthy Crop
        # --------------------------------------

        # Healthy crops should not receive
        # disease-specific weather warnings.

        if "healthy" in disease_key:

            weather_advice = []

        else:

            # --------------------------------------
            # Humidity
            # --------------------------------------

            if humidity >= 90:

                weather_advice.append(
                    "Very high humidity may favor disease development; "
                    "improve airflow and reduce prolonged leaf wetness."
                )

            elif humidity >= 70:

                weather_advice.append(
                    "High humidity may favor disease development; "
                    "improve airflow and reduce leaf wetness."
                )

            # --------------------------------------
            # Rainfall
            # --------------------------------------

            if rainfall >= 10:

                weather_advice.append(
                    "Recent rainfall may increase disease-spread risk; "
                    "inspect the crop after wet conditions."
                )

            elif rainfall > 0:

                weather_advice.append(
                    "Recent rainfall may increase leaf moisture; "
                    "monitor the crop for new symptoms."
                )

            # --------------------------------------
            # Temperature
            # --------------------------------------

            if 20 <= temperature <= 30:

                weather_advice.append(
                    "Current temperature may support disease development; "
                    "continue regular monitoring."
                )

            # --------------------------------------
            # No Additional Advice
            # --------------------------------------

            if not weather_advice:

                weather_advice.append(
                    "Current weather conditions do not trigger "
                    "additional weather-specific advice."
                )

    # ==========================================
    # Final Response
    # ==========================================

    return {
        "priority": priority,
        "urgency": urgency,
        "actions": recommendation["actions"],
        "prevention": recommendation["prevention"],
        "weather_advice": weather_advice
    }