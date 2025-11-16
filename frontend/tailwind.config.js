/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#4299e1',
          dark: '#3182ce',
        },
        secondary: '#48bb78',
        danger: '#fc8181',
        warning: '#ed8936',
      },
      borderWidth: {
        '3': '3px',
      },
      keyframes: {
        'slide-up': {
          from: { transform: 'translateY(100px)', opacity: '0' },
          to: { transform: 'translateY(0)', opacity: '1' },
        },
        typing: {
          '0%, 60%, 100%': { opacity: '0.3', transform: 'translateY(0)' },
          '30%': { opacity: '1', transform: 'translateY(-8px)' },
        },
        'slide-in': {
          from: { opacity: '0', transform: 'translateY(10px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: {
        'slide-up': 'slide-up 0.3s ease',
        'typing': 'typing 1.4s infinite',
        'slide-in': 'slide-in 0.3s ease',
      },
    },
  },
  plugins: [],
}
