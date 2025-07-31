function openDeletePopup(url,produitId, nomProduit) {
    const popup = document.getElementById('popup-confirm');
    const form = document.getElementById('popup-delete-form');
    const message = document.getElementById('popup-message');

    message.textContent = `Voulez-vous vraiment supprimer "${nomProduit}" ?`;
    form.action = url;

    popup.style.display = 'flex';
  }

  function closePopup() {
    document.getElementById('popup-confirm').style.display = 'none';
  }