import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, RefreshControl, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import api from '../services/apiService';

// Mock data for when backend is unavailable
const MOCK_OPPORTUNITIES = [
  {
    id: 1,
    title: 'Global Hackathon 2024',
    organization: 'TechCorp International',
    type: 'hackathon',
    deadline: '2024-12-31',
    track_count: 1250,
    description: 'Join developers worldwide in building innovative solutions',
  },
  {
    id: 2,
    title: 'AI/ML Scholarship Program',
    organization: 'AI Foundation',
    type: 'scholarship',
    deadline: '2024-11-15',
    track_count: 890,
    description: 'Full scholarship for AI and Machine Learning studies',
  },
  {
    id: 3,
    title: 'Summer Tech Internship',
    organization: 'Innovation Labs',
    type: 'internship',
    deadline: '2024-10-30',
    track_count: 756,
    description: 'Paid internship opportunity for software developers',
  },
  {
    id: 4,
    title: 'Web Development Bootcamp',
    organization: 'Code Academy',
    type: 'skill_program',
    deadline: '2024-12-01',
    track_count: 645,
    description: 'Intensive 12-week web development training program',
  },
  {
    id: 5,
    title: 'Blockchain Innovation Challenge',
    organization: 'Crypto Ventures',
    type: 'hackathon',
    deadline: '2024-11-20',
    track_count: 523,
    description: 'Build the next generation of blockchain applications',
  },
];

