"""Dados-semente das 13 espécies e geração de IDs estáveis (slug)."""

import re
import unicodedata


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
        "image_url": "",
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
        "image_url": "",
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
        "image_url": "",
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
        "image_url": "",
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
        "image_url": "",
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
        "image_url": "",
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
        "image_url": "",
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
        "image_url": "",
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
        "image_url": "",
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
        "image_url": "",
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
        "image_url": "",
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
        "image_url": "",
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
        "image_url": "",
        "optimal_temp_min": 20.0,
        "optimal_temp_max": 40.0,
        "water_dependency": "medium",
        "food_type": "granivore",
        "description_pt": "Ave símbolo do sertão nordestino, imortalizada na música de Luiz Gonzaga. Altamente adaptada ao clima seco.",
        "description_en": "Bird symbol of the northeastern backlands, immortalized in Luiz Gonzaga's song. Highly adapted to dry climate.",
    },
]


# Constantes fisiológicas por espécie (valores típicos da literatura).
#  - mass_kg: massa corporal adulta típica.
#  - kleiber_a: constante da Lei de Kleiber para TMB em kcal/dia (~70 mamíferos,
#    ~78 aves). Ectotérmicos (réptil) usam o modelo Q10 e ignoram este valor.
#  - body_temp_c: temperatura corporal típica do endotérmico (réptil = ambiente).
#  - ventilation_rate_lmin: ventilação-minuto em repouso, estimada por alometria
#    (≈ 0,38 · M^0,8 L/min).
# Fontes: Kleiber (1932); Lasiewski & Dawson (1967, aves); valores de massa/Tb de
# compêndios de fisiologia animal. Detalhes em CIENCIA.md.
PHYSIOLOGY = {
    "Hydrochoerus hydrochaeris": {"mass_kg": 50.0, "kleiber_a": 70.0, "body_temp_c": 38.0, "ventilation_rate_lmin": 8.7},
    "Vanellus chilensis":        {"mass_kg": 0.28, "kleiber_a": 78.0, "body_temp_c": 41.0, "ventilation_rate_lmin": 0.14},
    "Cavia aperea":              {"mass_kg": 0.5,  "kleiber_a": 70.0, "body_temp_c": 38.5, "ventilation_rate_lmin": 0.22},
    "Salvator merianae":         {"mass_kg": 3.5,  "kleiber_a": 70.0, "body_temp_c": 30.0, "ventilation_rate_lmin": 1.02},
    "Panthera onca":             {"mass_kg": 85.0, "kleiber_a": 70.0, "body_temp_c": 38.0, "ventilation_rate_lmin": 13.1},
    "Anodorhynchus hyacinthinus":{"mass_kg": 1.5,  "kleiber_a": 78.0, "body_temp_c": 41.0, "ventilation_rate_lmin": 0.52},
    "Inia geoffrensis":          {"mass_kg": 120.0,"kleiber_a": 70.0, "body_temp_c": 36.0, "ventilation_rate_lmin": 17.3},
    "Leontopithecus rosalia":    {"mass_kg": 0.6,  "kleiber_a": 70.0, "body_temp_c": 38.0, "ventilation_rate_lmin": 0.25},
    "Puma concolor":             {"mass_kg": 55.0, "kleiber_a": 70.0, "body_temp_c": 38.5, "ventilation_rate_lmin": 9.4},
    "Bradypus variegatus":       {"mass_kg": 4.0,  "kleiber_a": 70.0, "body_temp_c": 33.0, "ventilation_rate_lmin": 1.15},
    "Mazama gouazoubira":        {"mass_kg": 17.0, "kleiber_a": 70.0, "body_temp_c": 38.5, "ventilation_rate_lmin": 3.7},
    "Tolypeutes tricinctus":     {"mass_kg": 1.5,  "kleiber_a": 70.0, "body_temp_c": 35.0, "ventilation_rate_lmin": 0.52},
    "Patagioenas picazuro":      {"mass_kg": 0.35, "kleiber_a": 78.0, "body_temp_c": 41.0, "ventilation_rate_lmin": 0.17},
}


def _seed_entry(sp: dict) -> dict:
    """Adiciona id (slug), imagem local e as constantes fisiológicas da espécie."""
    slug = slugify(sp["scientific_name"])
    return {**sp, "id": slug, "image_url": f"/images/{slug}", **PHYSIOLOGY[sp["scientific_name"]]}


SPECIES_SEED = [_seed_entry(sp) for sp in INITIAL_SPECIES]
