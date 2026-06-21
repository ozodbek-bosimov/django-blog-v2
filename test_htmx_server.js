const http = require('http');
const fs = require('fs');

http.createServer((req, res) => {
  if (req.url === '/') {
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(fs.readFileSync('test_htmx.html'));
  } else if (req.url === '/test') {
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(`
      <script>
        window.MY_VAR = (window.MY_VAR || 0) + 1;
        console.log("Evaluated! MY_VAR=" + window.MY_VAR);
      </script>
      <div>Content</div>
    `);
  } else if (req.url === '/static/js/htmx.min.js') {
    res.writeHead(200, { 'Content-Type': 'application/javascript' });
    res.end(fs.readFileSync('static/js/htmx.min.js'));
  }
}).listen(3000);
console.log("Server listening on 3000");
