import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, TextInput, Alert } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import api from '../services/apiService';

const INTEREST_OPTIONS = [
  'Web Dev', 'App Dev', 'AI/ML', 'Data Science',
  'Cybersecurity', 'Cloud Computing', 'UI/UX Design',
  'Blockchain', 'Game Dev', 'DevOps'
];

const EDUCATION_OPTIONS = [
  'High School',
  'B.Tech 1st Year',
  'B.Tech 2nd Year',
  'B.Tech 3rd Year',
  'B.Tech 4th Year',
  'M.Tech',
  'Graduate/Alumni'
];

export default function OnboardingScreen({ navigation }) {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    phone: '',
    education_level: 'B.Tech 1st Year',
    interests: []
  });

  const handleInterestToggle = (interest) => {
    setFormData(prev => ({
      ...prev,
      interests: prev.interests.includes(interest)
        ? prev.interests.filter(i => i !== interest)
        : [...prev.interests, interest]
    }));
  };

  const handleSubmit = async () => {
    if (formData.interests.length === 0) {
      Alert.alert('Required', 'Please select at least one interest');
      return;
    }

    setLoading(true);
    try {
      const token = await AsyncStorage.getItem('authToken');
      await api.put('/profile', {
        phone: formData.phone || null,
        education_level: formData.education_level,
        interests: formData.interests,
        skills: []
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      // Mark onboarding as complete
      await AsyncStorage.setItem('onboardingComplete', 'true');
      
      // Navigate to main app
      navigation.replace('MainTabs');
    } catch (error) {
      console.error('Onboarding error:', error);
      Alert.alert('Error', 'Failed to save profile. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.logo}>HACKITALL</Text>
          <Text style={styles.title}>Complete Your Profile</Text>
          <Text style={styles.subtitle}>Let's customize your HackItAll experience</Text>
        </View>

        {/* Phone Number */}
        <View style={styles.section}>
          <Text style={styles.label}>📱 Phone Number (Optional)</Text>
          <TextInput
            style={styles.input}
            placeholder="e.g. +1 555-0123"
            placeholderTextColor="rgba(255, 255, 255, 0.3)"
            value={formData.phone}
            onChangeText={(text) => setFormData({ ...formData, phone: text })}
            keyboardType="phone-pad"
          />
        </View>

        {/* Education Level */}
        <View style={styles.section}>
          <Text style={styles.label}>🎓 Current Year of Study</Text>
          <View style={styles.educationGrid}>
            {EDUCATION_OPTIONS.map((option) => (
              <TouchableOpacity
                key={option}
                style={[
                  styles.educationOption,
                  formData.education_level === option && styles.educationOptionActive
                ]}
                onPress={() => setFormData({ ...formData, education_level: option })}
              >
                <Text style={[
                  styles.educationOptionText,
                  formData.education_level === option && styles.educationOptionTextActive
                ]}>
                  {option}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Interests */}
        <View style={styles.section}>
          <Text style={styles.label}>💡 Areas of Interest</Text>
          <Text style={styles.helperText}>
            Select the fields you want to discover opportunities for
          </Text>
          <View style={styles.interestsGrid}>
            {INTEREST_OPTIONS.map((interest) => (
              <TouchableOpacity
                key={interest}
                style={[
                  styles.interestTag,
                  formData.interests.includes(interest) && styles.interestTagActive
                ]}
                onPress={() => handleInterestToggle(interest)}
              >
                <Text style={[
                  styles.interestTagText,
                  formData.interests.includes(interest) && styles.interestTagTextActive
                ]}>
                  {interest}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Submit Button */}
        <TouchableOpacity
          style={[styles.submitButton, loading && styles.submitButtonDisabled]}
          onPress={handleSubmit}
          disabled={loading || formData.interests.length === 0}
        >
          <Text style={styles.submitButtonText}>
            {loading ? 'Saving...' : 'Start Exploring Opportunities'}
          </Text>
        </TouchableOpacity>

        {formData.interests.length === 0 && (
          <Text style={styles.errorText}>Please select at least one interest</Text>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#050508',
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: 24,
  },
  header: {
    alignItems: 'center',
    marginBottom: 32,
  },
  logo: {
    fontFamily: 'monospace',
    fontSize: 20,
    fontWeight: '800',
    color: '#00f0ff',
    letterSpacing: 3,
    marginBottom: 24,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: '#ffffff',
    marginBottom: 8,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.6)',
    textAlign: 'center',
  },
  section: {
    marginBottom: 32,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
    marginBottom: 12,
  },
  helperText: {
    fontSize: 13,
    color: 'rgba(255, 255, 255, 0.5)',
    marginBottom: 12,
  },
  input: {
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 14,
    fontSize: 15,
    color: '#ffffff',
  },
  educationGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  educationOption: {
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 8,
  },
  educationOptionActive: {
    backgroundColor: 'rgba(0, 240, 255, 0.1)',
    borderColor: '#00f0ff',
  },
  educationOptionText: {
    fontSize: 13,
    color: 'rgba(255, 255, 255, 0.7)',
    fontWeight: '500',
  },
  educationOptionTextActive: {
    color: '#00f0ff',
    fontWeight: '600',
  },
  interestsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  interestTag: {
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 20,
  },
  interestTagActive: {
    backgroundColor: 'rgba(0, 240, 255, 0.15)',
    borderColor: '#00f0ff',
  },
  interestTagText: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.7)',
    fontWeight: '500',
  },
  interestTagTextActive: {
    color: '#00f0ff',
    fontWeight: '600',
  },
  submitButton: {
    backgroundColor: '#00f0ff',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 8,
  },
  submitButtonDisabled: {
    opacity: 0.5,
  },
  submitButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#050508',
  },
  errorText: {
    fontSize: 12,
    color: '#ff6464',
    textAlign: 'center',
    marginTop: 12,
  },
});
