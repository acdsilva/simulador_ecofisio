"""Modelos Pydantic da API, com validação e limites de tamanho."""

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field

from .config import CHAT_MAX_CHARS, CHAT_MAX_MESSAGES


class Species(BaseModel):
    id: str
    name_pt: str
    name_en: str
    scientific_name: str
    biome: str
    type: str  # mammal, bird, reptile
    thermoregulation: str  # regulator or conformer
    image_url: str
    optimal_temp_min: float
    optimal_temp_max: float
    water_dependency: str  # low, medium, high
    food_type: str
    description_pt: str
    description_en: str
    # Constantes fisiológicas (modelo científico)
    mass_kg: float
    kleiber_a: float
    body_temp_c: float
    ventilation_rate_lmin: float


class SimulationRequest(BaseModel):
    species_id: str = Field(..., min_length=1, max_length=100)
    temperature: float = Field(..., ge=-90, le=70)
    water_availability: float = Field(..., ge=0, le=100)
    food_availability: float = Field(..., ge=0, le=100)
    language: Literal["pt", "en"] = "pt"
    # --- Modo científico (opcionais; default mantém o modo simples) ---
    food_availability_kcal: Optional[float] = Field(None, ge=0, le=10000)
    predator_presence: bool = False
    o2_inspired: float = Field(20.9, ge=15, le=25)
    o2_expired: float = Field(16.0, ge=8, le=21)


class SimulationResponse(BaseModel):
    metabolic_rate: float
    body_temperature: float
    survival_probability: float
    energy_expenditure: float
    water_status: str
    food_status: str
    homeostasis_status: str
    stress_level: float
    # --- Métricas científicas (modelo Kleiber / respirometria) ---
    basal_metabolic_rate_kcal: float
    vo2_ml_g_h: float
    energy_from_o2_kcal: float
    total_expenditure_kcal: float
    energy_balance_kcal: float
    thermoregulation_cost_kcal: float
    stress_breakdown: Dict[str, float]


class ExplanationRequest(BaseModel):
    species_name: str = Field(..., min_length=1, max_length=120)
    simulation_result: SimulationResponse
    language: Literal["pt", "en"] = "pt"


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    text: str = Field(..., min_length=1, max_length=CHAT_MAX_CHARS)


class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., min_length=1, max_length=CHAT_MAX_MESSAGES)
    species_name: Optional[str] = Field(None, max_length=120)
    language: Literal["pt", "en"] = "pt"
