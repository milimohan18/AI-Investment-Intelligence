let myChart = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    fetchTickers();
});

// Fetch available tickers from the backend API
async function fetchTickers() {
    try {
        const response = await fetch('/api/tickers');
        const data = await response.json();
        
        const tickerList = document.getElementById('ticker-list');
        tickerList.innerHTML = ''; // Clear default

        if (data.tickers && data.tickers.length > 0) {
            data.tickers.forEach((ticker, index) => {
                const li = document.createElement('li');
                li.textContent = ticker;
                li.onclick = () => selectTicker(ticker, li);
                tickerList.appendChild(li);

                // Auto-select the first ticker
                if (index === 0) {
                    selectTicker(ticker, li);
                }
            });
        } else {
            tickerList.innerHTML = '<li>No data found</li>';
        }
    } catch (error) {
        console.error('Error fetching tickers:', error);
    }
}

// Select a ticker and fetch its data
async function selectTicker(ticker, element) {
    // Update active state in UI
    document.querySelectorAll('.ticker-list li').forEach(el => el.classList.remove('active'));
    if (element) {
        element.classList.add('active');
    }

    // Update Title
    document.getElementById('dashboard-title').textContent = `${ticker} Predictions`;
    
    // Fetch data
    try {
        const response = await fetch(`/api/data/${ticker}`);
        const data = await response.json();
        renderChart(data);
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

// Render moving interactive graph using Chart.js
function renderChart(data) {
    const ctx = document.getElementById('predictionChart').getContext('2d');
    
    // Process Data
    const labels = [];
    const actualData = [];
    const predictedData = [];

    // Parse History (Optional if you want to show trailing lines)
    if (data.predictions) {
        data.predictions.forEach(row => {
            labels.push(row.Date);
            actualData.push(row.Actual !== null ? parseFloat(row.Actual) : null);
            predictedData.push(row.Predicted !== null ? parseFloat(row.Predicted) : null);
        });
    }

    // Update the "Last Updated" and "Current Value" UI
    if (labels.length > 0) {
        document.getElementById('last-updated').textContent = labels[labels.length - 1];
        
        // Let's assume the predicted values are standard normalized returns or direct prices
        const latestPred = predictedData[predictedData.length - 1];
        if (latestPred !== undefined && latestPred !== null) {
            const displayVal = (latestPred * 100).toFixed(2) + '%';
            document.getElementById('current-price').textContent = `Latest Prediction: ${displayVal}`;
        }
    }

    // Chart.js Theme Config
    Chart.defaults.color = '#8b949e';
    Chart.defaults.font.family = 'Inter';

    // Gradients
    const gradientActual = ctx.createLinearGradient(0, 0, 0, 400);
    gradientActual.addColorStop(0, 'rgba(88, 166, 255, 0.4)');
    gradientActual.addColorStop(1, 'rgba(88, 166, 255, 0.0)');

    const gradientPredicted = ctx.createLinearGradient(0, 0, 0, 400);
    gradientPredicted.addColorStop(0, 'rgba(188, 140, 255, 0.4)');
    gradientPredicted.addColorStop(1, 'rgba(188, 140, 255, 0.0)');

    // Destroy existing chart if it exists
    if (myChart) {
        myChart.destroy();
    }

    myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Actual Returns',
                    data: actualData,
                    borderColor: '#58a6ff',
                    backgroundColor: gradientActual,
                    borderWidth: 2,
                    pointBackgroundColor: '#58a6ff',
                    pointBorderColor: '#fff',
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    fill: false,
                    tension: 0.4 // Smooth curves
                },
                {
                    label: 'Predicted Returns',
                    data: predictedData,
                    borderColor: '#bc8cff',
                    backgroundColor: gradientPredicted,
                    borderWidth: 2,
                    borderDash: [5, 5],
                    pointBackgroundColor: '#bc8cff',
                    pointBorderColor: '#fff',
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    fill: true,
                    tension: 0.4 // Smooth curves
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        boxWidth: 8
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(22, 27, 34, 0.9)',
                    titleColor: '#fff',
                    bodyColor: '#c9d1d9',
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderWidth: 1,
                    padding: 12,
                    boxPadding: 6,
                    usePointStyle: true,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += context.parsed.y.toFixed(4);
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)',
                        drawBorder: false
                    },
                    ticks: {
                        maxTicksLimit: 10
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)',
                        drawBorder: false
                    }
                }
            },
            animation: {
                duration: 1500,
                easing: 'easeOutQuart'
            }
        }
    });
}
