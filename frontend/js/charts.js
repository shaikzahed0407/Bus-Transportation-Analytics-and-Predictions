/**
 * KSRTC Kalaburagi Division - BusPulse Modular Chart Helpers
 * Provides standardized palettes, gradients, and Chart.js configuration presets.
 */

const ChartTheme = {
  purple: '#8B5CF6',
  purpleSoft: 'rgba(139, 92, 246, 0.14)',
  purpleBorder: '#7C3AED',
  green: '#10B981',
  greenSoft: 'rgba(16, 185, 129, 0.14)',
  amber: '#F59E0B',
  blue: '#3B82F6',
  red: '#EF4444',
  text: '#18181B',
  textMuted: '#71717A',
  gridBorder: 'rgba(0, 0, 0, 0.06)'
};

/**
 * Creates a vertical linear gradient on a canvas context.
 */
function createLinearGradient(ctx, colorTop, colorBottom, height = 300) {
  const gradient = ctx.createLinearGradient(0, 0, 0, height);
  gradient.addColorStop(0, colorTop);
  gradient.addColorStop(1, colorBottom);
  return gradient;
}

/**
 * Returns standardized responsive Chart.js options.
 */
function getDefaultChartOptions(titleText = null) {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top',
        labels: {
          usePointStyle: true,
          boxWidth: 8,
          boxHeight: 8,
          font: { family: "'Segoe UI', Inter, sans-serif", size: 12 }
        }
      },
      title: {
        display: Boolean(titleText),
        text: titleText || '',
        font: { size: 13, weight: 'bold' }
      },
      tooltip: {
        backgroundColor: '#18181B',
        titleFont: { size: 12, weight: 'bold' },
        bodyFont: { size: 12 },
        padding: 10,
        cornerRadius: 6
      }
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { color: ChartTheme.textMuted, font: { size: 11 } }
      },
      y: {
        grid: { color: ChartTheme.gridBorder },
        ticks: { color: ChartTheme.textMuted, font: { size: 11 } }
      }
    }
  };
}

