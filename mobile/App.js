import React, { useEffect, useState } from 'react';
import { Text } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { StatusBar } from 'expo-status-bar';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';

// Import screens
import WelcomeScreen from './src/screens/WelcomeScreen';
import LoginScreen from './src/screens/LoginScreen';
import RegisterScreen from './src/screens/RegisterScreen';
import OnboardingScreen from './src/screens/OnboardingScreen';
import HomeScreen from './src/screens/HomeScreen';
import OpportunitiesScreen from './src/screens/OpportunitiesScreen';
import OpportunityDetailScreen from './src/screens/OpportunityDetailScreen';
import ProfileScreen from './src/screens/ProfileScreen';
import EditProfileScreen from './src/screens/EditProfileScreen';
import TrackedScreen from './src/screens/TrackedScreen';
import LeaguesScreen from './src/screens/LeaguesScreen';

// Import notification setup
import { registerForPushNotificationsAsync, setupNotificationHandlers } from './src/services/notificationService';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarActiveTintColor: '#00f0ff',
        tabBarInactiveTintColor: 'rgba(255, 255, 255, 0.5)',
        tabBarStyle: {
          backgroundColor: '#0a0a12',
          borderTopColor: 'rgba(0, 240, 255, 0.2)',
          borderTopWidth: 1,
          height: 60,
          paddingBottom: 8,
          paddingTop: 8,
        },
        tabBarLabelStyle: {
          fontSize: 11,
          fontWeight: '600',
        },
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;

          if (route.name === 'Home') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === 'Opportunities') {
            iconName = focused ? 'search' : 'search-outline';
          } else if (route.name === 'Tracked') {
            iconName = focused ? 'bookmark' : 'bookmark-outline';
          } else if (route.name === 'Leagues') {
            iconName = focused ? 'trophy' : 'trophy-outline';
          } else if (route.name === 'Profile') {
            iconName = focused ? 'person' : 'person-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
      })}
    >
      <Tab.Screen 
        name="Home" 
        component={HomeScreen}
        options={{ 
          title: 'Discover',
          headerShown: false,
        }}
      />
      <Tab.Screen 
        name="Opportunities" 
        component={OpportunitiesScreen}
        options={{ 
          title: 'Search',
          headerShown: false,
        }}
      />
      <Tab.Screen 
        name="Tracked" 
        component={TrackedScreen}
        options={{ 
          title: 'Saved',
          headerShown: false,
        }}
      />
      <Tab.Screen 
        name="Leagues" 
        component={LeaguesScreen}
        options={{ 
          title: 'Leagues',
          headerShown: false,
        }}
      />
      <Tab.Screen 
        name="Profile" 
        component={ProfileScreen}
        options={{ 
          title: 'Profile',
          headerShown: false,
        }}
      />
    </Tab.Navigator>
  );
}

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [needsOnboarding, setNeedsOnboarding] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
    setupNotifications();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = await AsyncStorage.getItem('authToken');
      const onboardingComplete = await AsyncStorage.getItem('onboardingComplete');
      
      setIsAuthenticated(!!token);
      setNeedsOnboarding(!!token && !onboardingComplete);
    } catch (error) {
      console.error('Error checking auth status:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const setupNotifications = async () => {
    try {
      await registerForPushNotificationsAsync();
      setupNotificationHandlers();
    } catch (error) {
      console.error('Error setting up notifications:', error);
    }
  };

  if (isLoading) {
    return null; // Or a loading screen
  }

  return (
    <>
      <NavigationContainer>
        <Stack.Navigator screenOptions={{ headerShown: false }}>
          {!isAuthenticated ? (
            <>
              <Stack.Screen name="Welcome" component={WelcomeScreen} />
              <Stack.Screen name="Login" component={LoginScreen} />
              <Stack.Screen name="Register" component={RegisterScreen} />
              <Stack.Screen name="MainTabs" component={MainTabs} />
              <Stack.Screen 
                name="OpportunityDetail" 
                component={OpportunityDetailScreen}
                options={{ headerShown: true, title: 'Opportunity Details' }}
              />
            </>
          ) : needsOnboarding ? (
            <>
              <Stack.Screen name="Onboarding" component={OnboardingScreen} />
              <Stack.Screen name="MainTabs" component={MainTabs} />
              <Stack.Screen 
                name="OpportunityDetail" 
                component={OpportunityDetailScreen}
                options={{ headerShown: true, title: 'Opportunity Details' }}
              />
              <Stack.Screen 
                name="EditProfile" 
                component={EditProfileScreen}
                options={{ headerShown: true, title: 'Edit Profile' }}
              />
            </>
          ) : (
            <>
              <Stack.Screen name="MainTabs" component={MainTabs} />
              <Stack.Screen 
                name="OpportunityDetail" 
                component={OpportunityDetailScreen}
                options={{ headerShown: true, title: 'Opportunity Details' }}
              />
              <Stack.Screen 
                name="EditProfile" 
                component={EditProfileScreen}
                options={{ headerShown: true, title: 'Edit Profile' }}
              />
            </>
          )}
        </Stack.Navigator>
      </NavigationContainer>
      <StatusBar style="light" />
    </>
  );
}
