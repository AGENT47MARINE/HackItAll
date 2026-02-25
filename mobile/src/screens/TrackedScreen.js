import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  RefreshControl,
  Alert,
} from 'react-native';
import { trackingAPI } from '../services/apiService';
import OpportunityCard from '../components/OpportunityCard';

export default function TrackedScreen({ navigation }) {
  const [tracked, setTracked] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadTracked();
  }, []);

  const loadTracked = async () => {
    try {
      const data = await trackingAPI.getTracked();
      setTracked(data);
    } catch (error) {
      console.error('Error loading tracked opportunities:', error);
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
      'Are you sure you want to remove this from your tracker?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Remove',
          style: 'destructive',
          onPress: async () => {
            try {
              await trackingAPI.removeTracked(opportunityId);
              setTracked(tracked.filter(t => t.opportunity_id !== opportunityId));
            } catch (error) {
              Alert.alert('Error', 'Failed to remove opportunity');
            }
          },
        },
      ]
    );
  };

  const handleOpportunityPress = (trackedItem) => {
    navigation.navigate('OpportunityDetail', { opportunity: trackedItem.opportunity });
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Saved Opportunities</Text>
        <Text style={styles.headerSubtitle}>
          {tracked.length} {tracked.length === 1 ? 'opportunity' : 'opportunities'} tracked
        </Text>
      </View>

      <FlatList
        data={tracked}
        keyExtractor={(item) => item.opportunity_id}
        renderItem={({ item }) => (
          <View>
            <OpportunityCard
              opportunity={item.opportunity}
              onPress={() => handleOpportunityPress(item)}
              isExpired={item.is_expired}
            />
            <TouchableOpacity
              style={styles.removeButton}
              onPress={() => handleRemove(item.opportunity_id)}
            >
              <Text style={styles.removeButtonText}>Remove</Text>
            </TouchableOpacity>
          </View>
        )}
        contentContainerStyle={styles.listContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>No saved opportunities</Text>
            <Text style={styles.emptySubtext}>
              Save opportunities to track deadlines and get reminders
            </Text>
          </View>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  header: {
    backgroundColor: '#fff',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#666',
    marginTop: 5,
  },
  listContent: {
    padding: 15,
  },
  removeButton: {
    backgroundColor: '#FF3B30',
    padding: 10,
    borderRadius: 8,
    alignItems: 'center',
    marginHorizontal: 15,
    marginTop: -10,
    marginBottom: 15,
  },
  removeButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 40,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#666',
    marginBottom: 10,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
  },
});
