function getHealthStatistics() {
    return new Promise(function(resolve, reject) {
        $.ajax({
            type: "GET",
            url: "health_statistics",
            success: function (result) {
                resolve(result);
            },
            error: function (result) {
                reject(result);
            }
        });
    })
}

function initialiseHealthCharts() {
    getHealthStatistics().then(function (data) {
        // Create a chart
        var ctx = document.getElementById('healthChart').getContext('2d');
        var chart = new Chart(ctx, {
            type: 'line',
            data: {
            labels: data.index,
            datasets: [{
                label: 'Height',
                data: data.height_value,
                borderColor: 'red',
                fill: false
            }, {
                label: 'Weight',
                data: data.weight_value,
                borderColor: 'blue',
                fill: false
            }, {
                label: 'BMI',
                data: data.bmi_value,
                borderColor: 'green',
                fill: false
            }]
            },
            options: {
            responsive: true,
            title: {
                display: true,
                text: 'Health Statistics'
            },
            tooltips: {
                mode: 'index',
                intersect: false
            },
            hover: {
                mode: 'nearest',
                intersect: true
            },
            scales: {
                xAxes: [{
                display: true,
                scaleLabel: {
                    display: true,
                    labelString: 'Date'
                }
                }],
                yAxes: [{
                display: true,
                scaleLabel: {
                    display: true,
                    labelString: 'Value'
                }
                }]
            }
            }
        });
    });
}

initialiseHealthCharts();