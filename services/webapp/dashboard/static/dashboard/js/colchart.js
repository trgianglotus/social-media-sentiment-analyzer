google.charts.load('current', {packages: ['corechart']});
                       
                       function drawChart() {
                        // Define the chart to be drawn.
                        var data = google.visualization.arrayToDataTable([
                            ['Element', 'Density', { role: 'style' }],
                            ['Happy', 8, '#80ff00'],            // RGB value
                            ['Unhappy', 5, 'ff3333'] // CSS-style declaration
                        ]);

                        var options = {title: 'Happy Vs Sad','backgroundColor': '#313348','titleTextStyle': {
        'color': 'White'},'hAxis': {'textStyle': {'color': 'white'},'titleTextStyle': {'color': 'white'}},'vAxis': {'textStyle': {'color': 'white'},
        'titleTextStyle': {
            'color': 'white'}
    },'legend': {'textStyle': {'color': 'white'}},'chartArea': {'width': 300, 'height': 300}}; 

                        // Instantiate and draw the chart.
                        var chart = new google.visualization.ColumnChart(document.getElementById('colchart'));
                        chart.draw(data, options);
                    }
                    google.charts.setOnLoadCallback(drawChart);
                       