document.addEventListener('DOMContentLoaded', function () {

  document.getElementById('remise-global').addEventListener('input', afficherPanier);
  

  const panier = [];
  let client = null;
  
  const cartBody = document.getElementById('cart-body');
  const totalPriceEl = document.getElementById('total-price');
  
  let totalGlobalAvecRemise = 0;

  const inputNumClient = document.getElementById('client-num');
  const inputNomClient = document.getElementById('client-name');
  const inputContactClient = document.getElementById('client-contact');
  const inputPointClient = document.getElementById('client-point');
  const barcodeArea = document.getElementById('barcode-scanner');
  const searchInput = document.getElementById('search-nom-produit');
  const resultatsListe = document.getElementById('resultats-produits');

  const btnValiderVente = document.getElementById('btn-valider-vente');
  const btnAddClient = document.getElementById('btn-add-client');
  const montantRecuInput = document.getElementById("montantRecu");
  const montantRenduDisplay = document.getElementById("montantRendu");
  const sonAlerteStock = new Audio('/static/audio/alerte_danger.mp3');
  const sonProduitTrouve = new Audio('/static/audio/succes1.ogg');
  const sonProduitNonTrouve = new Audio('/static/audio/error.mp3');


  // 📦 Scanner de code-barres (appuyer sur "Entrée" après scan)
  barcodeArea.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') {
      e.preventDefault();
      ajouterProduit();
    }
  });
  
// 🔍 Recherche par nom
searchInput.addEventListener('input', function () {
  const query = this.value.toLowerCase();
  resultatsListe.innerHTML = '';

  if (query.length < 1) return;

  fetch(`/vente/api/produit/?search=${query}`)  // 🔁 À adapter selon ton API
    .then(res => res.json())
    .then(data => {
      if (data.success && data.produits.length > 0) {
        data.produits.forEach(prod => {
          const li = document.createElement('li');
          li.className = 'list-group-item list-group-item-action';
          li.innerHTML = `<i class="bi bi-plus-circle text-success me-2"></i> ${prod.nom_produit}`;
          li.addEventListener('click', () => {
            ajouterProduitManuellement(prod);
            searchInput.value = '';
            resultatsListe.innerHTML = '';
          });
          resultatsListe.appendChild(li);
        });
      }
    });
});

  // 🔍 Ajouter un client (ou récupérer infos client existant)
  btnAddClient.addEventListener('click', chercherClient);

  // ✅ Valider la vente
  btnValiderVente.addEventListener('click', validerVente);

  // 🎯 Ajouter produit au panier
  function ajouterProduit() {
    const code = barcodeArea.value.trim();

    if (!code) return alert('Merci de scanner un code-barres.');

    fetch(`/vente/api/produit/?code=${code}`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const prod = data.produit;
                // === Jouer son produit trouvé ===
                sonProduitTrouve.currentTime = 0;
               sonProduitTrouve.play();
                const index = panier.findIndex(p => p.id_produit === prod.id_produit);
                const quantiteActuelle = index > -1 ? panier[index].quantite : 0;
                const stockDisponible = prod.quantite;

                if (quantiteActuelle + 1 > stockDisponible) {
                    // 🔊 Joue un son d'alerte si le stock est insuffisant
                    sonAlerteStock.currentTime = 0;
                    sonAlerteStock.play();

                    alert(`❌ Stock insuffisant pour ce produit !\nStock disponible : ${stockDisponible}`);
                    barcodeArea.value = '';
                    barcodeArea.focus();
                    return;
                }

                if (index > -1) {
                    panier[index].quantite += 1;
                } else {
                    panier.push({
                        image_url : prod.image_url,
                        id_produit: prod.id_produit,
                        nom_produit: prod.nom_produit,
                        reference: prod.reference,
                        quantite: 1,
                        prix_unitaire: parseFloat(prod.prix_vente),
                        remise: 0,
                        stock: prod.quantite  // ✅ important pour les contrôles

                    });
                }
                
                afficherPanier();
                barcodeArea.value = '';
                barcodeArea.focus();
            } else {
              // === Jouer son produit non trouvé ===
              sonProduitNonTrouve.currentTime = 0;
          sonProduitNonTrouve.play();
                alert(data.message || 'Produit non trouvé');
            }
        })
        .catch(() => alert('Erreur lors de la récupération du produit'));
}
function ajouterProduitManuellement(prod) {
  const index = panier.findIndex(p => p.id_produit === prod.id_produit);
  const quantiteActuelle = index > -1 ? panier[index].quantite : 0;
  const stockDisponible = prod.quantite;

  if (quantiteActuelle + 1 > stockDisponible) {
    const audio = new Audio('/static/audio/alerte_danger.mp3');
    audio.play();
    alert(`❌ Stock insuffisant pour ce produit !\nStock disponible : ${stockDisponible}`);
    return;
  }

  if (index > -1) {
    panier[index].quantite += 1;
  } else {
    panier.push({
      image_url: prod.image_url,
      id_produit: prod.id_produit,
      nom_produit: prod.nom_produit,
      reference: prod.reference,
      quantite: 1,
      prix_unitaire: parseFloat(prod.prix_vente),
      remise: 0,
      stock: prod.quantite  // ➕ Ajout pour contrôle plus tard
    });
  }
   sonProduitTrouve.currentTime = 0;
    sonProduitTrouve.play();
  afficherPanier();
}




  // 🔍 Chercher un client
  function chercherClient() {
    const numero = inputNumClient.value.trim();
    if (!numero) return alert('Merci de saisir un numéro client');

    fetch(`/vente/client/?numero=${numero}`)
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          client = data.client;
          inputNomClient.innerHTML =  `${client.nom} `;
          inputContactClient.innerHTML = ` ${client.telephone }`;
          inputPointClient.innerHTML =  `${client.point} `;
        } else {
          // Client non trouvé, création fictive
          const idAleatoire = Math.floor(Math.random() * 10000);
          client = {
            id: null,
            nom: numero,
            telephone: 'N/A',
            code: numero,
          };
          inputNomClient.value = client.nom;
          inputContactClient.value = client.telephone;
        }
      })
      .catch(() => alert('Erreur lors de la recherche client'));
  }

  

  // 🧾 Afficher panier
