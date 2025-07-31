function openDeletePopup(url,produitId, nom_frs) {
    const popup = document.getElementById('popup-confirm');
    const form = document.getElementById('popup-delete-form');
    const message = document.getElementById('popup-message');

    message.textContent = `Voulez-vous vraiment supprimer "${nom_frs}" ?`;
    form.action = url;

    popup.style.display = 'flex';
  }

  function closePopup() {
    document.getElementById('popup-confirm').style.display = 'none';
  }