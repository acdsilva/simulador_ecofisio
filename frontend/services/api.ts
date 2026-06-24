import axios from 'axios';

// URL do backend.
// - Produção (o backend serve o app no mesmo domínio): deixe vazio → usa caminho relativo "/api".
// - Desenvolvimento com servidores separados: defina EXPO_PUBLIC_BACKEND_URL no .env
//   (ex.: http://localhost:8001).
const API_URL = process.env.EXPO_PUBLIC_BACKEND_URL || '';

const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Species {
  id: string;
  name_pt: string;
  name_en: string;
  scientific_name: string;
  biome: string;
  type: string;
  thermoregulation: string;
  image_url: string;
  optimal_temp_min: number;
  optimal_temp_max: number;
  water_dependency: string;
  food_type: string;
  description_pt: string;
  description_en: string;
  mass_kg?: number;
  kleiber_a?: number;
  body_temp_c?: number;
  ventilation_rate_lmin?: number;
}

export interface SimulationResult {
  metabolic_rate: number;
  body_temperature: number;
  survival_probability: number;
  energy_expenditure: number;
  water_status: string;
  food_status: string;
  homeostasis_status: string;
  stress_level: number;
  // Modo científico
  basal_metabolic_rate_kcal: number;
  vo2_ml_g_h: number;
  energy_from_o2_kcal: number;
  total_expenditure_kcal: number;
  energy_balance_kcal: number;
  thermoregulation_cost_kcal: number;
  stress_breakdown: Record<string, number>;
}

export interface ScientificOptions {
  foodKcal?: number;
  predator?: boolean;
  o2Inspired?: number;
  o2Expired?: number;
}

export const speciesApi = {
  getAll: async (): Promise<Species[]> => {
    const response = await api.get('/species');
    return response.data;
  },

  getByBiome: async (biome: string): Promise<Species[]> => {
    const response = await api.get(`/species/biome/${biome}`);
    return response.data;
  },

  getById: async (id: string): Promise<Species> => {
    const response = await api.get(`/species/${id}`);
    return response.data;
  },
};

export const simulationApi = {
  simulate: async (
    speciesId: string,
    temperature: number,
    waterAvailability: number,
    foodAvailability: number,
    language: string,
    options?: ScientificOptions
  ): Promise<SimulationResult> => {
    const response = await api.post('/simulate', {
      species_id: speciesId,
      temperature,
      water_availability: waterAvailability,
      food_availability: foodAvailability,
      language,
      ...(options?.foodKcal != null ? { food_availability_kcal: options.foodKcal } : {}),
      ...(options?.predator != null ? { predator_presence: options.predator } : {}),
      ...(options?.o2Inspired != null ? { o2_inspired: options.o2Inspired } : {}),
      ...(options?.o2Expired != null ? { o2_expired: options.o2Expired } : {}),
    });
    return response.data;
  },

  getExplanation: async (
    speciesName: string,
    simulationResult: SimulationResult,
    language: string
  ): Promise<string> => {
    const response = await api.post('/explain', {
      species_name: speciesName,
      simulation_result: simulationResult,
      language,
    });
    return response.data.explanation;
  },
};

export interface ChatMessage {
  role: 'user' | 'assistant';
  text: string;
}

export const chatApi = {
  send: async (
    messages: ChatMessage[],
    speciesName: string | null,
    language: string
  ): Promise<string> => {
    const response = await api.post('/chat', {
      messages,
      species_name: speciesName,
      language,
    });
    return response.data.reply;
  },
};

export const biomesApi = {
  getAll: async (): Promise<string[]> => {
    const response = await api.get('/biomes');
    return response.data.biomes;
  },
};
