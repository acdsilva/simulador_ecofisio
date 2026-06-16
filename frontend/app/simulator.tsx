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
import { useRouter, useLocalSearchParams } from 'expo-router';
import { useLanguage } from '../contexts/LanguageContext';
import { Species, SimulationResult, speciesApi, simulationApi } from '../services/api';
import { Ionicons } from '@expo/vector-icons';
import Slider from '@react-native-community/slider';

export default function SimulatorScreen() {
  const router = useRouter();
  const { id } = useLocalSearchParams();
  const { language, t } = useLanguage();
  
  const [species, setSpecies] = useState<Species | null>(null);
  const [temperature, setTemperature] = useState(25);
  const [waterAvailability, setWaterAvailability] = useState(70);
  const [foodAvailability, setFoodAvailability] = useState(70);
  const [simulationResult, setSimulationResult] = useState<SimulationResult | null>(null);
  const [explanation, setExplanation] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [simulating, setSimulating] = useState(false);
  const [loadingExplanation, setLoadingExplanation] = useState(false);

  useEffect(() => {
    loadSpecies();
  }, [id]);

  const loadSpecies = async () => {
    try {
      setLoading(true);
      const data = await speciesApi.getById(id as string);
      setSpecies(data);
      setTemperature((data.optimal_temp_min + data.optimal_temp_max) / 2);
    } catch (error) {
      console.error('Error loading species:', error);
    } finally {
      setLoading(false);
    }
  };

  const runSimulation = async () => {
    if (!species) return;
    
    try {
      setSimulating(true);
      setExplanation('');
      const result = await simulationApi.simulate(
        species.id!,
        temperature,
        waterAvailability,
        foodAvailability,
        language
      );
      setSimulationResult(result);
    } catch (error) {
      console.error('Error running simulation:', error);
    } finally {
      setSimulating(false);
    }
  };

  const getAIExplanation = async () => {
    if (!species || !simulationResult) return;
    
    try {
      setLoadingExplanation(true);
      const speciesName = language === 'pt' ? species.name_pt : species.name_en;
      const exp = await simulationApi.getExplanation(speciesName, simulationResult, language);
      setExplanation(exp);
    } catch (error) {
      console.error('Error getting explanation:', error);
    } finally {
      setLoadingExplanation(false);
    }
  };

  const getStatusColor = (status: string) => {
    if (status === 'adequate' || status === 'stable') return '#4CAF50';
    if (status === 'insufficient' || status === 'stressed') return '#FF9800';
    return '#F44336';
  };

  const translateStatus = (status: string) => {
    return t(status) || status;
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#4CAF50" />
        <Text style={styles.loadingText}>{t('loading')}</Text>
      </View>
    );
  }

  if (!species) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>{t('error')}</Text>
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
        <Text style={styles.headerTitle}>{t('simulator')}</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView style={styles.content}>
        <View style={styles.speciesHeader}>
          <Image source={{ uri: species.image_url }} style={styles.headerImage} resizeMode="cover" />
          <View style={styles.speciesHeaderInfo}>
            <Text style={styles.speciesName}>
              {language === 'pt' ? species.name_pt : species.name_en}
            </Text>
            <Text style={styles.scientificName}>{species.scientific_name}</Text>
            <View style={styles.thermoInfo}>
              <Ionicons name="thermometer-outline" size={16} color="#4CAF50" />
              <Text style={styles.thermoText}>
                {t('thermoregulation')}: {t(species.thermoregulation)}
              </Text>
            </View>
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{t('environmentalParameters')}</Text>
          
          <View style={styles.parameter}>
            <View style={styles.parameterHeader}>
              <Ionicons name="thermometer" size={24} color="#FF5722" />
              <Text style={styles.parameterLabel}>{t('temperature')}</Text>
              <Text style={styles.parameterValue}>{temperature.toFixed(1)}°C</Text>
            </View>
            <Slider
              style={styles.slider}
              minimumValue={-10}
              maximumValue={45}
              value={temperature}
              onValueChange={setTemperature}
              minimumTrackTintColor="#FF5722"
              maximumTrackTintColor="#444"
              thumbTintColor="#FF5722"
            />
            <View style={styles.sliderLabels}>
              <Text style={styles.sliderLabel}>-10°C</Text>
              <Text style={styles.sliderLabel}>45°C</Text>
            </View>
          </View>

          <View style={styles.parameter}>
            <View style={styles.parameterHeader}>
              <Ionicons name="water" size={24} color="#2196F3" />
              <Text style={styles.parameterLabel}>{t('waterAvailability')}</Text>
              <Text style={styles.parameterValue}>{waterAvailability.toFixed(0)}%</Text>
            </View>
            <Slider
              style={styles.slider}
              minimumValue={0}
              maximumValue={100}
              value={waterAvailability}
              onValueChange={setWaterAvailability}
              minimumTrackTintColor="#2196F3"
              maximumTrackTintColor="#444"
              thumbTintColor="#2196F3"
            />
            <View style={styles.sliderLabels}>
              <Text style={styles.sliderLabel}>0%</Text>
              <Text style={styles.sliderLabel}>100%</Text>
            </View>
          </View>

          <View style={styles.parameter}>
            <View style={styles.parameterHeader}>
              <Ionicons name="restaurant" size={24} color="#8BC34A" />
              <Text style={styles.parameterLabel}>{t('foodAvailability')}</Text>
              <Text style={styles.parameterValue}>{foodAvailability.toFixed(0)}%</Text>
            </View>
            <Slider
              style={styles.slider}
              minimumValue={0}
              maximumValue={100}
              value={foodAvailability}
              onValueChange={setFoodAvailability}
              minimumTrackTintColor="#8BC34A"
              maximumTrackTintColor="#444"
              thumbTintColor="#8BC34A"
            />
            <View style={styles.sliderLabels}>
              <Text style={styles.sliderLabel}>0%</Text>
              <Text style={styles.sliderLabel}>100%</Text>
            </View>
          </View>

          <TouchableOpacity
            style={styles.simulateButton}
            onPress={runSimulation}
            disabled={simulating}
          >
            {simulating ? (
              <ActivityIndicator color="white" />
            ) : (
              <>
                <Ionicons name="play-circle" size={24} color="white" />
                <Text style={styles.simulateButtonText}>{t('simulate')}</Text>
              </>
            )}
          </TouchableOpacity>
        </View>

        {simulationResult && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>{t('physiologicalResponse')}</Text>
            
            <View style={styles.resultsGrid}>
              <View style={styles.resultCard}>
                <Ionicons name="speedometer" size={32} color="#9C27B0" />
                <Text style={styles.resultLabel}>{t('metabolicRate')}</Text>
                <Text style={styles.resultValue}>{simulationResult.metabolic_rate}x</Text>
              </View>

              <View style={styles.resultCard}>
                <Ionicons name="thermometer" size={32} color="#FF5722" />
                <Text style={styles.resultLabel}>{t('bodyTemperature')}</Text>
                <Text style={styles.resultValue}>{simulationResult.body_temperature}°C</Text>
              </View>

              <View style={styles.resultCard}>
                <Ionicons name="heart" size={32} color="#F44336" />
                <Text style={styles.resultLabel}>{t('survivalProbability')}</Text>
                <Text style={[styles.resultValue, { color: getStatusColor(simulationResult.homeostasis_status) }]}>
                  {simulationResult.survival_probability}%
                </Text>
              </View>

              <View style={styles.resultCard}>
                <Ionicons name="flash" size={32} color="#FFC107" />
                <Text style={styles.resultLabel}>{t('energyExpenditure')}</Text>
                <Text style={styles.resultValue}>{simulationResult.energy_expenditure}x</Text>
              </View>
            </View>

            <View style={styles.statusSection}>
              <View style={styles.statusRow}>
                <Text style={styles.statusLabel}>{t('waterStatus')}:</Text>
                <View style={[styles.statusBadge, { backgroundColor: getStatusColor(simulationResult.water_status) }]}>
                  <Text style={styles.statusText}>{translateStatus(simulationResult.water_status)}</Text>
                </View>
              </View>

              <View style={styles.statusRow}>
                <Text style={styles.statusLabel}>{t('foodStatus')}:</Text>
                <View style={[styles.statusBadge, { backgroundColor: getStatusColor(simulationResult.food_status) }]}>
                  <Text style={styles.statusText}>{translateStatus(simulationResult.food_status)}</Text>
                </View>
              </View>

              <View style={styles.statusRow}>
                <Text style={styles.statusLabel}>{t('homeostasisStatus')}:</Text>
                <View style={[styles.statusBadge, { backgroundColor: getStatusColor(simulationResult.homeostasis_status) }]}>
                  <Text style={styles.statusText}>{translateStatus(simulationResult.homeostasis_status)}</Text>
                </View>
              </View>

              <View style={styles.statusRow}>
                <Text style={styles.statusLabel}>{t('stressLevel')}:</Text>
                <Text style={[styles.statusValue, { color: getStatusColor(simulationResult.homeostasis_status) }]}>
                  {simulationResult.stress_level}%
                </Text>
              </View>
            </View>

            <TouchableOpacity
              style={styles.explanationButton}
              onPress={getAIExplanation}
              disabled={loadingExplanation}
            >
              {loadingExplanation ? (
                <ActivityIndicator color="white" />
              ) : (
                <>
                  <Ionicons name="bulb" size={24} color="white" />
                  <Text style={styles.explanationButtonText}>{t('getExplanation')}</Text>
                </>
              )}
            </TouchableOpacity>

            {explanation && (
              <View style={styles.explanationCard}>
                <View style={styles.explanationHeader}>
                  <Ionicons name="sparkles" size={24} color="#4CAF50" />
                  <Text style={styles.explanationTitle}>{t('aiExplanation')}</Text>
                </View>
                <Text style={styles.explanationText}>{explanation}</Text>
              </View>
            )}
          </View>
        )}
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
  content: {
    flex: 1,
  },
  speciesHeader: {
    flexDirection: 'row',
    backgroundColor: '#2a2a2a',
    margin: 16,
    borderRadius: 12,
    overflow: 'hidden',
  },
  headerImage: {
    width: 120,
    height: 120,
  },
  speciesHeaderInfo: {
    flex: 1,
    padding: 16,
    justifyContent: 'center',
  },
  speciesName: {
    fontSize: 20,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 4,
  },
  scientificName: {
    fontSize: 14,
    fontStyle: 'italic',
    color: '#888',
    marginBottom: 8,
  },
  thermoInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  thermoText: {
    color: '#4CAF50',
    fontSize: 13,
    marginLeft: 6,
  },
  section: {
    margin: 16,
    backgroundColor: '#2a2a2a',
    borderRadius: 12,
    padding: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 16,
  },
  parameter: {
    marginBottom: 24,
  },
  parameterHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  parameterLabel: {
    flex: 1,
    fontSize: 15,
    color: 'white',
    marginLeft: 8,
  },
  parameterValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#4CAF50',
  },
  slider: {
    width: '100%',
    height: 40,
  },
  sliderLabels: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  sliderLabel: {
    color: '#888',
    fontSize: 12,
  },
  simulateButton: {
    backgroundColor: '#4CAF50',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    borderRadius: 8,
    marginTop: 8,
  },
  simulateButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  resultsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  resultCard: {
    width: '48%',
    backgroundColor: '#1a1a1a',
    borderRadius: 8,
    padding: 12,
    alignItems: 'center',
    marginBottom: 12,
  },
  resultLabel: {
    color: '#888',
    fontSize: 12,
    marginTop: 8,
    textAlign: 'center',
  },
  resultValue: {
    color: 'white',
    fontSize: 20,
    fontWeight: 'bold',
    marginTop: 4,
  },
  statusSection: {
    marginBottom: 16,
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  statusLabel: {
    color: 'white',
    fontSize: 14,
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  statusText: {
    color: 'white',
    fontSize: 13,
    fontWeight: '600',
  },
  statusValue: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  explanationButton: {
    backgroundColor: '#9C27B0',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    borderRadius: 8,
  },
  explanationButtonText: {
    color: 'white',
    fontSize: 15,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  explanationCard: {
    backgroundColor: '#1a1a1a',
    borderRadius: 8,
    padding: 16,
    marginTop: 16,
  },
  explanationHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  explanationTitle: {
    color: '#4CAF50',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  explanationText: {
    color: '#ccc',
    fontSize: 14,
    lineHeight: 22,
  },
});
