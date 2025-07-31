document.addEventListener("DOMContentLoaded", function () {
    // Simuler les données (à remplacer par fetch si besoin)
    const categories = ['Boissons', 'Épicerie', 'Hygiène', 'Fruits'];
    const stocks = [120, 80, 40, 30];
    const produits = ['Coca', 'Savon', 'Farine', 'Pomme'];
    const quantites = [50, 25, 30, 15];

    // Statistiques
    

    // Graphique camembert (catégories)
    new Chart(document.getElementById("category-chart"), {
        type: "doughnut",
        data: {
            labels: categories,
            datasets: [{
                label: "Catégories",
                data: stocks,
                backgroundColor: ['#dc3545', '#ffc107', '#198754', '#0d6efd'],
                height : 160,
                hoverOffset: 6
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });

    // Graphique en barres (quantité par produit)
    new Chart(document.getElementById("supply-chart"), {
        type: "bar",
        data: {
            labels: produits,
            datasets: [{
                label: "Quantité",
                data: quantites,
                backgroundColor: '#e60026'
            }]
        },
        options: {
            responsive: true,
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true
                }
            }
        }
    });
});