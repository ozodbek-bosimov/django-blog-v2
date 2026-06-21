const http = require('http');
const fs = require('fs');

http.createServer((req, res) => {
  if (req.url === '/') {
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(fs.readFileSync('test_htmx_dom.html'));
  } else if (req.url === '/test') {
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(`
      <div id="my-new-div">Hello</div>
      <script>
        const el = document.getElementById("my-new-div");
        console.log("Found element:", !!el);
      </script>
    `);
  } else if (req.url === '/static/js/htmx.min.js') {
    res.writeHead(200, { 'Content-Type': 'application/javascript' });
    res.end(fs.readFileSync('static/js/htmx.min.js'));
  }
}).listen(3001);
console.log("Server listening on 3001");
