"""
EcoFisioLab API — backend independente (FastAPI).

- Sem dependências proprietárias: a IA usa o SDK oficial do Google Gemini
  (google-generativeai) quando há GEMINI_API_KEY; caso contrário, gera uma
  explicação educativa localmente. O app nunca quebra por falta de chave.
- Persistência opcional: usa MongoDB se MONGO_URL estiver definido; senão,
  roda 100% em memória (ideal para desenvolvimento e demonstrações).
"""

import asyncio
import os
import re
import unicodedata
from contextlib import asynccontextmanager
from typing import List, Optional, Protocol

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

load_dotenv()

# ---------------------------------------------------------------------------
# Configuração via ambiente
# ---------------------------------------------------------------------------
MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "ecofisiolab")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]


# ---------------------------------------------------------------------------
# Modelos
# ---------------------------------------------------------------------------
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


class SimulationRequest(BaseModel):
    species_id: str
    temperature: float
    water_availability: float
    food_availability: float
    language: str  # pt or en


class SimulationResponse(BaseModel):
    metabolic_rate: float
    body_temperature: float
    survival_probability: float
    energy_expenditure: float
    water_status: str
    food_status: str
    homeostasis_status: str
    stress_level: float


class ExplanationRequest(BaseModel):
    species_name: str
    simulation_result: SimulationResponse
    language: str


class ChatMessage(BaseModel):
    role: str  # "user" ou "assistant"
    text: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    species_name: Optional[str] = None
    language: str = "pt"


# ---------------------------------------------------------------------------
# Dados das espécies (semente)
# ---------------------------------------------------------------------------
def slugify(value: str) -> str:
    """ID estável e legível a partir do nome científico (ex.: panthera-onca)."""
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return value


