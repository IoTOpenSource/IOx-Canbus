document.addEventListener('DOMContentLoaded', function () {
    const ctxSpeed = document.getElementById('speedChart').getContext('2d');
    const ctxRPM = document.getElementById('rpmChart').getContext('2d');
    const ctxFuel = document.getElementById('fuelChart').getContext('2d');

    const speedChart = new Chart(ctxSpeed, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Vehicle Speed (kmph)',
                data: [],
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1,
                fill: false
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    const rpmChart = new Chart(ctxRPM, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Engine RPM',
                data: [],
                borderColor: 'rgba(153, 102, 255, 1)',
                borderWidth: 1,
                fill: false
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    const fuelChart = new Chart(ctxFuel, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Fuel Level (%)',
                data: [],
                borderColor: 'rgba(255, 159, 64, 1)',
                borderWidth: 1,
                fill: false
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    function updateCharts(data) {
        const now = new Date(data.timestamp).toLocaleTimeString();

        // Update speedChart
        if (data.vehicleSpeed) {
            speedChart.data.datasets[0].data.push(data.vehicleSpeed.value);
            speedChart.update();
        }

        // Update rpmChart
        if (data.engineRPM) {
            rpmChart.data.datasets[0].data.push(data.engineRPM.value);
            rpmChart.update();
        }

        // Update fuelChart
        if (data.fuelLevel) {
            fuelChart.data.datasets[0].data.push(data.fuelLevel.value);
            fuelChart.update();
        }
    }

    function fetchData() {
        fetch('/data')
            .then(response => response.json())
            .then(data => {
                console.log('Fetched data:', data);
                updateCharts(data);
                setTimeout(fetchData, 5000);
            })
            .catch(error => {
                console.error('Error fetching data:', error);
            });
    }

    fetchData();
});
