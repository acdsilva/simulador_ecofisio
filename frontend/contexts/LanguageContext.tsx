import React, { createContext, useContext, useState, ReactNode } from 'react';

type Language = 'pt' | 'en';

interface Translations {
  [key: string]: {
    pt: string;
    en: string;
  };
}

const translations: Translations = {
  appTitle: {
    pt: 'EcoFisioLab',
    en: 'EcoFisioLab'
  },
  appSubtitle: {
    pt: 'Ciências em Contexto',
    en: 'Sciences in Context'
  },
  selectSpecies: {
    pt: 'Selecionar Espécie',
    en: 'Select Species'
  },
  simulator: {
    pt: 'Simulador',
    en: 'Simulator'
  },
  allBiomes: {
    pt: 'Todos os Biomas',
    en: 'All Biomes'
  },
  pampa: {
    pt: 'Pampa',
    en: 'Pampa'
  },
  amazonia: {
    pt: 'Amazônia',
    en: 'Amazon'
  },
  mataAtlantica: {
    pt: 'Mata Atlântica',
    en: 'Atlantic Forest'
  },
  caatinga: {
    pt: 'Caatinga',
    en: 'Caatinga'
  },
  scientificName: {
    pt: 'Nome Científico',
    en: 'Scientific Name'
  },
  biome: {
    pt: 'Bioma',
    en: 'Biome'
  },
  type: {
    pt: 'Tipo',
    en: 'Type'
  },
  thermoregulation: {
    pt: 'Termorregulação',
    en: 'Thermoregulation'
  },
  regulator: {
    pt: 'Regulador',
    en: 'Regulator'
  },
  conformer: {
    pt: 'Conformador',
    en: 'Conformer'
  },
  mammal: {
    pt: 'Mamífero',
    en: 'Mammal'
  },
  bird: {
    pt: 'Ave',
    en: 'Bird'
  },
  reptile: {
    pt: 'Réptil',
    en: 'Reptile'
  },
  startSimulation: {
    pt: 'Iniciar Simulação',
    en: 'Start Simulation'
  },
  environmentalParameters: {
    pt: 'Parâmetros Ambientais',
    en: 'Environmental Parameters'
  },
  temperature: {
    pt: 'Temperatura',
    en: 'Temperature'
  },
  waterAvailability: {
    pt: 'Disponibilidade de Água',
    en: 'Water Availability'
  },
  foodAvailability: {
    pt: 'Disponibilidade de Alimento',
    en: 'Food Availability'
  },
  simulate: {
    pt: 'Simular',
    en: 'Simulate'
  },
  physiologicalResponse: {
    pt: 'Resposta Fisiológica',
    en: 'Physiological Response'
  },
  metabolicRate: {
    pt: 'Taxa Metabólica',
    en: 'Metabolic Rate'
  },
  bodyTemperature: {
    pt: 'Temperatura Corporal',
    en: 'Body Temperature'
  },
  survivalProbability: {
    pt: 'Probabilidade de Sobrevivência',
    en: 'Survival Probability'
  },
  energyExpenditure: {
    pt: 'Gasto Energético',
    en: 'Energy Expenditure'
  },
  waterStatus: {
    pt: 'Status de Água',
    en: 'Water Status'
  },
  foodStatus: {
    pt: 'Status de Alimento',
    en: 'Food Status'
  },
  homeostasisStatus: {
    pt: 'Status de Homeostase',
    en: 'Homeostasis Status'
  },
  stressLevel: {
    pt: 'Nível de Estresse',
    en: 'Stress Level'
  },
  adequate: {
    pt: 'Adequado',
    en: 'Adequate'
  },
  insufficient: {
    pt: 'Insuficiente',
    en: 'Insufficient'
  },
  critical: {
    pt: 'Crítico',
    en: 'Critical'
  },
  stable: {
    pt: 'Estável',
    en: 'Stable'
  },
  stressed: {
    pt: 'Estressado',
    en: 'Stressed'
  },
  aiExplanation: {
    pt: 'Explicação IA',
    en: 'AI Explanation'
  },
  getExplanation: {
    pt: 'Obter Explicação',
    en: 'Get Explanation'
  },
  loading: {
    pt: 'Carregando...',
    en: 'Loading...'
  },
  error: {
    pt: 'Erro',
    en: 'Error'
  },
  back: {
    pt: 'Voltar',
    en: 'Back'
  },
  habitatMap: {
    pt: 'Mapa de Habitats',
    en: 'Habitat Map'
  },
  hoverPrompt: {
    pt: 'Passe o mouse (ou toque) sobre um estado para ver os animais daquele habitat.',
    en: 'Hover (or tap) a state to see the animals of that habitat.'
  },
  legend: {
    pt: 'Legenda',
    en: 'Legend'
  },
  otherBiomes: {
    pt: 'Outros biomas',
    en: 'Other biomes'
  },
  speciesInHabitat: {
    pt: 'Selecione um habitat no mapa ou na legenda.',
    en: 'Select a habitat on the map or legend.'
  },
  noSpeciesHere: {
    pt: 'Sem animais cadastrados neste bioma.',
    en: 'No animals registered in this biome.'
  },
  chatTitle: {
    pt: 'Converse com o Professor',
    en: 'Chat with the Teacher'
  },
  chatIntro: {
    pt: 'Tire dúvidas de biologia ou peça referências sobre este tema.',
    en: 'Ask biology questions or request references on this topic.'
  },
  chatPlaceholder: {
    pt: 'Escreva sua pergunta...',
    en: 'Type your question...'
  },
  send: {
    pt: 'Enviar',
    en: 'Send'
  },
  suggestBooks: {
    pt: '📚 Recomende livros e artigos sobre este assunto',
    en: '📚 Recommend books and articles on this topic'
  },
  suggestWhy: {
    pt: 'Por que isso acontece?',
    en: 'Why does this happen?'
  },
  suggestExample: {
    pt: 'Dê um exemplo do dia a dia',
    en: 'Give an everyday example'
  },
  suggestCuriosity: {
    pt: 'Conte uma curiosidade sobre esta espécie',
    en: 'Tell a fun fact about this species'
  },
  professor: {
    pt: 'Professor',
    en: 'Teacher'
  },
  scientificMode: {
    pt: 'Modo científico',
    en: 'Scientific mode'
  },
  foodKcal: {
    pt: 'Alimento (kcal/dia)',
    en: 'Food (kcal/day)'
  },
  predatorPresent: {
    pt: 'Predador presente',
    en: 'Predator present'
  },
  o2Inspired: {
    pt: 'O₂ inspirado',
    en: 'Inspired O₂'
  },
  o2Expired: {
    pt: 'O₂ expirado',
    en: 'Expired O₂'
  },
  scientificResults: {
    pt: 'Métricas Científicas',
    en: 'Scientific Metrics'
  },
  bmr: {
    pt: 'Taxa Metabólica Basal (Kleiber)',
    en: 'Basal Metabolic Rate (Kleiber)'
  },
  vo2: {
    pt: 'Consumo de O₂ (VO₂)',
    en: 'O₂ Consumption (VO₂)'
  },
  energyFromO2: {
    pt: 'Energia por respirometria',
    en: 'Energy by respirometry'
  },
  totalExpenditure: {
    pt: 'Gasto energético total',
    en: 'Total energy expenditure'
  },
  energyBalance: {
    pt: 'Balanço energético',
    en: 'Energy balance'
  },
  thermoCost: {
    pt: 'Custo de termorregulação',
    en: 'Thermoregulation cost'
  },
  stressBreakdown: {
    pt: 'Composição do estresse',
    en: 'Stress breakdown'
  },
  stTermico: { pt: 'Térmico', en: 'Thermal' },
  stAgua: { pt: 'Água', en: 'Water' },
  stEnergia: { pt: 'Energia', en: 'Energy' },
  stPredador: { pt: 'Predador', en: 'Predator' }
};

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [language, setLanguage] = useState<Language>('pt');

  const t = (key: string): string => {
    return translations[key]?.[language] || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};
