/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        nexus: {
          dark: '#070a12',
          card: 'rgba(13, 18, 30, 0.75)',
          border: 'rgba(56, 189, 248, 0.15)',
          cyan: '#06b6d4',
          blue: '#3b82f6',
          purple: '#8b5cf6',
          pink: '#ec4899',
          glow: 'rgba(6, 182, 212, 0.4)',
        }
      },
      fontFamily: {
        sans: ['Space Grotesk', 'Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace']
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 12s linear infinite',
        'glow-pulse': 'glowPulse 2s ease-in-out infinite alternate',
      },
      keyframes: {
        glowPulse: {
          '0%': { boxShadow: '0 0 15px rgba(6, 182, 212, 0.3)' },
          '100%': { boxShadow: '0 0 35px rgba(6, 182, 212, 0.7)' },
        }
      }
    },
  },
  plugins: [],
}
