google.charts.load('current', {packages: ['corechart']});
                       
                       function drawChart() {
                        // Define the chart to be drawn.
                        var data = google.visualization.arrayToDataTable([
                            ['Gender', 'Density', { role: 'style' }],
                            ['Male', 8, ' #85c1e9 '],            // RGB value
                            ['Female', 5, '#F48FB1'] // CSS-style declaration
                        ]);

                        var options = {title: 'depression among males and females','backgroundColor': '#313348','titleTextStyle': {
        'color': 'White'},'hAxis': {'textStyle': {'color': 'white'},'titleTextStyle': {'color': 'white'}},'vAxis': {'textStyle': {'color': 'white'},
        'titleTextStyle': {
            'color': 'white'}
    },'legend': {'colors': ['#fcb441'],'textStyle': {'color': 'white'}},'chartArea': {'width': 300, 'height': 300}}; 

                        // Instantiate and draw the chart.
                        var chart = new google.visualization.ColumnChart(document.getElementById('colchart'));
                        chart.draw(data, options);
                    }
                    google.charts.setOnLoadCallback(drawChart);
                       