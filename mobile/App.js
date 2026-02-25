import React, { useEffect, useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { StatusBar } from 'expo-status-bar';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Import screens
import LoginScreen from './src/screens/LoginScreen';
import RegisterScreen from './src/screens/RegisterScreen';
import HomeScreen from './src/screens/HomeScreen';
import OpportunitiesScreen from './src/screens/OpportunitiesScreen';
import OpportunityDetailScreen from './src/screens/OpportunityDetailScreen';
import ProfileScreen from './src/screens/ProfileScreen';
import TrackedScreen from './src/screens/TrackedScreen';

// Import notification setup
import { registerForPushNotificationsAsync, setupNotificationHandlers } from './src/services/notificationService';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={{
        tabBarActiveTintColor: '#007AFF',
        tabBarInactiveTintColor: 'gray',
      }}
    >
      <Tab.Screen 
        name="Home" 
        component={HomeScreen}
        options={{ title: 'Discover' }}
      />
      <Tab.Screen 
        name="Opportunities" 
        component={OpportunitiesScreen}
        options={{ title: 'Search' }}
      />
      <Tab.Screen 
        name="Tracked" 
        component={TrackedScreen}
        options={{ title: 'Saved' }}
      />
      <Tab.Screen 
        name="Profile" 
        component={ProfileScreen}
        options={{ title: 'Profile' }}
      />
    </Tab.Navigator>
  );
}

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
    setupNotifications();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = await AsyncStorage.getItem('authToken');
      setIsAuthenticated(!!token);
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
              <Stack.Screen name="Login" component={LoginScreen} />
              <Stack.Screen name="Register" component={RegisterScreen} />
            </>
          ) : (
            <>
              <Stack.Screen name="MainTabs" component={MainTabs} />
              <Stack.Screen 
                name="OpportunityDetail" 
                component={OpportunityDetailScreen}
                options={{ headerShown: true, title: 'Opportunity Details' }}
              />
            </>
          )}
        </Stack.Navigator>
      </NavigationContainer>
      <StatusBar style="auto" />
    </>
  );
}
