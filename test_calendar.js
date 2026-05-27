const fetch = require('node-fetch');

fetch('https://github-calendar.vercel.app/api?username=ozodbek-bosimov')
  .then(res => res.text())
  .then(text => console.log(text))
  .catch(console.error);
