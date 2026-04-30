import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: { 950: "#0a0a0b", 900: "#101113", 800: "#16181c", 700: "#1f2227" },
        accent: { DEFAULT: "#6ee7b7", muted: "#34d399" },
      },
    },
  },
  plugins: [],
};
export default config;
