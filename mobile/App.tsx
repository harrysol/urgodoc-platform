import "react-native-gesture-handler";
import "./global.css";

import { DarkTheme, NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { StatusBar } from "expo-status-bar";
import React from "react";
import { GestureHandlerRootView } from "react-native-gesture-handler";
import { SafeAreaProvider } from "react-native-safe-area-context";

import type { RootStackParamList } from "./src/navigation/types";
import { CalibrationScreen } from "./src/screens/CalibrationScreen";
import { HomeScreen } from "./src/screens/HomeScreen";
import { ProcessingScreen } from "./src/screens/ProcessingScreen";
import { TryOnScreen } from "./src/screens/TryOnScreen";

const Stack = createNativeStackNavigator<RootStackParamList>();

const theme = {
  ...DarkTheme,
  colors: { ...DarkTheme.colors, background: "#0B0B12", card: "#15151F", primary: "#7C5CFF" },
};

export default function App() {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <SafeAreaProvider>
        <NavigationContainer theme={theme}>
          <StatusBar style="light" />
          <Stack.Navigator
            screenOptions={{
              headerStyle: { backgroundColor: "#0B0B12" },
              headerTintColor: "#fff",
              contentStyle: { backgroundColor: "#0B0B12" },
            }}
          >
            <Stack.Screen name="Home" component={HomeScreen} options={{ headerShown: false }} />
            <Stack.Screen name="Processing" component={ProcessingScreen} options={{ title: "Generating" }} />
            <Stack.Screen name="TryOn" component={TryOnScreen} options={{ title: "Try-On" }} />
            <Stack.Screen name="Calibration" component={CalibrationScreen} options={{ title: "Calibration" }} />
          </Stack.Navigator>
        </NavigationContainer>
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
}
