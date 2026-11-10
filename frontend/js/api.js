/**
 * KSRTC Kalaburagi Division - BusPulse Frontend API Client
 * Implements HYBRID MODE:
 * 1. Attempts live async fetch from the Flask REST API at http://127.0.0.1:5000/api/v1
 * 2. Gracefully falls back to local data if the Python server is offline or unreachable.
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
   * POST request for What-If simulator.
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
   * Updates an optional header status pill if present in the UI.
   */
  _updateStatusPill(isOnline) {
    const pill = document.getElementById('backendStatusPill');
    if (!pill) return;
    if (isOnline) {
      pill.innerHTML = '🟢 <span style="color:#059669; font-weight:700;">API Connected</span>';
      pill.title = 'Live Flask Backend Active (http://127.0.0.1:5000)';
    } else {
      pill.innerHTML = '🟡 <span style="color:#D97706; font-weight:700;">Offline Cache</span>';
      pill.title = 'Using local snapshot. Start backend with: python backend/app.py';
    }
  }
};

// Auto-check connectivity when page loads
if (typeof document !== 'undefined') {
  document.addEventListener('DOMContentLoaded', () => {
    BusPulseAPI.checkHealth();
  });
}