export default function HomeScreen({ navigation }) {
  const [trending, setTrending] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [useMockData, setUseMockData] = useState(false);

  useEffect(() => {
    loadTrending();
  }, []);

  const loadTrending = async () => {
    try {
      const response = await api.get('/opportunities/trending');
      setTrending(response.data.slice(0, 10));
      setUseMockData(false);
    } catch (error) {
      // Silent fallback to mock data
      setTrending(MOCK_OPPORTUNITIES);
      setUseMockData(true);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadTrending();
  };

  const getTypeColor = (type) => {
    const colors = {
      hackathon: '#00f0ff',
      scholarship: '#00ff88',
      internship: '#7b61ff',
      skill_program: '#ff6b9d',
    };
    return colors[type] || '#00f0ff';
  };

  const getTypeIcon = (type) => {
    const icons = {
      hackathon: 'code-slash',
      scholarship: 'school',
      internship: 'briefcase',
      skill_program: 'bulb',
    };
    return icons[type] || 'star';
  };

  return (
    <View style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#00f0ff" />}
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.logo}>HACKITALL</Text>
          <Text style={styles.title}>
            Discover <Text style={styles.gradientText}>Trending</Text>
          </Text>
          <Text style={styles.subtitle}>
            Most tracked opportunities right now
          </Text>
          {useMockData && (
            <View style={styles.mockBadge}>
              <Ionicons name="information-circle" size={14} color="#ff6b9d" />
              <Text style={styles.mockText}>Demo Mode - Connect to backend for live data</Text>
            </View>
          )}
        </View>

        {/* Trending List */}
        <View style={styles.content}>
          {loading ? (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="large" color="#00f0ff" />
              <Text style={styles.loadingText}>Loading opportunities...</Text>
            </View>
          ) : trending.length === 0 ? (
            <View style={styles.emptyContainer}>
              <Ionicons name="search-outline" size={64} color="rgba(255, 255, 255, 0.2)" />
              <Text style={styles.emptyTitle}>No opportunities found</Text>
              <Text style={styles.emptyText}>Check back later for new opportunities</Text>
            </View>
          ) : (
            trending.map((opportunity, index) => (
              <TouchableOpacity
                key={opportunity.id}
                style={styles.card}
                onPress={() => navigation.navigate('OpportunityDetail', { id: opportunity.id })}
                activeOpacity={0.7}
              >
                <View style={styles.cardHeader}>
                  <View style={styles.rankBadge}>
                    <Text style={styles.rankText}>#{index + 1}</Text>
                  </View>
                  <View style={[styles.typeBadge, { backgroundColor: `${getTypeColor(opportunity.type)}15` }]}>
                    <Ionicons name={getTypeIcon(opportunity.type)} size={14} color={getTypeColor(opportunity.type)} />
                    <Text style={[styles.typeText, { color: getTypeColor(opportunity.type) }]}>
                      {opportunity.type.replace('_', ' ').toUpperCase()}
                    </Text>
                  </View>
                </View>
                
                <Text style={styles.cardTitle} numberOfLines={2}>
                  {opportunity.title}
                </Text>
                
                {opportunity.organization && (
                  <View style={styles.orgRow}>
                    <Ionicons name="business-outline" size={14} color="rgba(255, 255, 255, 0.5)" />
                    <Text style={styles.cardOrg} numberOfLines={1}>
                      {opportunity.organization}
                    </Text>
                  </View>
                )}
                
                <View style={styles.cardFooter}>
                  {opportunity.deadline && (
                    <View style={styles.footerItem}>
                      <Ionicons name="calendar-outline" size={14} color="rgba(255, 255, 255, 0.5)" />
                      <Text style={styles.cardDeadline}>
                        {new Date(opportunity.deadline).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                      </Text>
                    </View>
                  )}
                  {opportunity.track_count > 0 && (
                    <View style={styles.footerItem}>
                      <Ionicons name="flame" size={14} color="#00ff88" />
                      <Text style={styles.cardTracks}>
                        {opportunity.track_count} tracking
                      </Text>
                    </View>
                  )}
                </View>
              </TouchableOpacity>
            ))
          )}
        </View>
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
  header: {
    paddingHorizontal: 24,
    paddingTop: 60,
    paddingBottom: 32,
    backgroundColor: 'rgba(0, 240, 255, 0.02)',
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(0, 240, 255, 0.1)',
  },
  logo: {
    fontFamily: 'monospace',
    fontSize: 12,
    fontWeight: '800',
    color: '#00f0ff',
    letterSpacing: 3,
    marginBottom: 16,
  },
  title: {
    fontSize: 36,
    fontWeight: '800',
    color: '#ffffff',
    marginBottom: 8,
    letterSpacing: -1,
  },
  gradientText: {
    color: '#00f0ff',
  },
  subtitle: {
    fontSize: 15,
    color: 'rgba(255, 255, 255, 0.6)',
    lineHeight: 22,
  },
  mockBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginTop: 12,
    padding: 8,
    backgroundColor: 'rgba(255, 107, 157, 0.1)',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: 'rgba(255, 107, 157, 0.2)',
  },
  mockText: {
    fontSize: 11,
    color: '#ff6b9d',
    fontWeight: '600',
  },
  content: {
    paddingHorizontal: 16,
    paddingTop: 20,
    paddingBottom: 24,
  },
  loadingContainer: {
    paddingVertical: 60,
    alignItems: 'center',
    gap: 16,
  },
  loadingText: {
    color: 'rgba(255, 255, 255, 0.6)',
    fontSize: 15,
    fontWeight: '500',
  },
  emptyContainer: {
    paddingVertical: 80,
    alignItems: 'center',
    gap: 12,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#ffffff',
    marginTop: 16,
  },
  emptyText: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.5)',
    textAlign: 'center',
  },
  card: {
    backgroundColor: 'rgba(255, 255, 255, 0.03)',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.08)',
    borderRadius: 20,
    padding: 20,
    marginBottom: 16,
    shadowColor: '#00f0ff',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 3,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 14,
    gap: 10,
  },
  rankBadge: {
    backgroundColor: 'rgba(0, 240, 255, 0.15)',
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderWidth: 1,
    borderColor: 'rgba(0, 240, 255, 0.3)',
  },
  rankText: {
    color: '#00f0ff',
    fontSize: 13,
    fontWeight: '800',
    letterSpacing: 0.5,
  },
  typeBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  typeText: {
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
  cardTitle: {
    fontSize: 19,
    fontWeight: '700',
    color: '#ffffff',
    marginBottom: 10,
    lineHeight: 26,
    letterSpacing: -0.3,
  },
  orgRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginBottom: 14,
  },
  cardOrg: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.6)',
    fontWeight: '500',
  },
  cardFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: 'rgba(255, 255, 255, 0.06)',
  },
  footerItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  cardDeadline: {
    fontSize: 13,
    color: 'rgba(255, 255, 255, 0.6)',
    fontWeight: '600',
  },
  cardTracks: {
    fontSize: 13,
    color: '#00ff88',
    fontWeight: '700',
  },
});
