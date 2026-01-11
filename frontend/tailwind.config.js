/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {

      colors: {
        brand: {
          navy: "#213448",
          blue: "#547792",
          sea: "#94B4C1",
          beige: "#EAE0CF",
        },
      },


      boxShadow: {
        soft: "0 10px 30px rgba(0,0,0,0.25)",
      },


      fontFamily: {
         sans: ["var(--font-sans)", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
