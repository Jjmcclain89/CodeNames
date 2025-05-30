/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'game-red': '#DC2626',
        'game-blue': '#2563EB', 
        'game-neutral': '#6B7280',
        'game-assassin': '#1F2937'
      }
    },
  },
  plugins: [],
}
