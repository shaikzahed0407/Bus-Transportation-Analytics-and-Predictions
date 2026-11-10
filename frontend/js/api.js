/**
 * KSRTC Kalaburagi Division - BusPulse Frontend API Client
 * Implements HYBRID DYNAMIC MODE:
 * 1. Attempts live async fetch from the Flask REST API at http://127.0.0.1:5000/api/v1
 * 2. Gracefully falls back to local data if the Python server is offline or unreachable.
 * 3. Supports live ETM dataset upload and automatic chart/KPI hydration without breaking any styling.
 */

const API_BASE_URL = 'http://127.0.0.1:5000/api/v1';

const BusPulseAPI = {
  isBackendOnline: null,

  /**
   * Pings the Flask backend health check endpoint.
   */
  async checkHealth() {
    try {
      const res = await fetch(`${API_BASE_URL}/health`, { signal: AbortSignal.timeout(1200) });
      if (res.ok) {
        this.isBackendOnline = true;
        this._updateStatusPill(true);
        const data = await res.json();
        if (data.dataset_date) {
          const badge = document.getElementById('topbarDateBadge');
          if (badge) badge.textContent = `📅 ${data.dataset_date}`;
        }
        return true;
      }
    } catch (e) {
      this.isBackendOnline = false;
      this._updateStatusPill(false);
    }
    return false;
  },

  /**
   * Universal fetch helper with fallback.
   */
  async get(endpoint, fallbackData = null) {
    try {
      const res = await fetch(`${API_BASE_URL}${endpoint}`, { signal: AbortSignal.timeout(2000) });
      if (res.ok) {
        this._updateStatusPill(true);
        return await res.json();
      }
      throw new Error(`HTTP ${res.status}`);
    } catch (err) {
      this._updateStatusPill(false);
      return fallbackData;
    }
  },

  /**
   * POST request for What-If simulator or actions.
   */
  async post(endpoint, body, fallbackData = null) {
    try {
      const res = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
        signal: AbortSignal.timeout(2500)
      });
      if (res.ok) return await res.json();
      throw new Error(`HTTP ${res.status}`);
    } catch (err) {
      return fallbackData;
    }
  },

  /**
   * Upload dataset file (.xlsx, .csv, .json)
   */
  async uploadDataset(file) {
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await fetch(`${API_BASE_URL}/data/upload`, {
        method: 'POST',
        body: formData,
        signal: AbortSignal.timeout(10000)
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || `HTTP ${res.status}`);
      }
      return await res.json();
    } catch (err) {
      throw err;
    }
  },

  /**
   * Dynamically updates the Overview page KPI cards & charts from live API data
   */
  async hydrateOverview() {
    try {
      const kpi = await this.get('/kpi/summary');
      if (kpi) {
        const elSubsidy = document.getElementById('kpi-subsidy');
        if (elSubsidy) elSubsidy.textContent = `₹${Number(kpi.shakti_subsidy_claim).toLocaleString('en-IN')}`;

        const elSubsidySub = document.getElementById('kpi-subsidy-sub');
        if (elSubsidySub) elSubsidySub.textContent = `${kpi.shakti_share_pct}% women free fare (reimbursable)`;

        const elBuses = document.getElementById('kpi-buses');
        if (elBuses) elBuses.textContent = kpi.active_fleet_buses;

        const elPax = document.getElementById('kpi-passengers');
        if (elPax) elPax.textContent = Number(kpi.total_passengers).toLocaleString('en-IN');

        const elTkts = document.getElementById('kpi-tickets');
        if (elTkts) elTkts.textContent = Number(kpi.total_tickets).toLocaleString('en-IN');

        const elCol = document.getElementById('kpi-collected');
        if (elCol) elCol.textContent = `₹${Number(kpi.cash_collected).toLocaleString('en-IN')}`;

        // Update Revenue Pie Chart if present
        if (window.revenuePieInstance) {
          window.revenuePieInstance.data.datasets[0].data = [kpi.cash_collected, kpi.shakti_subsidy_claim];
          window.revenuePieInstance.update();
        }
      }

      const hourlyData = await this.get('/analytics/hourly');
      if (hourlyData && hourlyData.hourly && window.hourlyChartInstance) {
        const hList = hourlyData.hourly;
        window.hourlyChartInstance.data.labels = hList.map(h => h.label);
        window.hourlyChartInstance.data.datasets[0].data = hList.map(h => h.passengers);
        window.hourlyChartInstance.update();
      }
    } catch (e) {
      console.warn('BusPulseAPI overview hydration fallback active:', e);
    }
  },

  /**
   * Updates header status pill.
   */
  _updateStatusPill(isOnline) {
    const pill = document.getElementById('backendStatusPill');
    if (!pill) return;
    if (isOnline) {
      pill.innerHTML = '🟢 <span style="color:#059669; font-weight:700; margin-left:4px;">API Live</span>';
      pill.title = 'Live Flask Analytics Active (http://127.0.0.1:5000)';
    } else {
      pill.innerHTML = '🟡 <span style="color:#D97706; font-weight:700; margin-left:4px;">Offline Snapshot</span>';
      pill.title = 'Using cached snapshot. Start backend with: python backend/app.py';
    }
  },

  /**
   * Setup file upload handlers for the topbar button
   */
  setupUploadHandler() {
    const uploadBtn = document.getElementById('uploadDatasetBtn');
    const fileInput = document.getElementById('datasetFileInput');
    if (!uploadBtn || !fileInput) return;

    uploadBtn.addEventListener('click', () => {
      fileInput.click();
    });

    fileInput.addEventListener('change', async (e) => {
      const file = e.target.files[0];
      if (!file) return;

      if (typeof showToast === 'function') {
        showToast(`Uploading ${file.name} to KSRTC Analytics Engine...`);
      }

      try {
        const result = await this.uploadDataset(file);
        if (typeof showToast === 'function') {
          showToast(`Success: Loaded ${result.records_loaded.toLocaleString()} tickets (${result.total_passengers.toLocaleString()} pax)!`);
        }
        await this.hydrateOverview();
      } catch (err) {
        if (typeof showToast === 'function') {
          showToast(`Upload failed: ${err.message || 'Make sure backend is running'}`);
        }
      } finally {
        fileInput.value = '';
      }
    });
  }
};

// Auto-init on load
if (typeof document !== 'undefined') {
  document.addEventListener('DOMContentLoaded', async () => {
    await BusPulseAPI.checkHealth();
    BusPulseAPI.setupUploadHandler();
  });
}

window.BusPulseAPI = BusPulseAPI;
