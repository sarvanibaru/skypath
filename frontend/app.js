// detects if running in Docker (port 3000) or locally (direct file)
const API = window.location.port === '3000' ? '' : 'http://localhost:4000';

function formatTime(isoString) {
  return isoString.split('T')[1].slice(0, 5);
}

function formatDuration(minutes) {
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return m > 0 ? `${h}h ${m}m` : `${h}h`;
}

function stopsLabel(count) {
  if (count === 0) return 'Direct';
  if (count === 1) return '1 Stop';
  return `${count} Stops`;
}

function stopsBadgeClass(count) {
  if (count === 0) return 'direct';
  if (count === 2) return 'two-stop';
  return '';
}

function showLoading() {
  hide('loading', false);
  hide('api-error', true);
  hide('results-header', true);
  hide('empty-state', true);
  hide('form-error', true);
  document.getElementById('itineraries').innerHTML = '';
}

function hide(id, hidden) {
  document.getElementById(id).classList.toggle('hidden', hidden);
}

function showFormError(msg) {
  const el = document.getElementById('form-error');
  el.textContent = msg;
  el.classList.remove('hidden');
  document.getElementById('itineraries').innerHTML = '';
  hide('results-header', true);
  hide('empty-state', true);
  hide('api-error', true);
}

function showApiError(msg) {
  const el = document.getElementById('api-error');
  el.textContent = msg;
  el.classList.remove('hidden');
  hide('loading', true);
}

function validateInputs(origin, destination, date) {
  if (!origin)      return 'Please enter an origin airport code';
  if (!destination) return 'Please enter a destination airport code';
  if (!date)        return 'Please select a date';
  if (!/^[A-Z]{3}$/.test(origin))
    return `Invalid origin code "${origin}" — must be 3 letters`;
  if (!/^[A-Z]{3}$/.test(destination))
    return `Invalid destination code "${destination}" — must be 3 letters`;
  if (origin === destination)
    return 'Origin and destination cannot be the same';
  return null;
}

function renderCard(itinerary) {
  const { segments, layovers, totalDurationMinutes, totalPrice } = itinerary;
  const stops = segments.length - 1;

  // build timeline rows
  let timelineHTML = '';
  segments.forEach((seg, i) => {
    timelineHTML += `
      <div class="timeline-segment">
        <div class="timeline-dot"></div>
        <div class="seg-times">
          <div class="seg-time-row">
            <span class="seg-time">${formatTime(seg.departureTime)}</span>
            <span class="seg-code">${seg.origin}</span>
          </div>
          <div class="seg-time-row" style="margin-top:4px">
            <span class="seg-time">${formatTime(seg.arrivalTime)}</span>
            <span class="seg-code">${seg.destination}</span>
          </div>
        </div>
        <div class="seg-info">
          <span class="seg-flight-num">${seg.flightNumber}</span>
          <span class="seg-airline">${seg.airline}</span>
        </div>
      </div>
    `;

    if (layovers[i]) {
      timelineHTML += `
        <div class="layover-row">
          ⏱ ${formatDuration(layovers[i].durationMinutes)} layover at ${layovers[i].airport}
        </div>
      `;
    }
  });

  return `
    <div class="itinerary-card">
      <div class="card-header">
        <span class="stops-badge ${stopsBadgeClass(stops)}">
          ${stopsLabel(stops)}
        </span>
        <span class="card-price">$${totalPrice.toFixed(2)}</span>
      </div>

      <div class="timeline">
        ${timelineHTML}
      </div>

      <div class="card-footer">
        <span>⏱ ${formatDuration(totalDurationMinutes)} total</span>
        <span>✈ ${segments.length} flight${segments.length > 1 ? 's' : ''}</span>
        <span>💰 $${(totalPrice / segments.length).toFixed(0)} avg per flight</span>
      </div>
    </div>
  `;
}

async function handleSearch() {
  const origin      = document.getElementById('origin').value.trim().toUpperCase();
  const destination = document.getElementById('destination').value.trim().toUpperCase();
  const date        = document.getElementById('date').value;

  const error = validateInputs(origin, destination, date);
  if (error) { showFormError(error); return; }

  const btn = document.getElementById('search-btn');
  btn.disabled = true;
  showLoading();

  try {
    const res  = await fetch(
      `${API}/api/search?origin=${origin}&destination=${destination}&date=${date}`
    );
    const data = await res.json();

    if (!res.ok) {
      showApiError(`Error: ${data.detail || 'Something went wrong'}`);
      return;
    }

    hide('loading', true);

    if (data.itineraries.length === 0) {
      hide('empty-state', false);
      return;
    }

    hide('results-header', false);
    document.getElementById('results-count').textContent =
      `${data.count} itinerar${data.count === 1 ? 'y' : 'ies'} found for ${origin} → ${destination}`;

    document.getElementById('itineraries').innerHTML =
      data.itineraries.map(renderCard).join('');

  } catch (err) {
    showApiError('Could not connect to the server. Is the backend running?');
  } finally {
    btn.disabled = false;
  }
}

document.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') handleSearch();
});