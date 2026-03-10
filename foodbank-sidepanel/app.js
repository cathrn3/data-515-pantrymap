/* =====================================================
   PantryMap – Food Bank Side Panel  |  app.js
   ===================================================== */

// ── CONFIG ──────────────────────────────────────────────
const DATA_FILE  = 'data/food_resources.csv';
const MAX_NEARBY = 10;          // how many banks to show when address is entered
const DEFAULT_CENTER = [47.4969, -122.0492]; // King/Pierce County area
const DEFAULT_ZOOM   = 10;

// Simulated ratings (column not in CSV — we generate them once per resource)
const ratingCache = {};
function getRating(id) {
  if (!ratingCache[id]) {
    // Seeded pseudo-random so results stay stable across re-renders
    const seed = id.split('').reduce((a, c) => a + c.charCodeAt(0), 0);
    ratingCache[id] = +(3 + ((seed * 9301 + 49297) % 233280) / 233280 * 2).toFixed(1);
  }
  return ratingCache[id];
}

// ── STATE ────────────────────────────────────────────────
let allFoodBanks  = [];     // full dataset
let displayedBanks = [];    // currently visible in panel
let map, markersLayer;
let activeCardId  = null;
let markerMap     = {};     // id → leaflet marker

// ── DOM REFS ──────────────────────────────────────────────
const addressInput = document.getElementById('addressInput');
const searchBtn    = document.getElementById('searchBtn');
const clearBtn     = document.getElementById('clearBtn');
const cardList     = document.getElementById('cardList');
const resultCount  = document.getElementById('resultCount');
const sortSelect   = document.getElementById('sortSelect');
const mapLoader    = document.getElementById('mapLoader');

// ── INIT ─────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initMap();
  loadData();

  searchBtn.addEventListener('click', handleSearch);
  addressInput.addEventListener('keydown', e => { if (e.key === 'Enter') handleSearch(); });
  addressInput.addEventListener('input',   () => { clearBtn.hidden = !addressInput.value.trim(); });
  clearBtn.addEventListener('click',       handleClear);
  sortSelect.addEventListener('change',    () => renderCards(displayedBanks));
});

// ── MAP SETUP ─────────────────────────────────────────────
function initMap() {
  map = L.map('map', { zoomControl: false }).setView(DEFAULT_CENTER, DEFAULT_ZOOM);

  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://carto.com/">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 19
  }).addTo(map);

  L.control.zoom({ position: 'bottomright' }).addTo(map);

  markersLayer = L.layerGroup().addTo(map);
}

// ── DATA LOADING ──────────────────────────────────────────
function loadData() {
  Papa.parse(DATA_FILE, {
    download: true,
    header: true,
    skipEmptyLines: true,
    complete: results => {
      allFoodBanks = results.data
        .filter(r => r.Latitude && r.Longitude && !isNaN(parseFloat(r.Latitude)))
        .map((r, i) => ({
          id:        `fb-${i}`,
          type:      (r['Food Resource Type'] || '').toLowerCase().trim(),
          agency:    r['Agency']            || 'Unknown Agency',
          location:  r['Location']          || '',
          status:    (r['Operational Status'] || '').toLowerCase().trim(),
          serves:    r['Who They Serve']    || '',
          address:   r['Address']           || '',
          lat:       parseFloat(r['Latitude']),
          lng:       parseFloat(r['Longitude']),
          phone:     r['Phone Number']      || '',
          website:   r['Website']           || '',
          hours:     r['Days/Hours']        || '',
          updated:   r['Date Updated']      || '',
          rating:    getRating(`fb-${i}-${r['Location']}`),
          distance:  null
        }));

      displayedBanks = [...allFoodBanks];
      renderCards(displayedBanks);
      placeMarkers(displayedBanks, null);
      mapLoader.classList.add('hidden');
    },
    error: err => {
      mapLoader.innerHTML = `<p style="color:#ef4444">⚠️ Could not load data.<br><small>${err.message}</small></p>`;
    }
  });
}

// ── SEARCH ───────────────────────────────────────────────
async function handleSearch() {
  const query = addressInput.value.trim();
  if (!query) {
    handleClear();
    return;
  }

  resultCount.textContent = 'Searching…';
  searchBtn.disabled = true;

  try {
    const coords = await geocodeAddress(query);
    if (!coords) {
      resultCount.textContent = 'Address not found. Showing all.';
      displayedBanks = [...allFoodBanks];
      renderCards(displayedBanks);
      placeMarkers(displayedBanks, null);
      return;
    }

    // Haversine distance for each bank
    const withDist = allFoodBanks.map(b => ({
      ...b,
      distance: haversine(coords.lat, coords.lng, b.lat, b.lng)
    }));

    // Sort by distance, take nearest MAX_NEARBY
    withDist.sort((a, b) => a.distance - b.distance);
    displayedBanks = withDist.slice(0, MAX_NEARBY);

    renderCards(displayedBanks);
    placeMarkers(displayedBanks, coords);

    // Add a "you are here" marker
    addUserMarker(coords, query);

    // Fit map to all shown markers
    const bounds = displayedBanks.map(b => [b.lat, b.lng]);
    bounds.push([coords.lat, coords.lng]);
    map.fitBounds(bounds, { padding: [50, 50] });

  } catch (e) {
    resultCount.textContent = 'Search error. Try again.';
  } finally {
    searchBtn.disabled = false;
  }
}

