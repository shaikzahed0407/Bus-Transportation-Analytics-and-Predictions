// settings.js – Handles Merge/Replace Dataset, Backups, History and Live Status

document.addEventListener('DOMContentLoaded', () => {
  const mergeBtn = document.getElementById('mergeDatasetBtn');
  const replaceBtn = document.getElementById('replaceDatasetBtn');
  const fileInput = document.getElementById('datasetFileInput');
  const replaceModal = document.getElementById('replaceConfirmModal');
  const cancelReplaceBtn = document.getElementById('cancelReplaceBtn');
  const confirmReplaceBtn = document.getElementById('confirmReplaceBtn');

  const backupsTableBody = document.querySelector('#backupsTable tbody');
  const historyTableBody = document.querySelector('#historyTable tbody');

  let currentMode = 'merge';

  // Helper for toasts
  function notify(msg, type = 'info') {
    if (typeof showToast === 'function') {
      showToast(msg);
    } else {
      console.log(`[Toast] ${msg}`);
    }
  }

  // ══ 1. Load Live Dataset Status ══
  async function loadStatus() {
    try {
      const res = await fetch('/api/v1/data/status');
      if (!res.ok) return;
      const data = await res.json();
      if (data.loaded) {
        document.getElementById('statRecords').textContent = Number(data.records || 0).toLocaleString();
        document.getElementById('statBuses').textContent = Number(data.buses || 0).toLocaleString();
        document.getElementById('statRoutes').textContent = Number(data.routes || 0).toLocaleString();
        document.getElementById('statPax').textContent = Number(data.passengers || 0).toLocaleString();
      }
    } catch (err) {
      console.warn('Status fetch error:', err);
    }
  }

  // ══ 2. Merge Dataset Action ══
  if (mergeBtn) {
    mergeBtn.addEventListener('click', () => {
      currentMode = 'merge';
      notify('Select an Excel, CSV, or JSON file to merge...');
      fileInput.click();
    });
  }

  // ══ 3. Replace Dataset Action (Modal Trigger) ══
  if (replaceBtn) {
    replaceBtn.addEventListener('click', () => {
      currentMode = 'replace';
      if (replaceModal) {
        replaceModal.style.display = 'flex';
      }
    });
  }

  if (cancelReplaceBtn) {
    cancelReplaceBtn.addEventListener('click', () => {
      if (replaceModal) replaceModal.style.display = 'none';
    });
  }

  if (confirmReplaceBtn) {
    confirmReplaceBtn.addEventListener('click', () => {
      if (replaceModal) replaceModal.style.display = 'none';
      notify('Select the new baseline file to replace dataset...');
      fileInput.click();
    });
  }

  // Close modal if backdrop clicked
  if (replaceModal) {
    replaceModal.addEventListener('click', (e) => {
      if (e.target === replaceModal) replaceModal.style.display = 'none';
    });
  }

  // ══ 4. File Upload & Ingestion ══
  if (fileInput) {
    fileInput.addEventListener('change', async (e) => {
      const file = e.target.files[0];
      if (!file) return;

      const validExts = ['.xlsx', '.xls', '.csv', '.json'];
      const fileExt = '.' + file.name.split('.').pop().toLowerCase();
      if (!validExts.includes(fileExt)) {
        alert('Unsupported file format! Please select an .xlsx, .xls, .csv, or .json file.');
        fileInput.value = '';
        return;
      }

      notify(`Uploading and processing ${file.name} (${currentMode.toUpperCase()})...`);

      const formData = new FormData();
      formData.append('file', file);

      try {
        const res = await fetch(`/api/v1/data/upload?mode=${encodeURIComponent(currentMode)}`, {
          method: 'POST',
          body: formData
        });

        const result = await res.json();
        if (!res.ok) {
          throw new Error(result.error || `HTTP ${res.status}`);
        }

        notify(`Success! ${Number(result.records_loaded || 0).toLocaleString()} records processed (${result.mode}).`);

        // Refresh all tables and status
        await loadStatus();
        await loadBackups();
        await loadHistory();
      } catch (err) {
        console.error('Upload failed:', err);
        alert(`Dataset processing failed: ${err.message}`);
        notify(`Error: ${err.message}`);
      } finally {
        fileInput.value = '';
      }
    });
  }

  // ══ 5. Load Backups Table ══
  async function loadBackups() {
    if (!backupsTableBody) return;
    try {
      const res = await fetch('/api/v1/data/backups');
      if (!res.ok) throw new Error('Failed to fetch backups');
      const backups = await res.json();

      backupsTableBody.innerHTML = '';
      if (!backups || backups.length === 0) {
        backupsTableBody.innerHTML = `
          <tr>
            <td colspan="5" style="text-align:center; padding:20px; color:var(--text-muted); font-style:italic;">
              No prior backups yet. A snapshot will be saved automatically whenever a dataset is replaced.
            </td>
          </tr>`;
        return;
      }

      backups.forEach(b => {
        const tr = document.createElement('tr');
        const formattedDate = b.created_at ? new Date(b.created_at).toLocaleString() : '—';
        const sizeStr = b.size_kb && b.size_kb !== '-' ? `${b.size_kb} KB` : 'Cloud Managed';

        tr.innerHTML = `
          <td style="font-weight:600; font-family:monospace; color:var(--text-primary);">${escapeHtml(b.name)}</td>
          <td><span style="font-size:0.8rem; background:var(--bg-hover); padding:3px 8px; border-radius:4px;">${escapeHtml(b.type || 'Snapshot')}</span></td>
          <td style="font-size:0.85rem; color:var(--text-muted);">${sizeStr}</td>
          <td style="font-size:0.85rem; color:var(--text-secondary);">${formattedDate}</td>
          <td>
            ${b.name.endsWith('.csv') ? 
              `<a href="/api/v1/data/backups/${encodeURIComponent(b.name)}" class="btn-download-sm" download>
                ⬇️ Download CSV
              </a>` : 
              `<span style="font-size:0.8rem; color:var(--text-muted);">Supabase Table</span>`
            }
          </td>
        `;
        backupsTableBody.appendChild(tr);
      });
    } catch (err) {
      console.warn('Failed to load backups:', err);
      backupsTableBody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:16px; color:#ef4444;">Could not load backups.</td></tr>`;
    }
  }

  // ══ 6. Load History Table ══
  async function loadHistory() {
    if (!historyTableBody) return;
    try {
      const res = await fetch('/api/v1/data/history');
      if (!res.ok) throw new Error('Failed to fetch history');
      const entries = await res.json();

      historyTableBody.innerHTML = '';
      if (!entries || entries.length === 0) {
        historyTableBody.innerHTML = `
          <tr>
            <td colspan="5" style="text-align:center; padding:20px; color:var(--text-muted); font-style:italic;">
              No ingestion events recorded yet.
            </td>
          </tr>`;
        return;
      }

      entries.forEach(e => {
        const tr = document.createElement('tr');
        const formattedDate = e.timestamp ? new Date(e.timestamp).toLocaleString() : '—';
        const isMerge = (e.mode || '').toUpperCase() === 'MERGE';
        const badgeClass = isMerge ? 'badge-merge' : 'badge-replace';
        const badgeText = isMerge ? '➕ MERGE' : '🔄 REPLACE';
        const recordsStr = e.records_loaded ? Number(e.records_loaded).toLocaleString() : '—';

        tr.innerHTML = `
          <td style="font-size:0.85rem; color:var(--text-secondary);">${formattedDate}</td>
          <td><span class="${badgeClass}">${badgeText}</span></td>
          <td style="font-weight:500; font-family:monospace; font-size:0.85rem;">${escapeHtml(e.filename || 'Direct Upload')}</td>
          <td style="font-size:0.85rem; font-weight:600;">${recordsStr} rows</td>
          <td><span class="badge-success">● ${escapeHtml(e.status || 'Success')}</span></td>
        `;
        historyTableBody.appendChild(tr);
      });
    } catch (err) {
      console.warn('Failed to load history:', err);
      historyTableBody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:16px; color:#ef4444;">Could not load history.</td></tr>`;
    }
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  // Initial loads
  loadStatus();
  loadBackups();
  loadHistory();
});
