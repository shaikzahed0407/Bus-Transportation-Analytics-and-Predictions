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
    if (typeof Chart !== 'undefined') {
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
      { from: "Budhavihar", to: "CBS", coords: [[17.3620, 76.8710], [17.3368, 76.8285]], pax: 1525, color: "#8B5CF6", note: "Busiest Corridor (1,525 daily pax)" },
      { from: "CBS", to: "Supermarket", coords: [[17.3368, 76.8285], [17.3328, 76.8340]], pax: 1029, color: "#10B981", note: "High Frequency Shuttle (1,029 pax)" },
      { from: "CBS", to: "Sedam Road", coords: [[17.3368, 76.8285], [17.3160, 76.8530]], pax: 878, color: "#F59E0B", note: "Industrial Route (878 pax)" },
      { from: "Supermarket", to: "Ruknuddin Dargah", coords: [[17.3328, 76.8340], [17.3450, 76.8420]], pax: 713, color: "#3B82F6", note: "High Demand Segment (713 pax)" },
      { from: "CBS", to: "SVP Circle", coords: [[17.3368, 76.8285], [17.3340, 76.8385]], pax: 662, color: "#EC4899", note: "Urban Core Link (662 pax)" }
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

        // Use CartoDB Voyager which allows file:// and browser loading without 403 blocks
        const primaryTileLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
          maxZoom: 19,
          subdomains: 'abcd',
          attribution: '© <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> · © <a href="https://carto.com/attributions" target="_blank">CARTO</a> · KSRTC Kalaburagi GIS'
        });

        // Automatic fallback to Esri WorldStreetMap if network limits Carto
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
          "Voyager Streets": primaryTileLayer,
          "Light Canvas": L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', { subdomains: 'abcd', maxZoom: 19 }),
          "Satellite Imagery": L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', { maxZoom: 18 })
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

        // 2. Corridors Layer
        corridorsLayerGroup = L.layerGroup();
        kalaburagiCorridors.forEach(c => {
          const polyline = L.polyline(c.coords, {
            color: c.color,
            weight: 4.5,
            opacity: 0.82,
            dashArray: '6, 6'
          });
          polyline.bindPopup(`
            <div style="font-family:'Segoe UI',sans-serif; padding:2px;">
              <strong style="color:#18181B;">🚌 ${c.from} ↔ ${c.to}</strong><br>
              <div style="font-size:12px; color:#52525B; margin-top:2px;">${c.note}</div>
            </div>
          `);
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
  