function handleClear() {
  addressInput.value = '';
  clearBtn.hidden = true;
  displayedBanks = [...allFoodBanks];
  allFoodBanks.forEach(b => b.distance = null);
  renderCards(displayedBanks);
  placeMarkers(displayedBanks, null);
  map.setView(DEFAULT_CENTER, DEFAULT_ZOOM);
  sortSelect.value = 'distance';
}

// ── GEOCODING via Nominatim ───────────────────────────────
async function geocodeAddress(query) {
  const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&limit=1`;
  const res  = await fetch(url, { headers: { 'Accept-Language': 'en' } });
  const data = await res.json();
  if (!data.length) return null;
  return { lat: parseFloat(data[0].lat), lng: parseFloat(data[0].lon) };
}

// ── HAVERSINE ─────────────────────────────────────────────
function haversine(lat1, lon1, lat2, lon2) {
  const R = 3958.8; // miles
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a = Math.sin(dLat/2)**2 + Math.cos(toRad(lat1))*Math.cos(toRad(lat2))*Math.sin(dLon/2)**2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
}
const toRad = d => d * Math.PI / 180;

// ── RENDER CARDS ─────────────────────────────────────────
function renderCards(banks) {
  // Apply sort
  const sortedBanks = [...banks];
  const mode = sortSelect.value;
  if (mode === 'name')     sortedBanks.sort((a,b) => a.agency.localeCompare(b.agency));
  if (mode === 'rating')   sortedBanks.sort((a,b) => b.rating - a.rating);
  if (mode === 'distance') sortedBanks.sort((a,b) => {
    if (a.distance === null && b.distance === null) return 0;
    if (a.distance === null) return 1;
    if (b.distance === null) return -1;
    return a.distance - b.distance;
  });

  // Count label
  const isFiltered = allFoodBanks.some(b => b.distance !== null);
  resultCount.textContent = isFiltered
    ? `${sortedBanks.length} nearest food bank${sortedBanks.length !== 1 ? 's' : ''}`
    : `${sortedBanks.length} food bank${sortedBanks.length !== 1 ? 's' : ''} in the area`;

  if (!sortedBanks.length) {
    cardList.innerHTML = `
      <div class="no-results">
        <div class="no-results-icon">🔍</div>
        <h3>No food banks found</h3>
        <p>Try a different address or clear the search to see all locations.</p>
      </div>`;
    return;
  }

  cardList.innerHTML = sortedBanks.map(b => buildCard(b)).join('');

  // Attach click listeners
  sortedBanks.forEach(b => {
    document.getElementById(`card-${b.id}`)
      .addEventListener('click', () => focusBank(b));
  });
}

function buildCard(b) {
  const badgeCls   = b.type.includes('food bank') && b.type.includes('meal') ? 'badge-both'
                   : b.type.includes('food bank') ? 'badge-foodbank'
                   : 'badge-meal';
  const badgeLabel = b.type.includes('food bank') && b.type.includes('meal') ? 'Food Bank + Meal'
                   : b.type.includes('food bank') ? 'Food Bank'
                   : 'Meal Program';

  const stars = buildStars(b.rating);
  const distHtml = b.distance !== null
    ? `<span class="distance-chip">📍 ${b.distance.toFixed(1)} mi</span>` : '';

  const statusHtml = b.status === 'open'
    ? '<span class="status-pill open">Open</span>'
    : '<span class="status-pill closed">Closed</span>';

  const phone = b.phone
    ? `<div class="card-row"><span class="row-icon">📞</span><span>${b.phone}</span></div>` : '';
  const hours = b.hours
    ? `<div class="card-row"><span class="row-icon">🕐</span><span>${b.hours}</span></div>` : '';
  const address = b.address
    ? `<div class="card-row"><span class="row-icon">📍</span><span>${b.address}</span></div>` : '';

  return `
    <div class="fb-card ${activeCardId === b.id ? 'active' : ''}" id="card-${b.id}" data-id="${b.id}">
      <div class="card-header">
        <div class="card-name">${b.location || b.agency}</div>
        <span class="card-badge ${badgeCls}">${badgeLabel}</span>
      </div>
      <div class="card-row">
        <div class="rating-stars">${stars}</div>
        <span class="rating-num">${b.rating.toFixed(1)}</span>
        ${distHtml}
      </div>
      <div class="card-row">${statusHtml}</div>
      ${phone}
      ${hours}
      ${address}
    </div>`;
}

function buildStars(rating) {
  let html = '';
  for (let i = 1; i <= 5; i++) {
    if (rating >= i)        html += '<span class="star filled">★</span>';
    else if (rating > i-1)  html += '<span class="star half">★</span>';
    else                    html += '<span class="star">★</span>';
  }
  return html;
}

// ── FOCUS / PAN TO BANK ───────────────────────────────────
function focusBank(b) {
  activeCardId = b.id;

  // Update active card style
  document.querySelectorAll('.fb-card').forEach(el => el.classList.remove('active'));
  const card = document.getElementById(`card-${b.id}`);
  if (card) {
    card.classList.add('active');
    card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  // Pan map
  map.setView([b.lat, b.lng], 14, { animate: true });

  // Open popup
  const m = markerMap[b.id];
  if (m) m.openPopup();
}

// ── MARKERS ───────────────────────────────────────────────
function placeMarkers(banks, userCoords) {
  markersLayer.clearLayers();
  markerMap = {};

  // Remove old user marker if any
  if (window._userMarker) { window._userMarker.remove(); window._userMarker = null; }

  banks.forEach(b => {
    const color = b.type.includes('food bank') && b.type.includes('meal') ? '#f59e0b'
                : b.type.includes('food bank') ? '#3b82f6'
                : '#22c55e';

    const icon = L.divIcon({
      className: '',
      html: `<div style="
        width:30px;height:30px;border-radius:50% 50% 50% 0;transform:rotate(-45deg);
        background:${color};border:2px solid rgba(255,255,255,0.3);
        box-shadow:0 4px 12px rgba(0,0,0,0.4);
        display:flex;align-items:center;justify-content:center;
      "><div style="transform:rotate(45deg);font-size:13px;">${b.type.includes('meal') && !b.type.includes('food bank') ? '🍽️' : '🥫'}</div></div>`,
      iconSize:   [30, 30],
      iconAnchor: [15, 30],
      popupAnchor:[0, -32]
    });

    const marker = L.marker([b.lat, b.lng], { icon })
      .bindPopup(buildPopup(b), { maxWidth: 280 });

    marker.on('click', () => {
      activeCardId = b.id;
      document.querySelectorAll('.fb-card').forEach(el => el.classList.remove('active'));
      const card = document.getElementById(`card-${b.id}`);
      if (card) { card.classList.add('active'); card.scrollIntoView({ behavior: 'smooth', block: 'nearest' }); }
    });

    markersLayer.addLayer(marker);
    markerMap[b.id] = marker;
  });
}

