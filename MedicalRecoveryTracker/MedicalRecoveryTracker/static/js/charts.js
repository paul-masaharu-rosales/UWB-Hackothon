/**
 * MediTrack - Symptom Charts Visualization
 * This file handles the visualization of symptom data using Chart.js
 */

// Main function to initialize the symptom chart
function initSymptomChart() {
  const chartContainer = document.getElementById('symptomChart');
  
  // If chart container doesn't exist, return
  if (!chartContainer) return;
  
  // Get the canvas element
  const ctx = document.getElementById('symptomChartCanvas').getContext('2d');
  
  // Show loading indicator
  showChartLoading();
  
  // Fetch the journal data
  fetch('/journal/data')
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to fetch journal data');
      }
      return response.json();
    })
    .then(data => {
      // Hide loading indicator
      hideChartLoading();
      
      // If there's no data, show empty state
      if (!data.datasets || data.datasets.length === 0) {
        showEmptyState();
        return;
      }
      
      // Create chart
      createSymptomChart(ctx, data);
    })
    .catch(error => {
      console.error('Error fetching journal data:', error);
      hideChartLoading();
      showChartError(error.message);
    });
}

// Function to create symptom chart
function createSymptomChart(ctx, data) {
  // Define colors for different symptoms
  const colors = [
    '#1e88e5', // Primary blue
    '#43a047', // Green
    '#5e35b1', // Purple
    '#fb8c00', // Orange
    '#e53935', // Red
    '#00acc1', // Cyan
    '#8e24aa', // Deep Purple
    '#ffb300', // Amber
    '#546e7a', // Blue Grey
    '#6d4c41'  // Brown
  ];
  
  // Process datasets to ensure they have the correct format
  const datasets = data.datasets.map((dataset, index) => {
    // Calculate positions for all dates
    const positions = data.labels.map(label => {
      const dateIndex = dataset.dates.indexOf(label);
      return dateIndex !== -1 ? dataset.data[dateIndex] : null;
    });
    
    return {
      label: dataset.label,
      data: positions,
      backgroundColor: dataset.backgroundColor || colors[index % colors.length],
      borderColor: dataset.borderColor || colors[index % colors.length],
      borderWidth: dataset.borderWidth || 2,
      tension: dataset.tension || 0.3,
      fill: dataset.fill || false,
      pointRadius: 4,
      pointHoverRadius: 6
    };
  });
  
  // Create the chart
  window.symptomChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.labels,
      datasets: datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: 'Symptom Severity Over Time',
          font: {
            size: 16,
            weight: 'bold'
          },
          padding: {
            top: 10,
            bottom: 20
          }
        },
        tooltip: {
          mode: 'index',
          intersect: false,
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          titleColor: '#333',
          bodyColor: '#333',
          borderColor: '#ddd',
          borderWidth: 1,
          padding: 12,
          displayColors: true,
          callbacks: {
            title: function(tooltipItems) {
              const date = new Date(tooltipItems[0].label);
              return date.toLocaleDateString('en-US', { 
                year: 'numeric', 
                month: 'short', 
                day: 'numeric' 
              });
            }
          }
        },
        legend: {
          position: 'bottom',
          labels: {
            usePointStyle: true,
            padding: 20,
            font: {
              size: 12
            }
          }
        }
      },
      scales: {
        x: {
          grid: {
            display: false
          },
          ticks: {
            maxRotation: 45,
            minRotation: 45,
            callback: function(value, index, values) {
              const date = new Date(this.getLabelForValue(value));
              return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            }
          }
        },
        y: {
          beginAtZero: true,
          suggestedMax: 10,
          ticks: {
            stepSize: 1,
            callback: function(value) {
              if (value === 0) return '0';
              if (value === 10) return '10 (Severe)';
              if (value === 1) return '1 (Mild)';
              return value;
            }
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          }
        }
      }
    }
  });
}

// Function to show loading indicator
function showChartLoading() {
  const container = document.getElementById('chartContainer');
  if (!container) return;
  
  const loadingEl = document.createElement('div');
  loadingEl.id = 'chartLoading';
  loadingEl.className = 'text-center my-5';
  loadingEl.innerHTML = `
    <div class="spinner-border text-primary" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
    <p class="mt-2">Loading chart data...</p>
  `;
  
  container.appendChild(loadingEl);
}

// Function to hide loading indicator
function hideChartLoading() {
  const loadingEl = document.getElementById('chartLoading');
  if (loadingEl) {
    loadingEl.remove();
  }
}

// Function to show error message
function showChartError(message) {
  const container = document.getElementById('chartContainer');
  if (!container) return;
  
  const errorEl = document.createElement('div');
  errorEl.className = 'alert alert-danger my-3';
  errorEl.innerHTML = `
    <i class="fas fa-exclamation-triangle me-2"></i>
    <strong>Error:</strong> ${message}
  `;
  
  container.appendChild(errorEl);
}

// Function to show empty state
function showEmptyState() {
  const container = document.getElementById('chartContainer');
  if (!container) return;
  
  const emptyEl = document.createElement('div');
  emptyEl.className = 'text-center my-5 py-5';
  emptyEl.innerHTML = `
    <i class="fas fa-chart-line fa-3x text-muted mb-3"></i>
    <h4>No symptom data available</h4>
    <p class="text-muted">Record symptoms in your medical journal to see them visualized here.</p>
    <a href="/journal" class="btn btn-primary mt-2">
      <i class="fas fa-plus me-2"></i>
      Add Symptoms
    </a>
  `;
  
  container.appendChild(emptyEl);
}

// Initialize charts when the document is ready
document.addEventListener('DOMContentLoaded', function() {
  initSymptomChart();
});
