const xlsx = require('xlsx');
const fs = require('fs');

const wb = xlsx.readFile('C:/Users/tawfe/.gemini/antigravity/brain/c24f9ec1-3d40-425f-8100-d03f24cb1018/.user_uploaded/media_1794211825279_20e7111a.xlsx');
const ws = wb.Sheets[wb.SheetNames[0]];
const data = xlsx.utils.sheet_to_json(ws);

// Convert Excel date serials to actual dates
function excelDateToJS(serial) {
  if (!serial) return null;
  const utc_days = Math.floor(serial - 25569);
  const utc_value = utc_days * 86400;
  return new Date(utc_value * 1000);
}

function excelTimeToHHMM(timeVal) {
  if (timeVal === undefined || timeVal === null) return 'N/A';
  const totalMinutes = Math.round(timeVal * 24 * 60);
  const hours = Math.floor(totalMinutes / 60) % 24;
  const minutes = totalMinutes % 60;
  return `${hours.toString().padStart(2,'0')}:${minutes.toString().padStart(2,'0')}`;
}

// Process data
const processed = data.map(row => {
  const date = excelDateToJS(row['Date']);
  const timeStr = excelTimeToHHMM(row['Time']);
  const hour = row['Time'] ? Math.floor(row['Time'] * 24) % 24 : null;
  return {
    waybill: row['Waybill Number'],
    ticket: row['Ticket Number'],
    from: row['From Stop'],
    to: row['To Stop'],
    date: date ? date.toISOString().split('T')[0] : null,
    dateObj: date,
    month: date ? date.getMonth() + 1 : null,
    year: date ? date.getFullYear() : null,
    dayOfWeek: date ? date.getDay() : null,
    time: timeStr,
    hour: hour,
    passengers: row['Total Psgr'] || 0,
    collected: row['Coll Amt'] || 0,
    uncollected: row['Uncoll Amt'] || 0,
    totalRevenue: (row['Coll Amt'] || 0) + (row['Uncoll Amt'] || 0)
  };
});

console.log('Total records:', processed.length);
console.log('Sample:', JSON.stringify(processed[0], null, 2));

// Analysis 1: Unique stops
const allStops = new Set([...processed.map(r => r.from), ...processed.map(r => r.to)]);
console.log('\nUnique stops:', allStops.size, [...allStops].slice(0, 20));

// Analysis 2: Date range
const dates = processed.filter(r => r.date).map(r => r.date).sort();
console.log('\nDate range:', dates[0], 'to', dates[dates.length - 1]);

// Analysis 3: Total stats
const totalPassengers = processed.reduce((s, r) => s + r.passengers, 0);
const totalCollected = processed.reduce((s, r) => s + r.collected, 0);
const totalUncollected = processed.reduce((s, r) => s + r.uncollected, 0);
console.log('\nTotal Passengers:', totalPassengers);
console.log('Total Collected:', totalCollected);
console.log('Total Uncollected:', totalUncollected);

// Analysis 4: Revenue by route
const routeMap = {};
processed.forEach(r => {
  const key = `${r.from} → ${r.to}`;
  if (!routeMap[key]) routeMap[key] = { route: key, passengers: 0, collected: 0, uncollected: 0, count: 0 };
  routeMap[key].passengers += r.passengers;
  routeMap[key].collected += r.collected;
  routeMap[key].uncollected += r.uncollected;
  routeMap[key].count++;
});
const topRoutes = Object.values(routeMap).sort((a, b) => b.passengers - a.passengers).slice(0, 15);
console.log('\nTop 15 routes by passengers:', JSON.stringify(topRoutes, null, 2));

// Analysis 5: Hourly distribution
const hourlyMap = {};
processed.forEach(r => {
  if (r.hour !== null) {
    if (!hourlyMap[r.hour]) hourlyMap[r.hour] = { hour: r.hour, passengers: 0, trips: 0, collected: 0 };
    hourlyMap[r.hour].passengers += r.passengers;
    hourlyMap[r.hour].trips++;
    hourlyMap[r.hour].collected += r.collected;
  }
});
const hourly = Object.values(hourlyMap).sort((a, b) => a.hour - b.hour);
console.log('\nHourly distribution:', JSON.stringify(hourly, null, 2));

// Analysis 6: Daily revenue trend (by date)
const dailyMap = {};
processed.forEach(r => {
  if (r.date) {
    if (!dailyMap[r.date]) dailyMap[r.date] = { date: r.date, passengers: 0, trips: 0, collected: 0, uncollected: 0 };
    dailyMap[r.date].passengers += r.passengers;
    dailyMap[r.date].trips++;
    dailyMap[r.date].collected += r.collected;
    dailyMap[r.date].uncollected += r.uncollected;
  }
});
const daily = Object.values(dailyMap).sort((a, b) => a.date.localeCompare(b.date));
console.log('\nDaily trend (first 10):', JSON.stringify(daily.slice(0, 10), null, 2));
console.log('Daily trend (last 5):', JSON.stringify(daily.slice(-5), null, 2));
console.log('Total days:', daily.length);

// Analysis 7: Top stops (boarding)
const stopMap = {};
processed.forEach(r => {
  if (!stopMap[r.from]) stopMap[r.from] = { stop: r.from, boardings: 0, revenue: 0 };
  stopMap[r.from].boardings += r.passengers;
  stopMap[r.from].revenue += r.collected;
});
const topStops = Object.values(stopMap).sort((a, b) => b.boardings - a.boardings).slice(0, 10);
console.log('\nTop 10 stops by boardings:', JSON.stringify(topStops, null, 2));

// Analysis 8: Waybill (bus trip) stats
const waybillMap = {};
processed.forEach(r => {
  if (!waybillMap[r.waybill]) waybillMap[r.waybill] = { waybill: r.waybill, passengers: 0, collected: 0, uncollected: 0, tickets: 0 };
  waybillMap[r.waybill].passengers += r.passengers;
  waybillMap[r.waybill].collected += r.collected;
  waybillMap[r.waybill].uncollected += r.uncollected;
  waybillMap[r.waybill].tickets++;
});
const waybills = Object.values(waybillMap);
console.log('\nTotal unique bus trips (waybills):', waybills.length);
const totalTickets = processed.length;
console.log('Total tickets:', totalTickets);

// Analysis 9: Day of week
const dowMap = { 0:'Sun', 1:'Mon', 2:'Tue', 3:'Wed', 4:'Thu', 5:'Fri', 6:'Sat' };
const dowStats = {};
processed.forEach(r => {
  if (r.dayOfWeek !== null) {
    const day = dowMap[r.dayOfWeek];
    if (!dowStats[day]) dowStats[day] = { day, passengers: 0, trips: 0, revenue: 0 };
    dowStats[day].passengers += r.passengers;
    dowStats[day].trips++;
    dowStats[day].revenue += r.collected;
  }
});
console.log('\nDay of week stats:', JSON.stringify(dowStats, null, 2));

// Save all analytics to JSON
const analytics = { 
  totals: { totalPassengers, totalCollected, totalUncollected, totalTickets, totalBusTrips: waybills.length, totalRoutes: Object.keys(routeMap).length, totalStops: allStops.size },
  topRoutes, hourly, daily, topStops, dowStats, allStops: [...allStops].sort()
};
fs.writeFileSync('C:/Users/tawfe/Downloads/Hackathon/ProjectFolder/analytics.json', JSON.stringify(analytics, null, 2));
console.log('\nAnalytics saved!');

