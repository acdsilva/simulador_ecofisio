"""Respostas fisiológicas da simulação.

Combina o modo simples (índices relativos, retrocompatíveis com a UI) com um
modelo científico: Lei de Kleiber (TMB), Q10 para ectotérmicos, custo de
termorregulação, respirometria (VO₂) e balanço energético.
"""

from typing import Optional

# Constantes do modelo científico
A_ECTO = 6.0          # constante metabólica base de ectotérmicos (kcal/dia)
Q10 = 2.5             # fator Q10 (metabolismo do ectotérmico vs. temperatura)
T_REF_ECTO = 30.0     # temperatura de referência do ectotérmico (°C)
KCAL_PER_L_O2 = 4.8   # equivalente calórico do oxigênio (kcal por litro de O₂)
MIN_PER_DAY = 1440


def run_physiology(
    species: dict,
    temperature: float,
    water_pct: float,
    food_pct: float,
    *,
    food_kcal: Optional[float] = None,
    predator: bool = False,
    o2_inspired: float = 20.9,
    o2_expired: float = 16.0,
) -> dict:
    water = water_pct / 100.0
    food = food_pct / 100.0
    optimal_min = species["optimal_temp_min"]
    optimal_max = species["optimal_temp_max"]
    is_regulator = species["thermoregulation"] == "regulator"
    mass = species.get("mass_kg", 1.0) or 1.0

    # ===== Estresse térmico (0..1) =====
    if optimal_min <= temperature <= optimal_max:
        temp_stress = 0.0
    else:
        temp_diff = min(abs(temperature - optimal_min), abs(temperature - optimal_max))
        temp_stress = min(temp_diff / 20.0, 1.0)

    # ===== Temperatura corporal (por classe) =====
    # Endotérmico mantém Tb da espécie (mamífero ~38, ave ~41); ectotérmico = ambiente.
    body_temp = species.get("body_temp_c", 37.0) if is_regulator else temperature

    # ===== Taxa metabólica basal: Kleiber (endo) / Q10 (ecto) =====
    if is_regulator:
        bmr_kcal = species["kleiber_a"] * (mass ** 0.75)
    else:
        bmr_kcal = A_ECTO * (mass ** 0.75) * (Q10 ** ((body_temp - T_REF_ECTO) / 10.0))

    # ===== Custo de termorregulação (apenas endotérmicos) =====
    thermo_cost = bmr_kcal * 1.5 * temp_stress if is_regulator else 0.0

    # ===== Atividade + vigilância contra predador =====
    activity_cost = 0.5 * bmr_kcal
    predator_cost = 0.3 * bmr_kcal if predator else 0.0
    total_expenditure = bmr_kcal + thermo_cost + activity_cost + predator_cost

    # ===== Respirometria (VO₂) =====
    vent = species.get("ventilation_rate_lmin", 0.0)
    extraction = max(0.0, o2_inspired - o2_expired) / 100.0
    vo2_l_min = vent * extraction
    vo2_ml_g_h = (vo2_l_min * 60.0 / mass) if mass > 0 else 0.0  # mL O₂ / g / h
    energy_from_o2 = vo2_l_min * KCAL_PER_L_O2 * MIN_PER_DAY      # kcal/dia

    # ===== Balanço energético =====
    if food_kcal is None:
        # modo simples: aproxima kcal a partir da disponibilidade (%)
        food_kcal = food * total_expenditure * 1.2
    energy_balance = food_kcal - total_expenditure
    energy_stress = (
        0.0 if energy_balance >= 0 else min(abs(energy_balance) / max(total_expenditure, 1.0), 1.0)
    )

    # ===== Estresses de água e predador =====
    water_impact = {"high": 2.0, "medium": 1.0, "low": 0.5}.get(species["water_dependency"], 1.0)
    water_stress = min((1.0 - water) * water_impact, 1.0)
    predator_stress = 0.5 if predator else 0.0

    # ===== Estresse total e sobrevivência =====
    total_stress = min((temp_stress + water_stress + energy_stress + predator_stress) / 3.0, 1.0)
    survival = max(0.0, 1.0 - total_stress)
    stress_breakdown = {
        "termico": round(temp_stress * 100, 1),
        "agua": round(water_stress * 100, 1),
        "energia": round(energy_stress * 100, 1),
        "predador": round(predator_stress * 100, 1),
    }

    # ===== Índices do modo simples (relativos ao basal) =====
    if is_regulator:
        metabolic_rate = round(1.0 + 1.5 * temp_stress, 2)
    else:
        metabolic_rate = round(Q10 ** ((body_temp - T_REF_ECTO) / 10.0), 2)
    energy_expenditure = round(metabolic_rate * (1.0 + total_stress), 2)
    water_status = "adequate" if water > 0.5 else "insufficient" if water > 0.2 else "critical"
    food_status = "adequate" if food > 0.5 else "insufficient" if food > 0.2 else "critical"
    if total_stress < 0.3:
        homeostasis_status = "stable"
    elif total_stress < 0.6:
        homeostasis_status = "stressed"
    else:
        homeostasis_status = "critical"

    return {
        # --- modo simples (retrocompatível) ---
        "metabolic_rate": metabolic_rate,
        "body_temperature": round(body_temp, 1),
        "survival_probability": round(survival * 100, 1),
        "energy_expenditure": energy_expenditure,
        "water_status": water_status,
        "food_status": food_status,
        "homeostasis_status": homeostasis_status,
        "stress_level": round(total_stress * 100, 1),
        # --- modo científico ---
        "basal_metabolic_rate_kcal": round(bmr_kcal, 1),
        "vo2_ml_g_h": round(vo2_ml_g_h, 3),
        "energy_from_o2_kcal": round(energy_from_o2, 1),
        "total_expenditure_kcal": round(total_expenditure, 1),
        "energy_balance_kcal": round(energy_balance, 1),
        "thermoregulation_cost_kcal": round(thermo_cost, 1),
        "stress_breakdown": stress_breakdown,
    }
