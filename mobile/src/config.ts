import Constants from "expo-constants";

/**
 * Base URL of the FastAPI backend (including the /api/v1 prefix).
 *
 * Resolution order:
 *   1. EXPO_PUBLIC_API_URL env var (set in your shell or EAS build profile)
 *   2. expo.extra.apiUrl from app.json
 *   3. localhost fallback
 *
 * On a physical device, localhost won't reach your dev machine — set
 * EXPO_PUBLIC_API_URL to your machine's LAN IP, e.g. http://192.168.1.20:8000/api/v1
 */
export const API_BASE_URL =
  process.env.EXPO_PUBLIC_API_URL ??
  (Constants.expoConfig?.extra?.apiUrl as string | undefined) ??
  "http://localhost:8000/api/v1";

/** How often (ms) the client polls a product job for status updates. */
export const POLL_INTERVAL_MS = 2500;
