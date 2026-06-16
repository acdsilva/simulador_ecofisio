import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Image,
  ActivityIndicator,
  StatusBar,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { useLanguage } from '../contexts/LanguageContext';
import { Species, speciesApi, biomesApi } from '../services/api';
import { Ionicons } from '@expo/vector-icons';

export default function SpeciesScreen() {
  const router = useRouter();
  const { language, t } = useLanguage();
  const [species, setSpecies] = useState<Species[]>([]);
  const [biomes, setBiomes] = useState<string[]>([]);
  const [selectedBiome, setSelectedBiome] = useState<string>('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [allSpecies, allBiomes] = await Promise.all([
        speciesApi.getAll(),
        biomesApi.getAll(),
      ]);
      setSpecies(allSpecies);
      setBiomes(allBiomes);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredSpecies = selectedBiome === 'all'
    ? species
    : species.filter(s => s.biome === selectedBiome);

  const biomeKeys: Record<string, string> = {
    'Pampa': 'pampa',
    'Amazônia': 'amazonia',
    'Mata Atlântica': 'mataAtlantica',
    'Caatinga': 'caatinga',
  };

  const translateBiome = (biome: string) => {
    const key = biomeKeys[biome];
    return key ? t(key) : biome;
  };

  const translateType = (type: string) => {
    if (type === 'mammal') return t('mammal');
    if (type === 'bird') return t('bird');
    if (type === 'reptile') return t('reptile');
    return type;
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#4CAF50" />
        <Text style={styles.loadingText}>{t('loading')}</Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" />
      
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color="white" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>{t('selectSpecies')}</Text>
        <View style={{ width: 40 }} />
      </View>

      <View style={styles.filterContainer}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          <TouchableOpacity
            style={[styles.filterButton, selectedBiome === 'all' && styles.filterButtonActive]}
            onPress={() => setSelectedBiome('all')}
          >
            <Text style={[styles.filterText, selectedBiome === 'all' && styles.filterTextActive]}>
              {t('allBiomes')}
            </Text>
          </TouchableOpacity>
          {biomes.map(biome => (
            <TouchableOpacity
              key={biome}
              style={[styles.filterButton, selectedBiome === biome && styles.filterButtonActive]}
              onPress={() => setSelectedBiome(biome)}
            >
              <Text style={[styles.filterText, selectedBiome === biome && styles.filterTextActive]}>
                {translateBiome(biome)}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      <ScrollView style={styles.content}>
        {filteredSpecies.map(sp => (
          <TouchableOpacity
            key={sp.id}
            style={styles.speciesCard}
            onPress={() => router.push(`/simulator?id=${sp.id}`)}
          >
            <Image
              source={{ uri: sp.image_url }}
              style={styles.speciesImage}
              resizeMode="cover"
            />
            <View style={styles.speciesInfo}>
              <Text style={styles.speciesName}>
                {language === 'pt' ? sp.name_pt : sp.name_en}
              </Text>
              <Text style={styles.scientificName}>{sp.scientific_name}</Text>
              
              <View style={styles.tags}>
                <View style={[styles.tag, { backgroundColor: '#2196F3' }]}>
                  <Text style={styles.tagText}>{translateBiome(sp.biome)}</Text>
                </View>
                <View style={[styles.tag, { backgroundColor: '#FF9800' }]}>
                  <Text style={styles.tagText}>{translateType(sp.type)}</Text>
                </View>
              </View>

              <Text style={styles.speciesDescription}>
                {language === 'pt' ? sp.description_pt : sp.description_en}
              </Text>
            </View>
            <Ionicons name="chevron-forward" size={24} color="#4CAF50" />
          </TouchableOpacity>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a1a',
  },
  loadingContainer: {
    flex: 1,
    backgroundColor: '#1a1a1a',
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    color: 'white',
    marginTop: 16,
    fontSize: 16,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#2a2a2a',
  },
  backButton: {
    padding: 8,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: 'white',
  },
  filterContainer: {
    padding: 16,
  },
  filterButton: {
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 20,
    backgroundColor: '#2a2a2a',
    marginRight: 12,
  },
  filterButtonActive: {
    backgroundColor: '#4CAF50',
  },
  filterText: {
    color: '#888',
    fontSize: 14,
    fontWeight: '600',
  },
  filterTextActive: {
    color: 'white',
  },
  content: {
    flex: 1,
    paddingHorizontal: 16,
  },
  speciesCard: {
    backgroundColor: '#2a2a2a',
    borderRadius: 12,
    marginBottom: 16,
    overflow: 'hidden',
    flexDirection: 'row',
    alignItems: 'center',
  },
  speciesImage: {
    width: 100,
    height: 100,
  },
  speciesInfo: {
    flex: 1,
    padding: 12,
  },
  speciesName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 4,
  },
  scientificName: {
    fontSize: 13,
    fontStyle: 'italic',
    color: '#888',
    marginBottom: 8,
  },
  tags: {
    flexDirection: 'row',
    marginBottom: 8,
  },
  tag: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    marginRight: 6,
  },
  tagText: {
    color: 'white',
    fontSize: 11,
    fontWeight: '600',
  },
  speciesDescription: {
    fontSize: 13,
    color: '#ccc',
    lineHeight: 18,
  },
});
