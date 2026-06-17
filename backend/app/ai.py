"""Integração de IA (Google Gemini opcional) com fallback local determinístico.

A explicação e o chat funcionam mesmo sem chave: usam textos gerados localmente.
Com GEMINI_API_KEY, o modelo é descoberto dinamicamente (evita nome fixo
descontinuado) e reutilizado em explicação e chat.
"""

import asyncio
from typing import List, Optional

from .config import GEMINI_API_KEY, GEMINI_MODEL, log
from .models import ChatMessage, SimulationResponse


# ---------------------------------------------------------------------------
# Prompts
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


# ---------------------------------------------------------------------------
# Chamada ao Gemini (modelo resolvido dinamicamente)
# ---------------------------------------------------------------------------
_resolved_model: Optional[str] = None


def _resolve_gemini_model(genai) -> str:
    global _resolved_model
    if _resolved_model:
        return _resolved_model
    try:
        available = [
            m.name.split("/")[-1]
            for m in genai.list_models()
            if "generateContent" in getattr(m, "supported_generation_methods", [])
        ]
    except Exception:
        available = []
    preference = [GEMINI_MODEL, "gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.5-pro", "gemini-1.5-flash"]
    chosen = None
    for p in preference:
        if p and (not available or p in available):
            chosen = p
            break
    if not chosen:
        flash = [a for a in available if "flash" in a]
        chosen = (flash or available or [GEMINI_MODEL])[0]
    _resolved_model = chosen
    log.info("[ai] modelo Gemini selecionado: %s (%d disponíveis)", chosen, len(available))
    return chosen


async def _gemini_generate(prompt: str) -> Optional[str]:
    """Chama o Gemini e retorna o texto; None se não houver chave ou ocorrer erro."""
    if not GEMINI_API_KEY:
        return None
    try:
        import google.generativeai as genai  # import tardio

        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(_resolve_gemini_model(genai))
        response = await asyncio.to_thread(model.generate_content, prompt)
        return (getattr(response, "text", "") or "").strip() or None
    except Exception as exc:  # noqa: BLE001
        log.warning("[ai] Gemini indisponível (%s)", exc)
        return None


async def generate_explanation(species_name: str, r: SimulationResponse, language: str) -> str:
    """Tenta o Gemini; se indisponível, usa a explicação local determinística."""
    text = await _gemini_generate(build_prompt(species_name, r, language))
    return text or build_local_explanation(species_name, r, language)


async def generate_chat_reply(
    messages: List[ChatMessage], species_name: Optional[str], language: str
) -> str:
    if messages:
        text = await _gemini_generate(build_chat_prompt(messages, species_name, language))
        if text:
            return text
    return chat_fallback(messages, language)
