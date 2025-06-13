import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

function createDateRangeIcon(start, end) {
  const radius = 32;
  const svg = `
    <svg width="${radius*2}" height="${radius*2}" xmlns="http://www.w3.org/2000/svg">
      <circle cx="${radius}" cy="${radius}" r="${radius-2}" fill="#fff" stroke="#333" stroke-width="2" />
      <text x="${radius}" y="${radius-10}" text-anchor="middle" fill="#1976d2" font-size="12" font-family="sans-serif" font-weight="bold">${start}</text>
      <text x="${radius}" y="${radius+6}" text-anchor="middle" fill="#888" font-size="14" font-family="sans-serif">-</text>
      <text x="${radius}" y="${radius+22}" text-anchor="middle" fill="#d32f2f" font-size="12" font-family="sans-serif" font-weight="bold">${end}</text>
    </svg>
  `;
  return L.divIcon({
    className: '',
    html: svg,
    iconSize: [radius*2, radius*2],
    iconAnchor: [radius, radius]
  });
}

function formatDate(yyyymmdd) {
  if (!yyyymmdd || yyyymmdd.length < 8) return yyyymmdd;
  return yyyymmdd.slice(0,4) + '-' + yyyymmdd.slice(4,6) + '-' + yyyymmdd.slice(6,8);
}

function MapView() {
  const [stations, setStations] = useState([]);

  useEffect(() => {
    fetch('/station_date_ranges.csv')
      .then(res => res.text())
      .then(text => {
        const lines = text.split('\n');
        const header = lines[0].split(',');
        const data = lines.slice(1).map(line => {
          const cols = line.split(',');
          if (cols.length < 5) return null;
          return {
            station_id: cols[0],
            von_datum: cols[1],
            bis_datum: cols[2],
            geoBreite: parseFloat(cols[3]),
            geoLaenge: parseFloat(cols[4])
          };
        }).filter(Boolean);
        setStations(data);
      });
  }, []);

  return (
    <MapContainer center={[51, 10]} zoom={6} style={{ height: '100vh', width: '100vw' }}>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution="© OpenStreetMap contributors"
      />
      {stations.map((s, i) => (
        <Marker
          key={i}
          position={[s.geoBreite, s.geoLaenge]}
          icon={createDateRangeIcon(formatDate(s.von_datum), formatDate(s.bis_datum))}
        >
          <Popup>
            <b>Station:</b> {s.station_id}<br/>
            <b>Start:</b> {formatDate(s.von_datum)}<br/>
            <b>End:</b> {formatDate(s.bis_datum)}
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}

export default MapView;