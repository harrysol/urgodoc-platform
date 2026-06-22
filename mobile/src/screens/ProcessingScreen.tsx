import React, { useEffect } from "react";
import { ActivityIndicator, Pressable, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import type { TaskStatus } from "../api/types";
import { useProductPolling } from "../hooks/useProductPolling";
import type { ScreenProps } from "../navigation/types";

const STEP_LABELS: Record<TaskStatus, string> = {
  PENDING: "Queued…",
  SCRAPING: "Capturing the product page…",
  EXTRACTING: "Reading product details with AI…",
  GENERATING_3D: "Sculpting the 3D garment…",
  COMPLETED: "Done!",
  FAILED: "Something went wrong",
};

const ORDER: TaskStatus[] = ["PENDING", "SCRAPING", "EXTRACTING", "GENERATING_3D", "COMPLETED"];

export function ProcessingScreen({ route, navigation }: ScreenProps<"Processing">) {
  const { productId } = route.params;
  const { product, error } = useProductPolling(productId);

  // Auto-advance to the try-on view when the model is ready.
  useEffect(() => {
    if (product?.status === "COMPLETED") {
      navigation.replace("TryOn", { product });
    }
  }, [product, navigation]);

  const status = product?.status ?? "PENDING";
  const currentIndex = ORDER.indexOf(status);
  const isFailed = status === "FAILED";

  return (
    <SafeAreaView className="flex-1 bg-ink">
      <View className="flex-1 p-6 justify-center gap-8">
        <View className="items-center gap-4">
          {!isFailed ? <ActivityIndicator size="large" color="#7C5CFF" /> : null}
          <Text className="text-white text-2xl font-bold text-center">
            {STEP_LABELS[status]}
          </Text>
          {product?.status_detail ? (
            <Text className="text-muted text-center">{product.status_detail}</Text>
          ) : null}
          {status === "GENERATING_3D" && product?.progress ? (
            <Text className="text-accent text-lg font-semibold">{product.progress}%</Text>
          ) : null}
        </View>

        {!isFailed ? (
          <View className="gap-3">
            {ORDER.slice(0, 4).map((step, i) => {
              const done = i < currentIndex;
              const active = i === currentIndex;
              return (
                <View key={step} className="flex-row items-center gap-3">
                  <View
                    className={`w-3 h-3 rounded-full ${
                      done ? "bg-accent" : active ? "bg-accent" : "bg-surface"
                    }`}
                  />
                  <Text
                    className={`text-base ${
                      done || active ? "text-white" : "text-muted"
                    }`}
                  >
                    {STEP_LABELS[step]}
                  </Text>
                </View>
              );
            })}
          </View>
        ) : null}

        {isFailed || error ? (
          <View className="gap-4">
            {product?.error_message ? (
              <Text className="text-red-400 text-center">{product.error_message}</Text>
            ) : null}
            {error ? <Text className="text-muted text-center text-xs">{error}</Text> : null}
            <Pressable
              onPress={() => navigation.popToTop()}
              className="bg-accent rounded-2xl py-4 items-center"
            >
              <Text className="text-white font-semibold">Try another link</Text>
            </Pressable>
          </View>
        ) : null}
      </View>
    </SafeAreaView>
  );
}
