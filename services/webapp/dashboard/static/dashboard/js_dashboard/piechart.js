// Load google charts
google.charts.load('current', {'packages':['corechart']});
google.charts.setOnLoadCallback(drawChart);

// Draw the chart and set the chart values
function drawChart() {
  var data = google.visualization.arrayToDataTable([
  ['Task', 'Hours per Day'],
  ['Happy', 2],
  ['Sad', 5],
  ['Neutral', 2],
]);

  // Optional; add a title and set the width and height of the chart
  var options = {'title':'My Average Day', 'width':550, 'height':400, 'backgroundColor': '#313348','titleTextStyle': {
'color': 'White'},'legend': {'textStyle': {'color': 'white'}},'is3D': true,'chartArea': {'width': 500, 'height': 300}};
  
  // Display the chart inside the <div> element with id="piechart"
  var chart = new google.visualization.PieChart(document.getElementById('piechart'));
  chart.draw(data, options);
}