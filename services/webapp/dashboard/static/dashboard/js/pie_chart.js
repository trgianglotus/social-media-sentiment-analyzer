var ctx = document.getElementById('myChart').getContext('2d');
var myChart = new Chart(ctx, {
    type: 'pie',
    data: {
        labels: [ 
            'Neutral',
            'Stress',
        ],
        datasets: [{
            label: 'Number of tweets',
            data: [20, 30],
            backgroundColor: [
                'rgba(54, 162, 235, 0.9)',
                'rgba(255, 99, 132, 0.9)',
            ],
            borderColor: [
                'rgba(54, 162, 235, 0.9)',
                'rgba(255, 99, 132, 0.9)',
            ],
            borderWidth: 1
        }]
    },

});
