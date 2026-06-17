import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  StatusBar,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { useLanguage } from '../contexts/LanguageContext';
import { Ionicons } from '@expo/vector-icons';

export default function HomeScreen() {
  const router = useRouter();
  const { language, setLanguage, t } = useLanguage();

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" />
      
      <View style={styles.header}>
        <View style={styles.languageToggle}>
          <TouchableOpacity
            style={[styles.langButton, language === 'pt' && styles.langButtonActive]}
            onPress={() => setLanguage('pt')}
          >
            <Text style={[styles.langText, language === 'pt' && styles.langTextActive]}>PT</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.langButton, language === 'en' && styles.langButtonActive]}
            onPress={() => setLanguage('en')}
          >
            <Text style={[styles.langText, language === 'en' && styles.langTextActive]}>EN</Text>
          </TouchableOpacity>
        </View>
      </View>

      <View style={styles.content}>
        <View style={styles.logoContainer}>
          <Ionicons name="leaf" size={80} color="#4CAF50" />
          <Text style={styles.title}>{t('appTitle')}</Text>
          <Text style={styles.subtitle}>{t('appSubtitle')}</Text>
        </View>

        <View style={styles.description}>
          <Text style={styles.descriptionText}>
            {language === 'pt'
              ? 'Explore a fisiologia ecológica através de simulações interativas. Descubra como diferentes espécies dos biomas brasileiros respondem às mudanças ambientais.'
              : 'Explore ecological physiology through interactive simulations. Discover how different species from Brazilian biomes respond to environmental changes.'}
          </Text>
        </View>

        <TouchableOpacity
          style={styles.startButton}
          onPress={() => router.push('/species')}
        >
          <Ionicons name="play" size={24} color="white" style={styles.buttonIcon} />
          <Text style={styles.startButtonText}>{t('selectSpecies')}</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.mapButton}
          onPress={() => router.push('/map')}
        >
          <Ionicons name="map" size={22} color="#4CAF50" style={styles.buttonIcon} />
          <Text style={styles.mapButtonText}>{t('habitatMap')}</Text>
        </TouchableOpacity>

        <View style={styles.features}>
          <View style={styles.feature}>
            <Ionicons name="thermometer" size={32} color="#FF9800" />
            <Text style={styles.featureText}>
              {language === 'pt' ? 'Controle Temperatura' : 'Control Temperature'}
            </Text>
          </View>
          <View style={styles.feature}>
            <Ionicons name="water" size={32} color="#2196F3" />
            <Text style={styles.featureText}>
              {language === 'pt' ? 'Água e Alimento' : 'Water & Food'}
            </Text>
          </View>
          <View style={styles.feature}>
            <Ionicons name="analytics" size={32} color="#9C27B0" />
            <Text style={styles.featureText}>
              {language === 'pt' ? 'Análise em Tempo Real' : 'Real-time Analysis'}
            </Text>
          </View>
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a1a',
  },
  header: {
    padding: 16,
    alignItems: 'flex-end',
  },
  languageToggle: {
    flexDirection: 'row',
    backgroundColor: '#2a2a2a',
    borderRadius: 8,
    padding: 4,
  },
  langButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 6,
  },
  langButtonActive: {
    backgroundColor: '#4CAF50',
  },
  langText: {
    color: '#888',
    fontSize: 14,
    fontWeight: '600',
  },
  langTextActive: {
    color: 'white',
  },
  content: {
    flex: 1,
    paddingHorizontal: 24,
    justifyContent: 'space-around',
  },
  logoContainer: {
    alignItems: 'center',
    marginTop: 20,
  },
  title: {
    fontSize: 42,
    fontWeight: 'bold',
    color: 'white',
    marginTop: 16,
  },
  subtitle: {
    fontSize: 18,
    color: '#4CAF50',
    marginTop: 8,
  },
  description: {
    backgroundColor: '#2a2a2a',
    padding: 20,
    borderRadius: 12,
    marginVertical: 24,
  },
  descriptionText: {
    color: '#ccc',
    fontSize: 16,
    lineHeight: 24,
    textAlign: 'center',
  },
  startButton: {
    backgroundColor: '#4CAF50',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 18,
    borderRadius: 12,
    marginTop: 16,
  },
  mapButton: {
    backgroundColor: '#2a2a2a',
    borderWidth: 1,
    borderColor: '#4CAF50',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    borderRadius: 12,
    marginTop: 12,
    marginBottom: 16,
  },
  mapButtonText: {
    color: '#4CAF50',
    fontSize: 16,
    fontWeight: 'bold',
  },
  buttonIcon: {
    marginRight: 8,
  },
  startButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  features: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginTop: 24,
  },
  feature: {
    alignItems: 'center',
    flex: 1,
  },
  featureText: {
    color: '#888',
    fontSize: 12,
    marginTop: 8,
    textAlign: 'center',
  },
});
