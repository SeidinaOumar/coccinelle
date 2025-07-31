from django.shortcuts import render, redirect
from baseSQL.models import Produit , Stock , Approvisionnement , LigneAppro, CategorieProduit, MouvementStock, Utilisateur, Fournisseur
from django.db.models import Sum , F, Q, Func
from django.utils import timezone
from Stocks.forms import ApprovisionnementForm, ApprovisionnementForm0, CategorieForm
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from datetime import timedelta
from datetime import date
from django.db import models
from django.shortcuts import render
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.db.models.functions import TruncMonth
from baseSQL.models import Produit, CategorieProduit
from baseSQL.models import MouvementStock
from datetime import datetime, timedelta
from collections import OrderedDict



import json
# Create your views here.


# Vue pour afficher la page stock et approv
def page_stock(request):
    #1 recherche d'un produit

    query = request.GET.get('search','')

    produits = Produit.objects.all()

    if query :

        #filtre des produits par nom et reference au moment dela saisie
         produits = produits.filter(
              Q(nom_produit__icontains=query)|
              Q(reference__icontains=query)
         ) 
    # 1️⃣ Données pour le graphique circulaire (quantité par catégorie)
    categorie_data = CategorieProduit.objects.all()
    donut_labels = []
    donut_data = []

    for cat in categorie_data:
        total = Produit.objects.filter(categorie=cat).aggregate(Sum('quantite'))['quantite__sum'] or 0
        donut_labels.append(cat.nom)
        donut_data.append(total)

    # 2️⃣ Données pour les courbes (Entrées / Sorties des 6 derniers mois)
    today = timezone.now().date()

    # Initialisation des mois et données vides
    mois_labels = []
    mois_dict = OrderedDict()

    # Générer les 6 derniers mois
    for i in range(5, -1, -1):
        mois = (today.replace(day=1) - timedelta(days=30*i)).replace(day=1)
        key = mois.strftime('%Y-%m')
        mois_labels.append(mois.strftime('%b'))
        mois_dict[key] = {'entree': 0, 'sortie': 0}

    six_months_ago = (today.replace(day=1) - timedelta(days=30*5)).replace(day=1)

    # Requête avec TruncMonth (compatible MySQL et PostgreSQL)
    mouvements = (
        MouvementStock.objects
        .filter(date_mouvement__gte=six_months_ago)
        .annotate(month=TruncMonth('date_mouvement'))
        .values('month', 'type_mouvement')
        .annotate(total=Sum('quantite'))
        .order_by('month')
    )

    for mvt in mouvements:
        key = mvt['month'].strftime('%Y-%m')
        if key in mois_dict:
        # Note: adapte la casse des types de mouvement à ce que tu utilises en base
            if mvt['type_mouvement'].lower() in ['entrée', 'aprovisionement', 'approvisionnement']:
                mois_dict[key]['entree'] += mvt['total']
            elif mvt['type_mouvement'].lower() == 'sortie':
                mois_dict[key]['sortie'] += mvt['total']

    entrees = [mois_dict[k]['entree'] for k in mois_dict]
    sorties = [mois_dict[k]['sortie'] for k in mois_dict]

    # 3️⃣ Données pour le bar chart (8 produits les plus stockés)
    top_produits = Produit.objects.all().order_by('-quantite')
    bar_labels = [p.nom_produit for p in produits]
    bar_data = [p.quantite for p in produits]     

    categories = CategorieProduit.objects.all()
    form_categorie= CategorieForm()
   # TRI des produits recents
    produits = produits.order_by('-id_produit')     

   # Czlcul des indicateurs

    total_produits = Produit.objects.count()
    total_categories = CategorieProduit.objects.count()
    stock_global = Stock.objects.aggregate(total=Sum('quantite'))['total'] or 0

    #compter les produts en stock faibles

    produits_stock_faible = Produit.objects.filter(stock_actuel__lte =F('stock_min')).count()

    # VALEUR DUSTOCK PAR CATEGORIE POUR LES INDICATEURS
    valeurs_categories = (
         Produit.objects.values('categorie__nom')
         .annotate(valeur_stock=Sum(F('stock_actuel')* F('prix_achat')))
         .order_by('-valeur_stock')
    )

    ##### calcul des indices d'alertes
    produits_seuil = Produit.objects.filter(quantite__lte=models.F('stock_min'))

      # Récupération des lignes d'approvisionnement proches de l'expiration
    approv_proche_expiration = LigneAppro.objects.filter(
        id_appro__date_expiration__isnull=False,
        id_appro__date_expiration__gt=date.today(),
        id_appro__date_expiration__lte=date.today() + timedelta(days=7)
    ).select_related('id_produit', 'id_appro')

    # Récupération des lignes d'approvisionnement expirées
    approv_expire = LigneAppro.objects.filter(
        id_appro__date_expiration__lt=date.today()
    ).select_related('id_produit', 'id_appro')

    # Nombre total d’alertes
    nb_alertes_total = (
        produits_seuil.count() +
        approv_proche_expiration.count() +
        approv_expire.count()
    )


    # envoi des donnééau templates
    context = {
        # Donut
        'chart_donut_labels': donut_labels,
        'chart_donut_data': donut_data,

        # Ligne
        'chart_line_labels': mois_labels,
        'chart_line_entrees': entrees,
        'chart_line_sorties': sorties,

        # Barres
        'chart_bar_labels': [p.nom_produit for p in top_produits],
        'chart_bar_data': [p.quantite for p in top_produits],
         'produits':produits,
         'total_produits': total_produits,
         'total_categories':total_categories,
         'stock_global': stock_global,
         'produits_stock_faible':produits_stock_faible ,
         'valeurs_categories':valeurs_categories, 
         'produits_seuil': produits_seuil,
         'approv_proche_expiration': approv_proche_expiration,
         'approv_expire': approv_expire,
         
         'nb_alertes_total': nb_alertes_total,
         'categories': categories,
         'form_categorie': form_categorie,
        

    }

    return render(request,'Stocks/templates/stock.html', context)
