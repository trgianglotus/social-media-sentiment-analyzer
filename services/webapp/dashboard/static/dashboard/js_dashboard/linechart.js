function drawChart() {
   // Define the chart to be drawn.
   var data = new google.visualization.DataTable();
   data.addColumn('string', 'Month');
   data.addColumn('number', 'Sentiment');
   
   data.addRows([
     ['Jan',  7.0],
     ['Feb',  6.9],
     ['Mar',  9.5],
     ['Apr',  14.5],
     ['May',  18.2],
     ['Jun',  21.5],
     
     ['Jul',  25.2],
     ['Aug',  26.5],
     ['Sep',  23.3],
     ['Oct',  18.3],
     ['Nov',  13.9],
     ['Dec',  9.6]
   ]);
     
   // Set chart options
   var options = {'title' : 'Sentiment level in %','titleTextStyle': {
      'color': 'White'},
     hAxis: {
         title: 'Month','color': 'white'
     },
     vAxis: {
         title: 'sentiment Level'
     },   
     pointsVisible: true,'width':565, 'height':400, 'backgroundColor': '#313348','titleTextStyle': {
      'color': 'White'},'legend': {'textStyle': {'color': 'white'},position: 'top', alignment: 'start'},'is3D': true,'chartArea': {'width': 450, 'height': 300}	  
   };

   // Instantiate and draw the chart.
   var chart = new google.visualization.LineChart(document.getElementById('linecon'));
   chart.draw(data, options);
}
google.charts.setOnLoadCallback(drawChart);