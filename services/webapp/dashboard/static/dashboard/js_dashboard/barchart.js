window.onload = function () {

    var chart = new CanvasJS.Chart("chartContainer", {
        animationEnabled: true,
        exportEnabled: true,
        theme: "light1", // "light1", "light2", "dark1", "dark2"
        title:{
            text: "Simple Column Chart with Index Labels"
        },
        data: [{
            type: "column", //change type to bar, line, area, pie, etc
            //indexLabel: "{y}", //Shows y value on all Data Points
            indexLabelFontColor: "#5A5757",
            indexLabelPlacement: "outside",
            dataPoints: [
                { x: 10, y: 71,indexLabel: "Highest"  },
                { x: 20, y: 55, indexLabel: "Lowest" },
            ]
        }]
    });
    chart.render();
    
    }