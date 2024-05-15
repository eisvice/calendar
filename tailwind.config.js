/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./mnts/templates/mnts/*.html", "./mnts/static/*.html", "./mnts/templates/registration/*.html"],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}

