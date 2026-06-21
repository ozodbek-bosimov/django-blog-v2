const http = require('http');
const fs = require('fs');

http.createServer((req, res) => {
  if (req.url === '/') {
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(fs.readFileSync('test_htmx_inline.html'));
  } else if (req.url === '/test') {
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(`
      <script>
        document.getElementById('log').innerHTML += 'Evaluated! <br>';
      </script>
    `);
  } else if (req.url === '/static/js/htmx.min.js') {
    res.writeHead(200, { 'Content-Type': 'application/javascript' });
    res.end(fs.readFileSync('static/js/htmx.min.js'));
  }
}).listen(3002);
console.log("Server listening on 3002");
