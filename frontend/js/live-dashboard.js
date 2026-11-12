/* Hydrate existing dashboard charts and tables from the shared API. */
(() => {
  const params = () => typeof getGlobalFilters === 'function' ? getGlobalFilters() : {};
  const get = (path) => BusPulseAPI.get(path, params());
  const money = value => Number(value || 0).toLocaleString();
  const set = (selector, value) => { const el = document.querySelector(selector); if (el) el.textContent = value; };
  let refreshSequence = 0;
  const updateChart = (id, labels, datasets) => {
    const canvas = document.getElementById(id);
    if (!canvas) return;
    const chart = Chart.getChart(canvas);
    if (!chart) return;
    chart.data.labels = labels;
    chart.data.datasets.forEach((dataset, i) => { if (datasets[i]) dataset.data = datasets[i]; });
    chart.update();
  };
  async function refresh() {
    const sequence = ++refreshSequence;
    window.setAnalyticsLoading?.(true);
    try {
    const [kpi, hourly, routes, buses, revenue, stops, alerts, forecast] = await Promise.all([
      get('/kpi/summary'), get('/analytics/hourly'), get('/analytics/routes'),
      get('/analytics/buses'), get('/analytics/revenue'), get('/analytics/stops'),
      get('/analytics/alerts'), get('/ai/forecast')
    ]);
    if (kpi) {
      set('#kpiTotalPax', money(kpi.total_passengers)); set('#kpiTotalTkts', money(kpi.total_tickets));
      set('#kpiActiveBuses', money(kpi.active_fleet_buses)); set('#kpiRevenueCollected', `₹${money(kpi.cash_collected)}`);
      set('#kpiShaktiSubsidy', `₹${money(kpi.shakti_subsidy_claim)}`); set('#kpiBusStops', money(kpi.active_stops));
      set('#kpiPeakHour', kpi.peak_hour || '—');
      const pie = Chart.getChart('revenuePie');
      if (pie) { pie.data.datasets[0].data = [kpi.cash_collected, kpi.shakti_subsidy_claim]; pie.update(); }
    }
    if (hourly?.hourly) {
      const rows = hourly.hourly; const labels = rows.map(x => x.label);
      updateChart('hourlyChart', labels, [rows.map(x => x.passengers)]);
      updateChart('hourlyPaxChart', labels, [rows.map(x => x.passengers)]);
      updateChart('revenueHourChart', labels, [rows.map(x => x.collected)]);
    }
    if (routes?.top_routes) {
      const rs = routes.top_routes;
      const body = document.getElementById('routeTableBody');
      if (body) body.innerHTML = rs.slice(0, 20).map((x,i) => `<tr><td>${i+1}</td><td>${x.from_stop}</td><td>${x.to_stop}</td><td>${money(x.passengers)}</td><td>—</td><td>₹${money(x.collected)}</td><td>₹${money(x.subsidy)}</td><td>${money(x.trips)}</td><td>—</td></tr>`).join('');
    }
    if (stops?.stops) {
      const ss = stops.stops;
      updateChart('stopChart', ss.slice(0,10).map(x => x.stop), [ss.slice(0,10).map(x => x.boardings)]);
      updateChart('pickupStopChart', ss.slice(0,10).map(x => x.stop), [ss.slice(0,10).map(x => x.boardings)]);
      const body = document.getElementById('pickupTableBody');
      if (body) body.innerHTML = ss.slice(0,20).map((x,i) => `<tr><td>${i+1}</td><td>${x.stop}</td><td>${money(x.boardings)}</td><td>—</td><td>${money(x.tickets)}</td><td>—</td></tr>`).join('');
    }
    if (buses?.fleet) {
      const fs = buses.fleet;
      updateChart('topBusesChart', fs.slice(0,15).map(x => x.waybill), [fs.slice(0,15).map(x => x.passengers)]);
      updateChart('busLoadChart', fs.slice(0,10).map(x => x.waybill), [fs.slice(0,10).map(x => x.passengers)]);
      const body = document.getElementById('busFleetTableBody');
      if (body) body.innerHTML = fs.map((x,i) => `<tr><td>${i+1}</td><td>${x.waybill}</td><td>${money(x.passengers)}</td><td>${money(x.tickets)}</td><td>${x.pax_per_ticket}</td><td>₹${money(x.collected)}</td><td>₹${money(x.subsidy)}</td><td>₹${money(x.totalFare)}</td><td>${x.stops_covered}</td><td>${x.hours_active}</td><td>${x.badge_label}</td></tr>`).join('');
    }
    if (revenue?.summary) {
      const summary = revenue.summary;
      const cash = Number(summary.cash_collected || 0);
      const subsidy = Number(summary.shakti_subsidy_receivable || 0);
      const gross = Number(summary.total_gross_revenue || 0);
      const collectionRate = gross ? cash / gross * 100 : 0;
      const moneyLabel = value => `₹${money(value)}`;
      set('#revenueShaktiValue', moneyLabel(subsidy));
      set('#revenueShaktiShare', `${summary.shakti_revenue_share_pct || 0}%`);
      set('#revenueCashValue', moneyLabel(cash));
      set('#revenueCashSub', `${money(summary.total_passengers)} passengers in selected records`);
      set('#revenueGrossValue', moneyLabel(gross));
      set('#revenueGrossSub', `${money(summary.total_tickets)} unique tickets in selected records`);
      set('#revenueAvgFareValue', moneyLabel(summary.avg_fare_per_passenger));
      set('#revenueAvgFareSub', `Cash realization ${moneyLabel(cash / Math.max(Number(summary.total_passengers || 0), 1))} per passenger`);
      set('#revenueDonutCash', moneyLabel(cash));
      set('#revenueDonutSubsidy', moneyLabel(subsidy));
      set('#revenueDonutEfficiency', `${collectionRate.toFixed(1)}%`);
      const pie = document.getElementById('revenuePie') && Chart.getChart(document.getElementById('revenuePie'));
      if (pie) { pie.data.datasets[0].data = [cash, subsidy]; pie.update(); }
      const byRevenue = revenue.by_route || [];
      updateChart('routeRevenueChart', byRevenue.slice(0, 8).map(x => x.route), [
        byRevenue.slice(0, 8).map(x => x.cash_collected),
        byRevenue.slice(0, 8).map(x => x.shakti_subsidy)
      ]);
    }
    if (forecast?.predicted) {
      updateChart('demandForecastChart', forecast.labels, [forecast.actual, forecast.predicted, forecast.upper_ci, forecast.lower_ci]);
      set('#forecastModelNote', `${forecast.validation_days}-day rolling holdout · MAE ${forecast.validation_mae ?? 'n/a'} pax/hour · MAPE ${forecast.validation_mape_pct ?? 'n/a'}%. ${forecast.data_quality}`);
    }
    if (Array.isArray(buses?.fleet) && buses.fleet.length) {
      const revenueRows = buses.fleet.slice().sort((a,b) => Number(b.collected)-Number(a.collected)).slice(0,10);
      updateChart('busRevenueChart', revenueRows.map(x => `#${String(x.waybill).slice(-5)}`), [revenueRows.map(x => Number(x.collected) || 0)]);
    }
    if (alerts?.alerts) {
      const cards = document.querySelectorAll('#section-alerts .alert-card');
      alerts.alerts.forEach((a,i) => { if (cards[i]) { const title=cards[i].querySelector('.alert-title'), desc=cards[i].querySelector('.alert-desc'); if(title) title.textContent=a.title; if(desc) desc.textContent=a.summary; } });
    }
    } finally {
      if (sequence === refreshSequence) window.setAnalyticsLoading?.(false);
    }
  }
  async function refreshSimulation() {
    const growth = Number(document.getElementById('paxGrowthSlider')?.value || 0);
    const shakti = Number(document.getElementById('shaktiShareSlider')?.value || 75);
    const tariff = Number(document.getElementById('tariffAdjSlider')?.value || 0);
    const result = await BusPulseAPI.post('/ai/simulate', {
      growth_pct: growth, shakti_pct: shakti, tariff_pct: tariff,
      from_date: params().from_date, to_date: params().to_date
    });
    if (!result) return;
    set('#simPaxOutput', `${money(result.projected_passengers)} pax`);
    set('#simCashOutput', `₹${money(result.projected_cash_revenue)}`);
    set('#simSubsidyOutput', `₹${money(result.projected_shakti_subsidy)}`);
    set('#simBusesOutput', `${money(result.buses_required)} units`);
  }
  document.addEventListener('DOMContentLoaded', () => {
    refresh(); refreshSimulation();
    window.addEventListener('buspulse:filter', () => { refresh(); refreshSimulation(); });
    ['paxGrowthSlider','shaktiShareSlider','tariffAdjSlider'].forEach(id => document.getElementById(id)?.addEventListener('input', refreshSimulation));
  });
})();
