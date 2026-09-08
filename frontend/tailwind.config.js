/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./public/index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        obsidian: '#090d16',
        panel: '#0d1424',
        card: '#131b2e',
        'tactical-border': '#1e293b',
        'brand-emerald': '#10b981',
        'brand-cyan': '#06b6d4',
        'brand-amber': '#f59e0b',
        'brand-rose': '#f43f5e',
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Menlo', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'tactical-glow': '0 0 25px -5px rgba(16, 185, 129, 0.25)',
        'alert-glow': '0 0 25px -5px rgba(244, 63, 94, 0.35)',
        'cyan-glow': '0 0 25px -5px rgba(6, 182, 212, 0.30)',
      },
      animation: {
        'radar-sweep': 'radar-sweep 4s linear infinite',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        'radar-sweep': {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        }
      }
    },
  },
  plugins: [],
}