INITIAL_SPECIES = [
    {
        "name_pt": "Capivara",
        "name_en": "Capybara",
        "scientific_name": "Hydrochoerus hydrochaeris",
        "biome": "Pampa",
        "type": "mammal",
        "thermoregulation": "regulator",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Capybara_%28Hydrochoerus_hydrochaeris%29.JPG/640px-Capybara_%28Hydrochoerus_hydrochaeris%29.JPG",
        "optimal_temp_min": 20.0,
        "optimal_temp_max": 35.0,
        "water_dependency": "high",
        "food_type": "herbivore",
        "description_pt": "A capivara é o maior roedor do mundo, semi-aquático e encontrado principalmente em regiões alagadas do Pampa. Depende fortemente de água para termorregulação.",
        "description_en": "The capybara is the world's largest rodent, semi-aquatic and found mainly in flooded regions of the Pampa. It heavily depends on water for thermoregulation.",
    },
    {
        "name_pt": "Quero-quero",
        "name_en": "Southern Lapwing",
        "scientific_name": "Vanellus chilensis",
        "biome": "Pampa",
        "type": "bird",
        "thermoregulation": "regulator",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Southern_Lapwing_%28Vanellus_chilensis%29_adult.jpg/640px-Southern_Lapwing_%28Vanellus_chilensis%29_adult.jpg",
        "optimal_temp_min": 15.0,
        "optimal_temp_max": 30.0,
        "water_dependency": "medium",
        "food_type": "insectivore",
        "description_pt": "Ave territorial comum no Pampa, conhecida por seu grito característico. Adapta-se bem a diferentes condições climáticas.",
        "description_en": "Territorial bird common in the Pampa, known for its characteristic cry. Adapts well to different climatic conditions.",
    },
    {
        "name_pt": "Preá",
        "name_en": "Brazilian Guinea Pig",
        "scientific_name": "Cavia aperea",
        "biome": "Pampa",
        "type": "mammal",
        "thermoregulation": "regulator",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Cavia_aperea_001.jpg/640px-Cavia_aperea_001.jpg",
        "optimal_temp_min": 18.0,
        "optimal_temp_max": 28.0,
        "water_dependency": "medium",
        "food_type": "herbivore",
        "description_pt": "Pequeno roedor nativo do Pampa, ancestral do porquinho-da-índia doméstico. Vive em grupos e é ativo durante o dia.",
        "description_en": "Small rodent native to the Pampa, ancestor of the domestic guinea pig. Lives in groups and is active during the day.",
    },
    {
        "name_pt": "Teiú",
        "name_en": "Argentine Black and White Tegu",
        "scientific_name": "Salvator merianae",
        "biome": "Pampa",
        "type": "reptile",
        "thermoregulation": "conformer",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9d/Tegu_Lizard_%28Salvator_merianae%29.jpg/640px-Tegu_Lizard_%28Salvator_merianae%29.jpg",
        "optimal_temp_min": 25.0,
        "optimal_temp_max": 35.0,
        "water_dependency": "low",
        "food_type": "omnivore",
        "description_pt": "Lagarto grande do Pampa, pecilotérmico, depende do sol para regular temperatura corporal. Hiberna no inverno.",
        "description_en": "Large lizard from the Pampa, ectothermic, depends on the sun to regulate body temperature. Hibernates in winter.",
    },
    {
        "name_pt": "Onça-pintada",
        "name_en": "Jaguar",
        "scientific_name": "Panthera onca",
        "biome": "Amazônia",
        "type": "mammal",
        "thermoregulation": "regulator",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Standing_jaguar.jpg/640px-Standing_jaguar.jpg",
        "optimal_temp_min": 22.0,
        "optimal_temp_max": 32.0,
        "water_dependency": "medium",
        "food_type": "carnivore",
        "description_pt": "Maior felino das Américas, apex predator da Amazônia. Excelente nadador e caçador.",
        "description_en": "Largest cat in the Americas, apex predator of the Amazon. Excellent swimmer and hunter.",
    },
    {
        "name_pt": "Arara-azul",
        "name_en": "Hyacinth Macaw",
        "scientific_name": "Anodorhynchus hyacinthinus",
        "biome": "Amazônia",
        "type": "bird",
        "thermoregulation": "regulator",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Anodorhynchus_hyacinthinus_-Hyacinth_Macaw_-side_of_head.jpg/640px-Anodorhynchus_hyacinthinus_-Hyacinth_Macaw_-side_of_head.jpg",
        "optimal_temp_min": 20.0,
        "optimal_temp_max": 35.0,
        "water_dependency": "medium",
        "food_type": "herbivore",
        "description_pt": "Maior arara do mundo, vive na Amazônia e Pantanal. Alimenta-se principalmente de castanhas.",
        "description_en": "Largest macaw in the world, lives in the Amazon and Pantanal. Feeds mainly on nuts.",
    },
    {
        "name_pt": "Boto-cor-de-rosa",
        "name_en": "Amazon River Dolphin",
        "scientific_name": "Inia geoffrensis",
        "biome": "Amazônia",
        "type": "mammal",
        "thermoregulation": "regulator",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/Pink_river_dolphin.jpg/640px-Pink_river_dolphin.jpg",
        "optimal_temp_min": 24.0,
        "optimal_temp_max": 30.0,
        "water_dependency": "high",
        "food_type": "carnivore",
        "description_pt": "Golfinho de água doce endêmico da Amazônia. Sua coloração rosa é mais intensa em machos adultos.",
        "description_en": "Freshwater dolphin endemic to the Amazon. Its pink coloration is more intense in adult males.",
    },
    {
        "name_pt": "Mico-leão-dourado",
        "name_en": "Golden Lion Tamarin",
        "scientific_name": "Leontopithecus rosalia",
        "biome": "Mata Atlântica",
        "type": "mammal",
        "thermoregulation": "regulator",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Golden_lion_tamarin_portrait3.jpg/640px-Golden_lion_tamarin_portrait3.jpg",
        "optimal_temp_min": 20.0,
        "optimal_temp_max": 28.0,
        "water_dependency": "medium",
        "food_type": "omnivore",
        "description_pt": "Primata endêmico da Mata Atlântica, símbolo da conservação brasileira. Sua pelagem dourada é única e inconfundível.",
        "description_en": "Primate endemic to the Atlantic Forest, symbol of Brazilian conservation. Its golden fur is unique and unmistakable.",
    },
    {
        "name_pt": "Onça-parda",
        "name_en": "Puma",
        "scientific_name": "Puma concolor",
        "biome": "Mata Atlântica",
        "type": "mammal",
        "thermoregulation": "regulator",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d6/Mountain_Lion_in_Glacier_National_Park.jpg/640px-Mountain_Lion_in_Glacier_National_Park.jpg",
        "optimal_temp_min": 18.0,
        "optimal_temp_max": 30.0,
        "water_dependency": "medium",
        "food_type": "carnivore",
        "description_pt": "Segundo maior felino das Américas, adaptável a diversos ambientes. Solitário e excelente caçador.",
        "description_en": "Second largest cat in the Americas, adaptable to various environments. Solitary and excellent hunter.",
    },
    {
        "name_pt": "Preguiça-de-três-dedos",
        "name_en": "Three-toed Sloth",
        "scientific_name": "Bradypus variegatus",
        "biome": "Mata Atlântica",
        "type": "mammal",
        "thermoregulation": "regulator",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Bradypus.jpg/640px-Bradypus.jpg",
        "optimal_temp_min": 22.0,
        "optimal_temp_max": 30.0,
        "water_dependency": "low",
        "food_type": "herbivore",
        "description_pt": "Mamífero arborícola de metabolismo extremamente lento. Passa a maior parte do tempo nas árvores da Mata Atlântica.",
        "description_en": "Arboreal mammal with extremely slow metabolism. Spends most of its time in Atlantic Forest trees.",
    },
    {
        "name_pt": "Veado-catingueiro",
        "name_en": "Gray Brocket Deer",
        "scientific_name": "Mazama gouazoubira",
        "biome": "Caatinga",
        "type": "mammal",
        "thermoregulation": "regulator",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Mazama_gouazoubira.jpg/640px-Mazama_gouazoubira.jpg",
        "optimal_temp_min": 22.0,
        "optimal_temp_max": 38.0,
        "water_dependency": "low",
        "food_type": "herbivore",
        "description_pt": "Veado adaptado ao clima semiárido da Caatinga. Possui grande resistência à escassez de água e altas temperaturas.",
        "description_en": "Deer adapted to the semi-arid climate of Caatinga. Has great resistance to water scarcity and high temperatures.",
    },
    {
        "name_pt": "Tatu-bola",
        "name_en": "Brazilian Three-banded Armadillo",
        "scientific_name": "Tolypeutes tricinctus",
        "biome": "Caatinga",
        "type": "mammal",
        "thermoregulation": "regulator",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f8/Tolypeutes_tricinctus.jpg/640px-Tolypeutes_tricinctus.jpg",
        "optimal_temp_min": 20.0,
        "optimal_temp_max": 35.0,
        "water_dependency": "low",
        "food_type": "insectivore",
        "description_pt": "Único tatu capaz de se enrolar completamente em bola. Endêmico do Brasil, mascote da Copa 2014.",
        "description_en": "Only armadillo capable of rolling into a complete ball. Endemic to Brazil, mascot of the 2014 World Cup.",
    },
    {
        "name_pt": "Asa-branca",
        "name_en": "Picazuro Pigeon",
        "scientific_name": "Patagioenas picazuro",
        "biome": "Caatinga",
        "type": "bird",
        "thermoregulation": "regulator",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Patagioenas_picazuro.jpg/640px-Patagioenas_picazuro.jpg",
        "optimal_temp_min": 20.0,
        "optimal_temp_max": 40.0,
        "water_dependency": "medium",
        "food_type": "granivore",
        "description_pt": "Ave símbolo do sertão nordestino, imortalizada na música de Luiz Gonzaga. Altamente adaptada ao clima seco.",
        "description_en": "Bird symbol of the northeastern backlands, immortalized in Luiz Gonzaga's song. Highly adapted to dry climate.",
    },
]

