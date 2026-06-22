/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./App.tsx", "./src/**/*.{js,jsx,ts,tsx}"],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      colors: {
        // Brand palette
        ink: "#0B0B12",
        surface: "#15151F",
        accent: "#7C5CFF",
        accentMuted: "#5C45BF",
        muted: "#8A8AA0",
      },
    },
  },
  plugins: [],
};