function addUserMarker(coords, label) {
  if (window._userMarker) window._userMarker.remove();
  const icon = L.divIcon({
    className: '',
    html: `<div style="
      width:20px;height:20px;border-radius:50%;
      background:#ef4444;border:3px solid #fff;
      box-shadow:0 0 0 4px rgba(239,68,68,0.3),0 4px 12px rgba(0,0,0,0.4);
    "></div>`,
    iconSize:   [20, 20],
    iconAnchor: [10, 10]
  });
  window._userMarker = L.marker([coords.lat, coords.lng], { icon })
    .bindPopup(`<div style="font-family:Inter,sans-serif;font-size:12px;"><b>📍 Your location</b><br><small>${label}</small></div>`)
    .addTo(map);
}

function buildPopup(b) {
  const phone   = b.phone   ? `<div class="popup-row"><span>📞</span><span>${b.phone}</span></div>` : '';
  const hours   = b.hours   ? `<div class="popup-row"><span>🕐</span><span>${b.hours}</span></div>` : '';
  const stars   = buildStars(b.rating);
  const distTxt = b.distance !== null ? ` · ${b.distance.toFixed(1)} mi away` : '';
  const website = b.website ? `<div class="popup-row"><span>🌐</span><a href="${b.website}" target="_blank" rel="noreferrer">Visit website</a></div>` : '';

  return `
    <div style="font-family:'Inter',sans-serif;">
      <div class="popup-name">${b.location || b.agency}</div>
      <div class="popup-row" style="margin-bottom:4px;">
        <span style="display:flex;gap:2px;">${stars}</span>
        <span style="color:#8b949e;font-size:11px;">${b.rating.toFixed(1)}${distTxt}</span>
      </div>
      ${phone}
      ${hours}
      ${website}
    </div>`;
}
