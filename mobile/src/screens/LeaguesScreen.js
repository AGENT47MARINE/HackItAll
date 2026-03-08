import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, RefreshControl, TouchableOpacity } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';
import { gamificationAPI } from '../services/apiService';

const BADGE_MAP = {
  'first_steps': { title: 'First Steps', icon: '🏃' },
  'onboarding': { title: 'Citizen', icon: '🏅' },
  'tracker_10': { title: 'Bug Catcher', icon: '🐛' },
  'first_scrape': { title: 'Data Miner', icon: '🕷️' },
  'content_10': { title: 'Knowledge Seeker', icon: '📚' },
  'analyze_5': { title: 'Strategist', icon: '🔍' },
  'applied_5': { title: 'Form Filler', icon: '📝' },
  'accepted_1': { title: 'Golden Ticket', icon: '🎫' },
  'completed_3': { title: 'Hat Trick', icon: '🎩' },
  'completed_10': { title: 'Legendary Dev', icon: '💀' },
  'streak_7': { title: 'Week Warrior', icon: '🔥' },
  'streak_30': { title: 'Monthly Monster', icon: '💎' },
};

const TIER_COLORS = {
  1: '#CD7F32', // Bronze
  2: '#C0C0C0', // Silver
  3: '#FFD700', // Gold
  4: '#E5E4E2', // Platinum
  5: '#B9F2FF', // Diamond
  6: '#0C0C0C', // Obsidian
};

const TIER_NAMES = {
  1: 'Bronze Byte',
  2: 'Silver Script',
  3: 'Gold Gopher',
  4: 'Platinum Python',
  5: 'Diamond Dev',
  6: 'Obsidian Oracle',
};