# Cada espécie ganha um id estável (slug do nome científico) e usa a imagem
# embutida no projeto, servida pelo backend em /images/<slug>. As imagens ficam
# em backend/static_images/ (domínio público / Creative Commons, via Wikimedia).
def _seed_entry(sp: dict) -> dict:
    slug = slugify(sp["scientific_name"])
    return {**sp, "id": slug, "image_url": f"/images/{slug}"}


SPECIES_SEED = [_seed_entry(sp) for sp in INITIAL_SPECIES]


# ---------------------------------------------------------------------------
# Camada de armazenamento (in-memory por padrão, Mongo opcional)
# ---------------------------------------------------------------------------
class Store(Protocol):
    async def init(self) -> None: ...
    async def list_species(self) -> List[dict]: ...
    async def get_species(self, species_id: str) -> Optional[dict]: ...
    async def list_biomes(self) -> List[str]: ...
    async def save_simulation(self, doc: dict) -> None: ...


class InMemoryStore:
    """Armazenamento em memória — não requer banco de dados externo."""

    def __init__(self, seed: List[dict]):
        self._species = {sp["id"]: dict(sp) for sp in seed}
        self._simulations: List[dict] = []

    async def init(self) -> None:
        return None

    async def list_species(self) -> List[dict]:
        return list(self._species.values())

    async def get_species(self, species_id: str) -> Optional[dict]:
        return self._species.get(species_id)

    async def list_biomes(self) -> List[str]:
        return sorted({sp["biome"] for sp in self._species.values()})

    async def save_simulation(self, doc: dict) -> None:
        self._simulations.append(doc)


