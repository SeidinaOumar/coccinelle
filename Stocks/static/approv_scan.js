document.getElementById('barcode').addEventListener('input', function(e) {
    const code = e.target.value;
    if (code.length >= 6) {  // Optionnel : seuil de validité
        fetch(`/get-product/?barcode=${code}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const produit = data.produit;
                document.getElementById('product-info').style.display = 'block';
                document.getElementById('product-name').textContent = produit.nom;
                document.getElementById('product-ref').textContent = produit.reference;
                document.getElementById('product-stock').textContent = produit.stock_actuel;
                document.getElementById('product-price-buy').textContent = produit.prix_achat;
               document.getElementById('product-price-sell').textContent = produit.prix_vente;

                document.getElementById('product-image').src = produit.image_url;
            } else {
                alert(data.message);
            }
        });
    }
});