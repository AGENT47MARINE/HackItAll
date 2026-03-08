import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, TextInput, RefreshControl, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import api from '../services/apiService';

// Mock data for offline/demo mode
const MOCK_OPPORTUNITIES = [
  {
    id: 1,
    title: 'Global AI Hackathon 2024',
    organization: 'TechCorp International',
    description: 'Build innovative AI solutions to solve real-world problems. $50K in prizes!',
    type: 'hackathon',
    deadline: '2024-04-15T23:59:59Z',
    track_count: 234,
  },
  {
    id: 2,
    title: 'Google Summer of Code',
    organization: 'Google',
    description: 'Work with open source organizations on exciting projects during summer.',
    type: 'internship',
    deadline: '2024-03-20T23:59:59Z',
    track_count: 1523,
  },
  {
    id: 3,
    title: 'Women in Tech Scholarship',
    organization: 'Tech Foundation',
    description: 'Full scholarship for women pursuing computer science degrees.',
    type: 'scholarship',
    deadline: '2024-05-01T23:59:59Z',
    track_count: 456,
  },
  {
    id: 4,
    title: 'AWS Cloud Skills Challenge',
    organization: 'Amazon Web Services',
    description: 'Learn cloud computing skills and earn AWS certifications.',
    type: 'skill_program',
    deadline: '2024-04-30T23:59:59Z',
    track_count: 789,
  },
  {
    id: 5,
    title: 'Blockchain Innovation Challenge',
    organization: 'CryptoVentures',
    description: 'Create decentralized applications using blockchain technology.',
    type: 'hackathon',
    deadline: '2024-03-25T23:59:59Z',
    track_count: 167,
  },
  {
    id: 6,
    title: 'Microsoft Learn Student Ambassador',
    organization: 'Microsoft',
    description: 'Join a global community of student leaders and tech enthusiasts.',
    type: 'skill_program',
    deadline: '2024-06-15T23:59:59Z',
    track_count: 892,
  },
  {
    id: 7,
    title: 'Cybersecurity Bootcamp',
    organization: 'SecureNet Academy',
    description: 'Intensive 12-week program covering ethical hacking and security.',
    type: 'skill_program',
    deadline: '2024-04-10T23:59:59Z',
    track_count: 345,
  },
  {
    id: 8,
    title: 'Startup Weekend',
    organization: 'Techstars',
    description: '54-hour event to build a startup from idea to pitch.',
    type: 'hackathon',
    deadline: '2024-03-18T23:59:59Z',
    track_count: 278,
  },
];

