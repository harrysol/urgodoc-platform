import { useCameraPermissions } from "expo-camera";
import React, { useMemo, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  Pressable,
  Text,
  TextInput,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { WebView, type WebViewMessageEvent } from "react-native-webview";

import { api } from "../api/client";
import type { UserDimensions } from "../api/types";
import { MEDIAPIPE_HTML } from "../calibration/mediapipeHtml";
import { useDeviceId } from "../hooks/useDeviceId";
import type { ScreenProps } from "../navigation/types";

export function CalibrationScreen({ navigation }: ScreenProps<"Calibration">) {
  const deviceId = useDeviceId();
  const [permission, requestPermission] = useCameraPermissions();
  const [height, setHeight] = useState("");
  const [scanning, setScanning] = useState(false);
  const [saving, setSaving] = useState(false);

  const heightNum = Number(height);
  const heightValid = heightNum >= 100 && heightNum <= 230;

  // Inject the user's height so the WebView can scale landmark distances to cm.
  const injectedBeforeLoad = useMemo(
    () => `window.USER_HEIGHT = ${heightValid ? heightNum : 170}; true;`,
    [heightNum, heightValid],
  );

  const startScan = async () => {
    if (!heightValid) {
      Alert.alert("Enter your height", "Height must be between 100 and 230 cm.");
      return;
    }
    if (!permission?.granted) {
      const res = await requestPermission();
      if (!res.granted) {
        Alert.alert("Camera needed", "Camera access is required to measure your body.");
        return;
      }
    }
    setScanning(true);
  };

  const onMessage = async (event: WebViewMessageEvent) => {
    let payload: { type: string; measurements?: UserDimensions; message?: string };
    try {
      payload = JSON.parse(event.nativeEvent.data);
    } catch {
      return;
    }

    if (payload.type === "error") {
      Alert.alert("Calibration error", payload.message ?? "Pose detection failed.");
      return;
    }

    if (payload.type === "result" && payload.measurements && deviceId) {
      try {
        setSaving(true);
        await api.saveDimensions(deviceId, payload.measurements);
        Alert.alert("Saved", "Your avatar is now sized to your measurements.", [
          { text: "OK", onPress: () => navigation.goBack() },
        ]);
      } catch (e) {
        Alert.alert("Save failed", e instanceof Error ? e.message : "Unknown error");
      } finally {
        setSaving(false);
      }
    }
  };

  if (scanning) {
    return (
      <SafeAreaView className="flex-1 bg-ink" edges={["bottom"]}>
        <WebView
          originWhitelist={["*"]}
          source={{ html: MEDIAPIPE_HTML }}
          injectedJavaScriptBeforeContentLoaded={injectedBeforeLoad}
          onMessage={onMessage}
          // Allow inline camera playback without a user gesture.
          allowsInlineMediaPlayback
          mediaPlaybackRequiresUserAction={false}
          mediaCapturePermissionGrantType="grant"
          javaScriptEnabled
          domStorageEnabled
          style={{ flex: 1, backgroundColor: "#0B0B12" }}
        />
        {saving ? (
          <View className="absolute inset-0 items-center justify-center bg-black/60">
            <ActivityIndicator size="large" color="#7C5CFF" />
            <Text className="text-white mt-3">Saving measurements…</Text>
          </View>
        ) : null}
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView className="flex-1 bg-ink">
      <View className="flex-1 p-6 gap-6 justify-center">
        <View className="gap-2">
          <Text className="text-white text-2xl font-bold">Body calibration</Text>
          <Text className="text-muted">
            Enter your height, then stand back so your whole body is visible. We use
            on-device MediaPipe pose tracking — no photos are uploaded.
          </Text>
        </View>

        <View className="gap-2">
          <Text className="text-white text-sm font-semibold">Height (cm)</Text>
          <TextInput
            value={height}
            onChangeText={setHeight}
            placeholder="178"
            placeholderTextColor="#5A5A70"
            keyboardType="number-pad"
            className="bg-surface text-white rounded-2xl px-4 py-4 text-base"
          />
        </View>

        <Pressable
          onPress={startScan}
          className="bg-accent active:bg-accentMuted rounded-2xl py-4 items-center"
        >
          <Text className="text-white font-semibold">Start camera scan</Text>
        </Pressable>

        <Pressable onPress={() => navigation.goBack()} className="items-center py-2">
          <Text className="text-muted">Cancel</Text>
        </Pressable>
      </View>
    </SafeAreaView>
  );
}
