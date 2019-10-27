var endpoint = '/api/chart/data/'
var data = []
var labels = []

$.ajax({
    method: "GET",
    url: endpoint,
    success: function(data){
        var ctx_pc = document.getElementById('main_pie_chart').getContext('2d');
        var myChart = new Chart(ctx_pc, {
            type: 'pie',
            data: {
                labels: data.pc_labels,
                datasets: [{
                    label: '# number of votes',
                    data: data.pc_data,
                    // data: [30, 40],
                    backgroundColor: [
                        '#ff3d53',
                        '#f1d51d',
                        
                    ],
                    
                    borderColor: [
                        '#23273d',
                        '#23273d',
                    ],
                    
                    borderWidth: 2,
                }]
            },
            options: {
                cutoutPercentage: 40,
                legend: {
                    labels: {
                        fontColor: "#c5c5c5",
                        fontSize: 14
                    }
                },
            
            }
        });

        
    }
})


$.ajax({
    method: "GET",
    url: endpoint,
    success: function(data){
        var ctx_l = document.getElementById('main_line_chart').getContext('2d');
var myLineChart = new Chart(ctx_l, {
type: 'line',
label: data.l_labels,
data: {
    labels: data.l_labels,
    datasets: [{
        label: '%',
        data: data.l_data,
        borderColor: "#f1d51d",
        fill: true,
        backgroundColor: '#dbdbdb28',
        pointBorderColor: "#fff",
        pointBackgroundColor: "#fff",
        hoverBorderColor: "#fff",
        hoverBackgroundColor: "#f1d51d",
        pointRadius: 7,
        pointHoverRadius: 5,
    }]
},
options: {
    legend: {
        labels: {
            fontColor: "white",
            fontSize: 12
        }
    },
    title: {
        display: true,
        text: 'Percentage of negative tweets over time',
        fontColor: '#fff',
    },
    scales: {
        yAxes: [{
            ticks: {
                fontColor: "white",
                fontSize: 12,
                // stepSize: 1,
                borderColor: "white",
            
            }, gridLines: {
                display: false,
            },
        }, 
    ],
        xAxes: [{
            ticks: {
                fontColor: "white",
                fontSize: 12,
                // stepSize: 1,
            },gridLines: {
                display: false,
            },
        }]
    }
}
});

        
    }
})