class MongoStore:
    """Armazenamento em MongoDB (usado quando MONGO_URL está definido)."""

    def __init__(self, mongo_url: str, db_name: str, seed: List[dict]):
        from motor.motor_asyncio import AsyncIOMotorClient  # import tardio

        self._client = AsyncIOMotorClient(mongo_url)
        self._db = self._client[db_name]
        self._seed = seed

    async def init(self) -> None:
        if await self._db.species.count_documents({}) == 0:
            await self._db.species.insert_many([dict(sp) for sp in self._seed])

    async def list_species(self) -> List[dict]:
        return [sp async for sp in self._db.species.find({}, {"_id": 0})]

    async def get_species(self, species_id: str) -> Optional[dict]:
        return await self._db.species.find_one({"id": species_id}, {"_id": 0})

    async def list_biomes(self) -> List[str]:
        return sorted(await self._db.species.distinct("biome"))

    async def save_simulation(self, doc: dict) -> None:
        await self._db.simulations.insert_one(doc)


def build_store() -> Store:
    if MONGO_URL:
        try:
            store = MongoStore(MONGO_URL, DB_NAME, SPECIES_SEED)
            print(f"[storage] Using MongoDB database '{DB_NAME}'")
            return store
        except ImportError:
            print("[storage] MONGO_URL set but 'motor' not installed — falling back to in-memory store")
    print("[storage] Using in-memory store")
    return InMemoryStore(SPECIES_SEED)


store: Store = build_store()


# ---------------------------------------------------------------------------
# Simulação fisiológica
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Explicação por IA (Gemini opcional, com fallback local)
# ---------------------------------------------------------------------------
def build_prompt(species_name: str, r: SimulationResponse, language: str) -> str:
    if language == "pt":
        return f"""Você é um professor de biologia explicando fisiologia ecológica para estudantes do ensino médio.

Espécie: {species_name}

Resultados da Simulação:
- Taxa Metabólica: {r.metabolic_rate}x
- Temperatura Corporal: {r.body_temperature}°C
- Probabilidade de Sobrevivência: {r.survival_probability}%
- Gasto Energético: {r.energy_expenditure}x
- Status de Água: {r.water_status}
- Status de Alimento: {r.food_status}
- Status de Homeostase: {r.homeostasis_status}
- Nível de Estresse: {r.stress_level}%

Explique em 2-3 parágrafos curtos:
1. O que está acontecendo fisiologicamente com este animal nessas condições
2. Como ele está tentando manter a homeostase
3. Quais são as implicações ecológicas dessas respostas

Use linguagem clara e acessível."""
    return f"""You are a biology teacher explaining ecological physiology to high school students.

Species: {species_name}

Simulation Results:
- Metabolic Rate: {r.metabolic_rate}x
- Body Temperature: {r.body_temperature}°C
- Survival Probability: {r.survival_probability}%
- Energy Expenditure: {r.energy_expenditure}x
- Water Status: {r.water_status}
- Food Status: {r.food_status}
- Homeostasis Status: {r.homeostasis_status}
- Stress Level: {r.stress_level}%

Explain in 2-3 short paragraphs:
1. What is happening physiologically with this animal under these conditions
2. How it is trying to maintain homeostasis
3. What are the ecological implications of these responses

Use clear and accessible language."""


_STATUS_TEXT = {
    "pt": {
        "stable": "estável", "stressed": "sob estresse", "critical": "em estado crítico",
        "adequate": "adequada", "insufficient": "insuficiente", "critical_res": "crítica",
    },
    "en": {
        "stable": "stable", "stressed": "under stress", "critical": "in a critical state",
        "adequate": "adequate", "insufficient": "insufficient", "critical_res": "critical",
    },
}


