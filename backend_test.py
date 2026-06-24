#!/usr/bin/env python3
"""
Suíte de testes da API do EcoFisioLab.

Pré-requisito: o backend rodando em http://localhost:8001
    cd backend && python server.py

Uso:
    python backend_test.py            # usa http://localhost:8001
    BASE_URL=http://host:porta python backend_test.py
"""

import os
import sys

import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:8001").rstrip("/")

EXPECTED_BIOMES = {"Pampa", "Amazônia", "Mata Atlântica", "Caatinga"}
EXPECTED_SPECIES_COUNT = 13
SPECIES_FIELDS = {
    "id", "name_pt", "name_en", "scientific_name", "biome", "type",
    "thermoregulation", "image_url", "optimal_temp_min", "optimal_temp_max",
    "water_dependency", "food_type", "description_pt", "description_en",
}
SIM_FIELDS = {
    "metabolic_rate", "body_temperature", "survival_probability",
    "energy_expenditure", "water_status", "food_status",
    "homeostasis_status", "stress_level",
}

passed = 0
failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"[PASS] {name}")
    else:
        failed += 1
        print(f"[FAIL] {name} — {detail}")


def main() -> int:
    # Evita UnicodeEncodeError em consoles não-UTF-8 (ex.: cp1252 no Windows).
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    print(f"=== Testando {BASE_URL} ===\n")

    # Health (a raiz "/" pode servir o app web; o status fica em /api/health)
    try:
        r = requests.get(f"{BASE_URL}/api/health", timeout=10)
        check("Health responde 200", r.status_code == 200, f"HTTP {r.status_code}")
        check("Health tem status", r.json().get("status") == "running", r.text)
    except Exception as e:
        check("Backend acessível", False, str(e))
        print("\nBackend inacessível — abortando.")
        return 1

    # Lista de espécies
    species = []
    try:
        r = requests.get(f"{BASE_URL}/api/species", timeout=10)
        species = r.json()
        check("GET /api/species 200", r.status_code == 200, f"HTTP {r.status_code}")
        check(
            f"Retorna {EXPECTED_SPECIES_COUNT} espécies",
            len(species) == EXPECTED_SPECIES_COUNT,
            f"obtido {len(species)}",
        )
        if species:
            missing = SPECIES_FIELDS - set(species[0].keys())
            check("Espécie tem todos os campos", not missing, f"faltando {missing}")
            check(
                "id é slug (string não vazia)",
                isinstance(species[0]["id"], str) and species[0]["id"] != "",
                repr(species[0].get("id")),
            )
    except Exception as e:
        check("GET /api/species", False, str(e))

    # Biomas
    try:
        r = requests.get(f"{BASE_URL}/api/biomes", timeout=10)
        biomes = set(r.json().get("biomes", []))
        check("GET /api/biomes 200", r.status_code == 200, f"HTTP {r.status_code}")
        check("Biomas corretos (4)", biomes == EXPECTED_BIOMES, f"obtido {biomes}")
    except Exception as e:
        check("GET /api/biomes", False, str(e))

    # Filtro por bioma
    try:
        r = requests.get(f"{BASE_URL}/api/species/biome/Pampa", timeout=10)
        pampa = r.json()
        check("Filtro por bioma 200", r.status_code == 200, f"HTTP {r.status_code}")
        check(
            "Todos do bioma filtrado",
            all(s["biome"] == "Pampa" for s in pampa) and len(pampa) > 0,
            f"{len(pampa)} espécies",
        )
    except Exception as e:
        check("Filtro por bioma", False, str(e))

    # Espécie por id + 404
    sample_id = species[0]["id"] if species else "panthera-onca"
    try:
        r = requests.get(f"{BASE_URL}/api/species/{sample_id}", timeout=10)
        check("GET espécie por id 200", r.status_code == 200, f"HTTP {r.status_code}")
        check("Espécie retornada tem id certo", r.json().get("id") == sample_id, r.text)

        r404 = requests.get(f"{BASE_URL}/api/species/nao-existe-xyz", timeout=10)
        check("Espécie inexistente -> 404", r404.status_code == 404, f"HTTP {r404.status_code}")
    except Exception as e:
        check("GET espécie por id", False, str(e))

    # Simulação
    sim_result = None
    try:
        payload = {
            "species_id": sample_id,
            "temperature": 28.0,
            "water_availability": 70.0,
            "food_availability": 70.0,
            "language": "pt",
        }
        r = requests.post(f"{BASE_URL}/api/simulate", json=payload, timeout=10)
        check("POST /api/simulate 200", r.status_code == 200, f"HTTP {r.status_code}")
        sim_result = r.json()
        missing = SIM_FIELDS - set(sim_result.keys())
        check("Resultado tem todos os campos", not missing, f"faltando {missing}")
        check(
            "Sobrevivência em 0–100",
            0 <= sim_result["survival_probability"] <= 100,
            str(sim_result.get("survival_probability")),
        )
        check(
            "Homeostase é valor válido",
            sim_result["homeostasis_status"] in {"stable", "stressed", "critical"},
            str(sim_result.get("homeostasis_status")),
        )

        r404 = requests.post(
            f"{BASE_URL}/api/simulate", json={**payload, "species_id": "nada"}, timeout=10
        )
        check("Simular espécie inexistente -> 404", r404.status_code == 404, f"HTTP {r404.status_code}")
    except Exception as e:
        check("POST /api/simulate", False, str(e))

    # Modo científico: Kleiber, respirometria e balanço energético
    try:
        sci_fields = {
            "basal_metabolic_rate_kcal", "vo2_ml_g_h", "energy_from_o2_kcal",
            "total_expenditure_kcal", "energy_balance_kcal", "thermoregulation_cost_kcal",
            "stress_breakdown",
        }
        base = {"species_id": "hydrochoerus-hydrochaeris", "temperature": 28,
                "water_availability": 70, "food_availability": 70, "language": "pt"}
        r = requests.post(f"{BASE_URL}/api/simulate", json=base, timeout=10).json()
        check("Resposta tem campos científicos", not (sci_fields - set(r.keys())), str(sci_fields - set(r.keys())))
        # Kleiber: capivara (50 kg, a=70) → TMB ≈ 70·50^0.75 ≈ 1316 kcal/dia
        bmr = r["basal_metabolic_rate_kcal"]
        check("TMB de Kleiber plausível (~1316)", 1200 <= bmr <= 1450, f"{bmr}")
        check("Gasto total ≥ TMB", r["total_expenditure_kcal"] >= bmr, "")
        check("stress_breakdown tem 4 fatores",
              set(r["stress_breakdown"].keys()) == {"termico", "agua", "energia", "predador"}, "")
        # Balanço energético: pouco alimento → negativo
        rneg = requests.post(f"{BASE_URL}/api/simulate", json={**base, "food_availability_kcal": 200}, timeout=10).json()
        check("Balanço energético negativo com pouco alimento", rneg["energy_balance_kcal"] < 0, str(rneg["energy_balance_kcal"]))
        # Q10: réptil metaboliza mais a 35 °C que a 15 °C
        rep = {"species_id": "salvator-merianae", "water_availability": 70, "food_availability": 70, "language": "pt"}
        b15 = requests.post(f"{BASE_URL}/api/simulate", json={**rep, "temperature": 15}, timeout=10).json()["basal_metabolic_rate_kcal"]
        b35 = requests.post(f"{BASE_URL}/api/simulate", json={**rep, "temperature": 35}, timeout=10).json()["basal_metabolic_rate_kcal"]
        check("Q10: réptil metaboliza mais no calor", b35 > b15, f"15°C={b15} 35°C={b35}")
    except Exception as e:
        check("Modo científico", False, str(e))

    # Explicação (Gemini ou fallback local)
    if sim_result:
        try:
            payload = {
                "species_name": "Onça-pintada",
                "simulation_result": sim_result,
                "language": "pt",
            }
            r = requests.post(f"{BASE_URL}/api/explain", json=payload, timeout=30)
            check("POST /api/explain 200", r.status_code == 200, f"HTTP {r.status_code}")
            text = r.json().get("explanation", "")
            check("Explicação não vazia", isinstance(text, str) and len(text) > 40, repr(text[:60]))
        except Exception as e:
            check("POST /api/explain", False, str(e))

    # Chat (Gemini ou fallback) + limites de payload
    try:
        r = requests.post(
            f"{BASE_URL}/api/chat",
            json={"messages": [{"role": "user", "text": "O que é homeostase?"}], "language": "pt"},
            timeout=40,
        )
        check("POST /api/chat 200", r.status_code == 200, f"HTTP {r.status_code}")
        check("Resposta do chat não vazia", len(r.json().get("reply", "")) > 10, "")

        big = requests.post(
            f"{BASE_URL}/api/chat",
            json={"messages": [{"role": "user", "text": "x" * 9000}], "language": "pt"},
            timeout=15,
        )
        check("Chat recusa texto gigante -> 422", big.status_code == 422, f"HTTP {big.status_code}")
    except Exception as e:
        check("POST /api/chat", False, str(e))

    # Segurança: path traversal deve ser bloqueado (usa http.client p/ não normalizar o path)
    try:
        import http.client
        from urllib.parse import urlparse

        u = urlparse(BASE_URL)
        conn = http.client.HTTPConnection(u.hostname, u.port or 80, timeout=15)
        conn.request("GET", "/../../backend/server.py")
        body = conn.getresponse().read()
        conn.close()
        leaked = b"from app.main import" in body or b"GEMINI_API_KEY" in body
        check("Path traversal bloqueado (não vaza fonte)", not leaked, "VAZOU código-fonte!")
    except Exception as e:
        check("Teste de path traversal", False, str(e))

    print(f"\n=== Resultado: {passed} passaram, {failed} falharam ===")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
