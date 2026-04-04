/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'bracci-offwhite': '#FAFAFA',
        'bracci-black': '#1A1A1A',
        'bracci-gold': '#C5A059',
        'bracci-gold-hover': '#B38D46',
        'bracci-gray': '#F1F1F1',
      },
      letterSpacing: {
        'luxury': '0.15em',
        'tight-luxury': '0.05em',
      },
      fontFamily: {
        'sans': ['Inter', 'system-ui', 'sans-serif'],
      },
      borderWidth: {
        'thin': '0.5px',
      }
    },
  },
  plugins: [],
}
