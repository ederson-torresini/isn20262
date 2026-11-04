const express = require("express");
const serverless = require("serverless-http");

const app = express();

// URLs das funções GET e POST, injetadas via variáveis de ambiente.
const config = {
  getUrl: process.env.API_GET_URL || "",
  postUrl: process.env.API_POST_URL || "",
};

const page = `<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Banheiros familiares</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>
  body { font-family: sans-serif; margin: 0; }
  #map { height: 60vh; }
  main { padding: 1rem; max-width: 40rem; margin: auto; }
  label { margin-right: 1rem; }
  #msg { margin-top: .5rem; }
</style>
</head>
<body>
<div id="map"></div>
<main>
  <h1>Banheiros familiares</h1>
  <p>Clique no mapa para escolher o local e informe as categorias que quiser.</p>
  <form id="form">
    <p>
      Latitude <input id="lat" type="number" step="any" required>
      Longitude <input id="lon" type="number" step="any" required>
    </p>
    <p>
      <label>Categorias (separadas por vírgula)
        <input id="cats" type="text" placeholder="ex.: unissex, acessível, fraldário"></label>
    </p>
    <button>Cadastrar</button>
    <div id="msg"></div>
  </form>
</main>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const CONFIG = __CONFIG__;
const map = L.map("map").setView([-27.59, -48.55], 12);
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "&copy; OpenStreetMap",
}).addTo(map);
const layer = L.layerGroup().addTo(map);
const msg = document.getElementById("msg");

function label(b) {
  const div = document.createElement("div");
  div.textContent = (b.categorias || []).join(", ") || "sem categorias informadas";
  return div;
}

async function load() {
  layer.clearLayers();
  const res = await fetch(CONFIG.getUrl);
  const items = await res.json();
  items.forEach((b) =>
    L.marker([b.latitude, b.longitude]).bindPopup(label(b)).addTo(layer));
}

map.on("click", (e) => {
  document.getElementById("lat").value = e.latlng.lat.toFixed(6);
  document.getElementById("lon").value = e.latlng.lng.toFixed(6);
});

document.getElementById("form").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const f = ev.target;
  const body = {
    latitude: parseFloat(f.lat.value),
    longitude: parseFloat(f.lon.value),
  };
  body.categorias = f.cats.value.split(",").map((c) => c.trim()).filter(Boolean);
  const res = await fetch(CONFIG.postUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  msg.textContent = res.ok ? "Cadastrado!" : "Erro: " + (await res.text());
  if (res.ok) load();
});

load().catch((e) => (msg.textContent = "Erro ao carregar: " + e));
</script>
</body>
</html>`;

app.get("/", (req, res) => {
  res
    .type("html")
    .send(
      page.replace(
        "__CONFIG__",
        JSON.stringify(config).replace(/</g, "\\u003c"),
      ),
    );
});

module.exports = app;
module.exports.handler = serverless(app);

if (require.main === module) {
  const port = process.env.PORT || 3000;
  app.listen(port, () => console.log(`http://localhost:${port}`));
}
