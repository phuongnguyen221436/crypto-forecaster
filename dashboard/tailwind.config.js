/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          primary: '#00c805',
          accent: '#1d1f23',
        },
      },
    },
  },
  plugins: [],
};