def ajouter_categorie(request):
    if request.method == 'POST':
       form = CategorieForm(request.POST)
       if form.is_valid():
            form.save()
            messages.success(request, 'Catégorie ajoutée avec succès.')
    return redirect('stock')
def edit_categorie(request, pk):
    categorie = get_object_or_404(CategorieProduit, pk=pk)
    form = CategorieForm(request.POST or None, instance=categorie)

    if form.is_valid():
        form.save()
        messages.success(request, "✅ Catégorie mise à jour avec succès.")
        return redirect('stock')

    # Tu peux envoyer aussi la catégorie si besoin dans le template
    return render(request, 'Stocks/templates/stock.html', {
        'form': form,
        'categorie': categorie,
        'edit_mode': True  # pour différencier en template
    })

def delete_categorie(request, pk):
    categorie = get_object_or_404(CategorieProduit, pk=pk)

    if request.method == 'POST':
        # Remplace `lignevente_set` par le bon related_name si besoin
        if hasattr(categorie, 'lignevente_set') and categorie.lignevente_set.exists():
            messages.error(request, "❌ Impossible de supprimer cette catégorie car elle est liée à des produits vendus.")
        else:
            categorie.delete()
            messages.success(request, "✅ Catégorie supprimée avec succès.")
        return redirect('stock')

    return render(request, 'Stocks/templates/stock.html', {
        'categorie': categorie,
        'delete_mode': True  # utile en template
    })
        
########### vue de l'historique des mouvements   donc les donnnes sont envoyé pa API
def api_mouvements_stock00(request):
    mouvements_qs = MouvementStock.objects.select_related('produit', 'utilisateur').order_by('-date_mouvement')[:100]
    mouvements = list(mouvements_qs.values(
        'produit__nom_produit',
        'type_mouvement',
        'quantite',
        'utilisateur__role',
        'date_mouvement',
    ))
    return JsonResponse(mouvements, safe=False)

###page des mouvemennts stocks
def mouvements_page(request):
 return render(request, "Stocks/templates/mouv_stock.html" )
def api_mouvements_stock(request):
    mouvements_qs = MouvementStock.objects.select_related('produit', 'utilisateur').order_by('-date_mouvement')
    mouvements = []

    for m in mouvements_qs:
        mouvements.append({
            'produit__nom_produit': m.produit.nom_produit,
            'produit__image': m.produit.image.url if m.produit.image else None,
            'type_mouvement': m.type_mouvement,
            'quantite': m.quantite,
            'utilisateur__username': m.utilisateur.username if m.utilisateur else "Inconnu",
            'date_mouvement': m.date_mouvement.strftime('%Y-%m-%d %H:%M'),
        })

    return JsonResponse(mouvements, safe=False)

 ######  VUE DU FORMULAIRE d' AAPROVISIONNEMENT ET LE TABLEAU ancienne methode
   
def Approvisionnement_view(request):
     success = False
     form = ApprovisionnementForm()

     if request.method == 'POST':
          form = ApprovisionnementForm(request.POST)
          if form.is_valid():
               produit = form.cleaned_data['produit']
               fournisseur = form.cleaned_data['fournisseur']
               quantite = form.cleaned_data['quantite']
               prix = form.cleaned_data['prix']
               date_expiration = form.cleaned_data.get('date_expiration')

               ######  LA creation d'un nouvel approv

               approv = Approvisionnement.objects.create(
                    id_utilisateur = request.user,
                    id_frs = fournisseur,
                    date = timezone.now(),
                    montant_total=quantite*prix,
                    date_expiration= date_expiration
               )
               #### Creationde la lgne d'apporv

               LigneAppro.objects.create(
                    id_appro = approv,
                    id_produit = produit,
                    quantite = quantite,
                    prix_unitaire = prix
               )

               ### mise à jour du stock

               produit.quantite += quantite
               produit.save()




               MouvementStock.objects.create(
                    utilisateur = request.user,
                    produit = produit,
                    type_mouvement = 'Entrée',
                    quantite=quantite,
                    date_mouvement = timezone.now()
               )

               success = True
               form = ApprovisionnementForm() ### met a jour le formulaire


     approvisionnements = LigneAppro.objects.select_related('id_appro',  'id_appro__id_frs')\
                         .order_by('-id_ligneappro') [:20]     


     context = {
          'form': form,
          'produits': Produit.objects.all(),
          'fournisseurs': Fournisseur.objects.all(),
          'approvisionnements': approvisionnements,
          'success': success
     }

     return render(request, 'Stocks/templates/approv.html', context)


