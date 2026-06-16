import React, { useEffect, useMemo, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Image,
  ActivityIndicator,
  StatusBar,
  useWindowDimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import Svg, { Path } from 'react-native-svg';
import { useLanguage } from '../contexts/LanguageContext';
import { Species, speciesApi } from '../services/api';
import {
  BRAZIL_STATES,
  BIOME_COLORS,
  MAP_WIDTH,
  MAP_HEIGHT,
  Biome,
} from '../data/brazilStates';

const BIOME_KEYS: Record<string, string> = {
  'Amazônia': 'amazonia',
  'Mata Atlântica': 'mataAtlantica',
  'Caatinga': 'caatinga',
  'Pampa': 'pampa',
  'Outros': 'otherBiomes',
};

// Biomas com espécies no app (na ordem da legenda). "Outros" fica à parte.
const HABITAT_BIOMES: Biome[] = ['Amazônia', 'Mata Atlântica', 'Caatinga', 'Pampa'];

export default function MapScreen() {
  const router = useRouter();
  const { language, t } = useLanguage();
  const { width } = useWindowDimensions();

  const [species, setSpecies] = useState<Species[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeBiome, setActiveBiome] = useState<Biome | null>(null);
  const [hoveredUf, setHoveredUf] = useState<string | null>(null);

  useEffect(() => {
    speciesApi
      .getAll()
      .then(setSpecies)
      .catch((e) => console.error('Error loading species:', e))
      .finally(() => setLoading(false));
  }, []);

  const speciesByBiome = useMemo(() => {
    const map: Record<string, Species[]> = {};
    for (const s of species) {
      (map[s.biome] = map[s.biome] || []).push(s);
    }
    return map;
  }, [species]);

  const translateBiome = (biome: string) => {
    const key = BIOME_KEYS[biome];
    return key ? t(key) : biome;
  };

  const svgWidth = Math.min(width - 32, 460);
  const svgHeight = (svgWidth * MAP_HEIGHT) / MAP_WIDTH;

  const enter = (uf: string, biome: Biome) => {
    setHoveredUf(uf);
    setActiveBiome(biome);
  };

  const activeSpecies = activeBiome ? speciesByBiome[activeBiome] || [] : [];

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" />

      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color="white" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>{t('habitatMap')}</Text>
        <View style={{ width: 40 }} />
      </View>

      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#4CAF50" />
          <Text style={styles.loadingText}>{t('loading')}</Text>
        </View>
      ) : (
        <ScrollView contentContainerStyle={styles.content}>
          <Text style={styles.prompt}>{t('hoverPrompt')}</Text>

          <View style={styles.mapWrapper}>
            <Svg width={svgWidth} height={svgHeight} viewBox={`0 0 ${MAP_WIDTH} ${MAP_HEIGHT}`}>
              {BRAZIL_STATES.map((s) => {
                const dimmed = activeBiome != null && s.biome !== activeBiome;
                const isHovered = hoveredUf === s.uf;
                return (
                  <Path
                    key={s.uf}
                    d={s.path}
                    fill={BIOME_COLORS[s.biome]}
                    fillOpacity={dimmed ? 0.4 : 1}
                    stroke={isHovered ? '#ffffff' : '#1a1a1a'}
                    strokeWidth={isHovered ? 2.2 : 0.7}
                    onPress={() => enter(s.uf, s.biome)}
                    // @ts-ignore — eventos de mouse (web)
                    onMouseEnter={() => enter(s.uf, s.biome)}
                    // @ts-ignore
                    onMouseLeave={() => setHoveredUf(null)}
                  />
                );
              })}
            </Svg>
          </View>

          {/* Legenda */}
          <View style={styles.legend}>
            <Text style={styles.sectionTitle}>{t('legend')}</Text>
            {HABITAT_BIOMES.map((b) => {
              const count = (speciesByBiome[b] || []).length;
              const selected = activeBiome === b;
              return (
                <TouchableOpacity
                  key={b}
                  style={[styles.legendRow, selected && styles.legendRowActive]}
                  onPress={() => {
                    setActiveBiome(b);
                    setHoveredUf(null);
                  }}
                >
                  <View style={[styles.swatch, { backgroundColor: BIOME_COLORS[b] }]} />
                  <Text style={styles.legendText}>{translateBiome(b)}</Text>
                  <Text style={styles.legendCount}>{count}</Text>
                </TouchableOpacity>
              );
            })}
            <View style={styles.legendRow}>
              <View style={[styles.swatch, { backgroundColor: BIOME_COLORS['Outros'] }]} />
              <Text style={[styles.legendText, { color: '#888' }]}>{t('otherBiomes')}</Text>
            </View>
          </View>

          {/* Painel do habitat ativo */}
          <View style={styles.panel}>
            {activeBiome ? (
              <>
                <View style={styles.panelHeader}>
                  <View style={[styles.swatch, { backgroundColor: BIOME_COLORS[activeBiome] }]} />
                  <Text style={styles.panelTitle}>{translateBiome(activeBiome)}</Text>
                </View>
                {activeSpecies.length > 0 ? (
                  activeSpecies.map((sp) => (
                    <TouchableOpacity
                      key={sp.id}
                      style={styles.speciesRow}
                      onPress={() => router.push(`/simulator?id=${sp.id}`)}
                    >
                      <Image source={{ uri: sp.image_url }} style={styles.thumb} resizeMode="cover" />
                      <View style={{ flex: 1 }}>
                        <Text style={styles.speciesName}>
                          {language === 'pt' ? sp.name_pt : sp.name_en}
                        </Text>
                        <Text style={styles.speciesSci}>{sp.scientific_name}</Text>
                      </View>
                      <Ionicons name="chevron-forward" size={20} color="#4CAF50" />
                    </TouchableOpacity>
                  ))
                ) : (
                  <Text style={styles.emptyText}>{t('noSpeciesHere')}</Text>
                )}
              </>
            ) : (
              <Text style={styles.emptyText}>{t('speciesInHabitat')}</Text>
            )}
          </View>
        </ScrollView>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#1a1a1a' },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  loadingText: { color: 'white', marginTop: 16, fontSize: 16 },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#2a2a2a',
  },
  backButton: { padding: 8 },
  headerTitle: { fontSize: 20, fontWeight: 'bold', color: 'white' },
  content: { padding: 16, alignItems: 'center' },
  prompt: { color: '#ccc', fontSize: 14, textAlign: 'center', marginBottom: 16, lineHeight: 20 },
  mapWrapper: { backgroundColor: '#101010', borderRadius: 12, padding: 8 },
  legend: {
    alignSelf: 'stretch',
    backgroundColor: '#2a2a2a',
    borderRadius: 12,
    padding: 16,
    marginTop: 20,
  },
  sectionTitle: { color: 'white', fontSize: 16, fontWeight: 'bold', marginBottom: 12 },
  legendRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    paddingHorizontal: 8,
    borderRadius: 8,
  },
  legendRowActive: { backgroundColor: '#1a1a1a' },
  swatch: { width: 18, height: 18, borderRadius: 4, marginRight: 12 },
  legendText: { color: 'white', fontSize: 15, flex: 1 },
  legendCount: { color: '#4CAF50', fontSize: 14, fontWeight: 'bold' },
  panel: {
    alignSelf: 'stretch',
    backgroundColor: '#2a2a2a',
    borderRadius: 12,
    padding: 16,
    marginTop: 16,
  },
  panelHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 12 },
  panelTitle: { color: 'white', fontSize: 18, fontWeight: 'bold' },
  speciesRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1a1a1a',
    borderRadius: 8,
    padding: 8,
    marginBottom: 8,
  },
  thumb: { width: 48, height: 48, borderRadius: 6, marginRight: 12, backgroundColor: '#333' },
  speciesName: { color: 'white', fontSize: 15, fontWeight: '600' },
  speciesSci: { color: '#888', fontSize: 12, fontStyle: 'italic' },
  emptyText: { color: '#888', fontSize: 14, textAlign: 'center', paddingVertical: 12 },
});
