google.charts.load('current', {'packages':['table']});
google.charts.setOnLoadCallback(drawTable);

function drawTable() {
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'Index');
    data.addColumn('string','Text');
    data.addColumn('string','Date')                
    data.addColumn('string', 'Status');
    data.addRows([
    ['1', 'i want to die','28-09-2019','negative'],
    ['2', 'i want to die','28-09-2019','negative'],
    ['3', 'i want to die','28-09-2019','negative']
    ]);

    var options = {
        showRowNumber: true,
        width: '100%', 
        height: '100%',
        'backgroundColor': '#313348'
     };
           
     // Instantiate and draw the chart.
     var chart = new google.visualization.Table(document.getElementById('table_div'));
     chart.draw(data, options);
  }
  google.charts.setOnLoadCallback(drawChart);
