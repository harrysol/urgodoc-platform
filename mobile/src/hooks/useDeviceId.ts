import AsyncStorage from "@react-native-async-storage/async-storage";
import * as Crypto from "expo-crypto";
import { useEffect, useState } from "react";

const STORAGE_KEY = "urgodoc.deviceId";

/**
 * Returns a stable per-install identifier, generating and persisting one on
 * first launch. Used as the `user_id` for storing body dimensions on the
 * backend (no auth system in this MVP).
 */
export function useDeviceId(): string | null {
  const [deviceId, setDeviceId] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      let id = await AsyncStorage.getItem(STORAGE_KEY);
      if (!id) {
        id = Crypto.randomUUID();
        await AsyncStorage.setItem(STORAGE_KEY, id);
      }
      if (!cancelled) setDeviceId(id);
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  return deviceId;
}
