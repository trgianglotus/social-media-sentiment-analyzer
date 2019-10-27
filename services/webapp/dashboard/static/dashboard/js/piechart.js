// Load google charts
google.charts.load('current', {'packages':['corechart']});
google.charts.setOnLoadCallback(drawChart);

// Draw the chart and set the chart values
function drawChart() {
  var data = google.visualization.arrayToDataTable([
  ['Task', 'Hours per Day'],
  ['Neutral', 5],
  ['Depressed', 2],
]);

  // Optional; add a title and set the width and height of the chart
  var options = {'title':'All tweets from students', 'width':550, 'height':400, 'backgroundColor': '#23273d','titleTextStyle': {
'color': 'White'}, 'legend': 
        {'textStyle': {'color': 'white', 'font-family': 'Times New Roman'}},
        'is3D': true,'chartArea': {'width': 500, 'height': 300}};
  
  // Display the chart inside the <div> element with id="piechart"
  var chart = new google.visualization.PieChart(document.getElementById('piechart'));
  chart.draw(data, options);
}
