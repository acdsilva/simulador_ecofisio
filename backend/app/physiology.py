"""Cálculo determinístico das respostas fisiológicas da simulação."""


def run_physiology(species: dict, temperature: float, water_pct: float, food_pct: float) -> dict:
    water = water_pct / 100.0
    food = food_pct / 100.0

    optimal_min = species["optimal_temp_min"]
    optimal_max = species["optimal_temp_max"]
    is_regulator = species["thermoregulation"] == "regulator"

    if optimal_min <= temperature <= optimal_max:
        temp_stress = 0.0
        body_temp = 37.0 if is_regulator else temperature
        metabolic_rate = 1.0
    else:
        temp_diff = min(abs(temperature - optimal_min), abs(temperature - optimal_max))
        temp_stress = min(temp_diff / 20.0, 1.0)
        if is_regulator:
            body_temp = 37.0
            metabolic_rate = 1.0 + temp_stress * 2.0
        else:
            body_temp = temperature
            metabolic_rate = max(0.1, 1.0 - temp_stress * 0.8)

    water_impact = {"high": 2.0, "medium": 1.0, "low": 0.5}
    water_stress = (1.0 - water) * water_impact.get(species["water_dependency"], 1.0)
    food_stress = (1.0 - food) * 1.5

    stress_level = min((temp_stress + water_stress + food_stress) / 3.0, 1.0)
    survival_probability = max(0.0, 1.0 - stress_level)
    energy_expenditure = metabolic_rate * (1.0 + stress_level)

    water_status = "adequate" if water > 0.5 else "insufficient" if water > 0.2 else "critical"
    food_status = "adequate" if food > 0.5 else "insufficient" if food > 0.2 else "critical"

    if stress_level < 0.3:
        homeostasis_status = "stable"
    elif stress_level < 0.6:
        homeostasis_status = "stressed"
    else:
        homeostasis_status = "critical"

    return {
        "metabolic_rate": round(metabolic_rate, 2),
        "body_temperature": round(body_temp, 1),
        "survival_probability": round(survival_probability * 100, 1),
        "energy_expenditure": round(energy_expenditure, 2),
        "water_status": water_status,
        "food_status": food_status,
        "homeostasis_status": homeostasis_status,
        "stress_level": round(stress_level * 100, 1),
    }
