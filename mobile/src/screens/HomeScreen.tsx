import React, { useState } from "react";
import {
  ActivityIndicator,
  Alert,
  Pressable,
  ScrollView,
  Text,
  TextInput,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { api } from "../api/client";
import type { ScreenProps } from "../navigation/types";

export function HomeScreen({ navigation }: ScreenProps<"Home">) {
  const [url, setUrl] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const onSubmit = async () => {
    const trimmed = url.trim();
    if (!/^https?:\/\//i.test(trimmed)) {
      Alert.alert("Invalid link", "Paste a full product URL starting with http(s)://");
      return;
    }
    try {
      setSubmitting(true);
      const product = await api.submitProduct(trimmed);
      setUrl("");
      navigation.navigate("Processing", { productId: product.id });
    } catch (e) {
      Alert.alert("Couldn't submit", e instanceof Error ? e.message : "Unknown error");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <SafeAreaView className="flex-1 bg-ink">
      <ScrollView contentContainerClassName="p-6 gap-6">
        <View className="mt-6 gap-2">
          <Text className="text-white text-3xl font-bold">UrgoDoc Try-On</Text>
          <Text className="text-muted text-base">
            Paste any fashion product link. We'll build a 3D garment and fit it to
            your avatar.
          </Text>
        </View>

        <View className="gap-3">
          <Text className="text-white text-sm font-semibold">Product URL</Text>
          <TextInput
            value={url}
            onChangeText={setUrl}
            placeholder="https://store.com/products/linen-shirt"
            placeholderTextColor="#5A5A70"
            autoCapitalize="none"
            autoCorrect={false}
            keyboardType="url"
            className="bg-surface text-white rounded-2xl px-4 py-4 text-base"
          />

          <Pressable
            onPress={onSubmit}
            disabled={submitting}
            className="bg-accent active:bg-accentMuted rounded-2xl py-4 items-center flex-row justify-center gap-2"
          >
            {submitting ? <ActivityIndicator color="#fff" /> : null}
            <Text className="text-white text-base font-semibold">
              {submitting ? "Submitting…" : "Generate 3D Try-On"}
            </Text>
          </Pressable>
        </View>

        <Pressable
          onPress={() => navigation.navigate("Calibration")}
          className="border border-accentMuted rounded-2xl py-4 items-center"
        >
          <Text className="text-accent text-base font-semibold">
            Calibrate my body (camera)
          </Text>
        </Pressable>

        <View className="bg-surface rounded-2xl p-4 gap-2">
          <Text className="text-white font-semibold">How it works</Text>
          <Text className="text-muted text-sm">
            1. Paste a retail link — we scrape the page and read the product with a
            Vision LLM.
          </Text>
          <Text className="text-muted text-sm">
            2. We generate a 3D garment (.glb) from the product image.
          </Text>
          <Text className="text-muted text-sm">
            3. Try it on your custom-dimension avatar, calibrated by your camera.
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}
