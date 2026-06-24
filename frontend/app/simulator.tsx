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
  TextInput,
  Switch,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { useLanguage } from '../contexts/LanguageContext';
import {
  Species,
  SimulationResult,
  ChatMessage,
  speciesApi,
  simulationApi,
  chatApi,
} from '../services/api';
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

  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);

  // Modo científico (controles avançados)
  const [scientificMode, setScientificMode] = useState(false);
  const [foodKcal, setFoodKcal] = useState(2000);
  const [predator, setPredator] = useState(false);
  const [o2Inspired, setO2Inspired] = useState(20.9);
  const [o2Expired, setO2Expired] = useState(16);

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
        language,
        scientificMode ? { foodKcal, predator, o2Inspired, o2Expired } : undefined
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

  const sendChat = async (text: string) => {
    const message = text.trim();
    if (!message || chatLoading) return;

    const speciesName = species ? (language === 'pt' ? species.name_pt : species.name_en) : null;
    const history: ChatMessage[] = [...chatMessages, { role: 'user', text: message }];
    setChatMessages(history);
    setChatInput('');
    try {
      setChatLoading(true);
      const reply = await chatApi.send(history, speciesName, language);
      setChatMessages([...history, { role: 'assistant', text: reply }]);
    } catch (error) {
      console.error('Error in chat:', error);
      setChatMessages([
        ...history,
        { role: 'assistant', text: language === 'pt' ? 'Erro ao responder. Tente novamente.' : 'Failed to reply. Try again.' },
      ]);
    } finally {
      setChatLoading(false);
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

          <View style={styles.sciRow}>
            <Ionicons name="flask" size={20} color={scientificMode ? '#9C27B0' : '#888'} />
            <Text style={styles.sciLabel}>{t('scientificMode')}</Text>
            <Switch
              value={scientificMode}
              onValueChange={setScientificMode}
              trackColor={{ false: '#444', true: '#9C27B0' }}
              thumbColor="#fff"
            />
          </View>

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

          {scientificMode && (
            <>
              <View style={styles.parameter}>
                <View style={styles.parameterHeader}>
                  <Ionicons name="nutrition" size={24} color="#FFC107" />
                  <Text style={styles.parameterLabel}>{t('foodKcal')}</Text>
                  <Text style={styles.parameterValue}>{foodKcal.toFixed(0)}</Text>
                </View>
                <Slider style={styles.slider} minimumValue={0} maximumValue={5000}
                  value={foodKcal} onValueChange={setFoodKcal}
                  minimumTrackTintColor="#FFC107" maximumTrackTintColor="#444" thumbTintColor="#FFC107" />
                <View style={styles.sliderLabels}>
                  <Text style={styles.sliderLabel}>0</Text>
                  <Text style={styles.sliderLabel}>5000</Text>
                </View>
              </View>

              <View style={styles.parameter}>
                <View style={styles.parameterHeader}>
                  <Ionicons name="cloud-outline" size={24} color="#03A9F4" />
                  <Text style={styles.parameterLabel}>{t('o2Inspired')}</Text>
                  <Text style={styles.parameterValue}>{o2Inspired.toFixed(1)}%</Text>
                </View>
                <Slider style={styles.slider} minimumValue={19} maximumValue={21}
                  value={o2Inspired} onValueChange={setO2Inspired}
                  minimumTrackTintColor="#03A9F4" maximumTrackTintColor="#444" thumbTintColor="#03A9F4" />
                <View style={styles.sliderLabels}>
                  <Text style={styles.sliderLabel}>19%</Text>
                  <Text style={styles.sliderLabel}>21%</Text>
                </View>
              </View>

              <View style={styles.parameter}>
                <View style={styles.parameterHeader}>
                  <Ionicons name="cloud" size={24} color="#607D8B" />
                  <Text style={styles.parameterLabel}>{t('o2Expired')}</Text>
                  <Text style={styles.parameterValue}>{o2Expired.toFixed(1)}%</Text>
                </View>
                <Slider style={styles.slider} minimumValue={12} maximumValue={21}
                  value={o2Expired} onValueChange={setO2Expired}
                  minimumTrackTintColor="#607D8B" maximumTrackTintColor="#444" thumbTintColor="#607D8B" />
                <View style={styles.sliderLabels}>
                  <Text style={styles.sliderLabel}>12%</Text>
                  <Text style={styles.sliderLabel}>21%</Text>
                </View>
              </View>

              <View style={styles.sciRow}>
                <Ionicons name="warning" size={20} color={predator ? '#F44336' : '#888'} />
                <Text style={styles.sciLabel}>{t('predatorPresent')}</Text>
                <Switch value={predator} onValueChange={setPredator}
                  trackColor={{ false: '#444', true: '#F44336' }} thumbColor="#fff" />
              </View>
            </>
          )}

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

            {scientificMode && simulationResult.basal_metabolic_rate_kcal != null && (
              <View style={styles.sciPanel}>
                <Text style={styles.sciPanelTitle}>{t('scientificResults')}</Text>

                {[
                  [t('bmr'), `${simulationResult.basal_metabolic_rate_kcal} kcal/dia`, undefined],
                  [t('totalExpenditure'), `${simulationResult.total_expenditure_kcal} kcal/dia`, undefined],
                  [
                    t('energyBalance'),
                    `${simulationResult.energy_balance_kcal >= 0 ? '+' : ''}${simulationResult.energy_balance_kcal} kcal`,
                    simulationResult.energy_balance_kcal >= 0 ? '#4CAF50' : '#F44336',
                  ],
                  [t('vo2'), `${simulationResult.vo2_ml_g_h} mL/g/h`, undefined],
                  [t('energyFromO2'), `${simulationResult.energy_from_o2_kcal} kcal/dia`, undefined],
                  [t('thermoCost'), `${simulationResult.thermoregulation_cost_kcal} kcal/dia`, undefined],
                ].map(([label, value, color], i) => (
                  <View key={i} style={styles.sciMetric}>
                    <Text style={styles.sciMetricLabel}>{label}</Text>
                    <Text style={[styles.sciMetricValue, color ? { color: color as string } : null]}>{value}</Text>
                  </View>
                ))}

                <Text style={styles.sciBreakTitle}>{t('stressBreakdown')}</Text>
                {([['stTermico', 'termico'], ['stAgua', 'agua'], ['stEnergia', 'energia'], ['stPredador', 'predador']] as const).map(
                  ([labelKey, key]) => {
                    const pct = simulationResult.stress_breakdown?.[key] ?? 0;
                    return (
                      <View key={key} style={styles.breakRow}>
                        <Text style={styles.breakLabel}>{t(labelKey)}</Text>
                        <View style={styles.breakBarBg}>
                          <View style={[styles.breakBarFill, { width: `${Math.min(pct, 100)}%` }]} />
                        </View>
                        <Text style={styles.breakPct}>{pct.toFixed(0)}%</Text>
                      </View>
                    );
                  }
                )}
              </View>
            )}

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

            <View style={styles.chatSection}>
              <View style={styles.explanationHeader}>
                <Ionicons name="chatbubbles" size={22} color="#4CAF50" />
                <Text style={styles.explanationTitle}>{t('chatTitle')}</Text>
              </View>
              <Text style={styles.chatIntro}>{t('chatIntro')}</Text>

              {chatMessages.map((m, i) => (
                <View
                  key={i}
                  style={[styles.bubbleWrap, m.role === 'user' ? styles.bubbleWrapUser : styles.bubbleWrapAi]}
                >
                  {m.role === 'assistant' && <Text style={styles.bubbleAuthor}>{t('professor')}</Text>}
                  <View style={[styles.bubble, m.role === 'user' ? styles.bubbleUser : styles.bubbleAi]}>
                    <Text style={m.role === 'user' ? styles.bubbleTextUser : styles.bubbleTextAi}>
                      {m.text}
                    </Text>
                  </View>
                </View>
              ))}

              {chatLoading && (
                <ActivityIndicator color="#4CAF50" style={{ marginVertical: 10, alignSelf: 'flex-start' }} />
              )}

              <View style={styles.suggestions}>
                {[t('suggestBooks'), t('suggestWhy'), t('suggestExample'), t('suggestCuriosity')].map((s) => (
                  <TouchableOpacity
                    key={s}
                    style={styles.chip}
                    onPress={() => sendChat(s)}
                    disabled={chatLoading}
                  >
                    <Text style={styles.chipText}>{s}</Text>
                  </TouchableOpacity>
                ))}
              </View>

              <View style={styles.chatInputRow}>
                <TextInput
                  style={styles.chatInput}
                  value={chatInput}
                  onChangeText={setChatInput}
                  placeholder={t('chatPlaceholder')}
                  placeholderTextColor="#888"
                  onSubmitEditing={() => sendChat(chatInput)}
                  editable={!chatLoading}
                  multiline
                />
                <TouchableOpacity
                  style={styles.chatSend}
                  onPress={() => sendChat(chatInput)}
                  disabled={chatLoading}
                >
                  <Ionicons name="send" size={20} color="white" />
                </TouchableOpacity>
              </View>
            </View>
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
  chatSection: {
    backgroundColor: '#1a1a1a',
    borderRadius: 8,
    padding: 16,
    marginTop: 16,
  },
  chatIntro: {
    color: '#888',
    fontSize: 13,
    marginBottom: 12,
  },
  bubbleWrap: {
    marginBottom: 10,
    maxWidth: '88%',
  },
  bubbleWrapUser: {
    alignSelf: 'flex-end',
    alignItems: 'flex-end',
  },
  bubbleWrapAi: {
    alignSelf: 'flex-start',
    alignItems: 'flex-start',
  },
  bubbleAuthor: {
    color: '#4CAF50',
    fontSize: 11,
    fontWeight: '700',
    marginBottom: 2,
    marginLeft: 4,
  },
  bubble: {
    paddingHorizontal: 12,
    paddingVertical: 9,
    borderRadius: 14,
  },
  bubbleUser: {
    backgroundColor: '#4CAF50',
    borderBottomRightRadius: 4,
  },
  bubbleAi: {
    backgroundColor: '#2a2a2a',
    borderBottomLeftRadius: 4,
  },
  bubbleTextUser: {
    color: 'white',
    fontSize: 14,
    lineHeight: 20,
  },
  bubbleTextAi: {
    color: '#eee',
    fontSize: 14,
    lineHeight: 20,
  },
  suggestions: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 6,
    marginBottom: 12,
  },
  chip: {
    backgroundColor: '#2a2a2a',
    borderWidth: 1,
    borderColor: '#3a3a3a',
    borderRadius: 16,
    paddingHorizontal: 12,
    paddingVertical: 8,
    marginRight: 8,
    marginBottom: 8,
  },
  chipText: {
    color: '#9CCC65',
    fontSize: 12,
  },
  chatInputRow: {
    flexDirection: 'row',
    alignItems: 'flex-end',
  },
  chatInput: {
    flex: 1,
    backgroundColor: '#2a2a2a',
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 10,
    color: 'white',
    fontSize: 14,
    maxHeight: 120,
    marginRight: 8,
  },
  chatSend: {
    backgroundColor: '#4CAF50',
    width: 44,
    height: 44,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
  },
  sciRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1a1a1a',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 8,
    marginBottom: 16,
  },
  sciLabel: {
    flex: 1,
    color: 'white',
    fontSize: 14,
    marginLeft: 8,
  },
  sciPanel: {
    backgroundColor: '#1a1a1a',
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#9C27B0',
  },
  sciPanelTitle: {
    color: '#CE93D8',
    fontSize: 15,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  sciMetric: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 6,
    borderBottomWidth: 1,
    borderBottomColor: '#2a2a2a',
  },
  sciMetricLabel: {
    color: '#bbb',
    fontSize: 13,
    flex: 1,
  },
  sciMetricValue: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
    marginLeft: 8,
  },
  sciBreakTitle: {
    color: '#CE93D8',
    fontSize: 13,
    fontWeight: 'bold',
    marginTop: 14,
    marginBottom: 8,
  },
  breakRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  breakLabel: {
    color: '#bbb',
    fontSize: 12,
    width: 64,
  },
  breakBarBg: {
    flex: 1,
    height: 10,
    backgroundColor: '#2a2a2a',
    borderRadius: 5,
    marginHorizontal: 8,
    overflow: 'hidden',
  },
  breakBarFill: {
    height: 10,
    backgroundColor: '#9C27B0',
    borderRadius: 5,
  },
  breakPct: {
    color: '#bbb',
    fontSize: 12,
    width: 38,
    textAlign: 'right',
  },
});
