var ctx = document.getElementById('myChart').getContext('2d');

new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['Jan','Feb','Mar','Apr','May','Jul','Aug'],
      datasets: [{ 
          data: [56,69,90,46,64,69,89],
          label: "Stress score",
          borderColor: "#3e95cd",
          fill: false,
          borderWidth: 1
        },
      ]
    },
    options: {
    
    }
  });