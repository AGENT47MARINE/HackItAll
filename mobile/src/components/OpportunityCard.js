import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';

export default function OpportunityCard({ opportunity, relevanceScore, onPress, isExpired }) {
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const getDaysUntilDeadline = (deadline) => {
    const now = new Date();
    const deadlineDate = new Date(deadline);
    const diffTime = deadlineDate - now;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const daysLeft = getDaysUntilDeadline(opportunity.deadline);
  const isUrgent = daysLeft <= 7 && daysLeft > 0;

  return (
    <TouchableOpacity
      style={[styles.card, isExpired && styles.cardExpired]}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <View style={styles.header}>
        <View style={styles.typeContainer}>
          <Text style={styles.typeText}>
            {opportunity.type.replace('_', ' ')}
          </Text>
        </View>
        {relevanceScore && (
          <View style={styles.scoreContainer}>
            <Text style={styles.scoreText}>
              {Math.round(relevanceScore * 100)}% match
            </Text>
          </View>
        )}
      </View>

      <Text style={styles.title} numberOfLines={2}>
        {opportunity.title}
      </Text>

      <Text style={styles.description} numberOfLines={3}>
        {opportunity.description}
      </Text>

      <View style={styles.footer}>
        <View style={styles.deadlineContainer}>
          <Text style={[styles.deadlineLabel, isUrgent && styles.urgent]}>
            Deadline:
          </Text>
          <Text style={[styles.deadline, isUrgent && styles.urgent]}>
            {formatDate(opportunity.deadline)}
          </Text>
          {isExpired && (
            <Text style={styles.expiredText}>(Expired)</Text>
          )}
          {isUrgent && !isExpired && (
            <Text style={styles.urgentText}>({daysLeft} days left)</Text>
          )}
        </View>
      </View>

      {opportunity.tags && opportunity.tags.length > 0 && (
        <View style={styles.tagsContainer}>
          {opportunity.tags.slice(0, 3).map((tag, index) => (
            <View key={index} style={styles.tag}>
              <Text style={styles.tagText}>{tag}</Text>
            </View>
          ))}
          {opportunity.tags.length > 3 && (
            <Text style={styles.moreText}>+{opportunity.tags.length - 3} more</Text>
          )}
        </View>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 15,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardExpired: {
    opacity: 0.6,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  typeContainer: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 12,
  },
  typeText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
    textTransform: 'capitalize',
  },
  scoreContainer: {
    backgroundColor: '#34C759',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 12,
  },
  scoreText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  description: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
    marginBottom: 12,
  },
  footer: {
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
    paddingTop: 10,
  },
  deadlineContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  deadlineLabel: {
    fontSize: 14,
    color: '#666',
    marginRight: 5,
  },
  deadline: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  urgent: {
    color: '#FF3B30',
  },
  expiredText: {
    fontSize: 12,
    color: '#999',
    marginLeft: 5,
  },
  urgentText: {
    fontSize: 12,
    color: '#FF3B30',
    marginLeft: 5,
    fontWeight: '600',
  },
  tagsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 10,
    alignItems: 'center',
  },
  tag: {
    backgroundColor: '#f0f0f0',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 10,
    marginRight: 6,
    marginBottom: 4,
  },
  tagText: {
    fontSize: 12,
    color: '#666',
  },
  moreText: {
    fontSize: 12,
    color: '#999',
    fontStyle: 'italic',
  },
});
