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
        var options = {
            chart: {
                height: 400,
                type: 'line'
            },
            series: [{
                name: 'Height (cm)',
                data: data.height_value
            }, {
                name: 'Weight (kg)',
                data: data.weight_value
            }, {
                name: 'BMI',
                data: data.bmi_value
            }],
            xaxis: {
                categories: data.index,
                title: {
                    text: 'Date'
                }
            },
            yaxis: {
                title: {
                    text: 'Value'
                }
            },
            title: {
                text: 'Health Statistics'
            },
            tooltip: {
                intersect: false,
                shared: true
            }
        };

        var chart = new ApexCharts(document.getElementById("#healthChart"), options);
        chart.render();
    });
}

initialiseHealthCharts();
