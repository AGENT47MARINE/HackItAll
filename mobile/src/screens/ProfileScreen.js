import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Switch, Alert } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Notifications from 'expo-notifications';
import { Ionicons } from '@expo/vector-icons';
import api from '../services/apiService';

export default function ProfileScreen({ navigation }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isGuest, setIsGuest] = useState(false);
  const [notificationsEnabled, setNotificationsEnabled] = useState(false);
  const [deadlineReminders, setDeadlineReminders] = useState(true);
  const [newOpportunities, setNewOpportunities] = useState(true);

  useEffect(() => {
    loadProfile();
    checkNotificationSettings();
  }, []);

  const loadProfile = async () => {
    try {
      const token = await AsyncStorage.getItem('authToken');
      if (!token) {
        // Guest mode - no token
        setIsGuest(true);
        setLoading(false);
        return;
      }
      
      const response = await api.get('/auth/me', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(response.data);
      setIsGuest(false);
    } catch (error) {
      console.error('Error loading profile:', error);
      // If 401 or any auth error, treat as guest
      if (error.response?.status === 401 || error.response?.status === 403) {
        setIsGuest(true);
        await AsyncStorage.removeItem('authToken');
        await AsyncStorage.removeItem('userId');
      }
    } finally {
      setLoading(false);
    }
  };

  const checkNotificationSettings = async () => {
    const { status } = await Notifications.getPermissionsAsync();
    setNotificationsEnabled(status === 'granted');
  };

  const handleToggleNotifications = async (value) => {
    if (value) {
      const { status } = await Notifications.requestPermissionsAsync();
      if (status === 'granted') {
        setNotificationsEnabled(true);
        Alert.alert('Success', 'Notifications enabled! You\'ll receive alerts for deadlines and new opportunities.');
      } else {
        Alert.alert('Permission Denied', 'Please enable notifications in your device settings.');
      }
    } else {
      setNotificationsEnabled(false);
      Alert.alert('Disabled', 'Notifications have been disabled.');
    }
  };

  const handleLogout = async () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Logout',
          style: 'destructive',
          onPress: async () => {
            await AsyncStorage.removeItem('authToken');
            await AsyncStorage.removeItem('userId');
            navigation.replace('Welcome');
          }
        }
      ]
    );
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <View style={styles.loadingContainer}>
          <Text style={styles.loadingText}>Loading profile...</Text>
        </View>
      </View>
    );
  }

  // Guest Mode UI
  if (isGuest) {
    return (
      <View style={styles.container}>
        <ScrollView style={styles.scrollView}>
          {/* Guest Header */}
          <View style={styles.header}>
            <View style={styles.avatar}>
              <Ionicons name="person-outline" size={40} color="#00f0ff" />
            </View>
            <Text style={styles.name}>Guest User</Text>
            <Text style={styles.email}>Browsing without account</Text>
          </View>

          {/* Guest Message */}
          <View style={styles.section}>
            <View style={styles.guestCard}>
              <Ionicons name="lock-open-outline" size={48} color="#00f0ff" style={{ marginBottom: 16 }} />
              <Text style={styles.guestTitle}>Create an Account</Text>
              <Text style={styles.guestMessage}>
                Sign up to track opportunities, get personalized recommendations, earn XP, and unlock achievements!
              </Text>
              
              <View style={styles.guestFeatures}>
                <View style={styles.featureItem}>
                  <Ionicons name="bookmark-outline" size={20} color="#00f0ff" style={{ marginRight: 12 }} />
                  <Text style={styles.featureText}>Track deadlines</Text>
                </View>
                <View style={styles.featureItem}>
                  <Ionicons name="bulb-outline" size={20} color="#00f0ff" style={{ marginRight: 12 }} />
                  <Text style={styles.featureText}>Get AI recommendations</Text>
                </View>
                <View style={styles.featureItem}>
                  <Ionicons name="trophy-outline" size={20} color="#00f0ff" style={{ marginRight: 12 }} />
                  <Text style={styles.featureText}>Earn badges & XP</Text>
                </View>
                <View style={styles.featureItem}>
                  <Ionicons name="notifications-outline" size={20} color="#00f0ff" style={{ marginRight: 12 }} />
                  <Text style={styles.featureText}>Deadline reminders</Text>
                </View>
              </View>

              <TouchableOpacity
                style={styles.signupButton}
                onPress={() => navigation.navigate('Register')}
              >
                <Text style={styles.signupButtonText}>Create Account</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.loginButton}
                onPress={() => navigation.navigate('Login')}
              >
                <Text style={styles.loginButtonText}>Already have an account? Login</Text>
              </TouchableOpacity>
            </View>
          </View>

          <View style={styles.footer}>
            <Text style={styles.footerText}>HackItAll Mobile v1.0.0</Text>
          </View>
        </ScrollView>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <ScrollView style={styles.scrollView}>
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.avatar}>
            <Text style={styles.avatarText}>
              {user?.name?.charAt(0).toUpperCase() || 'U'}
            </Text>
          </View>
          <Text style={styles.name}>{user?.name || 'User'}</Text>
          <Text style={styles.email}>{user?.email || ''}</Text>
          <TouchableOpacity
            style={styles.editButton}
            onPress={() => navigation.navigate('EditProfile')}
          >
            <Ionicons name="create-outline" size={16} color="#00f0ff" style={{ marginRight: 6 }} />
            <Text style={styles.editButtonText}>Edit Profile</Text>
          </TouchableOpacity>
        </View>

        {/* Notification Settings */}
        <View style={styles.section}>
          <View style={styles.sectionTitleRow}>
            <Ionicons name="notifications-outline" size={20} color="#00f0ff" />
            <Text style={styles.sectionTitle}>Notification Settings</Text>
          </View>
          <Text style={styles.sectionSubtitle}>
            Get alerts for deadlines and new opportunities
          </Text>

          <View style={styles.settingCard}>
            <View style={styles.settingRow}>
              <View style={styles.settingInfo}>
                <Text style={styles.settingLabel}>Push Notifications</Text>
                <Text style={styles.settingDescription}>
                  Enable notifications for this app
                </Text>
              </View>
              <Switch
                value={notificationsEnabled}
                onValueChange={handleToggleNotifications}
                trackColor={{ false: 'rgba(255, 255, 255, 0.1)', true: 'rgba(0, 240, 255, 0.3)' }}
                thumbColor={notificationsEnabled ? '#00f0ff' : 'rgba(255, 255, 255, 0.3)'}
              />
            </View>

            {notificationsEnabled && (
              <>
                <View style={styles.settingDivider} />
                <View style={styles.settingRow}>
                  <View style={styles.settingInfo}>
                    <Text style={styles.settingLabel}>Deadline Reminders</Text>
                    <Text style={styles.settingDescription}>
                      Get notified 3 days before deadlines
                    </Text>
                  </View>
                  <Switch
                    value={deadlineReminders}
                    onValueChange={setDeadlineReminders}
                    trackColor={{ false: 'rgba(255, 255, 255, 0.1)', true: 'rgba(0, 240, 255, 0.3)' }}
                    thumbColor={deadlineReminders ? '#00f0ff' : 'rgba(255, 255, 255, 0.3)'}
                  />
                </View>

                <View style={styles.settingDivider} />
                <View style={styles.settingRow}>
                  <View style={styles.settingInfo}>
                    <Text style={styles.settingLabel}>New Opportunities</Text>
                    <Text style={styles.settingDescription}>
                      Get notified about new matching opportunities
                    </Text>
                  </View>
                  <Switch
                    value={newOpportunities}
                    onValueChange={setNewOpportunities}
                    trackColor={{ false: 'rgba(255, 255, 255, 0.1)', true: 'rgba(0, 240, 255, 0.3)' }}
                    thumbColor={newOpportunities ? '#00f0ff' : 'rgba(255, 255, 255, 0.3)'}
                  />
                </View>
              </>
            )}
          </View>
        </View>

        {/* Account Info */}
        <View style={styles.section}>
          <View style={styles.sectionTitleRow}>
            <Ionicons name="person-outline" size={20} color="#00f0ff" />
            <Text style={styles.sectionTitle}>Account Information</Text>
          </View>
          
          <View style={styles.infoCard}>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Education Level</Text>
              <Text style={styles.infoValue}>
                {user?.education_level || 'Not specified'}
              </Text>
            </View>
            <View style={styles.infoDivider} />
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Interests</Text>
              <Text style={styles.infoValue}>
                {user?.interests?.join(', ') || 'Not specified'}
              </Text>
            </View>
          </View>
        </View>

        {/* Actions */}
        <View style={styles.section}>
          <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
            <Text style={styles.logoutButtonText}>Logout</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.footer}>
          <Text style={styles.footerText}>HackItAll Mobile v1.0.0</Text>
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
    color: 'rgba(255, 255, 255, 0.5)',
    fontSize: 16,
  },
  header: {
    alignItems: 'center',
    paddingVertical: 40,
    paddingHorizontal: 24,
    backgroundColor: 'rgba(255, 255, 255, 0.03)',
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 255, 255, 0.06)',
  },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: 'rgba(0, 240, 255, 0.2)',
    borderWidth: 2,
    borderColor: '#00f0ff',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  avatarText: {
    fontSize: 32,
    fontWeight: '700',
    color: '#00f0ff',
  },
  name: {
    fontSize: 24,
    fontWeight: '700',
    color: '#ffffff',
    marginBottom: 4,
  },
  email: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.6)',
  },
  editButton: {
    marginTop: 16,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 240, 255, 0.1)',
    borderWidth: 1,
    borderColor: '#00f0ff',
    paddingVertical: 10,
    paddingHorizontal: 24,
    borderRadius: 20,
  },
  editButtonText: {
    color: '#00f0ff',
    fontSize: 14,
    fontWeight: '600',
  },
  section: {
    padding: 24,
  },
  sectionTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 4,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#ffffff',
  },
  sectionSubtitle: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.6)',
    marginBottom: 16,
  },
  settingCard: {
    backgroundColor: 'rgba(255, 255, 255, 0.03)',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.06)',
    borderRadius: 16,
    padding: 16,
  },
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  settingInfo: {
    flex: 1,
    marginRight: 16,
  },
  settingLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
    marginBottom: 4,
  },
  settingDescription: {
    fontSize: 13,
    color: 'rgba(255, 255, 255, 0.6)',
    lineHeight: 18,
  },
  settingDivider: {
    height: 1,
    backgroundColor: 'rgba(255, 255, 255, 0.06)',
    marginVertical: 16,
  },
  infoCard: {
    backgroundColor: 'rgba(255, 255, 255, 0.03)',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.06)',
    borderRadius: 16,
    padding: 16,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  infoLabel: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.6)',
  },
  infoValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#ffffff',
    textAlign: 'right',
    flex: 1,
    marginLeft: 16,
  },
  infoDivider: {
    height: 1,
    backgroundColor: 'rgba(255, 255, 255, 0.06)',
    marginVertical: 12,
  },
  logoutButton: {
    backgroundColor: 'rgba(255, 100, 100, 0.1)',
    borderWidth: 1,
    borderColor: 'rgba(255, 100, 100, 0.3)',
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
  },
  logoutButtonText: {
    color: '#ff6464',
    fontSize: 16,
    fontWeight: '600',
  },
  footer: {
    paddingVertical: 24,
    alignItems: 'center',
  },
  footerText: {
    fontSize: 12,
    color: 'rgba(255, 255, 255, 0.3)',
  },
  guestCard: {
    backgroundColor: 'rgba(255, 255, 255, 0.03)',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.06)',
    borderRadius: 16,
    padding: 24,
    alignItems: 'center',
  },
  guestTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#ffffff',
    marginBottom: 12,
    textAlign: 'center',
  },
  guestMessage: {
    fontSize: 15,
    color: 'rgba(255, 255, 255, 0.7)',
    textAlign: 'center',
    lineHeight: 22,
    marginBottom: 24,
  },
  guestFeatures: {
    width: '100%',
    marginBottom: 24,
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
    paddingHorizontal: 16,
    backgroundColor: 'rgba(0, 240, 255, 0.05)',
    borderRadius: 8,
    marginBottom: 8,
  },
  featureText: {
    fontSize: 15,
    color: '#ffffff',
    fontWeight: '500',
  },
  signupButton: {
    width: '100%',
    backgroundColor: '#00f0ff',
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 12,
  },
  signupButtonText: {
    color: '#050508',
    fontSize: 16,
    fontWeight: '600',
  },
  loginButton: {
    paddingVertical: 10,
  },
  loginButtonText: {
    color: '#00f0ff',
    fontSize: 14,
    fontWeight: '500',
  },
});

