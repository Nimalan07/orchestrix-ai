/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#FFFFFF",
        foreground: "#080808",
        black: "#080808",
        grey: {
          50: "#FAFAFA",
          100: "#F5F5F7",
          200: "#EAEAEA",
          300: "#D4D4D8",
          400: "#A1A1AA",
          500: "#71717A",
          600: "#666666",
          700: "#3F3F46",
          800: "#27272A",
          900: "#18181B",
        },
        border: "#EAEAEA",
      },
      fontFamily: {
        serif: ["var(--font-serif)", "Playfair Display", "DM Serif Display", "Georgia", "serif"],
        sans: ["var(--font-sans)", "Inter", "-apple-system", "BlinkMacSystemFont", "sans-serif"],
        mono: ["var(--font-mono)", "JetBrains Mono", "Menlo", "Courier New", "monospace"],
      },
      animation: {
        "marquee": "marquee 35s linear infinite",
      },
      keyframes: {
        marquee: {
          "0%": { transform: "translateX(0%)" },
          "100%": { transform: "translateX(-50%)" },
        },
      },
    },
  },
  plugins: [],
};