def build_local_explanation(species_name: str, r: SimulationResponse, language: str) -> str:
    """Explicação educativa determinística usada quando não há chave de IA."""
    t = _STATUS_TEXT["pt" if language == "pt" else "en"]
    homeo = t.get(r.homeostasis_status, r.homeostasis_status)
    water = t.get(r.water_status if r.water_status != "critical" else "critical_res", r.water_status)
    food = t.get(r.food_status if r.food_status != "critical" else "critical_res", r.food_status)

    if language == "pt":
        p1 = (
            f"Nas condições simuladas, a(o) {species_name} apresenta taxa metabólica de "
            f"{r.metabolic_rate}x e temperatura corporal de {r.body_temperature}°C, com um "
            f"nível de estresse fisiológico de {r.stress_level}%. Isso indica um organismo {homeo}, "
            f"cujo gasto energético está em {r.energy_expenditure}x o valor de repouso."
        )
        if r.homeostasis_status == "stable":
            p2 = (
                "O animal consegue manter a homeostase com pouco esforço: os mecanismos de "
                "termorregulação e o balanço hídrico e energético operam dentro da faixa ideal, "
                "deixando mais energia disponível para crescimento, reprodução e atividade."
            )
        elif r.homeostasis_status == "stressed":
            p2 = (
                "Para manter a homeostase, o animal precisa ativar respostas compensatórias — "
                "ajustando o metabolismo e o comportamento (buscar sombra, água ou abrigo). "
                "Esse esforço extra desvia energia que normalmente seria usada em outras funções."
            )
        else:
            p2 = (
                "A capacidade de manter a homeostase está sendo ultrapassada: o estresse combinado "
                "de temperatura, água e alimento exige um gasto energético elevado que não é "
                "sustentável por muito tempo, aproximando o animal de seus limites fisiológicos."
            )
        p3 = (
            f"Em termos ecológicos, com água {water} e alimento {food}, a probabilidade de "
            f"sobrevivência estimada é de {r.survival_probability}%. Condições assim ajudam a "
            "entender por que cada espécie ocupa determinados ambientes e como mudanças climáticas "
            "ou perda de habitat podem deslocar os limites de tolerância de cada uma."
        )
        return f"{p1}\n\n{p2}\n\n{p3}"

    p1 = (
        f"Under the simulated conditions, the {species_name} shows a metabolic rate of "
        f"{r.metabolic_rate}x and a body temperature of {r.body_temperature}°C, with a "
        f"physiological stress level of {r.stress_level}%. This describes an organism that is {homeo}, "
        f"with energy expenditure at {r.energy_expenditure}x its resting value."
    )
    if r.homeostasis_status == "stable":
        p2 = (
            "The animal maintains homeostasis with little effort: thermoregulation and the water and "
            "energy balance operate within the ideal range, leaving more energy available for growth, "
            "reproduction and activity."
        )
    elif r.homeostasis_status == "stressed":
        p2 = (
            "To maintain homeostasis, the animal must trigger compensatory responses — adjusting its "
            "metabolism and behavior (seeking shade, water or shelter). This extra effort diverts "
            "energy that would normally support other functions."
        )
    else:
        p2 = (
            "Its ability to maintain homeostasis is being exceeded: the combined stress of temperature, "
            "water and food demands a high energy cost that cannot be sustained for long, pushing the "
            "animal toward its physiological limits."
        )
    p3 = (
        f"Ecologically, with {water} water and {food} food, the estimated survival probability is "
        f"{r.survival_probability}%. Scenarios like this help explain why each species occupies certain "
        "environments and how climate change or habitat loss can shift each one's tolerance limits."
    )
    return f"{p1}\n\n{p2}\n\n{p3}"


async def generate_explanation(species_name: str, r: SimulationResponse, language: str) -> str:
    """Tenta o Gemini; se não houver chave/SDK ou ocorrer erro, usa o fallback local."""
    if GEMINI_API_KEY:
        try:
            import google.generativeai as genai  # import tardio

            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel(GEMINI_MODEL)
            prompt = build_prompt(species_name, r, language)
            response = await asyncio.to_thread(model.generate_content, prompt)
            text = (getattr(response, "text", "") or "").strip()
            if text:
                return text
        except Exception as exc:  # noqa: BLE001 — qualquer falha cai no fallback
            print(f"[ai] Gemini indisponível ({exc}); usando explicação local")
    return build_local_explanation(species_name, r, language)


