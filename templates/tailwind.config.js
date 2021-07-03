  // tailwind.config.js
  module.exports = {
   purge: {
    enabled: true,
    content: [
      './templates/**/*.html',
      './templates/**/*.j2',
    ]
    },
    darkMode: false, // or 'media' or 'class'
    theme: {
      extend: {},
    },
    variants: {},
    plugins: [],
  }