export default function LeaguesScreen({ navigation }) {
  const [stats, setStats] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [isGuest, setIsGuest] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const token = await AsyncStorage.getItem('authToken');
      if (!token) {
        setIsGuest(true);
        setLoading(false);
        setRefreshing(false);
        return;
      }

      const [statsData, leaderboardData] = await Promise.all([
        gamificationAPI.getStats(),
        gamificationAPI.getLeaderboard(),
      ]);

      setStats(statsData);
      setLeaderboard(leaderboardData);
      setIsGuest(false);
    } catch (error) {
      // Silent fallback for guest mode or API errors
      if (error.response?.status === 401 || error.response?.status === 403) {
        setIsGuest(true);
      } else {
        console.error('Error loading gamification data:', error);
        // Set default values if API fails but user is authenticated
        setStats({
          total_xp: 0,
          league_tier: 1,
          tier_name: 'Bronze Byte',
          streak_days: 0,
          progress_pct: 0,
          next_tier_xp: 100,
          unlocked_badges: []
        });
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadData();
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <View style={styles.loadingContainer}>
          <Text style={styles.loadingText}>LOADING GAME DATA...</Text>
        </View>
      </View>
    );
  }

  // Guest Mode UI
  if (isGuest) {
    return (
      <View style={styles.container}>
        <ScrollView
          style={styles.scrollView}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#00f0ff" />}
        >
          <View style={styles.guestContainer}>
            <Ionicons name="trophy-outline" size={80} color="rgba(0, 240, 255, 0.3)" />
            <Text style={styles.guestTitle}>Join the League</Text>
            <Text style={styles.guestMessage}>
              Login to compete with other students, earn XP, unlock achievements, and climb the leaderboard!
            </Text>

            <View style={styles.guestFeatures}>
              <View style={styles.guestFeatureCard}>
                <Ionicons name="flash" size={32} color="#00f0ff" />
                <Text style={styles.guestFeatureTitle}>Earn XP</Text>
                <Text style={styles.guestFeatureDesc}>Complete actions to level up</Text>
              </View>
              <View style={styles.guestFeatureCard}>
                <Ionicons name="medal" size={32} color="#FFD700" />
                <Text style={styles.guestFeatureTitle}>Unlock Badges</Text>
                <Text style={styles.guestFeatureDesc}>Collect achievements</Text>
              </View>
              <View style={styles.guestFeatureCard}>
                <Ionicons name="podium" size={32} color="#7b61ff" />
                <Text style={styles.guestFeatureTitle}>Compete</Text>
                <Text style={styles.guestFeatureDesc}>Climb the leaderboard</Text>
              </View>
            </View>

            <TouchableOpacity
              style={styles.guestLoginButton}
              onPress={() => navigation.navigate('Login')}
            >
              <Text style={styles.guestLoginButtonText}>Login to Play</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.guestSignupButton}
              onPress={() => navigation.navigate('Register')}
            >
              <Text style={styles.guestSignupButtonText}>Create Account</Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      </View>
    );
  }

  const s = stats || {
    total_xp: 0,
    league_tier: 1,
    tier_name: 'Bronze Byte',
    streak_days: 0,
    progress_pct: 0,
    next_tier_xp: 100,
    unlocked_badges: []
  };

  const tierColor = TIER_COLORS[s.league_tier] || TIER_COLORS[1];

  return (
    <View style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#00f0ff" />}
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>YOUR LEAGUE</Text>
          <Text style={[styles.tierName, { color: tierColor }]}>{s.tier_name}</Text>
        </View>

        {/* Tier Card */}
        <View style={styles.tierCard}>
          <View style={[styles.tierBadge, { borderColor: tierColor }]}>
            <Text style={[styles.tierIcon, { color: tierColor }]}>
              {s.league_tier === 1 ? '🛡️' : s.league_tier === 2 ? '📜' : s.league_tier === 3 ? '🌟' : 
               s.league_tier === 4 ? '⚡' : s.league_tier === 5 ? '💎' : '👑'}
            </Text>
          </View>
          <Text style={[styles.tierLevel, { color: tierColor }]}>
            Level {s.league_tier}: {s.tier_name}
          </Text>

          {/* XP Progress */}
          <View style={styles.xpContainer}>
            <View style={styles.xpHeader}>
              <Text style={styles.xpLabel}>EXP</Text>
              <Text style={styles.xpValue}>{s.total_xp} / {s.next_tier_xp}</Text>
            </View>
            <View style={styles.xpBar}>
              <View style={[styles.xpFill, { width: `${s.progress_pct}%` }]} />
            </View>
          </View>

          {/* Stats Row */}
          <View style={styles.statsRow}>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{s.total_xp}</Text>
              <Text style={styles.statLabel}>Total XP</Text>
            </View>
            <View style={styles.statItem}>
              <View style={styles.statValueRow}>
                <Text style={styles.statIcon}>🔥</Text>
                <Text style={styles.statValue}>{s.streak_days}</Text>
              </View>
              <Text style={styles.statLabel}>STREAK</Text>
            </View>
            <View style={styles.statItem}>
              <View style={styles.statValueRow}>
                <Text style={styles.statIcon}>🏆</Text>
                <Text style={styles.statValue}>#12</Text>
              </View>
              <Text style={styles.statLabel}>GLOBAL</Text>
            </View>
          </View>
        </View>

        {/* Achievements */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>ACHIEVEMENTS</Text>
          <View style={styles.achievementsGrid}>
            {Object.entries(BADGE_MAP).map(([id, badge]) => {
              const isUnlocked = s.unlocked_badges.includes(id);
              return (
                <View key={id} style={[styles.badgeSlot, isUnlocked && styles.badgeSlotUnlocked]}>
                  <Text style={[styles.badgeIcon, !isUnlocked && styles.badgeIconLocked]}>
                    {badge.icon}
                  </Text>
                  <Text style={[styles.badgeTitle, !isUnlocked && styles.badgeTitleLocked]}>
                    {badge.title}
                  </Text>
                </View>
              );
            })}
          </View>
        </View>

        {/* Leaderboard */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>LEADERBOARD</Text>
          <View style={styles.leaderboardCard}>
            {leaderboard.length > 0 ? (
              leaderboard.map((player, idx) => (
                <View key={idx} style={[styles.leaderItem, idx === 0 && styles.leaderItemTop]}>
                  <Text style={styles.leaderRank}>{idx + 1}</Text>
                  <Text style={styles.leaderIcon}>
                    {player.tier === 1 ? '🛡️' : player.tier === 2 ? '📜' : player.tier === 3 ? '🌟' : 
                     player.tier === 4 ? '⚡' : player.tier === 5 ? '💎' : '👑'}
                  </Text>
                  <View style={styles.leaderInfo}>
                    <Text style={styles.leaderName} numberOfLines={1}>{player.email}</Text>
                    <View style={styles.leaderStats}>
                      <Text style={styles.leaderXP}>{player.xp} XP</Text>
                      <Text style={styles.leaderStreak}>• {player.streak} 🔥</Text>
                    </View>
                  </View>
                </View>
              ))
            ) : (
              <Text style={styles.emptyText}>No Data Recorded</Text>
            )}
          </View>
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
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    color: '#00f0ff',
    fontSize: 14,
    fontFamily: 'monospace',
    letterSpacing: 2,
  },
  header: {
    alignItems: 'center',
    paddingVertical: 32,
    paddingHorizontal: 24,
  },
  headerTitle: {
    fontSize: 16,
    fontWeight: '800',
    color: '#00f0ff',
    letterSpacing: 3,
    marginBottom: 8,
    fontFamily: 'monospace',
  },
  tierName: {
    fontSize: 24,
    fontWeight: '700',
  },
  tierCard: {
    backgroundColor: 'rgba(255, 255, 255, 0.03)',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.06)',
    borderRadius: 16,
    padding: 24,
    marginHorizontal: 16,
    marginBottom: 24,
    alignItems: 'center',
  },
  tierBadge: {
    width: 80,
    height: 80,
    borderRadius: 40,
    borderWidth: 3,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  tierIcon: {
    fontSize: 40,
  },
  tierLevel: {
    fontSize: 20,
    fontWeight: '700',
    marginBottom: 24,
  },
  xpContainer: {
    width: '100%',
    marginBottom: 24,
  },
  xpHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  xpLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: 'rgba(255, 255, 255, 0.6)',
  },
  xpValue: {
    fontSize: 12,
    fontWeight: '600',
    color: '#00f0ff',
  },
  xpBar: {
    height: 8,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: 4,
    overflow: 'hidden',
  },
  xpFill: {
    height: '100%',
    backgroundColor: '#00f0ff',
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    width: '100%',
  },
  statItem: {
    alignItems: 'center',
  },
  statValueRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  statIcon: {
    fontSize: 20,
  },
  statValue: {
    fontSize: 24,
    fontWeight: '700',
    color: '#ffffff',
  },
  statLabel: {
    fontSize: 11,
    color: 'rgba(255, 255, 255, 0.5)',
    marginTop: 4,
    fontWeight: '600',
  },
  section: {
    paddingHorizontal: 16,
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '800',
    color: '#00f0ff',
    letterSpacing: 2,
    marginBottom: 16,
    fontFamily: 'monospace',
  },
  achievementsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  badgeSlot: {
    width: '30%',
    backgroundColor: 'rgba(255, 255, 255, 0.03)',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.06)',
    borderRadius: 12,
    padding: 12,
    alignItems: 'center',
  },
  badgeSlotUnlocked: {
    backgroundColor: 'rgba(0, 240, 255, 0.05)',
    borderColor: 'rgba(0, 240, 255, 0.2)',
  },
  badgeIcon: {
    fontSize: 32,
    marginBottom: 8,
  },
  badgeIconLocked: {
    opacity: 0.3,
  },
  badgeTitle: {
    fontSize: 10,
    color: '#00f0ff',
    textAlign: 'center',
    fontWeight: '600',
  },
  badgeTitleLocked: {
    color: 'rgba(255, 255, 255, 0.3)',
  },
  leaderboardCard: {
    backgroundColor: 'rgba(255, 255, 255, 0.03)',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.06)',
    borderRadius: 16,
    padding: 16,
  },
  leaderItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 255, 255, 0.06)',
  },
  leaderItemTop: {
    backgroundColor: 'rgba(255, 215, 0, 0.05)',
    borderRadius: 8,
    paddingHorizontal: 8,
  },
  leaderRank: {
    fontSize: 16,
    fontWeight: '700',
    color: '#00f0ff',
    width: 30,
  },
  leaderIcon: {
    fontSize: 20,
    marginRight: 12,
  },
  leaderInfo: {
    flex: 1,
  },
  leaderName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#ffffff',
    marginBottom: 4,
  },
  leaderStats: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  leaderXP: {
    fontSize: 12,
    color: 'rgba(255, 255, 255, 0.6)',
  },
  leaderStreak: {
    fontSize: 12,
    color: 'rgba(255, 255, 255, 0.6)',
    marginLeft: 4,
  },
  emptyText: {
    textAlign: 'center',
    color: 'rgba(255, 255, 255, 0.4)',
    fontSize: 14,
    paddingVertical: 24,
  },
  guestContainer: {
    paddingVertical: 60,
    paddingHorizontal: 32,
    alignItems: 'center',
  },
  guestTitle: {
    fontSize: 28,
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
    marginBottom: 40,
  },
  guestFeatures: {
    width: '100%',
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 40,
    gap: 12,
  },
  guestFeatureCard: {
    flex: 1,
    backgroundColor: 'rgba(255, 255, 255, 0.03)',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.06)',
    borderRadius: 16,
    padding: 16,
    alignItems: 'center',
  },
  guestFeatureTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#ffffff',
    marginTop: 12,
    marginBottom: 4,
    textAlign: 'center',
  },
  guestFeatureDesc: {
    fontSize: 11,
    color: 'rgba(255, 255, 255, 0.6)',
    textAlign: 'center',
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
