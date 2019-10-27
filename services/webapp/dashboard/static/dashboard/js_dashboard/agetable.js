google.charts.load('current', {'packages':['corechart']});
google.charts.setOnLoadCallback(drawChart);
function drawChart() {
    // Define the chart to be drawn.
    var data = google.visualization.arrayToDataTable([
       ['Age', 'percentage'],
       ['11-15',  20],
       ['16-20',  30],
       ['21-25',  10],
       ['26-30',  30],
    ]);

    var options = {title: 'Age and Self Harm (in percentage)','backgroundColor': '#313348','titleTextStyle': {
        'color': 'White'},'hAxis': {'textStyle': {'color': 'white'},'titleTextStyle': {'color': 'white'}},'vAxis': {'textStyle': {'color': 'white'},
        'titleTextStyle': {
            'color': 'white'}
    },'legend': {'textStyle': {'color': 'white'}},'chartArea': {'width': 300, 'height': 300}}; 

    // Instantiate and draw the chart.
    var chart = new google.visualization.ColumnChart(document.getElementById('container'));
    chart.draw(data, options);
 }
 google.charts.setOnLoadCallback(drawChart);