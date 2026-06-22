import React, { useEffect, useState } from "react";
import { Linking, Pressable, ScrollView, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { ApiError, api } from "../api/client";
import type { UserDimensions } from "../api/types";
import { useDeviceId } from "../hooks/useDeviceId";
import type { ScreenProps } from "../navigation/types";
import { Avatar3D } from "../three/Avatar3D";

export function TryOnScreen({ route, navigation }: ScreenProps<"TryOn">) {
  const { product } = route.params;
  const deviceId = useDeviceId();
  const [dimensions, setDimensions] = useState<UserDimensions | null>(null);
  const [hasProfile, setHasProfile] = useState<boolean | null>(null);

  // Load the user's saved measurements (if calibrated) to size the avatar.
  useEffect(() => {
    if (!deviceId) return;
    let cancelled = false;
    (async () => {
      try {
        const profile = await api.getDimensions(deviceId);
        if (!cancelled) {
          setDimensions(profile);
          setHasProfile(true);
        }
      } catch (e) {
        if (cancelled) return;
        if (e instanceof ApiError && e.status === 404) setHasProfile(false);
        else setHasProfile(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [deviceId]);

  const data = product.extracted_data;
  const priceLabel =
    data?.price != null ? `${data.currency ?? ""}${data.price}`.trim() : null;

  return (
    <SafeAreaView className="flex-1 bg-ink" edges={["bottom"]}>
      <View className="flex-1">
        {/* 3D viewport */}
        <View className="h-[58%] bg-ink">
          <Avatar3D modelUrl={product.model_url} dimensions={dimensions} />
        </View>

        {/* Details sheet */}
        <ScrollView className="flex-1 bg-surface" contentContainerClassName="p-5 gap-3">
          <Text className="text-white text-xl font-bold">
            {data?.title ?? "Generated garment"}
          </Text>

          <View className="flex-row flex-wrap gap-2">
            {data?.brand ? <Chip text={data.brand} /> : null}
            {data?.category ? <Chip text={data.category} /> : null}
            {priceLabel ? <Chip text={priceLabel} /> : null}
            {data?.primary_color ? <Chip text={data.primary_color} /> : null}
            {data?.material ? <Chip text={data.material} /> : null}
          </View>

          {hasProfile === false ? (
            <Pressable
              onPress={() => navigation.navigate("Calibration")}
              className="bg-ink border border-accentMuted rounded-xl p-3 mt-1"
            >
              <Text className="text-accent text-center text-sm font-semibold">
                Using a default body — calibrate for a true fit
              </Text>
            </Pressable>
          ) : null}

          {data?.estimated_dimensions_cm ? (
            <View className="bg-ink rounded-xl p-4 gap-1 mt-1">
              <Text className="text-white font-semibold mb-1">
                Estimated garment dimensions
              </Text>
              <DimRow label="Chest width" value={data.estimated_dimensions_cm.chest_width_cm} />
              <DimRow label="Length" value={data.estimated_dimensions_cm.garment_length_cm} />
              <DimRow label="Shoulder" value={data.estimated_dimensions_cm.shoulder_width_cm} />
              <DimRow label="Sleeve" value={data.estimated_dimensions_cm.sleeve_length_cm} />
            </View>
          ) : null}

          <Pressable
            onPress={() =>
              Linking.openURL(product.affiliate_url ?? product.source_url)
            }
            className="bg-accent rounded-2xl py-4 items-center mt-2"
          >
            <Text className="text-white font-semibold">Shop this item</Text>
          </Pressable>

          <Pressable onPress={() => navigation.popToTop()} className="py-3 items-center">
            <Text className="text-muted">Try another link</Text>
          </Pressable>
        </ScrollView>
      </View>
    </SafeAreaView>
  );
}

function Chip({ text }: { text: string }) {
  return (
    <View className="bg-ink rounded-full px-3 py-1">
      <Text className="text-muted text-xs capitalize">{text}</Text>
    </View>
  );
}

function DimRow({ label, value }: { label: string; value: number | null }) {
  if (value == null) return null;
  return (
    <View className="flex-row justify-between">
      <Text className="text-muted text-sm">{label}</Text>
      <Text className="text-white text-sm">{value} cm</Text>
    </View>
  );
}
