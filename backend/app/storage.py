"""Camada de armazenamento: em memória por padrão, MongoDB se MONGO_URL existir."""

from collections import deque
from typing import List, Optional, Protocol

from .config import DB_NAME, MONGO_URL, SIM_HISTORY_MAX, log
from .species_data import SPECIES_SEED


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
        # deque com limite evita crescimento infinito de memória (DoS por spam).
        self._simulations: deque = deque(maxlen=SIM_HISTORY_MAX)

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
            log.info("Storage: MongoDB '%s'", DB_NAME)
            return store
        except ImportError:
            log.warning("MONGO_URL definido mas 'motor' não está instalado — usando memória")
    log.info("Storage: em memória")
    return InMemoryStore(SPECIES_SEED)


# Singleton usado pelas rotas; inicializado no lifespan do app.
store: Store = build_store()
