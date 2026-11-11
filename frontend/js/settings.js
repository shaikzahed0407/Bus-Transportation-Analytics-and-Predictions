// settings.js – handles Replace Dataset, backup list, and upload history

document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const replaceBtn = document.getElementById('replaceDatasetBtn');
  const backupsTableBody = document.querySelector('#backupsTable tbody');
  const historyTableBody = document.querySelector('#historyTable tbody');

  // Reuse the existing hidden file input from the topbar (if present) or create a new one
  let fileInput = document.getElementById('datasetFileInput');
  if (!fileInput) {
    fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.id = 'datasetFileInput';
    fileInput.accept = '.xlsx,.xls,.csv,.json';
    fileInput.style.display = 'none';
    document.body.appendChild(fileInput);
  }

  // ==== Replace Dataset ====
  replaceBtn.addEventListener('click', () => {
    const confirmed = window.confirm(
      '⚠️ This will completely replace the current dataset. A backup will be created automatically. Continue?'
    );
    if (!confirmed) return;
    fileInput.click();
  });

  fileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    // Determine which button triggered the file picker via a flag
    const isReplace = document.activeElement.id === 'replaceDatasetBtn';
    const mode = isReplace ? 'replace' : 'merge';
    if (typeof showToast === 'function') {
      showToast(`Uploading ${file.name} (${mode})...`);
    }
    const formData = new FormData();
    formData.append('file', file);
    try {
      const response = await fetch(`${window.BusPulseAPI ? '' : ''}/api/v1/data/upload?mode=${mode}`, {
        method: 'POST',
        body: formData,
        signal: AbortSignal.timeout(12000)
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error || `HTTP ${response.status}`);
      }
      const result = await response.json();
      if (typeof showToast === 'function') {
        showToast(`Success: ${result.records_loaded.toLocaleString()} rows ${mode === 'replace' ? 'replaced' : 'merged'}!`);
      }
      // Refresh backup & history tables after a replace
      if (mode === 'replace') {
        await loadBackups();
        await loadHistory();
      }
    } catch (err) {
      if (typeof showToast === 'function') {
        showToast(`Upload failed: ${err.message}`);
      }
    } finally {
      fileInput.value = '';
    }
  });

  // ==== Load Backups ====
  async function loadBackups() {
    try {
      const res = await fetch('/api/v1/data/backups');
      const backups = await res.json();
      backupsTableBody.innerHTML = '';
      backups.forEach(b => {
        const tr = document.createElement('tr');
        const btn = document.createElement('button');
        btn.className = 'btn btn-sm btn-primary';
        btn.textContent = 'Download';
        btn.addEventListener('click', () => downloadBackup(b.name));
        tr.innerHTML = `<td>${b.name}</td><td>${new Date(b.created_at).toLocaleString()}</td>`;
        const tdBtn = document.createElement('td');
        tdBtn.appendChild(btn);
        tr.appendChild(tdBtn);
        backupsTableBody.appendChild(tr);
      });
    } catch (e) {
      console.warn('Failed to load backups', e);
    }
  }

  async function downloadBackup(name) {
    const res = await fetch(`/api/v1/data/backups/${name}`);
    if (!res.ok) return;
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${name}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  // ==== Load History ====
  async function loadHistory() {
    try {
      const res = await fetch('/api/v1/data/history');
      const entries = await res.json();
      historyTableBody.innerHTML = '';
      entries.forEach(e => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${new Date(e.timestamp).toLocaleString()}</td><td>${e.mode}</td><td>${e.filename}</td>`;
        historyTableBody.appendChild(tr);
      });
    } catch (e) {
      console.warn('Failed to load history', e);
    }
  }

  // Initial load
  loadBackups();
  loadHistory();
});

