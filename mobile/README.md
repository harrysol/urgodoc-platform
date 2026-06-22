# UrgoDoc — Mobile (Expo / React Native)

Cross-platform client for the Fashion 3D Try-On platform. Built with **Expo +
TypeScript**, **NativeWind** (Tailwind), **Three.js via `@react-three/fiber` +
`expo-gl`** for 3D rendering, and **MediaPipe Pose** (in a WebView) for on-device
body calibration.

## Flow

```
Home ──paste link──▶ Processing ──poll──▶ TryOn (3D avatar + garment)
  │
  └── Calibration (camera + MediaPipe) ──▶ saves body dimensions
```

| Screen        | Purpose                                                          |
| ------------- | --------------------------------------------------------------- |
| Home          | Paste a retail URL, submit it, or open calibration              |
| Processing    | Polls the backend job, shows live pipeline progress             |
| TryOn         | Renders the generated `.glb` on a parametric, user-sized avatar |
| Calibration   | Front-camera MediaPipe pose scan → body measurements            |

## Project layout

```
mobile/
├── App.tsx                       # navigation + providers
├── src/
│   ├── config.ts                 # API base URL (EXPO_PUBLIC_API_URL)
│   ├── api/{client,types}.ts     # typed backend client
│   ├── hooks/                    # useDeviceId, useProductPolling
│   ├── navigation/types.ts       # stack param list
│   ├── screens/                  # Home / Processing / TryOn / Calibration
│   ├── three/                    # Avatar3D, AvatarMesh, GarmentModel, scaling
│   └── calibration/mediapipeHtml.ts  # MediaPipe Pose WebView page
├── app.json  babel.config.js  metro.config.js  tailwind.config.js  global.css
└── package.json
```

## Setup

```bash
cd mobile
npm install
npx expo start
```

Then scan the QR with **Expo Go**, or run `npm run ios` / `npm run android`.

### Point the app at your backend

`localhost` from a phone won't reach your dev machine. Set the API URL to your
machine's LAN IP (and make sure the FastAPI backend is running):

```bash
EXPO_PUBLIC_API_URL="http://192.168.1.20:8000/api/v1" npx expo start
```

Or edit `expo.extra.apiUrl` in `app.json`.

## Notes / caveats

- **3D rendering** uses `@react-three/fiber/native` + `expo-gl`. The garment GLB
  is loaded straight from the Tripo3D-hosted `model_url` returned by the backend
  and auto-fitted to the avatar's torso. Drag to rotate; it auto-spins when idle.
- **Avatar** is a parametric humanoid scaled to the user's saved measurements
  (sensible adult defaults until they calibrate).
- **Calibration** runs MediaPipe Tasks Vision (PoseLandmarker) inside a WebView
  against the front camera; measurements are derived from landmark distances
  using the entered height as the real-world scale, then `PUT` to the backend.
  Raw frames never leave the device.
- **Camera permissions:** declared in `app.json`. The WebView's `getUserMedia`
  is granted via `mediaCapturePermissionGrantType="grant"` (iOS). On some Android
  setups WebView camera access needs a development build rather than Expo Go.
- Run `npm run typecheck` to type-check without building.
```
