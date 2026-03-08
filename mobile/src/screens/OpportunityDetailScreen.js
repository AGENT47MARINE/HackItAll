import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Linking, Alert } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { aiAPI, trackingAPI } from '../services/apiService';
import api from '../services/apiService';

export default function OpportunityDetailScreen({ route, navigation }) {
  const { id } = route.params;
  const [opportunity, setOpportunity] = useState(null);
  const [fitAnalysis, setFitAnalysis] = useState(null);
  const [projectIdeas, setProjectIdeas] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [generatingIdeas, setGeneratingIdeas] = useState(false);
  const [saving, setSaving] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    checkAuth();
    loadOpportunity();
  }, [id]);

  const checkAuth = async () => {
    const token = await AsyncStorage.getItem('authToken');
    setIsAuthenticated(!!token);
  };

  const loadOpportunity = async () => {
    try {
      const response = await api.get(`/opportunities/${id}`);
      setOpportunity(response.data);
      
      // Load AI features if authenticated
      const token = await AsyncStorage.getItem('authToken');
      if (token) {
        loadFitAnalysis();
        loadProjectIdeas();
      }
    } catch (error) {
      // Silent fallback with mock data
      console.error('Error loading opportunity:', error);
      // Create mock opportunity data
      setOpportunity({
        id: id,
        title: 'Opportunity Details',
        organization: 'Organization Name',
        type: 'hackathon',
        description: 'This opportunity is currently unavailable. Please check back later or connect to the backend to see full details.',
        deadline: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
        url: null,
        track_count: 0,
      });
    } finally {
      setLoading(false);
    }
  };

  const loadFitAnalysis = async () => {
    setAnalyzing(true);
    try {
      const data = await aiAPI.analyzeFit(id);
      setFitAnalysis(data);
    } catch (error) {
      // Silent fail - AI features are optional
      setFitAnalysis(null);
    } finally {
      setAnalyzing(false);
    }
  };

  const loadProjectIdeas = async () => {
    setGeneratingIdeas(true);
    try {
      const data = await aiAPI.getIdeas(id);
      setProjectIdeas(data.ideas);
    } catch (error) {
      // Silent fail - AI features are optional
      setProjectIdeas(null);
    } finally {
      setGeneratingIdeas(false);
    }
  };

  const handleSave = async () => {
    if (!isAuthenticated) {
      Alert.alert(
        'Login Required',
        'You need to create an account to save opportunities. Would you like to register now?',
        [
          { text: 'Cancel', style: 'cancel' },
          { text: 'Register', onPress: () => navigation.navigate('Register') }
        ]
      );
      return;
    }

    setSaving(true);
    try {
      await trackingAPI.saveOpportunity(id);
      Alert.alert('Success', 'Opportunity saved to your tracker!');
    } catch (error) {
      if (error.response?.status === 409) {
        Alert.alert('Already Saved', 'This opportunity is already in your tracker');
      } else {
        Alert.alert('Error', 'Failed to save opportunity');
      }
    } finally {
      setSaving(false);
    }
  };

  const handleApply = () => {
    if (opportunity?.application_link) {
      Linking.openURL(opportunity.application_link);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <View style={styles.loadingContainer}>
          <Text style={styles.loadingText}>Loading opportunity...</Text>
        </View>
      </View>
    );
  }

  if (!opportunity) {
    return (
      <View style={styles.container}>
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyIcon}>◇</Text>
          <Text style={styles.emptyTitle}>Opportunity not found</Text>
          <Text style={styles.emptyText}>
            This opportunity may have been removed or doesn't exist
          </Text>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <ScrollView style={styles.scrollView}>
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.headerTop}>
            <Text style={styles.title}>{opportunity.title}</Text>
            <View style={styles.typeBadge}>
              <Text style={styles.typeBadgeText}>
                {opportunity.type.replace('_', ' ').toUpperCase()}
              </Text>
            </View>
          </View>
          {opportunity.deadline && (
            <View style={styles.deadlineRow}>
              <Text style={styles.deadlineLabel}>Deadline:</Text>
              <Text style={styles.deadlineValue}>{formatDate(opportunity.deadline)}</Text>
            </View>
          )}
        </View>

        {/* Content */}
        <View style={styles.content}>
          {/* AI Fit Analysis */}
          {isAuthenticated && (analyzing || fitAnalysis) && (
            <View style={[
              styles.aiCard,
              fitAnalysis?.is_ready ? styles.aiCardReady : (fitAnalysis ? styles.aiCardNotReady : null)
            ]}>
              <Text style={styles.aiCardTitle}>🤖 AI Fit Analysis</Text>
              {analyzing ? (
                <Text style={styles.analyzingText}>Analyzing your profile against this opportunity...</Text>
              ) : (
                <>
                  <Text style={styles.aiRecommendationText}>{fitAnalysis.recommendation_text}</Text>

                  {fitAnalysis.matching_skills?.length > 0 && (
                    <View style={styles.fitSkillsGroup}>
                      <Text style={styles.fitSkillsTitle}>✅ Matching Skills</Text>
                      <View style={styles.tagsContainer}>
                        {fitAnalysis.matching_skills.map((skill, index) => (
                          <View key={index} style={[styles.tag, styles.tagSuccess]}>
                            <Text style={styles.tagText}>{skill}</Text>
                          </View>
                        ))}
                      </View>
                    </View>
                  )}

                  {fitAnalysis.missing_skills?.length > 0 && (
                    <View style={styles.fitSkillsGroup}>
                      <Text style={styles.fitSkillsTitle}>⚠️ Missing Skills</Text>
                      <View style={styles.tagsContainer}>
                        {fitAnalysis.missing_skills.map((skill, index) => (
                          <View key={index} style={[styles.tag, styles.tagWarning]}>
                            <Text style={styles.tagText}>{skill}</Text>
                          </View>
                        ))}
                      </View>
                    </View>
                  )}
                </>
              )}
            </View>
          )}

          {/* AI Project Ideas */}
          {isAuthenticated && (generatingIdeas || projectIdeas) && (
            <View style={styles.aiCard}>
              <Text style={styles.aiCardTitle}>💡 Auto-Generated Project Ideas</Text>
              {generatingIdeas ? (
                <Text style={styles.analyzingText}>Brainstorming potential projects based on your skills...</Text>
              ) : (
                <View style={styles.ideasList}>
                  {projectIdeas?.map((idea, index) => (
                    <View key={index} style={styles.ideaItem}>
                      <Text style={styles.ideaTitle}>{idea.title}</Text>
                      <Text style={styles.ideaDesc}>{idea.description}</Text>
                    </View>
                  ))}
                </View>
              )}
            </View>
          )}

          {/* Description */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Description</Text>
            <Text style={styles.sectionText}>{opportunity.description}</Text>
          </View>

          {/* Organization */}
          {opportunity.organization && (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Organization</Text>
              <Text style={styles.sectionText}>{opportunity.organization}</Text>
            </View>
          )}

          {/* Required Skills */}
          {opportunity.required_skills && opportunity.required_skills.length > 0 && (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Required Skills</Text>
              <View style={styles.tagsContainer}>
                {opportunity.required_skills.map((skill, index) => (
                  <View key={index} style={styles.tag}>
                    <Text style={styles.tagText}>{skill}</Text>
                  </View>
                ))}
              </View>
            </View>
          )}

          {/* Tags */}
          {opportunity.tags && opportunity.tags.length > 0 && (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Tags</Text>
              <View style={styles.tagsContainer}>
                {opportunity.tags.map((tag, index) => (
                  <View key={index} style={[styles.tag, styles.tagSecondary]}>
                    <Text style={styles.tagText}>{tag}</Text>
                  </View>
                ))}
              </View>
            </View>
          )}

          {/* Eligibility */}
          {opportunity.eligibility && (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Eligibility</Text>
              <Text style={styles.sectionText}>{opportunity.eligibility}</Text>
            </View>
          )}

          {/* Location */}
          {opportunity.location && (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Location</Text>
              <Text style={styles.sectionText}>{opportunity.location}</Text>
            </View>
          )}
        </View>
      </ScrollView>

      {/* Actions */}
      <View style={styles.actions}>
        <TouchableOpacity
          style={styles.saveButton}
          onPress={handleSave}
          disabled={saving}
        >
          <Text style={styles.saveButtonText}>
            {saving ? 'Saving...' : '📌 Save to Tracker'}
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.applyButton}
          onPress={handleApply}
        >
          <Text style={styles.applyButtonText}>Apply Now →</Text>
        </TouchableOpacity>
      </View>
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
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    color: 'rgba(255, 255, 255, 0.5)',
    fontSize: 16,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  emptyIcon: {
    fontSize: 48,
    marginBottom: 16,
    color: 'rgba(255, 255, 255, 0.3)',
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#ffffff',
    marginBottom: 8,
    textAlign: 'center',
  },
  emptyText: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.6)',
    textAlign: 'center',
    lineHeight: 20,
  },
  header: {
    padding: 24,
    backgroundColor: 'rgba(255, 255, 255, 0.03)',
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 255, 255, 0.06)',
  },
  headerTop: {
    marginBottom: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    color: '#ffffff',
    marginBottom: 12,
    lineHeight: 32,
  },
  typeBadge: {
    alignSelf: 'flex-start',
    backgroundColor: 'rgba(0, 240, 255, 0.1)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
  },
  typeBadgeText: {
    color: '#00f0ff',
    fontSize: 12,
    fontWeight: '600',
  },
  deadlineRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  deadlineLabel: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.6)',
    marginRight: 8,
  },
  deadlineValue: {
    fontSize: 14,
    color: '#00f0ff',
    fontWeight: '600',
  },
  content: {
    padding: 24,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#ffffff',
    marginBottom: 12,
  },
  sectionText: {
    fontSize: 15,
    color: 'rgba(255, 255, 255, 0.7)',
    lineHeight: 22,
  },
  tagsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  tag: {
    backgroundColor: 'rgba(0, 240, 255, 0.1)',
    borderWidth: 1,
    borderColor: 'rgba(0, 240, 255, 0.3)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
  },
  tagSecondary: {
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  tagText: {
    color: '#00f0ff',
    fontSize: 13,
    fontWeight: '500',
  },
  actions: {
    flexDirection: 'row',
    padding: 16,
    gap: 12,
    backgroundColor: 'rgba(255, 255, 255, 0.03)',
    borderTopWidth: 1,
    borderTopColor: 'rgba(255, 255, 255, 0.06)',
  },
  saveButton: {
    flex: 1,
    backgroundColor: 'rgba(0, 240, 255, 0.1)',
    borderWidth: 1,
    borderColor: '#00f0ff',
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
  },
  saveButtonText: {
    color: '#00f0ff',
    fontSize: 15,
    fontWeight: '600',
  },
  applyButton: {
    flex: 1,
    backgroundColor: '#00f0ff',
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
  },
  applyButtonText: {
    color: '#050508',
    fontSize: 15,
    fontWeight: '600',
  },
  aiCard: {
    backgroundColor: 'rgba(123, 97, 255, 0.05)',
    borderWidth: 1,
    borderColor: 'rgba(123, 97, 255, 0.2)',
    borderRadius: 16,
    padding: 20,
    marginBottom: 24,
  },
  aiCardReady: {
    borderColor: 'rgba(0, 255, 136, 0.3)',
    backgroundColor: 'rgba(0, 255, 136, 0.05)',
  },
  aiCardNotReady: {
    borderColor: 'rgba(255, 200, 0, 0.3)',
    backgroundColor: 'rgba(255, 200, 0, 0.05)',
  },
  aiCardTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#ffffff',
    marginBottom: 12,
  },
  analyzingText: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.6)',
    fontStyle: 'italic',
  },
  aiRecommendationText: {
    fontSize: 15,
    color: 'rgba(255, 255, 255, 0.8)',
    lineHeight: 22,
    marginBottom: 16,
  },
  fitSkillsGroup: {
    marginTop: 16,
  },
  fitSkillsTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#ffffff',
    marginBottom: 8,
  },
  tagSuccess: {
    backgroundColor: 'rgba(0, 255, 136, 0.1)',
    borderColor: 'rgba(0, 255, 136, 0.3)',
  },
  tagWarning: {
    backgroundColor: 'rgba(255, 200, 0, 0.1)',
    borderColor: 'rgba(255, 200, 0, 0.3)',
  },
  ideasList: {
    gap: 16,
  },
  ideaItem: {
    backgroundColor: 'rgba(255, 255, 255, 0.03)',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.06)',
  },
  ideaTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
    marginBottom: 8,
  },
  ideaDesc: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.7)',
    lineHeight: 20,
  },
});
