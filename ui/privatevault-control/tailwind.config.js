/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        graphite: {
          950: '#050505',
          900: '#0a0a0a',
          800: '#111111',
        },
        accent: {
          blue: '#0ea5e9',
          purple: '#a855f7',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      animation: {
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        'flow': 'flow 4s linear infinite',
        'reconstruct': 'reconstruct 1.5s ease-out forwards',
      },
    },
  },
  plugins: [],
}
