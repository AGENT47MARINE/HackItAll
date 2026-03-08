import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Ionicons, MaterialCommunityIcons, Feather } from '@expo/vector-icons';

// Custom icon component with vector icons
export const Icon = ({ name, size = 24, color = '#00f0ff', style, family = 'Ionicons' }) => {
  const IconComponent = family === 'MaterialCommunityIcons' ? MaterialCommunityIcons : 
                        family === 'Feather' ? Feather : Ionicons;
  
  return (
    <View style={[styles.container, style]}>
      <IconComponent name={name} size={size} color={color} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    justifyContent: 'center',
    alignItems: 'center',
  },
});

export default Icon;
