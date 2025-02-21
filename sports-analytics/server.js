const { createServer } = require("https");
const { parse } = require("url");
const next = require("next");
const fs = require("fs");

const dev = process.env.NODE_ENV !== "production";
const app = next({ dev });
const handle = app.getRequestHandler();

const httpsOptions = {
  key: fs.readFileSync(
    "C:/Users/MichaelArena/Desktop/Personal/Football/Django/127.0.0.1.key"
  ), // Adjust if moved
  cert: fs.readFileSync(
    "C:/Users/MichaelArena/Desktop/Personal/Football/Django/127.0.0.1.pem"
  ), // Adjust if moved
};

app.prepare().then(() => {
  createServer(httpsOptions, (req, res) => {
    const parsedUrl = parse(req.url, true);
    handle(req, res, parsedUrl);
  }).listen(3000, (err) => {
    if (err) throw err;
    console.log("> Ready on https://localhost:3000");
  });
});
