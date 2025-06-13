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
  const [minYear, setMinYear] = useState(null);
  const [maxYear, setMaxYear] = useState(null);
  const [sliderRange, setSliderRange] = useState([null, null]);

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
        // Find min and max year
        let years = data.flatMap(s => [s.von_datum?.slice(0,4), s.bis_datum?.slice(0,4)]).filter(Boolean).map(Number);
        let min = Math.min(...years);
        let max = Math.max(...years);
        setMinYear(min);
        setMaxYear(max);
        setSliderRange([min, max]);
      });
  }, []);

  // Filter stations by slider range
  const filteredStations = stations.filter(s => {
    const startYear = Number(s.von_datum?.slice(0,4));
    const endYear = Number(s.bis_datum?.slice(0,4));
    return (
      sliderRange[0] !== null && sliderRange[1] !== null &&
      startYear >= sliderRange[0] && endYear <= sliderRange[1]
    );
  });

  const handleSliderChange = (e, idx) => {
    const value = Number(e.target.value);
    setSliderRange(prev => {
      const next = [...prev];
      next[idx] = value;
      // Ensure min <= max
      if (next[0] > next[1]) {
        if (idx === 0) next[1] = next[0];
        else next[0] = next[1];
      }
      return next;
    });
  };

  return (
    <div style={{ height: '100vh', width: '100vw', position: 'relative' }}>
      {/* Year range input fields */}
      {minYear !== null && maxYear !== null && (
        <div style={{ position: 'absolute', zIndex: 1000, background: 'rgba(255,255,255,0.9)', padding: 12, borderRadius: 8, left: 20, top: 20 }}>
          <div style={{ marginBottom: 8 }}>
            <label>Year range: </label>
            <b>{sliderRange[0]}</b> - <b>{sliderRange[1]}</b>
          </div>
          <div style={{ marginBottom: 8 }}>
            <span>Entries displayed: <b>{filteredStations.length}</b></span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <input
              type="number"
              min={minYear}
              max={maxYear}
              value={sliderRange[0]}
              onChange={e => handleSliderChange({ target: { value: e.target.value } }, 0)}
              style={{ width: 80 }}
            />
            <span>to</span>
            <input
              type="number"
              min={minYear}
              max={maxYear}
              value={sliderRange[1]}
              onChange={e => handleSliderChange({ target: { value: e.target.value } }, 1)}
              style={{ width: 80 }}
            />
          </div>
        </div>
      )}
      <MapContainer center={[51, 10]} zoom={6} style={{ height: '100%', width: '100%' }}>
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution="© OpenStreetMap contributors"
        />
        {filteredStations.map((s, i) => (
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
    </div>
  );
}

export default MapView;