(() => {
  const tableBody = document.getElementById('datasetTableBody');
  if (!tableBody) return;

  const searchInput = document.getElementById('datasetSearch');
  const pageSizeInput = document.getElementById('datasetPageSize');
  const countLabel = document.getElementById('datasetCount');
  const pageLabel = document.getElementById('datasetPageLabel');
  const previousButton = document.getElementById('datasetPrevBtn');
  const nextButton = document.getElementById('datasetNextBtn');
  const downloadButton = document.getElementById('downloadDatasetBtn');
  const formatter = new Intl.NumberFormat('en-IN', { maximumFractionDigits: 2 });

  let page = 1;
  let totalPages = 0;
  let requestSequence = 0;
  let searchTimer;

  const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, char => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[char]);

  function currentParams(includePaging = true) {
    const filters = typeof getGlobalFilters === 'function' ? getGlobalFilters() : {};
    const params = { ...filters, q: searchInput?.value.trim() || '' };
    if (includePaging) {
      params.page = page;
      params.page_size = Number(pageSizeInput?.value || 50);
    }
    return params;
  }

  function displayValue(column, value) {
    if (value === null || value === undefined || value === '') return '—';
    if (['Collected Fare (INR)', 'Uncollected Fare (INR)', 'Total Fare (INR)'].includes(column)) {
      return `₹${formatter.format(Number(value) || 0)}`;
    }
    if (column === 'Shakti Pattern') {
      const yes = value === true || String(value).toLowerCase() === 'true';
      return `<span class="data-sheet-tag ${yes ? 'scheme' : 'cash'}">${yes ? 'Shakti' : 'Cash'}</span>`;
    }
    if (column === 'Data Source') {
      const synthetic = String(value).toLowerCase().includes('synthetic');
      return `<span class="data-sheet-tag ${synthetic ? 'synthetic' : 'source'}">${escapeHtml(value)}</span>`;
    }
    return escapeHtml(value);
  }

  async function loadRecords() {
    const sequence = ++requestSequence;
    window.setAnalyticsLoading?.(true);
    tableBody.innerHTML = '<tr><td colspan="14" class="data-sheet-empty"><span class="data-sheet-inline-spinner" aria-hidden="true"></span> Loading ticket records…</td></tr>';
    try {
      const result = await BusPulseAPI.get('/data/records', currentParams());
      if (sequence !== requestSequence) return;
      if (!result || !Array.isArray(result.rows)) throw new Error('The data service did not return ticket records.');

      totalPages = result.pages || 0;
      const rows = result.rows;
      if (!rows.length) {
        tableBody.innerHTML = '<tr><td colspan="14" class="data-sheet-empty">No ticket records match these filters.</td></tr>';
      } else {
        tableBody.innerHTML = rows.map(row => `<tr>${result.columns.map(column => `<td>${displayValue(column, row[column])}</td>`).join('')}</tr>`).join('');
      }

      const start = result.total ? (result.page - 1) * result.page_size + 1 : 0;
      const end = Math.min(result.page * result.page_size, result.total);
      countLabel.textContent = `Showing ${formatter.format(start)}–${formatter.format(end)} of ${formatter.format(result.total)} ticket records`;
      pageLabel.textContent = `Page ${result.page} of ${totalPages || 1}`;
      previousButton.disabled = result.page <= 1;
      nextButton.disabled = result.page >= totalPages;
    } catch (error) {
      if (sequence !== requestSequence) return;
      tableBody.innerHTML = '<tr><td colspan="14" class="data-sheet-empty">Could not load ticket records. Check that the dashboard API is running, then try again.</td></tr>';
      countLabel.textContent = 'Records unavailable';
      pageLabel.textContent = 'Page —';
      previousButton.disabled = true;
      nextButton.disabled = true;
      console.error('Data sheet request failed:', error);
    } finally {
      if (sequence === requestSequence) window.setAnalyticsLoading?.(false);
    }
  }

  searchInput?.addEventListener('input', () => {
    window.clearTimeout(searchTimer);
    searchTimer = window.setTimeout(() => { page = 1; loadRecords(); }, 250);
  });
  pageSizeInput?.addEventListener('change', () => { page = 1; loadRecords(); });
  previousButton?.addEventListener('click', () => { if (page > 1) { page--; loadRecords(); } });
  nextButton?.addEventListener('click', () => { if (page < totalPages) { page++; loadRecords(); } });
  window.addEventListener('buspulse:filter', () => { page = 1; loadRecords(); });
  downloadButton?.addEventListener('click', () => {
    const params = new URLSearchParams(currentParams(false));
    const base = typeof API_BASE_URL === 'string' ? API_BASE_URL : '/api/v1';
    window.location.assign(`${base}/data/records.csv?${params.toString()}`);
  });

  document.addEventListener('DOMContentLoaded', loadRecords);
})();
