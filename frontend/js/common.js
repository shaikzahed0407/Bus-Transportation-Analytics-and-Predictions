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
    if (typeof Chart !== 'undefined' && Chart.defaults) {
      Chart.defaults.font.family = "'Segoe UI', Inter, system-ui, sans-serif";
      Chart.defaults.font.size = 11.5;
      Chart.defaults.maintainAspectRatio = false;
      Chart.defaults.plugins.legend.labels.usePointStyle = true;
      Chart.defaults.plugins.legend.labels.pointStyleWidth = 9;
      Chart.defaults.plugins.legend.labels.boxHeight = 7;
      Chart.defaults.plugins.legend.labels.padding = 10;
    }

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
      if (sidebarToggle) {
        sidebarToggle.title = label;
        sidebarToggle.setAttribute('aria-label', label);
        sidebarToggle.setAttribute('aria-expanded', String(expanded));
      }
      if (sidebarToggleIcon) {
        sidebarToggleIcon.textContent = mobile
          ? (expanded ? '×' : '☰')
          : (expanded ? '‹' : '☰');
      }
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

    sidebarToggle?.addEventListener('click', () => {
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

    // ── Universal dynamic search ──
    const searchInput = document.getElementById('dashboardSearch');

    function filterTableRows(query) {
      const tbodies = Array.from(document.querySelectorAll('tbody'));
      let totalVisible = 0;

      if (tbodies.length > 0) {
        tbodies.forEach(tbody => {
          const rows = Array.from(tbody.querySelectorAll('tr:not(.no-results)'));
          let visibleInTable = 0;
          rows.forEach(row => {
            const match = !query || row.textContent.toLowerCase().includes(query);
            row.hidden = !match;
            if (match) visibleInTable++;
          });
          totalVisible += visibleInTable;

          let emptyRow = tbody.querySelector('.no-results');
          if (!visibleInTable && query) {
            if (!emptyRow) {
              emptyRow = document.createElement('tr');
              emptyRow.className = 'no-results';
              const colSpan = tbody.closest('table')?.querySelectorAll('thead th')?.length || 8;
              emptyRow.innerHTML = `<td colspan="${colSpan}" style="text-align:center; padding:18px; color:var(--text-muted); font-style:italic;">No matching records found for "${query}".</td>`;
              tbody.appendChild(emptyRow);
            }
            emptyRow.hidden = false;
          } else if (emptyRow) {
            emptyRow.remove();
          }
        });
      } else {
        // Fallback for non-table pages (Overview, Revenue, Alerts): filter cards
        const cards = Array.from(document.querySelectorAll('.card, .alert-card, .kpi-card'));
        cards.forEach(card => {
          const match = !query || card.textContent.toLowerCase().includes(query);
          card.style.opacity = match ? '1' : '0.22';
          card.style.filter = match ? 'none' : 'grayscale(60%)';
          if (match) totalVisible++;
        });
      }
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

    document.getElementById('notificationsBtn')?.addEventListener('click', (e) => {
      const sectionAlerts = document.getElementById('section-alerts');
      if (sectionAlerts) {
        e.preventDefault();
        sectionAlerts.scrollIntoView({ behavior: 'smooth', block: 'start' });
        showToast('Viewing operational alerts and insights.');
      }
    });

    document.getElementById('settingsBtn')?.addEventListener('click', () => {
      showToast('Department configuration & permissions settings.');
    });

    document.getElementById('logoutBtn')?.addEventListener('click', () => {
      showToast('KSRTC Operations Portal — Session Active.');
    });

    // ── Right-side map drawer & Leaflet GIS Engine ──
    const floatMap = document.getElementById('floatMap');
    const minBtn = document.getElementById('floatMapMinBtn');
    const mapLauncher = document.getElementById('mapLauncher');
    const mapBackdrop = document.getElementById('mapBackdrop');

    // Real Kalaburagi (Gulbarga) transit stops from the dataset
    const kalaburagiHubs = [
      { name: "Supermarket Transit Hub", coords: [17.3328, 76.8340], boardings: 4569, revenue: 13331, role: "Primary Commercial Hub", color: "#10B981" },
      { name: "CBS (Central Bus Stand)", coords: [17.3368, 76.8285], boardings: 4342, revenue: 17271, role: "Central Terminal", color: "#8B5CF6" },
      { name: "Sedam Road (Sedam R R)", coords: [17.3160, 76.8530], boardings: 2170, revenue: 5856, role: "Suburban Arterial Hub", color: "#F59E0B" },
      { name: "Budhavihar Terminal", coords: [17.3620, 76.8710], boardings: 1906, revenue: 14600, role: "North-East Corridor Anchor", color: "#EC4899" },
      { name: "Aland Check Post", coords: [17.3710, 76.8120], boardings: 1283, revenue: 2330, role: "Northern Gateway", color: "#06B6D4" },
      { name: "Old Hospital", coords: [17.3280, 76.8360], boardings: 1236, revenue: 2196, role: "Civic Transit Node", color: "#8B5CF6" },
      { name: "S V P Circle", coords: [17.3340, 76.8385], boardings: 1218, revenue: 3325, role: "Central Junction", color: "#8B5CF6" },
      { name: "Ruknuddin Dargah", coords: [17.3450, 76.8420], boardings: 1077, revenue: 2787, role: "Historic Transit Stop", color: "#8B5CF6" },
      { name: "Madiwala Vritta", coords: [17.3250, 76.8300], boardings: 758, revenue: 1907, role: "Feeder Point", color: "#71717A" }
    ];

    const kalaburagiCorridors = [
  {
    "from": "Budhavihar",
    "to": "CBS",
    "pax": 1525,
    "color": "#8B5CF6",
    "note": "Busiest Corridor (1,525 daily pax) \u00b7 Via Ring Rd & Nehru Ganj",
    "coords": [
      [
        17.36192,
        76.87135
      ],
      [
        17.36132,
        76.8712
      ],
      [
        17.36129,
        76.87119
      ],
      [
        17.36127,
        76.87119
      ],
      [
        17.36124,
        76.87119
      ],
      [
        17.36122,
        76.87119
      ],
      [
        17.36089,
        76.87126
      ],
      [
        17.3608,
        76.87123
      ],
      [
        17.36043,
        76.87113
      ],
      [
        17.36021,
        76.87108
      ],
      [
        17.36001,
        76.87104
      ],
      [
        17.35925,
        76.8709
      ],
      [
        17.35872,
        76.87081
      ],
      [
        17.35776,
        76.87065
      ],
      [
        17.35671,
        76.87017
      ],
      [
        17.35547,
        76.86952
      ],
      [
        17.35496,
        76.86926
      ],
      [
        17.35489,
        76.86923
      ],
      [
        17.35444,
        76.86896
      ],
      [
        17.35408,
        76.86874
      ],
      [
        17.35393,
        76.86866
      ],
      [
        17.35378,
        76.86866
      ],
      [
        17.35363,
        76.86866
      ],
      [
        17.35357,
        76.86866
      ],
      [
        17.35332,
        76.8687
      ],
      [
        17.35324,
        76.86871
      ],
      [
        17.3526,
        76.86882
      ],
      [
        17.35244,
        76.86885
      ],
      [
        17.35199,
        76.86893
      ],
      [
        17.35175,
        76.86898
      ],
      [
        17.35162,
        76.86899
      ],
      [
        17.35148,
        76.86903
      ],
      [
        17.35118,
        76.86911
      ],
      [
        17.35088,
        76.86917
      ],
      [
        17.35079,
        76.86919
      ],
      [
        17.35069,
        76.86881
      ],
      [
        17.35056,
        76.86835
      ],
      [
        17.35046,
        76.86806
      ],
      [
        17.35036,
        76.86771
      ],
      [
        17.34993,
        76.8661
      ],
      [
        17.34985,
        76.86579
      ],
      [
        17.34945,
        76.86454
      ],
      [
        17.34901,
        76.8634
      ],
      [
        17.34874,
        76.86274
      ],
      [
        17.34864,
        76.86245
      ],
      [
        17.34847,
        76.86195
      ],
      [
        17.34825,
        76.86133
      ],
      [
        17.34812,
        76.86094
      ],
      [
        17.34798,
        76.86057
      ],
      [
        17.34798,
        76.86052
      ],
      [
        17.34798,
        76.86044
      ],
      [
        17.34792,
        76.86021
      ],
      [
        17.34784,
        76.85985
      ],
      [
        17.34783,
        76.85976
      ],
      [
        17.34778,
        76.85966
      ],
      [
        17.34771,
        76.85953
      ],
      [
        17.34753,
        76.85907
      ],
      [
        17.34743,
        76.85869
      ],
      [
        17.34734,
        76.85837
      ],
      [
        17.34722,
        76.85803
      ],
      [
        17.34715,
        76.85788
      ],
      [
        17.34714,
        76.85773
      ],
      [
        17.34713,
        76.8577
      ],
      [
        17.34711,
        76.85751
      ],
      [
        17.34711,
        76.85741
      ],
      [
        17.34716,
        76.85707
      ],
      [
        17.34724,
        76.85678
      ],
      [
        17.34727,
        76.85669
      ],
      [
        17.34724,
        76.85664
      ],
      [
        17.34711,
        76.85638
      ],
      [
        17.34699,
        76.85616
      ],
      [
        17.34697,
        76.85612
      ],
      [
        17.34683,
        76.85578
      ],
      [
        17.34681,
        76.85573
      ],
      [
        17.34675,
        76.85559
      ],
      [
        17.34655,
        76.8552
      ],
      [
        17.3464,
        76.8552
      ],
      [
        17.34642,
        76.85496
      ],
      [
        17.34644,
        76.85458
      ],
      [
        17.34646,
        76.85438
      ],
      [
        17.34648,
        76.85317
      ],
      [
        17.34648,
        76.85314
      ],
      [
        17.34641,
        76.85272
      ],
      [
        17.34635,
        76.85255
      ],
      [
        17.34632,
        76.85252
      ],
      [
        17.34614,
        76.85241
      ],
      [
        17.34615,
        76.85205
      ],
      [
        17.34617,
        76.85189
      ],
      [
        17.34609,
        76.85131
      ],
      [
        17.34615,
        76.85045
      ],
      [
        17.34611,
        76.84956
      ],
      [
        17.34595,
        76.84899
      ],
      [
        17.34592,
        76.84889
      ],
      [
        17.34576,
        76.84832
      ],
      [
        17.34558,
        76.84796
      ],
      [
        17.3452,
        76.84719
      ],
      [
        17.34499,
        76.84676
      ],
      [
        17.34506,
        76.84508
      ],
      [
        17.34507,
        76.84486
      ],
      [
        17.3451,
        76.84451
      ],
      [
        17.34514,
        76.84415
      ],
      [
        17.34514,
        76.84405
      ],
      [
        17.34514,
        76.84347
      ],
      [
        17.34515,
        76.84279
      ],
      [
        17.34515,
        76.84267
      ],
      [
        17.34514,
        76.84233
      ],
      [
        17.34512,
        76.84193
      ],
      [
        17.34513,
        76.84179
      ],
      [
        17.34513,
        76.84143
      ],
      [
        17.34513,
        76.84098
      ],
      [
        17.34511,
        76.84049
      ],
      [
        17.34509,
        76.83983
      ],
      [
        17.34511,
        76.8394
      ],
      [
        17.34512,
        76.8389
      ],
      [
        17.34505,
        76.83848
      ],
      [
        17.34504,
        76.83832
      ],
      [
        17.34501,
        76.83778
      ],
      [
        17.34501,
        76.83756
      ],
      [
        17.34427,
        76.83759
      ],
      [
        17.34425,
        76.83759
      ],
      [
        17.34389,
        76.83761
      ],
      [
        17.34377,
        76.83761
      ],
      [
        17.34315,
        76.83762
      ],
      [
        17.34278,
        76.83763
      ],
      [
        17.34248,
        76.83762
      ],
      [
        17.34221,
        76.83762
      ],
      [
        17.34221,
        76.83765
      ],
      [
        17.34218,
        76.83767
      ],
      [
        17.34215,
        76.83768
      ],
      [
        17.34212,
        76.83767
      ],
      [
        17.3421,
        76.83765
      ],
      [
        17.34145,
        76.83767
      ],
      [
        17.34067,
        76.83767
      ],
      [
        17.34064,
        76.83761
      ],
      [
        17.34047,
        76.83714
      ],
      [
        17.34036,
        76.83678
      ],
      [
        17.34029,
        76.83663
      ],
      [
        17.34021,
        76.83641
      ],
      [
        17.34007,
        76.83618
      ],
      [
        17.33973,
        76.83568
      ],
      [
        17.33928,
        76.83473
      ],
      [
        17.33904,
        76.8341
      ],
      [
        17.33894,
        76.83393
      ],
      [
        17.33879,
        76.8337
      ],
      [
        17.33854,
        76.83336
      ],
      [
        17.33815,
        76.83284
      ],
      [
        17.33768,
        76.83213
      ],
      [
        17.33758,
        76.83195
      ],
      [
        17.33754,
        76.83182
      ],
      [
        17.33752,
        76.83165
      ],
      [
        17.33753,
        76.83145
      ],
      [
        17.33758,
        76.83121
      ],
      [
        17.33788,
        76.83008
      ],
      [
        17.33792,
        76.82991
      ],
      [
        17.33795,
        76.82968
      ],
      [
        17.33797,
        76.82932
      ],
      [
        17.33798,
        76.82908
      ],
      [
        17.33749,
        76.82914
      ],
      [
        17.33732,
        76.82917
      ],
      [
        17.33727,
        76.82896
      ],
      [
        17.33725,
        76.8289
      ],
      [
        17.33714,
        76.82841
      ]
    ],
    "distance_km": 6.47,
    "duration_min": 8.1
  },
  {
    "from": "CBS",
    "to": "Supermarket",
    "pax": 1029,
    "color": "#10B981",
    "note": "High Frequency Shuttle (1,029 pax) \u00b7 Via Station Rd & Tank Bund",
    "coords": [
      [
        17.33714,
        76.82841
      ],
      [
        17.33725,
        76.8289
      ],
      [
        17.33727,
        76.82896
      ],
      [
        17.33732,
        76.82917
      ],
      [
        17.33516,
        76.82961
      ],
      [
        17.33389,
        76.82986
      ],
      [
        17.33389,
        76.83073
      ],
      [
        17.33389,
        76.83101
      ],
      [
        17.3339,
        76.83121
      ],
      [
        17.33399,
        76.83213
      ],
      [
        17.33406,
        76.83306
      ],
      [
        17.33287,
        76.83304
      ],
      [
        17.33284,
        76.834
      ]
    ],
    "distance_km": 1.05,
    "duration_min": 2.0
  },
  {
    "from": "CBS",
    "to": "Sedam Road",
    "pax": 878,
    "color": "#F59E0B",
    "note": "Industrial Arterial Route (878 pax) \u00b7 Via SH 10 Sedam Rd",
    "coords": [
      [
        17.33714,
        76.82841
      ],
      [
        17.33725,
        76.8289
      ],
      [
        17.33727,
        76.82896
      ],
      [
        17.33732,
        76.82917
      ],
      [
        17.33516,
        76.82961
      ],
      [
        17.33389,
        76.82986
      ],
      [
        17.33389,
        76.83073
      ],
      [
        17.33389,
        76.83101
      ],
      [
        17.3339,
        76.83121
      ],
      [
        17.33399,
        76.83213
      ],
      [
        17.33406,
        76.83306
      ],
      [
        17.33412,
        76.83373
      ],
      [
        17.33415,
        76.83423
      ],
      [
        17.33416,
        76.83469
      ],
      [
        17.33415,
        76.83517
      ],
      [
        17.33414,
        76.83607
      ],
      [
        17.33412,
        76.83644
      ],
      [
        17.33416,
        76.83647
      ],
      [
        17.33419,
        76.8365
      ],
      [
        17.33419,
        76.83655
      ],
      [
        17.33418,
        76.83658
      ],
      [
        17.33416,
        76.83661
      ],
      [
        17.33412,
        76.83664
      ],
      [
        17.33408,
        76.83664
      ],
      [
        17.33405,
        76.83663
      ],
      [
        17.33403,
        76.83661
      ],
      [
        17.33402,
        76.83661
      ],
      [
        17.334,
        76.83658
      ],
      [
        17.334,
        76.83655
      ],
      [
        17.334,
        76.83651
      ],
      [
        17.33326,
        76.83602
      ],
      [
        17.33323,
        76.836
      ],
      [
        17.33303,
        76.83588
      ],
      [
        17.33294,
        76.83583
      ],
      [
        17.3328,
        76.83577
      ],
      [
        17.33255,
        76.83569
      ],
      [
        17.33074,
        76.83507
      ],
      [
        17.33047,
        76.83593
      ],
      [
        17.33046,
        76.83597
      ],
      [
        17.33038,
        76.83628
      ],
      [
        17.33027,
        76.83668
      ],
      [
        17.33022,
        76.83696
      ],
      [
        17.33017,
        76.83726
      ],
      [
        17.33015,
        76.83743
      ],
      [
        17.33002,
        76.83841
      ],
      [
        17.33001,
        76.83851
      ],
      [
        17.32997,
        76.83878
      ],
      [
        17.3299,
        76.83929
      ],
      [
        17.3299,
        76.83933
      ],
      [
        17.32987,
        76.83951
      ],
      [
        17.32986,
        76.83974
      ],
      [
        17.32984,
        76.84011
      ],
      [
        17.32984,
        76.84015
      ],
      [
        17.32982,
        76.84088
      ],
      [
        17.32982,
        76.841
      ],
      [
        17.32981,
        76.84157
      ],
      [
        17.3298,
        76.84205
      ],
      [
        17.32978,
        76.84224
      ],
      [
        17.32954,
        76.84328
      ],
      [
        17.32945,
        76.84366
      ],
      [
        17.32926,
        76.8444
      ],
      [
        17.32891,
        76.84583
      ],
      [
        17.32889,
        76.84591
      ],
      [
        17.32888,
        76.84595
      ],
      [
        17.32833,
        76.8482
      ],
      [
        17.32821,
        76.84873
      ],
      [
        17.32808,
        76.84923
      ],
      [
        17.32798,
        76.84967
      ],
      [
        17.32794,
        76.8498
      ],
      [
        17.32778,
        76.85043
      ],
      [
        17.32767,
        76.85088
      ],
      [
        17.3275,
        76.8516
      ],
      [
        17.32735,
        76.85224
      ],
      [
        17.32729,
        76.85249
      ],
      [
        17.32709,
        76.85327
      ],
      [
        17.32702,
        76.85353
      ],
      [
        17.32697,
        76.85376
      ],
      [
        17.32668,
        76.855
      ],
      [
        17.32666,
        76.85509
      ],
      [
        17.32653,
        76.85562
      ],
      [
        17.32643,
        76.85604
      ],
      [
        17.32641,
        76.85611
      ],
      [
        17.32643,
        76.85613
      ],
      [
        17.32644,
        76.85614
      ],
      [
        17.32645,
        76.85617
      ],
      [
        17.32645,
        76.85619
      ],
      [
        17.32645,
        76.85621
      ],
      [
        17.32644,
        76.85623
      ],
      [
        17.32642,
        76.85625
      ],
      [
        17.32639,
        76.85626
      ],
      [
        17.32637,
        76.85626
      ],
      [
        17.32635,
        76.85626
      ],
      [
        17.32634,
        76.85625
      ],
      [
        17.32632,
        76.85623
      ],
      [
        17.32631,
        76.85622
      ],
      [
        17.3263,
        76.85619
      ],
      [
        17.32613,
        76.85612
      ],
      [
        17.32592,
        76.85602
      ],
      [
        17.32568,
        76.8559
      ],
      [
        17.3255,
        76.85581
      ],
      [
        17.32474,
        76.85541
      ],
      [
        17.32406,
        76.85506
      ],
      [
        17.32323,
        76.8546
      ],
      [
        17.3224,
        76.85416
      ],
      [
        17.32158,
        76.85377
      ],
      [
        17.32081,
        76.85344
      ],
      [
        17.32074,
        76.85341
      ],
      [
        17.32057,
        76.85333
      ],
      [
        17.3203,
        76.85322
      ],
      [
        17.32021,
        76.85318
      ],
      [
        17.31914,
        76.85274
      ],
      [
        17.31849,
        76.8525
      ],
      [
        17.3178,
        76.85228
      ],
      [
        17.31769,
        76.85225
      ],
      [
        17.3176,
        76.85222
      ],
      [
        17.31644,
        76.85187
      ],
      [
        17.31629,
        76.85182
      ],
      [
        17.31491,
        76.8514
      ],
      [
        17.31434,
        76.85121
      ],
      [
        17.3144,
        76.85133
      ],
      [
        17.31452,
        76.85153
      ],
      [
        17.31475,
        76.85183
      ],
      [
        17.31483,
        76.85195
      ],
      [
        17.31486,
        76.85201
      ],
      [
        17.31501,
        76.85233
      ],
      [
        17.31516,
        76.85265
      ],
      [
        17.31523,
        76.8528
      ],
      [
        17.31567,
        76.85265
      ],
      [
        17.31583,
        76.85305
      ],
      [
        17.31587,
        76.85315
      ],
      [
        17.31599,
        76.85316
      ]
    ],
    "distance_km": 5.7,
    "duration_min": 6.5
  },
  {
    "from": "Supermarket",
    "to": "Ruknuddin Dargah",
    "pax": 713,
    "color": "#3B82F6",
    "note": "Heritage & Pilgrimage Route (713 pax) \u00b7 Via Muslim Chowk",
    "coords": [
      [
        17.33284,
        76.834
      ],
      [
        17.33284,
        76.83411
      ],
      [
        17.33193,
        76.83521
      ],
      [
        17.33191,
        76.83539
      ],
      [
        17.33256,
        76.83561
      ],
      [
        17.33282,
        76.83571
      ],
      [
        17.33294,
        76.83577
      ],
      [
        17.33306,
        76.83582
      ],
      [
        17.3333,
        76.83596
      ],
      [
        17.33374,
        76.83625
      ],
      [
        17.33406,
        76.83644
      ],
      [
        17.33409,
        76.83644
      ],
      [
        17.33412,
        76.83644
      ],
      [
        17.33416,
        76.83647
      ],
      [
        17.33419,
        76.8365
      ],
      [
        17.33454,
        76.83646
      ],
      [
        17.3348,
        76.83643
      ],
      [
        17.33498,
        76.83643
      ],
      [
        17.33514,
        76.83645
      ],
      [
        17.33545,
        76.83652
      ],
      [
        17.33553,
        76.83655
      ],
      [
        17.33599,
        76.8367
      ],
      [
        17.33645,
        76.8369
      ],
      [
        17.33657,
        76.83696
      ],
      [
        17.33695,
        76.83712
      ],
      [
        17.33715,
        76.83722
      ],
      [
        17.33767,
        76.83746
      ],
      [
        17.33797,
        76.83759
      ],
      [
        17.33802,
        76.83761
      ],
      [
        17.33806,
        76.83762
      ],
      [
        17.3381,
        76.83763
      ],
      [
        17.33818,
        76.83764
      ],
      [
        17.33844,
        76.83763
      ],
      [
        17.33889,
        76.83762
      ],
      [
        17.33969,
        76.8376
      ],
      [
        17.34031,
        76.8376
      ],
      [
        17.34064,
        76.83761
      ],
      [
        17.34124,
        76.83764
      ],
      [
        17.34182,
        76.83762
      ],
      [
        17.34209,
        76.83761
      ],
      [
        17.34211,
        76.83758
      ],
      [
        17.34214,
        76.83756
      ],
      [
        17.34217,
        76.83756
      ],
      [
        17.3422,
        76.83758
      ],
      [
        17.34221,
        76.83762
      ],
      [
        17.34248,
        76.83762
      ],
      [
        17.34278,
        76.83763
      ],
      [
        17.34315,
        76.83762
      ],
      [
        17.34377,
        76.83761
      ],
      [
        17.34389,
        76.83761
      ],
      [
        17.34425,
        76.83759
      ],
      [
        17.34427,
        76.83759
      ],
      [
        17.34501,
        76.83756
      ],
      [
        17.34501,
        76.83778
      ],
      [
        17.34504,
        76.83832
      ],
      [
        17.34505,
        76.83848
      ],
      [
        17.34512,
        76.8389
      ],
      [
        17.34511,
        76.8394
      ],
      [
        17.34509,
        76.83983
      ],
      [
        17.34511,
        76.84049
      ],
      [
        17.34513,
        76.84098
      ],
      [
        17.34513,
        76.84143
      ],
      [
        17.34513,
        76.84179
      ],
      [
        17.34512,
        76.84193
      ],
      [
        17.34499,
        76.84195
      ]
    ],
    "distance_km": 2.17,
    "duration_min": 2.6
  },
  {
    "from": "CBS",
    "to": "SVP Circle",
    "pax": 662,
    "color": "#EC4899",
    "note": "Urban Core Transit Link (662 pax) \u00b7 Via Main Rd",
    "coords": [
      [
        17.33714,
        76.82841
      ],
      [
        17.33725,
        76.8289
      ],
      [
        17.33727,
        76.82896
      ],
      [
        17.33732,
        76.82917
      ],
      [
        17.33516,
        76.82961
      ],
      [
        17.33389,
        76.82986
      ],
      [
        17.33389,
        76.83073
      ],
      [
        17.33389,
        76.83101
      ],
      [
        17.3339,
        76.83121
      ],
      [
        17.33399,
        76.83213
      ],
      [
        17.33406,
        76.83306
      ],
      [
        17.33412,
        76.83373
      ],
      [
        17.33415,
        76.83423
      ],
      [
        17.33416,
        76.83469
      ],
      [
        17.33415,
        76.83517
      ],
      [
        17.33414,
        76.83607
      ],
      [
        17.33412,
        76.83644
      ],
      [
        17.33416,
        76.83647
      ],
      [
        17.33419,
        76.8365
      ],
      [
        17.33419,
        76.83655
      ],
      [
        17.33418,
        76.83658
      ],
      [
        17.33416,
        76.83661
      ],
      [
        17.33412,
        76.83664
      ],
      [
        17.33408,
        76.83664
      ],
      [
        17.33391,
        76.83734
      ],
      [
        17.33382,
        76.83775
      ],
      [
        17.33371,
        76.83826
      ],
      [
        17.33403,
        76.83831
      ]
    ],
    "distance_km": 1.42,
    "duration_min": 2.2
  },
  {
    "from": "Aland Check Post",
    "to": "CBS",
    "pax": 615,
    "color": "#06B6D4",
    "note": "Northern Corridor Link (615 pax) \u00b7 Via SH 10 Aland Rd",
    "coords": [
      [
        17.36892,
        76.8147
      ],
      [
        17.36511,
        76.81555
      ],
      [
        17.36144,
        76.81638
      ],
      [
        17.36068,
        76.81656
      ],
      [
        17.3604,
        76.81663
      ],
      [
        17.36037,
        76.81663
      ],
      [
        17.36034,
        76.81664
      ],
      [
        17.36032,
        76.81664
      ],
      [
        17.3603,
        76.81662
      ],
      [
        17.35946,
        76.816
      ],
      [
        17.35946,
        76.81597
      ],
      [
        17.35962,
        76.81561
      ],
      [
        17.35935,
        76.81542
      ],
      [
        17.35864,
        76.81494
      ],
      [
        17.35813,
        76.81554
      ],
      [
        17.35809,
        76.81558
      ],
      [
        17.35776,
        76.81599
      ],
      [
        17.35753,
        76.81624
      ],
      [
        17.35749,
        76.81629
      ],
      [
        17.35743,
        76.81635
      ],
      [
        17.35737,
        76.8164
      ],
      [
        17.35713,
        76.8166
      ],
      [
        17.35713,
        76.81663
      ],
      [
        17.35712,
        76.81665
      ],
      [
        17.3571,
        76.81666
      ],
      [
        17.35709,
        76.81667
      ],
      [
        17.35706,
        76.81667
      ],
      [
        17.35704,
        76.81666
      ],
      [
        17.35694,
        76.81672
      ],
      [
        17.35692,
        76.81673
      ],
      [
        17.35661,
        76.81694
      ],
      [
        17.35634,
        76.81713
      ],
      [
        17.35523,
        76.81793
      ],
      [
        17.35481,
        76.81822
      ],
      [
        17.35435,
        76.81855
      ],
      [
        17.35381,
        76.81893
      ],
      [
        17.35374,
        76.81898
      ],
      [
        17.35265,
        76.81975
      ],
      [
        17.35256,
        76.81982
      ],
      [
        17.35231,
        76.81999
      ],
      [
        17.352,
        76.82018
      ],
      [
        17.35187,
        76.82028
      ],
      [
        17.35176,
        76.82036
      ],
      [
        17.35155,
        76.82051
      ],
      [
        17.35109,
        76.82082
      ],
      [
        17.35071,
        76.82108
      ],
      [
        17.35003,
        76.82153
      ],
      [
        17.34994,
        76.82158
      ],
      [
        17.34923,
        76.82209
      ],
      [
        17.3491,
        76.82218
      ],
      [
        17.34858,
        76.82258
      ],
      [
        17.34852,
        76.82263
      ],
      [
        17.34837,
        76.82275
      ],
      [
        17.34817,
        76.82297
      ],
      [
        17.34788,
        76.82339
      ],
      [
        17.34786,
        76.82341
      ],
      [
        17.3478,
        76.82353
      ],
      [
        17.34771,
        76.82366
      ],
      [
        17.34767,
        76.82374
      ],
      [
        17.34731,
        76.82444
      ],
      [
        17.34704,
        76.825
      ],
      [
        17.34698,
        76.82512
      ],
      [
        17.34664,
        76.82585
      ],
      [
        17.3465,
        76.82611
      ],
      [
        17.34634,
        76.82639
      ],
      [
        17.34629,
        76.82646
      ],
      [
        17.34625,
        76.82651
      ],
      [
        17.34625,
        76.82652
      ],
      [
        17.34605,
        76.82677
      ],
      [
        17.346,
        76.82683
      ],
      [
        17.3458,
        76.82701
      ],
      [
        17.34574,
        76.82707
      ],
      [
        17.34544,
        76.8273
      ],
      [
        17.34494,
        76.82771
      ],
      [
        17.34462,
        76.828
      ],
      [
        17.34436,
        76.82822
      ],
      [
        17.34427,
        76.82832
      ],
      [
        17.34418,
        76.82842
      ],
      [
        17.34414,
        76.82847
      ],
      [
        17.34407,
        76.82853
      ],
      [
        17.34407,
        76.82855
      ],
      [
        17.34406,
        76.82857
      ],
      [
        17.34405,
        76.82858
      ],
      [
        17.34403,
        76.82859
      ],
      [
        17.34401,
        76.8286
      ],
      [
        17.34399,
        76.82859
      ],
      [
        17.34397,
        76.82858
      ],
      [
        17.34396,
        76.82857
      ],
      [
        17.34396,
        76.82856
      ],
      [
        17.3437,
        76.82846
      ],
      [
        17.34331,
        76.82833
      ],
      [
        17.34284,
        76.82828
      ],
      [
        17.34207,
        76.82835
      ],
      [
        17.34171,
        76.82836
      ],
      [
        17.34076,
        76.82808
      ],
      [
        17.3403,
        76.82798
      ],
      [
        17.34007,
        76.82792
      ],
      [
        17.33996,
        76.8279
      ],
      [
        17.33991,
        76.82789
      ],
      [
        17.33972,
        76.82784
      ],
      [
        17.33965,
        76.82783
      ],
      [
        17.33959,
        76.82781
      ],
      [
        17.33947,
        76.82777
      ],
      [
        17.33909,
        76.82763
      ],
      [
        17.33875,
        76.82747
      ],
      [
        17.33836,
        76.82741
      ],
      [
        17.33811,
        76.82736
      ],
      [
        17.33761,
        76.82739
      ],
      [
        17.33695,
        76.82747
      ],
      [
        17.33698,
        76.82776
      ],
      [
        17.337,
        76.82783
      ],
      [
        17.33701,
        76.8279
      ],
      [
        17.33714,
        76.82841
      ]
    ],
    "distance_km": 4.39,
    "duration_min": 8.7
  }
];

    let leafletMapInstance = null;
    let hubsLayerGroup = null;
    let corridorsLayerGroup = null;
    let heatLayerGroup = null;

    function renderKalaburagiMap() {
      const container = document.getElementById('google-map-container');
      if (!container || typeof L === 'undefined') return;

      if (!leafletMapInstance) {
        container.innerHTML = '<div id="kalaburagiMapLeaflet" style="width:100%; height:100%; z-index:1;"></div>';

        leafletMapInstance = L.map('kalaburagiMapLeaflet', {
          center: [17.3370, 76.8380],
          zoom: 13,
          zoomControl: true
        });

        // OpenStreetMap standard tiles (100% free, no API key required)
        const primaryTileLayer = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
          maxZoom: 19,
          attribution: '© <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors · KSRTC Kalaburagi GIS'
        });

        // Automatic fallback to Esri WorldStreetMap if network limits OSM
        primaryTileLayer.on('tileerror', function() {
          if (!leafletMapInstance._hasFallbackTile) {
            leafletMapInstance._hasFallbackTile = true;
            L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
              maxZoom: 18,
              attribution: 'Tiles © Esri · KSRTC Kalaburagi GIS'
            }).addTo(leafletMapInstance);
          }
        });

        primaryTileLayer.addTo(leafletMapInstance);

        // Add interactive layer selector in bottom right for judges/officials
        const baseLayers = {
          "OpenStreetMap": primaryTileLayer,
          "Esri Streets": L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', { maxZoom: 18, attribution: 'Tiles © Esri · KSRTC Kalaburagi GIS' }),
          "Satellite Imagery": L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', { maxZoom: 18, attribution: 'Tiles © Esri' })
        };
        L.control.layers(baseLayers, null, { position: 'bottomright' }).addTo(leafletMapInstance);

        // 1. Hub Markers Layer
        hubsLayerGroup = L.layerGroup();
        kalaburagiHubs.forEach(hub => {
          const radius = Math.max(8, Math.min(22, Math.sqrt(hub.boardings) * 0.28));
          const marker = L.circleMarker(hub.coords, {
            radius: radius,
            fillColor: hub.color,
            color: '#ffffff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.88
          });

          marker.bindPopup(`
            <div style="font-family:'Segoe UI',sans-serif; min-width:180px; padding:2px;">
              <div style="font-size:13px; font-weight:700; color:#18181B; margin-bottom:4px;">📍 ${hub.name}</div>
              <div style="font-size:12px; color:#52525B;">Boardings: <strong style="color:#18181B;">${hub.boardings.toLocaleString()} pax</strong></div>
              <div style="font-size:12px; color:#52525B;">Fare Collected: <strong style="color:#059669;">₹${hub.revenue.toLocaleString()}</strong></div>
              <div style="margin-top:6px;"><span style="display:inline-block; font-size:10px; font-weight:700; padding:2px 8px; border-radius:12px; background:#EDE9FE; color:#8B5CF6;">${hub.role}</span></div>
            </div>
          `);
          hubsLayerGroup.addLayer(marker);
        });

        // 2. Corridors Layer (Real-World Road Network Transit Routing)
        corridorsLayerGroup = L.layerGroup();
        kalaburagiCorridors.forEach(c => {
          // Dark casing/shadow line underneath for high visibility on street maps
          const casing = L.polyline(c.coords, {
            color: '#1E1B4B',
            weight: 6,
            opacity: 0.35,
            lineCap: 'round',
            lineJoin: 'round'
          });
          corridorsLayerGroup.addLayer(casing);

          // Primary bus route line
          const polyline = L.polyline(c.coords, {
            color: c.color,
            weight: 4,
            opacity: 0.95,
            lineCap: 'round',
            lineJoin: 'round'
          });

          polyline.bindPopup(`
            <div style="font-family:'Segoe UI',sans-serif; min-width:210px; padding:3px;">
              <div style="font-size:13px; font-weight:700; color:#18181B; margin-bottom:4px;">🚌 ${c.from} ↔ ${c.to}</div>
              <div style="font-size:12px; color:#52525B;">${c.note}</div>
              <div style="margin-top:6px; display:flex; gap:6px; flex-wrap:wrap;">
                <span style="font-size:11px; font-weight:700; padding:2px 8px; border-radius:12px; background:#EDE9FE; color:#7C3AED;">${c.distance_km || '—'} km</span>
                <span style="font-size:11px; font-weight:700; padding:2px 8px; border-radius:12px; background:#ECFDF5; color:#059669;">~${c.duration_min || '—'} mins</span>
                <span style="font-size:11px; font-weight:700; padding:2px 8px; border-radius:12px; background:#FEF3C7; color:#D97706;">${c.pax.toLocaleString()} pax/day</span>
              </div>
            </div>
          `);

          // Hover interaction
          polyline.on('mouseover', function() {
            this.setStyle({ weight: 6, opacity: 1 });
            this.bringToFront();
          });
          polyline.on('mouseout', function() {
            this.setStyle({ weight: 4, opacity: 0.95 });
          });

          corridorsLayerGroup.addLayer(polyline);
        });

        // 3. Heatmap Demand Layer
        heatLayerGroup = L.layerGroup();
        kalaburagiHubs.forEach(hub => {
          const heatRadius = Math.max(300, Math.min(850, hub.boardings * 0.16));
          const circle = L.circle(hub.coords, {
            radius: heatRadius,
            fillColor: hub.boardings > 3000 ? '#EF4444' : hub.boardings > 1500 ? '#F59E0B' : '#8B5CF6',
            color: 'transparent',
            fillOpacity: 0.3
          });
          circle.bindPopup(`<strong>${hub.name}</strong><br>Passenger Intensity: ${hub.boardings.toLocaleString()} boardings`);
          heatLayerGroup.addLayer(circle);
        });

        // Default: Show Hubs and Corridors
        hubsLayerGroup.addTo(leafletMapInstance);
        corridorsLayerGroup.addTo(leafletMapInstance);
      }

      window.setTimeout(() => {
        leafletMapInstance.invalidateSize();
        if (typeof L !== 'undefined' && kalaburagiHubs.length > 0) {
          const bounds = L.latLngBounds(kalaburagiHubs.map(h => h.coords));
          leafletMapInstance.fitBounds(bounds, { padding: [35, 35] });
        }
      }, 250);
    }

    function switchMapTab(tabName) {
      if (!leafletMapInstance) return;
      if (tabName === 'Routes') {
        leafletMapInstance.addLayer(hubsLayerGroup);
        leafletMapInstance.addLayer(corridorsLayerGroup);
        if (leafletMapInstance.hasLayer(heatLayerGroup)) leafletMapInstance.removeLayer(heatLayerGroup);
      } else if (tabName === 'Zones') {
        leafletMapInstance.addLayer(corridorsLayerGroup);
        if (leafletMapInstance.hasLayer(hubsLayerGroup)) leafletMapInstance.removeLayer(hubsLayerGroup);
        if (leafletMapInstance.hasLayer(heatLayerGroup)) leafletMapInstance.removeLayer(heatLayerGroup);
      } else if (tabName === 'Heatmap') {
        leafletMapInstance.addLayer(heatLayerGroup);
        leafletMapInstance.addLayer(hubsLayerGroup);
        if (leafletMapInstance.hasLayer(corridorsLayerGroup)) leafletMapInstance.removeLayer(corridorsLayerGroup);
      }
    }

    function setMapOpen(isOpen) {
      if (!floatMap) return;
      floatMap.classList.toggle('open', isOpen);
      document.body.classList.toggle('map-open', isOpen);
      floatMap.setAttribute('aria-hidden', String(!isOpen));
      mapLauncher?.setAttribute('aria-expanded', String(isOpen));
      if (minBtn) {
        minBtn.textContent = isOpen ? '›' : '‹';
        minBtn.title = isOpen ? 'Minimise map' : 'Expand map';
        minBtn.setAttribute('aria-label', isOpen ? 'Minimise map' : 'Expand map');
      }
      if (isOpen) {
        renderKalaburagiMap();
      }
    }

    mapLauncher?.addEventListener('click', () => setMapOpen(true));
    minBtn?.addEventListener('click', () => setMapOpen(false));
    mapBackdrop?.addEventListener('click', () => setMapOpen(false));

    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && floatMap?.classList.contains('open')) {
        setMapOpen(false);
      }
    });

    document.querySelectorAll('.fmap-tab').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.fmap-tab').forEach(tab => tab.classList.remove('active'));
        btn.classList.add('active');
        switchMapTab(btn.textContent.trim());
      });
    });
  