/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'risk-high': '#e11d48',
        'risk-medium': '#f59e0b',
        'risk-safe': '#10b981',
      }
    },
  },
  plugins: [],
}
