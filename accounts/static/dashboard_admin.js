
const ctxLine = document.getElementById('lineChart');

const ctxBar = document.getElementById('barChart').getContext('2d');

  fetch("/accounts/api/ventes-semaine/")
    .then(response => response.json())
    .then(data => {
      new Chart(ctxBar, {
        type: 'bar',
        data: {
          labels: data.labels, // Exemple : ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
          datasets: [{
            label: 'Ventes',
            data: data.data, // Données dynamiques
            backgroundColor: 'red'
          }]
        },
        options: {
          responsive: true,
          plugins: { legend: { display: false } },
          scales: {
            y: { ticks: { color: 'white' }, beginAtZero: true },
            x: { ticks: { color: 'white' } }
          }
        }
      });
    })
    .catch(error => {
      console.error("Erreur de chargement des données du graphique :", error);
    });

new Chart(ctxLine, {
  type: 'line',
  data: {
    labels: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai'],
    datasets: [{
      label: 'Évolution des ventes',
      data: [50000, 60000, 40000, 80000, 70000],
      borderColor: 'red',
      borderWidth: 2,
      fill: false
    }]
  },
  options: {
    responsive: true,
    plugins: { legend: { display: false } },
    scales: {
      y: { ticks: { color: 'white' } },
      x: { ticks: { color: 'white' } }
    }
  }
});





