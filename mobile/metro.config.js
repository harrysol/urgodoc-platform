const { getDefaultConfig } = require("expo/metro-config");
const { withNativeWind } = require("nativewind/metro");

const config = getDefaultConfig(__dirname);

// Allow Metro to resolve the .glb/.gltf 3D assets bundled with the app, plus the
// usual binary asset types.
config.resolver.assetExts.push("glb", "gltf", "bin");

module.exports = withNativeWind(config, { input: "./global.css" });