# ---------------------------------------------------------------------------
# Chat com "professor de biologia" (Gemini opcional, com fallback)
# ---------------------------------------------------------------------------
def build_chat_prompt(messages: List[ChatMessage], species_name: Optional[str], language: str) -> str:
    if language == "pt":
        system = (
            "Você é um professor de biologia experiente e acolhedor, que ensina estudantes do "
            "ensino médio. Responda SEMPRE no contexto de biologia (ecologia, fisiologia, "
            "evolução, zoologia, botânica etc.). Se perguntarem algo fora de biologia, traga "
            "gentilmente de volta ao tema. Use linguagem clara, com exemplos. Quando o aluno "
            "pedir referências, recomende livros e artigos confiáveis, citando autor e ano "
            "quando possível. Seja conciso (no máximo ~150 palavras)."
        )
        ctx = f"\nTema atual: a espécie {species_name}." if species_name else ""
        labels = ("Aluno", "Professor")
        ending = "\nProfessor:"
    else:
        system = (
            "You are an experienced, welcoming biology teacher for high school students. Always "
            "answer within biology (ecology, physiology, evolution, zoology, botany, etc.). If "
            "asked something outside biology, gently steer back. Use clear language with examples. "
            "When asked for references, recommend reputable books and articles, citing author and "
            "year when possible. Be concise (max ~150 words)."
        )
        ctx = f"\nCurrent topic: the species {species_name}." if species_name else ""
        labels = ("Student", "Teacher")
        ending = "\nTeacher:"

    transcript = "\n".join(
        f"{labels[0] if m.role == 'user' else labels[1]}: {m.text}" for m in messages
    )
    return f"{system}{ctx}\n\n{transcript}{ending}"


def chat_fallback(messages: List[ChatMessage], language: str) -> str:
    last = messages[-1].text.lower() if messages else ""
    wants_refs = any(w in last for w in ["livro", "artigo", "referên", "book", "article", "paper"])
    if language == "pt":
        if wants_refs:
            return (
                "Estou sem acesso à IA agora, mas seguem pontos de partida confiáveis: o livro "
                '"Biologia" (Campbell), a Enciclopédia da Vida (eol.org), o Google Acadêmico '
                "(scholar.google.com) e a SciELO (scielo.org) para artigos em português. Para "
                "conversarmos livremente, peça para configurar a chave do Gemini no servidor."
            )
        return (
            "No momento estou sem acesso à IA para conversar (a chave do Gemini não está "
            "configurada no servidor). Assim que ativá-la, respondo suas dúvidas de biologia aqui."
        )
    if wants_refs:
        return (
            'I am offline right now, but here are reliable starting points: Campbell\'s "Biology", '
            "the Encyclopedia of Life (eol.org), Google Scholar (scholar.google.com) and PubMed "
            "(pubmed.ncbi.nlm.nih.gov). To chat freely, ask to set the Gemini key on the server."
        )
    return (
        "I am currently offline for chat (the Gemini key is not configured on the server). "
        "Once it is enabled, I can answer your biology questions right here."
    )


async def generate_chat_reply(
    messages: List[ChatMessage], species_name: Optional[str], language: str
) -> str:
    if GEMINI_API_KEY and messages:
        try:
            import google.generativeai as genai  # import tardio

            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel(GEMINI_MODEL)
            prompt = build_chat_prompt(messages, species_name, language)
            response = await asyncio.to_thread(model.generate_content, prompt)
            text = (getattr(response, "text", "") or "").strip()
            if text:
                return text
        except Exception as exc:  # noqa: BLE001
            print(f"[ai] Gemini (chat) indisponível ({exc}); usando fallback")
    return chat_fallback(messages, language)


# ---------------------------------------------------------------------------
# Aplicação
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    await store.init()
    yield


