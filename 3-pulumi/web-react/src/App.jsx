import { useState, useEffect } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './App.css';

function App() {
  const [map, setMap] = useState(null);
  const [lat, setLat] = useState('');
  const [lon, setLon] = useState('');
  const [cats, setCats] = useState('');
  const [msg, setMsg] = useState('');
  const [layer, setLayer] = useState(null);

  const API_GET_URL = import.meta.env.VITE_API_GET_URL || '/banheiros';
  const API_POST_URL = import.meta.env.VITE_API_POST_URL || '/banheiros';

  useEffect(() => {
    const mapInstance = L.map('map').setView([-27.59, -48.55], 12);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap',
    }).addTo(mapInstance);

    const layerGroup = L.layerGroup().addTo(mapInstance);
    setMap(mapInstance);
    setLayer(layerGroup);

    mapInstance.on('click', (e) => {
      setLat(e.latlng.lat.toFixed(6));
      setLon(e.latlng.lng.toFixed(6));
    });

    loadBathrooms(layerGroup);

    return () => {
      mapInstance.remove();
    };
  }, []);

  const loadBathrooms = async (layerGroup) => {
    try {
      const res = await fetch(API_GET_URL);
      const items = await res.json();
      layerGroup.clearLayers();
      items.forEach((b) => {
        L.marker([b.latitude, b.longitude])
          .bindPopup((b.categorias || []).join(', ') || 'sem categorias informadas')
          .addTo(layerGroup);
      });
    } catch (e) {
      setMsg(`Erro ao carregar: ${e}`);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const body = {
      latitude: parseFloat(lat),
      longitude: parseFloat(lon),
      categorias: cats.split(',').map((c) => c.trim()).filter(Boolean),
    };

    try {
      const res = await fetch(API_POST_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      if (res.ok) {
        setMsg('Cadastrado!');
        setLat('');
        setLon('');
        setCats('');
        loadBathrooms(layer);
      } else {
        const errorText = await res.text();
        setMsg(`Erro: ${errorText}`);
      }
    } catch (e) {
      setMsg(`Erro: ${e}`);
    }
  };

  return (
    <>
      <div id="map"></div>
      <main>
        <h1>Banheiros familiares</h1>
        <p>Clique no mapa para escolher o local e informe as categorias que quiser.</p>
        <form onSubmit={handleSubmit}>
          <p>
            Latitude{' '}
            <input
              id="lat"
              type="number"
              step="any"
              value={lat}
              onChange={(e) => setLat(e.target.value)}
              required
            />
            Longitude{' '}
            <input
              id="lon"
              type="number"
              step="any"
              value={lon}
              onChange={(e) => setLon(e.target.value)}
              required
            />
          </p>
          <p>
            <label>
              Categorias (separadas por vírgula)
              <input
                id="cats"
                type="text"
                placeholder="ex.: unissex, acessível, fraldário"
                value={cats}
                onChange={(e) => setCats(e.target.value)}
              />
            </label>
          </p>
          <button>Cadastrar</button>
          <div id="msg">{msg}</div>
        </form>
      </main>
    </>
  );
}

export default App;
