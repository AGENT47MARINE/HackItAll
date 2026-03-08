import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, RefreshControl, Alert, TextInput } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';
import { trackingAPI } from '../services/apiService';
import api from '../services/apiService';

const PHASES = ['Saved', 'Applied', 'Submitted', 'In Review', 'Result'];

const StatusTimeline = ({ status }) => {
  const statusMap = {
    saved: 0,
    applied: 1,
    submitted: 2,
    in_review: 3,
    accepted: 4,
    rejected: 4,
    completed: 4,
  };
  const activeIdx = statusMap[(status || 'saved').toLowerCase()] ?? 0;

  return (
    <View style={styles.timeline}>
      {PHASES.map((phase, i) => (
        <View key={i} style={styles.timelineStep}>
          <View style={[
            styles.timelineDot,
            i < activeIdx && styles.timelineDotCompleted,
            i === activeIdx && styles.timelineDotActive,
          ]} />
          {i < PHASES.length - 1 && (
            <View style={[
              styles.timelineLine,
              i < activeIdx && styles.timelineLineCompleted,
            ]} />
          )}
        </View>
      ))}
    </View>
  );
};

const getCountdown = (deadline) => {
  if (!deadline) return { text: '—', urgent: false };
  const now = new Date();
  const d = new Date(deadline);
  const diff = d - now;
  if (diff <= 0) return { text: 'Ended', urgent: false };
  const days = Math.floor(diff / 86400000);
  if (days > 14) return { text: `${days}d left`, urgent: false };
  if (days > 0) return { text: `${days}d left`, urgent: days <= 3 };
  const hrs = Math.floor(diff / 3600000);
  return { text: `${hrs}h left`, urgent: true };
};