app = FastAPI(title="EcoFisioLab API", version="1.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"message": "EcoFisioLab API", "status": "running", "ai": bool(GEMINI_API_KEY)}


@app.get("/api/ai-check")
async def ai_check():
    """Diagnóstico TEMPORÁRIO da IA (Gemini) — remover depois de configurar."""
    out = {"key_set": bool(GEMINI_API_KEY), "model": GEMINI_MODEL}
    if not GEMINI_API_KEY:
        return out
    try:
        import google.generativeai as genai

        genai.configure(api_key=GEMINI_API_KEY)
        try:
            out["available_models"] = [
                m.name
                for m in genai.list_models()
                if "generateContent" in getattr(m, "supported_generation_methods", [])
            ]
        except Exception as e:  # noqa: BLE001
            out["list_error"] = f"{type(e).__name__}: {e}"
        try:
            model = genai.GenerativeModel(GEMINI_MODEL)
            resp = await asyncio.to_thread(model.generate_content, "Responda apenas: ok")
            out["generate_ok"] = bool((getattr(resp, "text", "") or "").strip())
            out["sample"] = (getattr(resp, "text", "") or "")[:80]
        except Exception as e:  # noqa: BLE001
            out["generate_error"] = f"{type(e).__name__}: {e}"
    except Exception as e:  # noqa: BLE001
        out["sdk_error"] = f"{type(e).__name__}: {e}"
    return out


@app.get("/api/species", response_model=List[Species])
async def get_all_species():
    return [Species(**sp) for sp in await store.list_species()]


@app.get("/api/species/biome/{biome}", response_model=List[Species])
async def get_species_by_biome(biome: str):
    return [Species(**sp) for sp in await store.list_species() if sp["biome"] == biome]


@app.get("/api/species/{species_id}", response_model=Species)
async def get_species(species_id: str):
    species = await store.get_species(species_id)
    if not species:
        raise HTTPException(status_code=404, detail="Species not found")
    return Species(**species)


@app.get("/api/biomes")
async def get_biomes():
    return {"biomes": await store.list_biomes()}


@app.post("/api/simulate", response_model=SimulationResponse)
async def simulate_physiology(request: SimulationRequest):
    species = await store.get_species(request.species_id)
    if not species:
        raise HTTPException(status_code=404, detail="Species not found")

    result = run_physiology(
        species, request.temperature, request.water_availability, request.food_availability
    )

    await store.save_simulation(
        {
            "species_id": request.species_id,
            "temperature": request.temperature,
            "water_availability": request.water_availability,
            "food_availability": request.food_availability,
            "result": result,
        }
    )
    return SimulationResponse(**result)


@app.post("/api/explain")
async def get_ai_explanation(request: ExplanationRequest):
    explanation = await generate_explanation(
        request.species_name, request.simulation_result, request.language
    )
    return {"explanation": explanation}


@app.post("/api/chat")
async def chat(request: ChatRequest):
    reply = await generate_chat_reply(request.messages, request.species_name, request.language)
    return {"reply": reply}


# ---------------------------------------------------------------------------
# Imagens das espécies (embutidas em backend/static_images, servidas por slug)
# ---------------------------------------------------------------------------
IMAGES_DIR = os.path.join(os.path.dirname(__file__), "static_images")


@app.get("/images/{slug}")
async def get_species_image(slug: str):
    slug = os.path.basename(slug)  # evita path traversal
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        path = os.path.join(IMAGES_DIR, slug + ext)
        if os.path.isfile(path):
            return FileResponse(path)
    raise HTTPException(status_code=404, detail="Image not found")


# ---------------------------------------------------------------------------
# Servir o app web (build estático do Expo) no mesmo domínio da API.
# Permite publicar tudo como UM único serviço (um link só). Se o build não
# existir, o backend funciona apenas como API.
# ---------------------------------------------------------------------------
STATIC_DIR = os.getenv(
    "STATIC_DIR", os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
)


def setup_static() -> None:
    static_dir = os.path.abspath(STATIC_DIR)
    index_file = os.path.join(static_dir, "index.html")

    if not os.path.isfile(index_file):
        print(f"[web] Sem build do frontend em {static_dir} — servindo apenas a API")

        @app.get("/")
        async def root_info():
            return {"message": "EcoFisioLab API", "status": "running", "ai": bool(GEMINI_API_KEY)}

        return

    print(f"[web] Servindo o app web de {static_dir}")
    expo_dir = os.path.join(static_dir, "_expo")
    if os.path.isdir(expo_dir):
        app.mount("/_expo", StaticFiles(directory=expo_dir), name="expo-assets")

    # Rota "catch-all": serve arquivos estáticos, páginas .html das rotas do
    # Expo Router e, por fim, o index.html (SPA fallback). Declarada por último,
    # então as rotas /api/* acima têm prioridade.
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api") or full_path.startswith("_expo"):
            raise HTTPException(status_code=404, detail="Not found")
        candidate = os.path.join(static_dir, full_path)
        if full_path and os.path.isfile(candidate):
            return FileResponse(candidate)
        html_candidate = os.path.join(static_dir, full_path + ".html")
        if full_path and os.path.isfile(html_candidate):
            return FileResponse(html_candidate)
        return FileResponse(index_file)


setup_static()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8001")))
