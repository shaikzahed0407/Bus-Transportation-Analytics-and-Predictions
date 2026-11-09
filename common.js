// KSRTC Operations Dashboard - Shared Logic
    // ══ DATA ══
    const hourly = [
      { hour: 6, passengers: 102, trips: 57, collected: 398 },
      { hour: 7, passengers: 849, trips: 479, collected: 2154 },
      { hour: 8, passengers: 1396, trips: 886, collected: 2915 },
      { hour: 9, passengers: 2170, trips: 1325, collected: 5897 },
      { hour: 10, passengers: 2849, trips: 1762, collected: 7867 },
      { hour: 11, passengers: 3017, trips: 1798, collected: 8710 },
      { hour: 12, passengers: 3400, trips: 1965, collected: 9826 },
      { hour: 13, passengers: 2922, trips: 1756, collected: 8802 },
      { hour: 14, passengers: 2821, trips: 1637, collected: 8290 },
      { hour: 15, passengers: 3336, trips: 1880, collected: 9660 },
      { hour: 16, passengers: 3144, trips: 1764, collected: 7431 },
      { hour: 17, passengers: 2995, trips: 1694, collected: 9161 },
      { hour: 18, passengers: 2043, trips: 1229, collected: 6527 },
      { hour: 19, passengers: 1064, trips: 649, collected: 4086 },
      { hour: 20, passengers: 442, trips: 237, collected: 1875 },
      { hour: 21, passengers: 231, trips: 120, collected: 1123 },
      { hour: 22, passengers: 75, trips: 35, collected: 769 },
      { hour: 23, passengers: 18, trips: 2, collected: 0 }
    ];

    const topRoutes = [
      { route: "Budhavihar → Cbs", passengers: 812, collected: 6704, uncollected: 7891, count: 407 },
      { route: "Cbs → Budhavihar", passengers: 713, collected: 5320, uncollected: 7383, count: 335 },
      { route: "Cbs → Supermarket", passengers: 642, collected: 2349, uncollected: 5949, count: 366 },
      { route: "Cbs → Sedam R R", passengers: 445, collected: 1959, uncollected: 3948, count: 320 },
      { route: "Sedam R R → Cbs", passengers: 433, collected: 1810, uncollected: 4032, count: 315 },
      { route: "Budhavihar → S V P Circle", passengers: 395, collected: 3795, uncollected: 2934, count: 174 },
      { route: "Supermarket → Ruknuddin Darga", passengers: 391, collected: 1455, uncollected: 3808, count: 282 },
      { route: "Supermarket → Cbs", passengers: 387, collected: 1577, uncollected: 3640, count: 262 },
      { route: "Cbs → Kbn Darga", passengers: 368, collected: 1596, uncollected: 3864, count: 149 },
      { route: "Ruknuddin Darga → Supermarket", passengers: 322, collected: 1165, uncollected: 3031, count: 214 },
      { route: "Old Hospital → Cbs", passengers: 312, collected: 756, uncollected: 2766, count: 200 },
      { route: "Sedam R R → Supermarket", passengers: 308, collected: 1021, uncollected: 2975, count: 217 },
      { route: "Supermarket → Aland Check Post", passengers: 308, collected: 765, uncollected: 2808, count: 192 },
      { route: "Cbs → S V P Circle", passengers: 267, collected: 173, uncollected: 1383, count: 183 },
      { route: "Supermarket → S V P Circle", passengers: 262, collected: 402, uncollected: 2610, count: 136 }
    ];

    const topStops = [
      { stop: "Supermarket", boardings: 4569, revenue: 13331 },
      { stop: "Cbs", boardings: 4342, revenue: 17271 },
      { stop: "Sedam R R", boardings: 2170, revenue: 5856 },
      { stop: "Budhavihar", boardings: 1906, revenue: 14600 },
      { stop: "Aland Check Post", boardings: 1283, revenue: 2330 },
      { stop: "Old Hospital", boardings: 1236, revenue: 2196 },
      { stop: "S V P Circle", boardings: 1218, revenue: 3325 },
      { stop: "Ruknuddin Darga", boardings: 1077, revenue: 2787 },
      { stop: "Central Bus Stand", boardings: 866, revenue: 2766 },
      { stop: "Madiwala Vritta", boardings: 758, revenue: 1907 }
    ];


    // ══ CHART DEFAULTS ══
    Chart.defaults.font.family = "'Segoe UI', Inter, system-ui, sans-serif";
    Chart.defaults.font.size = 11.5;
    Chart.defaults.maintainAspectRatio = false;
    Chart.defaults.plugins.legend.labels.usePointStyle = true;
    Chart.defaults.plugins.legend.labels.pointStyleWidth = 9;
    Chart.defaults.plugins.legend.labels.boxHeight = 7;
    Chart.defaults.plugins.legend.labels.padding = 10;

    const PURPLE = '#8B5CF6';
    const PURPLE_SOFT = 'rgba(139,92,246,0.12)';
    const PURPLE_MID = 'rgba(139,92,246,0.55)';
    const GREEN = '#10B981';
    const RED = '#EF4444';
    const GRID_COLOR = '#F0F0F0';

    const hourLabels = hourly.map(h => `${h.hour}:00`);

    // ── Small UI helpers ──
    const toastEl = document.getElementById('toast');
    let toastTimer;

    function showToast(message) {
      if (!toastEl) return;
      toastEl.textContent = message;
      toastEl.classList.add('show');
      window.clearTimeout(toastTimer);
      toastTimer = window.setTimeout(() => toastEl.classList.remove('show'), 3000);
    }

    // ── Collapsible sidebar (desktop rail / mobile drawer) ──
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebarToggleIcon = document.getElementById('sidebarToggleIcon');
    const mobileSidebarToggle = document.getElementById('mobileSidebarToggle');
    const sidebarBackdrop = document.getElementById('sidebarBackdrop');
    const sidebarMedia = window.matchMedia('(max-width: 768px)');

    function updateSidebarControls(expanded) {
      const mobile = sidebarMedia.matches;
      const label = mobile
        ? (expanded ? 'Close navigation' : 'Open navigation')
        : (expanded ? 'Collapse sidebar' : 'Expand sidebar');
      sidebarToggle.title = label;
      sidebarToggle.setAttribute('aria-label', label);
      sidebarToggle.setAttribute('aria-expanded', String(expanded));
      sidebarToggleIcon.textContent = mobile
        ? (expanded ? '×' : '☰')
        : (expanded ? '‹' : '☰');
      if (mobileSidebarToggle) {
        mobileSidebarToggle.setAttribute('aria-expanded', String(expanded));
        mobileSidebarToggle.setAttribute('aria-label', expanded ? 'Close navigation' : 'Open navigation');
        mobileSidebarToggle.title = expanded ? 'Close navigation' : 'Open navigation';
      }
    }

    function setSidebarExpanded(expanded, persist = true) {
      if (sidebarMedia.matches) {
        document.body.classList.toggle('sidebar-mobile-open', expanded);
        document.body.classList.remove('sidebar-expanded');
      } else {
        document.body.classList.toggle('sidebar-expanded', expanded);
        document.body.classList.remove('sidebar-mobile-open');
        if (persist) {
          try { localStorage.setItem('ksrtc-sidebar-expanded', String(expanded)); } catch (_) {}
        }
      }
      updateSidebarControls(expanded);
    }

    let savedSidebarState = false;
    try { savedSidebarState = localStorage.getItem('ksrtc-sidebar-expanded') === 'true'; } catch (_) {}
    setSidebarExpanded(sidebarMedia.matches ? false : savedSidebarState, false);

    sidebarToggle.addEventListener('click', () => {
      const currentlyExpanded = sidebarMedia.matches
        ? document.body.classList.contains('sidebar-mobile-open')
        : document.body.classList.contains('sidebar-expanded');
      setSidebarExpanded(!currentlyExpanded);
    });

    mobileSidebarToggle?.addEventListener('click', () => setSidebarExpanded(true, false));
    sidebarBackdrop?.addEventListener('click', () => setSidebarExpanded(false, false));

    sidebarMedia.addEventListener('change', () => {
      document.body.classList.remove('sidebar-expanded', 'sidebar-mobile-open');
      let desktopExpanded = false;
      try { desktopExpanded = localStorage.getItem('ksrtc-sidebar-expanded') === 'true'; } catch (_) {}
      setSidebarExpanded(sidebarMedia.matches ? false : desktopExpanded, false);
    });

    // ── Sidebar navigation ──
    document.querySelectorAll('.nav-item[data-href]').forEach(btn => {
      btn.addEventListener('click', () => {
        const href = btn.dataset.href;
        if (href) {
          window.location.href = href;
        }
      });
    });

    // ── Search route and stop tables ──
    const searchInput = document.getElementById('dashboardSearch');
    const searchableTables = [
      document.getElementById('routeTableBody'),
      document.getElementById('stopTableBody')
    ].filter(Boolean);

    function filterTableRows(query) {
      searchableTables.forEach(tbody => {
        const rows = [...tbody.querySelectorAll('tr:not(.no-results)')];
        let visible = 0;
        rows.forEach(row => {
          const match = row.textContent.toLowerCase().includes(query);
          row.hidden = !match;
          if (match) visible++;
        });

        let emptyRow = tbody.querySelector('.no-results');
        if (!visible && query) {
          if (!emptyRow) {
            emptyRow = document.createElement('tr');
            emptyRow.className = 'no-results';
            const cell = document.createElement('td');
            cell.colSpan = tbody === document.getElementById('routeTableBody') ? 9 : 7;
            cell.textContent = 'No matching records found.';
            emptyRow.appendChild(cell);
            tbody.appendChild(emptyRow);
          }
          emptyRow.hidden = false;
        } else if (emptyRow) {
          emptyRow.remove();
        }
      });
    }

    if (searchInput) {
      searchInput.addEventListener('input', () => filterTableRows(searchInput.value.trim().toLowerCase()));
      document.addEventListener('keydown', event => {
        const activeTag = document.activeElement?.tagName?.toLowerCase();
        if (event.key === '/' && activeTag !== 'input' && activeTag !== 'textarea') {
          event.preventDefault();
          searchInput.focus();
        }
        if (event.key === 'Escape' && document.activeElement === searchInput) {
          searchInput.value = '';
          filterTableRows('');
          searchInput.blur();
        }
      });
    }

    // ── CSV export helpers ──
    function downloadBlob(content, filename, mimeType) {
      const blob = new Blob([content], { type: mimeType });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    }

    function exportTableToCSV(tableId) {
      const table = document.getElementById(tableId);
      if (!table) {
        showToast('The requested table is not available.');
        return;
      }
      const csvRows = [...table.querySelectorAll('tr')]
        .filter(row => !row.hidden && !row.classList.contains('no-results'))
        .map(row => [...row.querySelectorAll('th, td')].map(cell => {
          const value = cell.innerText.replace(/\s+/g, ' ').trim();
          return `"${value.replace(/"/g, '""')}"`;
        }).join(','));
      downloadBlob('\uFEFF' + csvRows.join('\r\n'), `${tableId}-${new Date().toISOString().slice(0, 10)}.csv`, 'text/csv;charset=utf-8;');
      showToast('CSV export prepared.');
    }

    function exportChartAsPNG(canvasId) {
      const canvas = document.getElementById(canvasId);
      if (!canvas) {
        showToast('The requested chart is not available.');
        return;
      }
      const link = document.createElement('a');
      link.href = canvas.toDataURL('image/png', 1);
      link.download = `${canvasId}-${new Date().toISOString().slice(0, 10)}.png`;
      link.click();
      showToast('Chart image downloaded.');
    }

    // Per-card Export / View All actions.
    document.querySelectorAll('[data-export-chart]').forEach(button => {
      button.addEventListener('click', () => exportChartAsPNG(button.dataset.exportChart));
    });
    document.querySelectorAll('[data-export-table]').forEach(button => {
      button.addEventListener('click', () => exportTableToCSV(button.dataset.exportTable));
    });
    document.querySelectorAll('[data-action="view-all-routes"]').forEach(button => {
      button.addEventListener('click', () => {
        document.getElementById('routeTable')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
      });
    });

    // Print dialog allows the department to save the dashboard as PDF.
    document.getElementById('downloadReportBtn')?.addEventListener('click', () => {
      showToast('Use the print dialog to save this dashboard as a PDF.');
      window.setTimeout(() => window.print(), 250);
    });

    document.getElementById('notificationsBtn')?.addEventListener('click', () => {
      document.getElementById('section-alerts')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      showToast('Showing the operational insights and alerts on this report.');
    });

    document.getElementById('settingsBtn')?.addEventListener('click', () => {
      showToast('This front-end preview has no account or settings backend connected yet.');
    });

    document.getElementById('logoutBtn')?.addEventListener('click', () => {
      showToast('Authentication is not configured in this dashboard preview.');
    });

    // ── Right-side map drawer ──
    const floatMap = document.getElementById('floatMap');
    const minBtn = document.getElementById('floatMapMinBtn');
    const mapLauncher = document.getElementById('mapLauncher');
    const mapTabs = document.getElementById('floatMapTabs');

    function setMapOpen(isOpen) {
      floatMap.classList.toggle('open', isOpen);
      document.body.classList.toggle('map-open', isOpen);
      floatMap.setAttribute('aria-hidden', String(!isOpen));
      mapLauncher.setAttribute('aria-expanded', String(isOpen));
      minBtn.textContent = isOpen ? '›' : '‹';
      minBtn.title = isOpen ? 'Minimise map' : 'Expand map';
      minBtn.setAttribute('aria-label', isOpen ? 'Minimise map' : 'Expand map');
    }

    mapLauncher.addEventListener('click', () => setMapOpen(true));
    minBtn.addEventListener('click', () => setMapOpen(false));
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && floatMap.classList.contains('open')) {
        setMapOpen(false);
      }
    });

    // Floating map tabs. No coordinates are embedded in the supplied data,
    // so these tabs explain what each geographic view would need.
    const mapViews = {
      'Routes': {
        title: 'Route view preview',
        text: 'Route-level passenger and revenue summaries are available in the tables. Drawing route lines requires stop coordinates or route geometry.',
        badge: '✦ Route summaries available'
      },
      'Zones': {
        title: 'Zone view not configured',
        text: 'Zone comparisons need each stop to be assigned to a geographic zone or ward in the source dataset.',
        badge: 'ⓘ Zone mapping required'
      },
      'Heatmap': {
        title: 'Passenger heatmap not configured',
        text: 'A geographic heatmap needs latitude and longitude for each stop, along with boarding counts for the selected period.',
        badge: 'ⓘ Stop coordinates required'
      }
    };

    document.querySelectorAll('.fmap-tab').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.fmap-tab').forEach(tab => tab.classList.remove('active'));
        btn.classList.add('active');
        const view = mapViews[btn.textContent.trim()];
        if (!view) return;
        document.getElementById('mapPlaceholderTitle').textContent = view.title;
        document.getElementById('mapPlaceholderText').textContent = view.text;
        document.getElementById('mapReadyBadge').textContent = view.badge;
      });
    });
  