export default function TrackedScreen({ navigation }) {
  const [tracked, setTracked] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [scrapeUrl, setScrapeUrl] = useState('');
  const [isScraping, setIsScraping] = useState(false);
  const [isGuest, setIsGuest] = useState(false);

  useEffect(() => {
    loadTracked();
  }, []);

  const loadTracked = async () => {
    try {
      const token = await AsyncStorage.getItem('authToken');
      if (!token) {
        setIsGuest(true);
        setLoading(false);
        setRefreshing(false);
        return;
      }
      
      const response = await api.get('/tracking/tracked', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setTracked(response.data);
      setIsGuest(false);
    } catch (error) {
      // Silent fallback for guest mode
      if (error.response?.status === 401 || error.response?.status === 403 || error.response?.status === 404) {
        setIsGuest(true);
        setTracked([]);
      } else {
        console.error('Error loading tracked:', error);
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadTracked();
  };

  const handleRemove = async (opportunityId) => {
    Alert.alert(
      'Remove Opportunity',
      'Remove this opportunity from your tracker?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Remove',
          style: 'destructive',
          onPress: async () => {
            try {
              const token = await AsyncStorage.getItem('authToken');
              await api.delete(`/tracking/tracked/${opportunityId}`, {
                headers: { Authorization: `Bearer ${token}` }
              });
              setTracked(prev => prev.filter(t => t.opportunity_id !== opportunityId));
            } catch (error) {
              Alert.alert('Error', 'Failed to remove opportunity');
            }
          }
        }
      ]
    );
  };

  const handleScrape = async () => {
    if (!scrapeUrl.trim()) return;
    setIsScraping(true);
    try {
      await trackingAPI.scrapeOpportunity(scrapeUrl);
      setScrapeUrl('');
      Alert.alert('Success', 'Opportunity added to tracker!');
      loadTracked();
    } catch (error) {
      if (error.response?.status === 409) {
        Alert.alert('Already Tracking', 'This opportunity is already in your tracker');
      } else {
        Alert.alert('Error', 'Failed to scrape opportunity');
      }
    } finally {
      setIsScraping(false);
    }
  };

  const handleUpdateStatus = async (item, newStatus) => {
    try {
      const token = await AsyncStorage.getItem('authToken');
      
      if (item.participation_id) {
        // Update existing participation
        await api.put(`/participation/${item.participation_id}`, 
          { status: newStatus },
          { headers: { Authorization: `Bearer ${token}` }}
        );
      } else {
        // Create new participation
        await api.post('/participation', 
          { opportunity_id: item.opportunity_id, status: newStatus },
          { headers: { Authorization: `Bearer ${token}` }}
        );
      }
      
      Alert.alert('Success', `Status updated to ${newStatus}`);
      loadTracked();
    } catch (error) {
      Alert.alert('Error', 'Failed to update status');
    }
  };

  const showStatusMenu = (item) => {
    const statusOptions = ['saved', 'applied', 'submitted', 'in_review', 'accepted', 'rejected'];
    const currentStatus = (item.status || 'saved').toLowerCase();
    
    Alert.alert(
      'Update Status',
      'Select the current status of your application:',
      [
        ...statusOptions.map(status => ({
          text: status.replace('_', ' ').toUpperCase() + (status === currentStatus ? ' ✓' : ''),
          onPress: () => handleUpdateStatus(item, status),
        })),
        { text: 'Cancel', style: 'cancel' }
      ]
    );
  };

  return (
    <View style={styles.container}>
      {/* Scraper Bar - Only show for authenticated users */}
      {!isGuest && (
        <View style={styles.scraperBar}>
          <TextInput
            style={styles.scraperInput}
            placeholder="Paste hackathon URL to auto-track..."
            placeholderTextColor="rgba(255, 255, 255, 0.4)"
            value={scrapeUrl}
            onChangeText={setScrapeUrl}
            autoCapitalize="none"
            keyboardType="url"
          />
          <TouchableOpacity
            style={[styles.scrapeButton, isScraping && styles.scrapeButtonDisabled]}
            onPress={handleScrape}
            disabled={isScraping}
          >
            <Text style={styles.scrapeButtonText}>
              {isScraping ? 'Scanning...' : 'Track'}
            </Text>
          </TouchableOpacity>
        </View>
      )}

      <ScrollView
        style={styles.scrollView}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#00f0ff" />}
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>
            Tracked <Text style={styles.accent}>Events</Text>
          </Text>
          {!loading && !isGuest && (
            <View style={styles.countBadge}>
              <Text style={styles.countText}>
                {tracked.length} {tracked.length === 1 ? 'event' : 'events'}
              </Text>
            </View>
          )}
        </View>

        {/* Loading */}
        {loading && (
          <View style={styles.loadingContainer}>
            <Text style={styles.loadingText}>Syncing your events...</Text>
          </View>
        )}

        {/* Guest Mode UI */}
        {!loading && isGuest && (
          <View style={styles.guestContainer}>
            <Ionicons name="bookmark-outline" size={64} color="rgba(0, 240, 255, 0.3)" />
            <Text style={styles.guestTitle}>Track Your Opportunities</Text>
            <Text style={styles.guestMessage}>
              Login to save opportunities, track deadlines, and manage your applications all in one place.
            </Text>
            
            <View style={styles.guestFeatures}>
              <View style={styles.guestFeatureItem}>
                <Ionicons name="checkmark-circle" size={20} color="#00f0ff" />
                <Text style={styles.guestFeatureText}>Save unlimited opportunities</Text>
              </View>
              <View style={styles.guestFeatureItem}>
                <Ionicons name="checkmark-circle" size={20} color="#00f0ff" />
                <Text style={styles.guestFeatureText}>Track application status</Text>
              </View>
              <View style={styles.guestFeatureItem}>
                <Ionicons name="checkmark-circle" size={20} color="#00f0ff" />
                <Text style={styles.guestFeatureText}>Get deadline reminders</Text>
              </View>
              <View style={styles.guestFeatureItem}>
                <Ionicons name="checkmark-circle" size={20} color="#00f0ff" />
                <Text style={styles.guestFeatureText}>Auto-scrape from URLs</Text>
              </View>
            </View>

            <TouchableOpacity
              style={styles.guestLoginButton}
              onPress={() => navigation.navigate('Login')}
            >
              <Text style={styles.guestLoginButtonText}>Login to Track</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.guestSignupButton}
              onPress={() => navigation.navigate('Register')}
            >
              <Text style={styles.guestSignupButtonText}>Create Account</Text>
            </TouchableOpacity>
          </View>
        )}

        {/* Empty State */}
        {!loading && !isGuest && tracked.length === 0 && (
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyIcon}>📌</Text>
            <Text style={styles.emptyTitle}>No events tracked yet</Text>
            <Text style={styles.emptyText}>
              Paste a hackathon URL above or save events from Discover to start tracking deadlines
            </Text>
          </View>
        )}

        {/* Cards */}
        {!loading && !isGuest && tracked.length > 0 && (
          <View style={styles.cardsContainer}>
            {tracked.map((item, index) => {
              const opp = item.opportunity || {};
              const countdown = getCountdown(opp.deadline);

              return (
                <View key={item.opportunity_id || index} style={styles.card}>
                  {/* Top Row */}
                  <View style={styles.cardTopRow}>
                    <View style={styles.typeBadge}>
                      <Text style={styles.typeBadgeText}>
                        {(opp.type || 'event').replace('_', ' ').toUpperCase()}
                      </Text>
                    </View>
                    <View style={[styles.countdownBadge, countdown.urgent && styles.countdownUrgent]}>
                      <Text style={[styles.countdownText, countdown.urgent && styles.countdownTextUrgent]}>
                        {countdown.text}
                      </Text>
                    </View>
                  </View>

                  {/* Title */}
                  <Text style={styles.cardTitle} numberOfLines={2}>
                    {opp.title || 'Untitled Event'}
                  </Text>

                  {/* Description */}
                  {opp.description && (
                    <Text style={styles.cardDescription} numberOfLines={3}>
                      {opp.description}
                    </Text>
                  )}

                  {/* Timeline */}
                  <StatusTimeline status={item.status || 'saved'} />

                  {/* Actions */}
                  <View style={styles.cardActions}>
                    <TouchableOpacity
                      style={styles.statusButton}
                      onPress={() => showStatusMenu(item)}
                    >
                      <Text style={styles.statusButtonText}>Update Status</Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                      style={styles.detailsButton}
                      onPress={() => navigation.navigate('OpportunityDetail', { id: item.opportunity_id })}
                    >
                      <Text style={styles.detailsButtonText}>Details</Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                      style={styles.removeButton}
                      onPress={() => handleRemove(item.opportunity_id)}
                    >
                      <Text style={styles.removeButtonText}>✕</Text>
                    </TouchableOpacity>
                  </View>
                </View>
              );
            })}
          </View>
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
  scraperBar: {
    flexDirection: 'row',
    padding: 16,
    backgroundColor: 'rgba(255, 255, 255, 0.03)',
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 255, 255, 0.06)',
    gap: 8,
  },
  scraperInput: {
    flex: 1,
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    color: '#ffffff',
    fontSize: 14,
  },
  scrapeButton: {
    backgroundColor: '#00f0ff',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
    justifyContent: 'center',
  },
  scrapeButtonDisabled: {
    opacity: 0.5,
  },
  scrapeButtonText: {
    color: '#050508',
    fontSize: 14,
    fontWeight: '600',
  },
  scrollView: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 24,
    paddingTop: 24,
    paddingBottom: 16,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: '#ffffff',
  },
  accent: {
    color: '#00f0ff',
  },
  countBadge: {
    backgroundColor: 'rgba(0, 240, 255, 0.1)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  countText: {
    color: '#00f0ff',
    fontSize: 12,
    fontWeight: '600',
  },
  loadingContainer: {
    paddingVertical: 60,
    alignItems: 'center',
  },
  loadingText: {
    color: 'rgba(255, 255, 255, 0.5)',
    fontSize: 16,
  },
  emptyContainer: {
    paddingVertical: 80,
    paddingHorizontal: 40,
    alignItems: 'center',
  },
  emptyIcon: {
    fontSize: 48,
    marginBottom: 16,
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
  cardsContainer: {
    padding: 16,
    gap: 16,
  },
  card: {
    backgroundColor: 'rgba(255, 255, 255, 0.03)',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.06)',
    borderRadius: 16,
    padding: 16,
  },
  cardTopRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  typeBadge: {
    backgroundColor: 'rgba(0, 240, 255, 0.1)',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 6,
  },
  typeBadgeText: {
    color: '#00f0ff',
    fontSize: 11,
    fontWeight: '600',
  },
  countdownBadge: {
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 6,
  },
  countdownUrgent: {
    backgroundColor: 'rgba(255, 100, 100, 0.1)',
  },
  countdownText: {
    color: 'rgba(255, 255, 255, 0.7)',
    fontSize: 11,
    fontWeight: '600',
  },
  countdownTextUrgent: {
    color: '#ff6464',
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#ffffff',
    marginBottom: 8,
    lineHeight: 24,
  },
  cardDescription: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.6)',
    marginBottom: 16,
    lineHeight: 20,
  },
  timeline: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  timelineStep: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
  },
  timelineDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    borderWidth: 2,
    borderColor: 'rgba(255, 255, 255, 0.3)',
  },
  timelineDotCompleted: {
    backgroundColor: '#00f0ff',
    borderColor: '#00f0ff',
  },
  timelineDotActive: {
    backgroundColor: '#00f0ff',
    borderColor: '#00f0ff',
  },
  timelineLine: {
    flex: 1,
    height: 2,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    marginHorizontal: 4,
  },
  timelineLineCompleted: {
    backgroundColor: '#00f0ff',
  },
  cardActions: {
    flexDirection: 'row',
    gap: 8,
  },
  statusButton: {
    flex: 2,
    backgroundColor: 'rgba(123, 97, 255, 0.1)',
    borderWidth: 1,
    borderColor: '#7b61ff',
    paddingVertical: 10,
    borderRadius: 8,
    alignItems: 'center',
  },
  statusButtonText: {
    color: '#7b61ff',
    fontSize: 14,
    fontWeight: '600',
  },
  detailsButton: {
    flex: 1,
    backgroundColor: 'rgba(0, 240, 255, 0.1)',
    borderWidth: 1,
    borderColor: '#00f0ff',
    paddingVertical: 10,
    borderRadius: 8,
    alignItems: 'center',
  },
  detailsButtonText: {
    color: '#00f0ff',
    fontSize: 14,
    fontWeight: '600',
  },
  removeButton: {
    backgroundColor: 'rgba(255, 100, 100, 0.1)',
    borderWidth: 1,
    borderColor: 'rgba(255, 100, 100, 0.3)',
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  removeButtonText: {
    color: '#ff6464',
    fontSize: 16,
    fontWeight: '600',
  },
  guestContainer: {
    paddingVertical: 60,
    paddingHorizontal: 32,
    alignItems: 'center',
  },
  guestTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#ffffff',
    marginTop: 24,
    marginBottom: 12,
    textAlign: 'center',
  },
  guestMessage: {
    fontSize: 15,
    color: 'rgba(255, 255, 255, 0.7)',
    textAlign: 'center',
    lineHeight: 22,
    marginBottom: 32,
  },
  guestFeatures: {
    width: '100%',
    marginBottom: 32,
    gap: 12,
  },
  guestFeatureItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    paddingVertical: 8,
  },
  guestFeatureText: {
    fontSize: 15,
    color: '#ffffff',
    fontWeight: '500',
  },
  guestLoginButton: {
    width: '100%',
    backgroundColor: '#00f0ff',
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 12,
  },
  guestLoginButtonText: {
    color: '#050508',
    fontSize: 16,
    fontWeight: '600',
  },
  guestSignupButton: {
    width: '100%',
    backgroundColor: 'rgba(0, 240, 255, 0.1)',
    borderWidth: 1,
    borderColor: '#00f0ff',
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
  },
  guestSignupButtonText: {
    color: '#00f0ff',
    fontSize: 16,
    fontWeight: '600',
  },
});
