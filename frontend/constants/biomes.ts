// Mapeia o nome do bioma (como vem do backend) para a chave de tradução do
// LanguageContext. Centraliza o que antes estava duplicado em species.tsx e map.tsx.

export const BIOME_TRANSLATION_KEYS: Record<string, string> = {
  Pampa: 'pampa',
  Amazônia: 'amazonia',
  'Mata Atlântica': 'mataAtlantica',
  Caatinga: 'caatinga',
  Outros: 'otherBiomes',
};

/** Rótulo traduzido de um bioma; cai no próprio nome se não houver tradução. */
export function biomeLabel(biome: string, t: (key: string) => string): string {
  const key = BIOME_TRANSLATION_KEYS[biome];
  return key ? t(key) : biome;
}