def get_product_by_barcode(request, codes_barres):
    try:
        produit = Produit.objects.get(codes_barres=codes_barres)
        data = {
            'success': True,
            'id_produit': produit.id_produit,
            'nom': produit.nom_produit,
            'reference': produit.reference,
            'stock': produit.quantite,
            'prix_achat': produit.prix_achat,
            'prix_vente': produit.prix_vente,
            'image_url': produit.image.url if produit.image else '/static/default.png',
        }
    except Produit.DoesNotExist:
        data = {'success': False}
    
    return JsonResponse(data)


def approvisionnement_view0(request):
    form = ApprovisionnementForm0()
    message = ""
    historique = LigneAppro.objects.select_related('id_produit', 'id_appro').order_by('-id_ligneappro')[:10]

    if request.method == "POST":
        form = ApprovisionnementForm0(request.POST)
        if form.is_valid():
            id_produit = request.POST.get("id_produit")
            produit = get_object_or_404(Produit, id_produit=id_produit)
             # 👈 récupérer depuis le champ caché
            quantite = form.cleaned_data['quantite']
            prix_achat = form.cleaned_data['prix_achat']
            prix_vente = form.cleaned_data['prix_vente']
            fournisseur = form.cleaned_data['fournisseur']
            date_expiration = form.cleaned_data.get('date_expiration')
            print("Reçu :", id_produit, quantite, prix_achat, prix_vente, fournisseur)


            # Vérification produit

            # Mise à jour du produit
            produit.quantite += quantite
            produit.prix_achat = prix_achat
            produit.prix_vente = prix_vente
            produit.save()
            

            # Enregistrement de l'approvisionnement
            approv = Approvisionnement.objects.create(
                id_utilisateur=request.user,
                id_frs=fournisseur,
                date=timezone.now(),
                montant_total=quantite * prix_achat,
                date_expiration= date_expiration,
            )

            # Ligne d’approvisionnement
            LigneAppro.objects.create(
                id_appro=approv,
                id_produit=produit,
                quantite=quantite,
                prix_unitaire=prix_achat
            )

            # Historique de mouvement
            MouvementStock.objects.create(
                produit=produit,
                type_mouvement='Entrée',
                quantite=quantite,
                utilisateur=request.user,
                commentaire='Approvisionnement via formulaire personnalisé'
            )

            messages.success(request, f"Le produit '{produit.nom_produit}' a été approvisionné avec succès.")

            form = ApprovisionnementForm0()  # Réinitialiser
            
        else:
            print("Erreurs formulaire :", form.errors)


    return render(request, "Stocks/templates/approv_scan.html", {
        "form": form,
        "message": message,
        "historique": historique
    })


######  LES INDICATEUR DE L' ALERTES STOCKS
def stock_alertes(request):
    print("✅ Vue stock_alertes appelée")
    # Produits en dessous du seuil minimum
    produits_seuil = Produit.objects.filter(quantite__lte=models.F('stock_min'))

    # Approvisionnements proches de la date d'expiration (7 jours)
    approv_proche_expiration = Approvisionnement.objects.filter(
        date_expiration__isnull=False,
        date_expiration__gt=date.today(),
        date_expiration__lte=date.today() + timedelta(days=7)
    )

    # Approvisionnements expirés
    approv_expire = Approvisionnement.objects.filter(
        date_expiration__lt=date.today()
    )

    context = {
        'produits_seuil': produits_seuil,
        'approv_proche_expiration': approv_proche_expiration,
        'approv_expire': approv_expire,
    }
    
    return render(request, 'Stocks/templates/stock.html', context)

##### liste complete des produits et crud sur cette ligne
def all_produit(request):
    produits = Produit.objects.all()
    return render(request, 'Stocks/templates/stock.html', {'produits': produits})

def edit_product(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    form = ProduitForm(request.POST or None, instance=produit)
    if form.is_valid():
       form.save()
       return redirect('liste_produit')
    return render(request, 'Stocks/templates/liste_produit.html', {'form': form})

def delete_product(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    if request.method == 'POST':
        produit.delete()
        return redirect('all_produit')
    return render(request, 'Stocks/templates/liste_produit.html', {'produit': produit}) 
    

def scan_produit(request):
    code = request.GET.get('code')
    try:
        produit = Produit.objects.get(codes_barres=code)
        data = {
            "found": True,
            "nom": produit.nom_produit,
            "reference": produit.reference,
            "prix_vente": produit.prix_vente,
            "stock_actuel": produit.quanite,
            "categorie": produit.categorie.nom if produit.categorie else "Non défini",
            "image": produit.image.url if produit.image else ""
        }
    except Produit.DoesNotExist:
        data = { "found": False }

    return JsonResponse(data)
