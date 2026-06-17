"""Rotas da API (/api/*) e imagens das espécies (/images/<slug>)."""

import os
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from .ai import generate_chat_reply, generate_explanation
from .config import GEMINI_API_KEY, IMAGES_DIR
from .models import (
    ChatRequest,
    ExplanationRequest,
    SimulationRequest,
    SimulationResponse,
    Species,
)
from .physiology import run_physiology
from .ratelimit import ai_rate_limit
from .storage import store

router = APIRouter()


@router.get("/api/health")
async def health():
    return {"message": "EcoFisioLab API", "status": "running", "ai": bool(GEMINI_API_KEY)}


@router.get("/api/species", response_model=List[Species])
async def get_all_species():
    return [Species(**sp) for sp in await store.list_species()]


@router.get("/api/species/biome/{biome}", response_model=List[Species])
async def get_species_by_biome(biome: str):
    return [Species(**sp) for sp in await store.list_species() if sp["biome"] == biome]


@router.get("/api/species/{species_id}", response_model=Species)
async def get_species(species_id: str):
    species = await store.get_species(species_id)
    if not species:
        raise HTTPException(status_code=404, detail="Species not found")
    return Species(**species)


@router.get("/api/biomes")
async def get_biomes():
    return {"biomes": await store.list_biomes()}


@router.post("/api/simulate", response_model=SimulationResponse)
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


@router.post("/api/explain", dependencies=[Depends(ai_rate_limit)])
async def get_ai_explanation(request: ExplanationRequest):
    explanation = await generate_explanation(
        request.species_name, request.simulation_result, request.language
    )
    return {"explanation": explanation}


@router.post("/api/chat", dependencies=[Depends(ai_rate_limit)])
async def chat(request: ChatRequest):
    reply = await generate_chat_reply(request.messages, request.species_name, request.language)
    return {"reply": reply}


@router.get("/images/{slug}")
async def get_species_image(slug: str):
    slug = os.path.basename(slug)  # evita path traversal
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        path = os.path.join(str(IMAGES_DIR), slug + ext)
        if os.path.isfile(path):
            return FileResponse(path)
    raise HTTPException(status_code=404, detail="Image not found")
