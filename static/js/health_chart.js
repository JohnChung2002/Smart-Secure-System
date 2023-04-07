function getHealthStatistics() {
    return new Promise(function(resolve, reject) {
        $.ajax({
            type: "GET",
            url: "health_statistic",
            success: function (result) {
                resolve(jQuery.parseJSON(result));
            },
            error: function (result) {
                reject(result);
            }
        });
    })
}

function initialiseHealthCharts() {
    const weightChart = document.getElementById('weightChart');
    const heightChart = document.getElementById('heightChart');
    const bmiChart = document.getElementById('bmiChart');
    getHealthStatistics().then(function (result) {
        weightData = {x: result.index, y: result.weight_value};
        heightData = {x: result.index, y: result.height_value};
        bmiData = {x: result.index, y: result.bmi_value};
        new Chart(weightChart, {
            type: 'line',
            data: {
                datasets: [{
                    label: 'Weight',
                    data: weightData,
                    borderWidth: 1
                }]
            }
        });
        new Chart(heightChart, {
            type: 'line',
            data: {
                datasets: [{
                    label: 'Height',
                    data: heightData,
                    borderWidth: 1
                }]
            }
        });
        new Chart(bmiChart, {
            type: 'line',
            data: {
                datasets: [{
                    label: 'BMI',
                    data: bmiData,
                    borderWidth: 1
                }]
            }
        });
    });
}