function afficherPanier() {
  cartBody.innerHTML = ''; // Vider le panier affiché

  if (panier.length === 0) {
    cartBody.innerHTML = `<div class="text-muted text-center py-3">Votre panier est vide</div>`;
    totalPriceEl.innerHTML = ' 0 FCFA';
    return;
  }

  let total = 0;
  const fragment = document.createDocumentFragment();

  panier.forEach((p, index) => {
    const sousTotal = p.quantite * p.prix_unitaire * (1 - (p.remise || 0) / 100);
    total += sousTotal;

    const card = document.createElement('div');
   card.className = 'panier-item-card card py-2 px-2 d-flex flex-row align-items-center shadow-sm rounded-3 mb-2';
   card.style.gap = '0.5rem';
   card.style.width = '48%';
   card.style.minWidth = '100px';



  card.innerHTML = `
  <div class="d-flex align-items-center w-100">

    <!-- Image du produit -->
    <img src="${p.image_url}" alt="Image produit" class="rounded me-2" 
         style="width: 60px; height: 60px; object-fit: cover; flex-shrink: 0;">

    <!-- Infos produit (nom, ref) -->
    <div class="flex-grow-1 me-3">
      <h6 class="mb-1" style="font-size: 14px; white-space: normal;" title="${p.nom_produit}">
        ${p.nom_produit}
      </h6>
      <small class="text-muted">Réf : ${p.reference}</small>
    </div>

    <!-- Contrôle quantité -->
    <div class="quantity-controls d-flex flex-column align-items-center me-3" style="margin-top: -5px;">
      <small class="text-muted mb-1" style="font-size: 12px;">Quantité</small>
      <input 
        type="number" 
        class="form-control form-control-sm qty-value" 
        min="1" max="99" 
        value="${p.quantite}" 
        data-index="${index}" 
        style="width: 60px; text-align: center;" 
      >
    </div>

    <!-- Prix unitaire et total -->
    <div class="text-end me-3" style="min-width: 100px;">
      <small class="text-muted d-block" style="font-size: 11px;">PU : ${p.prix_unitaire.toFixed(0).toLocaleString()} FCFA</small>
      <strong class="text-danger d-block" style="font-size: 14px;">
        ${sousTotal.toFixed(0).toLocaleString()} FCFA
      </strong>
    </div>

    <!-- Bouton supprimer -->
    <button class="btn btn-danger btn-sm btn-delete" title="Supprimer">
      <i class="bi bi-trash3-fill"></i>
    </button>
  </div>
`;



    // Gestion des boutons de quantité
// Gestion des boutons de quantité
 const inputQty = card.querySelector('.qty-value');

  // Variables pour gérer la quantité (une seule déclaration)
  let quantiteScannee = p.quantite;
  let ancienneValeur = p.quantite;

  // Événement input
  inputQty.addEventListener('input', function () {
    const nouvelleQuantite = parseInt(this.value);
    const idx = parseInt(this.dataset.index);
    const stockDisponible = panier[idx].stock || 99;

    if (isNaN(nouvelleQuantite) || nouvelleQuantite < 1) {
      this.classList.remove("is-invalid");
      return;
    }

    if (nouvelleQuantite > stockDisponible) {
      this.classList.add("is-invalid");
      return;
    }

    panier[idx].quantite = nouvelleQuantite;
    ancienneValeur = nouvelleQuantite;
    quantiteScannee = nouvelleQuantite; // Accepte la modif
    this.classList.remove("is-invalid");

    const sousTotal = panier[idx].quantite * panier[idx].prix_unitaire * (1 - (panier[idx].remise || 0) / 100);
    card.querySelector('.fw-bold').textContent = `${sousTotal.toFixed(0).toLocaleString()} FCFA`;

    mettreAJourMontantRendu();

    const remiseGlobale = parseFloat(document.getElementById('remise-global').value) || 0;
    const total = panier.reduce((acc, p) => acc + p.quantite * p.prix_unitaire * (1 - (p.remise || 0) / 100), 0);
    const totalAvecRemise = total * (1 - remiseGlobale / 100);
    totalPriceEl.innerHTML = ` ${totalAvecRemise.toFixed(0).toLocaleString()} FCFA`;
  });

  // Événement blur
  inputQty.addEventListener('blur', function () {
    const idx = parseInt(this.dataset.index);
    const stockDisponible = panier[idx].stock || 99;
    let valeurActuelle = parseInt(this.value);

    if (isNaN(valeurActuelle) || valeurActuelle < 1) {
      valeurActuelle = quantiteScannee;
      this.value = valeurActuelle;
      this.classList.remove("is-invalid");
      panier[idx].quantite = valeurActuelle;
      ancienneValeur = valeurActuelle;
      return;
    }

    if (valeurActuelle > stockDisponible) {
      sonAlerteStock.currentTime = 0;
      sonAlerteStock.play();
      alert(`❌ Quantité demandée supérieure au stock disponible !\nStock disponible : ${stockDisponible}`);

      valeurActuelle = quantiteScannee;
      this.value = valeurActuelle;
      panier[idx].quantite = valeurActuelle;
      ancienneValeur = valeurActuelle;
      this.classList.remove("is-invalid");

      const sousTotal = panier[idx].quantite * panier[idx].prix_unitaire * (1 - (panier[idx].remise || 0) / 100);
      card.querySelector('.fw-bold').textContent = `${sousTotal.toFixed(0).toLocaleString()} FCFA`;

      mettreAJourMontantRendu();

      const remiseGlobale = parseFloat(document.getElementById('remise-global').value) || 0;
      const total = panier.reduce((acc, p) => acc + p.quantite * p.prix_unitaire * (1 - (p.remise || 0) / 100), 0);
      const totalAvecRemise = total * (1 - remiseGlobale / 100);
      totalPriceEl.innerHTML = ` ${totalAvecRemise.toFixed(0).toLocaleString()} FCFA`;

      return;
    }

    panier[idx].quantite = valeurActuelle;
    ancienneValeur = valeurActuelle;
    quantiteScannee = valeurActuelle;
    this.classList.remove("is-invalid");
  });




    // Suppression d’un article
    card.querySelector('.btn-delete').addEventListener('click', () => {
      panier.splice(index, 1);
      afficherPanier();
    });

    fragment.appendChild(card);
  });

  cartBody.appendChild(fragment);

  const remiseGlobale = parseFloat(document.getElementById('remise-global').value) || 0;
  const totalAvecRemise = total * (1 - remiseGlobale / 100);

  totalPriceEl.innerHTML = ` ${totalAvecRemise.toFixed(0).toLocaleString()} FCFA`;
}



  document.getElementById('remise-global').addEventListener('input', () => {
  afficherPanier();
  mettreAJourMontantRendu(); // Ajoute cette ligne
});


  // ❌ Retirer un produit
  window.retirerProduit = function (index) {
    panier.splice(index, 1);
    afficherPanier();
  };

 function mettreAJourMontantRendu() {
  const montantRecu = parseFloat(montantRecuInput.value);
  const remiseGlobale = parseFloat(document.getElementById('remise-global').value) || 0;

  // Calcule du total avec remise
  let totalSansRemiseGlobale = panier.reduce((acc, p) => {
    const sousTotal = p.quantite * p.prix_unitaire * (1 - (p.remise || 0) / 100);
    return acc + sousTotal;
  }, 0);

  const total = totalSansRemiseGlobale * (1 - remiseGlobale / 100);

  if (!isNaN(montantRecu) && !isNaN(total)) {
    const rendu = montantRecu - total;

    montantRenduDisplay.textContent = rendu >= 0
      ? `${rendu.toFixed(0)} FCFA`
      : "Montant insuffisant";

    if (rendu >= 0) {
      montantRecuInput.classList.remove("is-invalid");
      montantRecuInput.classList.add("is-valid");
      montantRenduDisplay.classList.remove("text-danger");
      montantRenduDisplay.classList.add("text-success");
    } else {
      montantRecuInput.classList.remove("is-valid");
      montantRecuInput.classList.add("is-invalid");
      montantRenduDisplay.classList.remove("text-success");
      montantRenduDisplay.classList.add("text-danger");
    }
  } else {
    montantRenduDisplay.textContent = "0 FCFA";
    montantRecuInput.classList.remove("is-valid", "is-invalid");
    montantRenduDisplay.classList.remove("text-success", "text-danger");
  }
}



  // ✅ Envoyer vente
  function validerVente() {
     if (!client) {
        // Envoie null pour id_client pour que backend crée/utilise client anonyme unique
        client = null;
    }
    if (panier.length === 0) return alert('Le panier est vide');


    const remiseGlobale = parseFloat(document.getElementById('remise-global').value) || 0;

    // Calcule du total avant remise globale
    let totalSansRemiseGlobale = panier.reduce((acc, p) => {
    const sousTotal = p.quantite * p.prix_unitaire * (1 - (p.remise || 0) / 100);
    return acc + sousTotal;
    }, 0);

// Application de la remise globale
const montanttotal = totalSansRemiseGlobale * (1 - remiseGlobale / 100);




    const venteData = {
      id_client: client ? client.id : null, // null si client non défini
      id_utilisateur: 1, // À remplacer dynamiquement
      date_vente: new Date().toISOString(),
      montanttotal: montanttotal.toFixed(0),
      remise: remiseGlobale,
      statut: 'validée',
      lignes: panier.map(p => ({
        id_produit: p.id_produit,
        quantite: p.quantite,
        prix_unitaire: p.prix_unitaire,
        remise: p.remise || 0,
      })),
    };

    fetch('/vente/valider/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      body: JSON.stringify(venteData),
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          alert(`✅ Vente validée ! Code reçu : ${data.code_facture}`);
          panier.length = 0;
          client = null;
          inputNumClient.value = '';
          inputNomClient.value = '';
          inputContactClient.value = '';
          afficherPanier();
          chargerDernieresFactures(); // Pour actualiser juste après la vente

        window.open(`/vente/facture/${data.code_facture}/`, '_blank');

    
    // ensuite tu peux mettre à jour la div avec le bouton imprimer et l'URL correcte
   
            
        } else {
          alert(data.message || 'Erreur lors de la validation');
        }
      })
      .catch(() => alert('Erreur réseau lors de la validation'));
  }

  // 🔐 Récupération du token CSRF
  function getCookie(name) {
    const cookies = document.cookie.split(';');
    for (const cookie of cookies) {
      const [key, value] = cookie.trim().split('=');
      if (key === name) return decodeURIComponent(value);
    }
    return null;
  }
  montantRecuInput.addEventListener('input', mettreAJourMontantRendu);


  const btnAnnulerClient = document.getElementById('btn-annuler-client');

btnAnnulerClient.addEventListener('click', annulerClient);

function annulerClient() {
  client = null;

  inputNumClient.value = '';
  inputNomClient.textContent = '';
  inputContactClient.textContent = '';
  inputPointClient.textContent = '';
  
  alert("✅ Client annulé !");
}


});