export default function OpportunitiesScreen({ navigation }) {
  const [opportunities, setOpportunities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState(null);
  const [useMockData, setUseMockData] = useState(false);

  const types = [
    { key: null, label: 'All' },
    { key: 'hackathon', label: 'Hackathon' },
    { key: 'scholarship', label: 'Scholarship' },
    { key: 'internship', label: 'Internship' },
    { key: 'skill_program', label: 'Skill Program' },
  ];

  useEffect(() => {
    searchOpportunities();
  }, [selectedType]);

  const searchOpportunities = async () => {
    setLoading(true);
    try {
      const params = {};
      if (searchQuery) params.search = searchQuery;
      if (selectedType) params.type = [selectedType];

      const response = await api.get('/opportunities/search', { params });
      setOpportunities(response.data);
      setUseMockData(false);
    } catch (error) {
      // Silent fallback to mock data - no console spam
      setUseMockData(true);
      filterMockData();
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const filterMockData = () => {
    let filtered = [...MOCK_OPPORTUNITIES];
    
    // Filter by type
    if (selectedType) {
      filtered = filtered.filter(opp => opp.type === selectedType);
    }
    
    // Filter by search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(opp => 
        opp.title.toLowerCase().includes(query) ||
        opp.organization.toLowerCase().includes(query) ||
        opp.description.toLowerCase().includes(query)
      );
    }
    
    setOpportunities(filtered);
  };

  const onRefresh = () => {
    setRefreshing(true);
    searchOpportunities();
  };

  const handleSearch = () => {
    searchOpportunities();
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

  return (
    <View style={styles.container}>
      {/* Search Bar */}
      <View style={styles.searchSection}>
        <View style={styles.searchBar}>
          <TextInput
            style={styles.searchInput}
            placeholder="Search opportunities..."
            placeholderTextColor="rgba(255, 255, 255, 0.4)"
            value={searchQuery}
            onChangeText={setSearchQuery}
            onSubmitEditing={handleSearch}
          />
          <TouchableOpacity style={styles.searchButton} onPress={handleSearch}>
            <Ionicons name="search" size={20} color="#050508" />
          </TouchableOpacity>
        </View>

        {/* Filter Chips */}
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.filterChips}>
          {types.map((type) => (
            <TouchableOpacity
              key={type.key || 'all'}
              style={[
                styles.filterChip,
                selectedType === type.key && styles.filterChipActive,
              ]}
              onPress={() => setSelectedType(type.key)}
            >
              <Text style={[
                styles.filterChipText,
                selectedType === type.key && styles.filterChipTextActive,
              ]}>
                {type.label}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      <ScrollView
        style={styles.scrollView}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#00f0ff" />}
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>
            Explore <Text style={styles.accent}>Opportunities</Text>
          </Text>
          {useMockData && (
            <View style={styles.demoModeBadge}>
              <Ionicons name="information-circle-outline" size={14} color="#ff6b9d" />
              <Text style={styles.demoModeText}>Demo Mode - Connect to see live data</Text>
            </View>
          )}
          {!loading && opportunities.length > 0 && (
            <Text style={styles.resultsCount}>
              Found <Text style={styles.resultsCountHighlight}>{opportunities.length}</Text> opportunities
            </Text>
          )}
        </View>

        {/* Loading */}
        {loading && (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#00f0ff" />
            <Text style={styles.loadingText}>Searching opportunities...</Text>
          </View>
        )}

        {/* Empty State */}
        {!loading && opportunities.length === 0 && (
          <View style={styles.emptyContainer}>
            <Ionicons name="search-outline" size={64} color="rgba(255, 255, 255, 0.3)" />
            <Text style={styles.emptyTitle}>No opportunities found</Text>
            <Text style={styles.emptyText}>
              Try adjusting your search criteria or filters
            </Text>
          </View>
        )}

        {/* Opportunities List */}
        {!loading && opportunities.length > 0 && (
          <View style={styles.opportunitiesContainer}>
            {opportunities.map((opportunity) => (
              <TouchableOpacity
                key={opportunity.id}
                style={styles.card}
                onPress={() => navigation.navigate('OpportunityDetail', { id: opportunity.id })}
              >
                {/* Type Badge */}
                <View style={[styles.typeBadge, { backgroundColor: `${getTypeColor(opportunity.type)}20` }]}>
                  <Text style={[styles.typeBadgeText, { color: getTypeColor(opportunity.type) }]}>
                    {opportunity.type.replace('_', ' ').toUpperCase()}
                  </Text>
                </View>

                {/* Title */}
                <Text style={styles.cardTitle} numberOfLines={2}>
                  {opportunity.title}
                </Text>

                {/* Organization */}
                {opportunity.organization && (
                  <Text style={styles.cardOrg} numberOfLines={1}>
                    {opportunity.organization}
                  </Text>
                )}

                {/* Description */}
                {opportunity.description && (
                  <Text style={styles.cardDescription} numberOfLines={3}>
                    {opportunity.description}
                  </Text>
                )}

                {/* Footer */}
                <View style={styles.cardFooter}>
                  {opportunity.deadline && (
                    <View style={styles.cardFooterItem}>
                      <Ionicons name="calendar-outline" size={14} color="rgba(255, 255, 255, 0.5)" />
                      <Text style={styles.cardDeadline}>
                        {new Date(opportunity.deadline).toLocaleDateString()}
                      </Text>
                    </View>
                  )}
                  {opportunity.track_count > 0 && (
                    <View style={styles.cardFooterItem}>
                      <Ionicons name="flame" size={14} color="#00ff88" />
                      <Text style={styles.cardTracks}>
                        {opportunity.track_count} tracking
                      </Text>
                    </View>
                  )}
                </View>
              </TouchableOpacity>
            ))}
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
  searchSection: {
    backgroundColor: 'rgba(255, 255, 255, 0.03)',
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 255, 255, 0.06)',
    paddingTop: 16,
    paddingBottom: 12,
  },
  searchBar: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    marginBottom: 12,
    gap: 8,
  },
  searchInput: {
    flex: 1,
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 12,
    color: '#ffffff',
    fontSize: 15,
  },
  searchButton: {
    backgroundColor: '#00f0ff',
    width: 48,
    height: 48,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  filterChips: {
    paddingHorizontal: 16,
  },
  filterChip: {
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 8,
  },
  filterChipActive: {
    backgroundColor: 'rgba(0, 240, 255, 0.1)',
    borderColor: '#00f0ff',
  },
  filterChipText: {
    color: 'rgba(255, 255, 255, 0.7)',
    fontSize: 14,
    fontWeight: '500',
  },
  filterChipTextActive: {
    color: '#00f0ff',
    fontWeight: '600',
  },
  scrollView: {
    flex: 1,
  },
  header: {
    paddingHorizontal: 24,
    paddingTop: 24,
    paddingBottom: 16,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: '#ffffff',
    marginBottom: 8,
  },
  accent: {
    color: '#00f0ff',
  },
  demoModeBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 107, 157, 0.1)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
    marginBottom: 8,
    alignSelf: 'flex-start',
    gap: 6,
  },
  demoModeText: {
    fontSize: 12,
    color: '#ff6b9d',
    fontWeight: '500',
  },
  resultsCount: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.6)',
  },
  resultsCountHighlight: {
    color: '#00f0ff',
    fontWeight: '600',
  },
  loadingContainer: {
    paddingVertical: 60,
    alignItems: 'center',
    gap: 16,
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
  emptyTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#ffffff',
    marginTop: 16,
    marginBottom: 8,
    textAlign: 'center',
  },
  emptyText: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.6)',
    textAlign: 'center',
    lineHeight: 20,
  },
  opportunitiesContainer: {
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
  typeBadge: {
    alignSelf: 'flex-start',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 6,
    marginBottom: 12,
  },
  typeBadgeText: {
    fontSize: 11,
    fontWeight: '600',
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#ffffff',
    marginBottom: 8,
    lineHeight: 24,
  },
  cardOrg: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.6)',
    marginBottom: 8,
  },
  cardDescription: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.6)',
    marginBottom: 12,
    lineHeight: 20,
  },
  cardFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  cardFooterItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  cardDeadline: {
    fontSize: 13,
    color: 'rgba(255, 255, 255, 0.5)',
  },
  cardTracks: {
    fontSize: 13,
    color: '#00ff88',
    fontWeight: '600',
  },
});
