from django.shortcuts import render
# vente/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from baseSQL.models import Produit, Client, Vente, LigneVente, Facture, MouvementStock, Utilisateur, RetourProduit, LigneRetour
from django.utils import timezone
from django.db import transaction
from .forms import ClientForm
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.db.models import Sum, F, Count
import json
from django.http import JsonResponse
from decimal import Decimal
from django.db.models.functions import TruncDay
from django.utils.dateparse import parse_datetime
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa  # ou utiliser WeasyPrint
from django.utils.dateparse import parse_datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


import json
def nouvelle_vente(request):
    produits = Produit.objects.all()
    return render(request, 'Vente/templates/vente.html', {'produits': produits})

def rechercher_client(request):
    contact = request.GET.get("contact")
    try:
        client = Client.objects.get(contact=contact)
        data = {
            'id': client.id_client,
            'nom': client.nom_client,
            'email': client.email,
            'adresse': client.adresse,
            'point': client.point,
            'tel': client.contact
        }
    except Client.DoesNotExist:
        data = {'id': None}
    return JsonResponse(data)

def rechercher_produit(request):
    query = request.GET.get("q", "")
    produits = Produit.objects.filter(nom_produit__icontains=query)[:10]
    results = [
        {'id': p.id_produit, 'nom': p.nom_produit, 'ref': p.reference, 'prix': float(p.prix_vente), 'quantite': p.quantite}
        for p in produits
    ]
    return JsonResponse(results, safe=False)


####  VOICI LA LONGUE ET PUISSANTE PROCCESSUS DE VENTE QUI ENVOI LES DONNEE AVEC AJAX JS
#### POUR QUE L4AFFICHAGE DES PRODUITS SOIT TRIER  ET LE CLIENT AUSSI
@csrf_exempt
@transaction.atomic
def enregistrer_vente(request):
    if request.method == "POST":
        data = json.loads(request.body)
        client_id = data.get('client_id')

        client = None
        if client_id:
            try:
                client = Client.objects.get(id_client=int(client_id))
            except (Client.DoesNotExist, ValueError):
                try:
                    client = Client.objects.get(contact=client_id)
                except Client.DoesNotExist:
                    client = None

        lignes = data.get("produits", [])  #  recuperation du tableau

        if not lignes:
            return JsonResponse({'success': False, 'message': "Aucun produit reçu."})

        total = 0
        vente = Vente.objects.create(
            id_client=client if client else None,
            id_utilisateur=request.user,
            date_vente=timezone.now(),
            montanttotal=0,
            statut="validée"
        )

        for ligne in lignes:
            try:
                prod = Produit.objects.get(pk=int(ligne['id_produit']))
            except Produit.DoesNotExist:
                return JsonResponse({'success': False, 'message': f"Produit ID {ligne['id_produit']} introuvable."})

            qte = int(ligne['quantite'])
            prix = prod.prix_vente  # on prend le prix depuis la base
            if qte > prod.quantite:
                return JsonResponse({'success': False, 'message': f"Stock insuffisant pour {prod.nom_produit}."})

            sous_total = qte * prix

            LigneVente.objects.create(
                id_vente=vente,
                id_produit=prod,
                quantite=qte,
                prix_unitaire=prix,
                sous_total=sous_total
            )

            prod.quantite -= qte
            prod.save()
            total += sous_total

        vente.montanttotal = total
        vente.save()

        MouvementStock.objects.create(
            utilisateur=request.user,
            produit=prod,
            type_mouvement='Sortie',
            quantite=qte,
            date_mouvement=timezone.now()
        )

        code_facture = f"FACT{str(vente.id_vente).zfill(6)}"
        Facture.objects.create(
            id_vente=vente,
            code_facture=code_facture,
            date_emission=timezone.now(),
            date_paiement=timezone.now(),
            montant_ht=total,
            montant_ttc=total,
            montant_net=total,
            mode_paiement='cash'
        )

        if client:
            client.point += int(total // 10000) * 10
            client.save()

        return JsonResponse({'success': True, 'message': 'Vente enregistrée avec succès', 'id_vente': vente.id_vente})
    
    ####ce Vue est pour la facture courante après la vente
def facture_view1(request, id_vente):
    facture = Facture.objects.get(id_vente = id_vente)
    lignes = LigneVente.objects.filter(id_vente= id_vente)
    return render(request, 'Vente/templates/fact.html', {
        'facture': facture,
        'lignes': lignes
    })


####test pour l'historique des  achats clients

def facture_view01(request, id_vente):
    facture = Facture.objects.get(id_facture = id_vente)
    lignes = LigneVente.objects.filter(id_vente= id_vente)
    return render(request, 'Vente/templates/fact.html', {
        'facture': facture,
        'lignes': lignes
    })

#### vente avec scan essai

# dans views.py de l'app vente
from django.http import JsonResponse
from baseSQL.models import Produit

# views.py dans app vente ou baseSQL
from django.http import JsonResponse
from baseSQL.models import Produit

def chercher_produit_par_code_barres(request):

    code = request.GET.get('code', '').strip()
    search = request.GET.get('search', '').strip()

    # 🔍 Recherche par code-barres
    if code:
        try:
            produit = Produit.objects.get(codes_barres=code)
            data = {
                'id_produit': produit.id_produit,
                'nom_produit': produit.nom_produit,
                'prix_vente': float(produit.prix_vente),
                'quantite': produit.quantite,
                'reference': produit.reference,
                'image_url': produit.image.url if produit.image else '',
            }
            return JsonResponse({'success': True, 'produit': data})
        except Produit.DoesNotExist:
            return JsonResponse({'success': False, 'message': "Produit non trouvé"})

    # 🔍 Recherche par nom (autocomplétion)
    elif search:
        produits = Produit.objects.filter(nom_produit__icontains=search)[:10]
        data = []
        for p in produits:
            data.append({
                'id_produit': p.id_produit,
                'nom_produit': p.nom_produit,
                'prix_vente': float(p.prix_vente),
                'quantite': p.quantite,
                'reference': p.reference,
                'image_url': p.image.url if p.image else '',
            })
        return JsonResponse({'success': True, 'produits': data})

    # ❌ Aucun paramètre fourni
    return JsonResponse({'success': False, 'message': "Code-barres ou nom manquant"})


def chercher_ou_creer_client(request):
    numero = request.GET.get('numero', '').strip()
    if not numero:
        return JsonResponse({'success': False, 'message': "Numéro manquant"})

    # Chercher client existant
    client = Client.objects.filter(contact=numero).first()
    if client:
        data = {
            'id': client.id_client,
            'nom': client.nom_client,
            'telephone': client.contact,
            'email': client.email or '',
            'point' : client.point
            # autres champs si besoin
        }
        return JsonResponse({'success': True, 'client': data})

    # Si client non trouvé, ne PAS créer, renvoyer une erreur
    return JsonResponse({'success': False, 'message': "Client non trouvé"})


@csrf_exempt
def ajouter_client(request):
    if request.method == "POST":
        data = json.loads(request.body)
        nom_client = data.get("nom_client")
        contact = data.get("contact", "")
        adresse = data.get("adresse", "")

        if not nom_client:
            return JsonResponse({"status": "error", "message": "Le nom est requis."})
        
        if Client.objects.filter(contact=contact).exists():
            return JsonResponse({"status": "error", "message": "Ce numéro existe déjà."})

        client = Client.objects.create(
            nom_client=nom_client,
            contact=contact,
            adresse=adresse
        )

        return JsonResponse({
            "status": "success",
            "message": "Client ajouté avec succès",
            "client": {
                "id": client.id_client,
                "nom": client.nom_client,
                "contact": client.contact,
                "adresse": client.adresse,
                "point": client.point
            }
        })

    return JsonResponse({"status": "error", "message": "Requête invalide"})



def api_produit(request):
    code = request.GET.get('code', '').strip()
    search = request.GET.get('search', '').strip()

    # 📦 Si code-barres fourni
    if code:
        try:
            produit = Produit.objects.get(codes_barres=code)
            data = {
                'id_produit': produit.id_produit,
                'nom_produit': produit.nom_produit,
                'prix_vente': float(produit.prix_vente),
                'quantite': produit.quantite,
                'reference': produit.reference,
                'image_url': produit.image.url if produit.image else '',
            }
            return JsonResponse({'success': True, 'produit': data})
        except Produit.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Produit non trouvé'}, status=404)

    # 🔍 Si recherche par nom
    elif search:
        produits = Produit.objects.filter(nom_produit__icontains=search)[:10]
        resultats = []
        for p in produits:
            resultats.append({
                'id_produit': p.id_produit,
                'nom_produit': p.nom_produit,
                'prix_vente': float(p.prix_vente),
                'quantite': p.quantite,
                'reference': p.reference,
                'image_url': p.image.url if p.image else '',
            })
        return JsonResponse({'success': True, 'produits': resultats})

    # ❌ Aucun paramètre fourni
    return JsonResponse({'success': False, 'message': 'Code-barres ou recherche manquante'}, status=400)


    


from django.db import transaction

@csrf_exempt
def valider_vente(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée'}, status=405)
    try:
        data = json.loads(request.body)
        
        id_client = data.get('id_client')
        utilisateur = request.user
        montanttotal = data.get('montanttotal')
        remise = data.get('remise', 0)
        statut = data.get('statut', 'validée')
        lignes = data.get('lignes', [])

        # Si aucun client envoyé, récupérer ou créer le client anonyme unique
        if not id_client:
            client_anonyme, created = Client.objects.get_or_create(
                nom_client="Client-Anonyme",
                defaults={'contact': 'N/A', 'email': ''}
            )
            client = client_anonyme
        else:
            client = Client.objects.get(id_client=id_client)

        with transaction.atomic():
            vente = Vente.objects.create(
                id_client=client,
                id_utilisateur=utilisateur,
                date_vente=timezone.now(),
                montanttotal=montanttotal,
                remise=remise,
                statut=statut,
            )

            for ligne in lignes:
                produit = Produit.objects.get(pk=int(ligne['id_produit']))
                quantite = ligne['quantite']
                prix_unitaire = ligne['prix_unitaire']
                sous_total = quantite * prix_unitaire
                
                LigneVente.objects.create(
                    id_vente=vente,
                    id_produit=produit,
                    quantite=quantite,
                    prix_unitaire=prix_unitaire,
                    sous_total=sous_total
                )

                produit.quantite -= quantite
                produit.save()

                MouvementStock.objects.create(
                    utilisateur=utilisateur,
                    produit=produit,
                    type_mouvement='Sortie',
                    quantite=quantite,
                    date_mouvement=timezone.now()
                )

            code_facture = f"RECU{str(vente.id_vente).zfill(6)}"
            Facture.objects.create(
                id_vente=vente,
                code_facture=code_facture,
                date_emission=timezone.now(),
                date_paiement=timezone.now(),
                montant_ht=vente.montanttotal,
                montant_ttc=vente.montanttotal,
                montant_net=vente.montanttotal,
                mode_paiement='cash'
            )

        return JsonResponse({'success': True, 'code_facture': code_facture, 'id_vente': vente.id_vente})

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
    



##### vue pur afficher les trois derniere ventes sur l'esoacce vente
###   MAIS PAR UTLISATEUR

   
    
def latest_factures(request):
    utilisateur = request.user  # ✅ Utilisateur connecté
    
    factures = Facture.objects.filter(
        id_vente__id_utilisateur=utilisateur
    ).select_related('id_vente__id_client').order_by('-date_emission')[:3]
    
    data = {
        'factures': [
            {
                'id': f.id_facture,
                'code_facture': f.code_facture,
                'client': f.id_vente.id_client.nom_client if f.id_vente.id_client else "Client anonyme",
            }
            for f in factures
        ]
    }
    return JsonResponse(data)


def imprimer_facture(request, code_facture):
    facture = get_object_or_404(Facture, code_facture=code_facture)
    vente = facture.id_vente
    lignes_vente = LigneVente.objects.filter(id_vente=vente)

    context = {
        'facture': facture,
        'vente': vente,
        'lignes_vente': lignes_vente,
    }

    return render(request, 'Vente/templates/fact.html', context)

def facture_view00(request, id_vente):
    facture = Facture.objects.get(id_vente = id_vente)
    lignes = LigneVente.objects.filter(id_vente= id_vente)
    return render(request, 'Vente/templates/fact.html', {
        'facture': facture,
        'lignes': lignes
    })

################ ======== RAPPORTS DES VENTES +++++++++++++ #########
def rapport(request):
    date1 = request.GET.get('date1')
    date2 = request.GET.get('date2')
    caissier_id = request.GET.get('caissier')
    produit_query = request.GET.get('produit')
    nom = request.user.first_name
    prenom = request.user.last_name
    ventes = Vente.objects.all()

    # Filtrage par date
    if date1 and date2:
       dt1 = parse_datetime(date1)  # convertit la chaîne en datetime Python
       dt2 = parse_datetime(date2)
       if dt1 and dt2:
         ventes = ventes.filter(date_vente__range=[dt1, dt2])
    # Filtrage par caissier
    if caissier_id:
        ventes = ventes.filter(id_utilisateur__id_utilisateur=caissier_id)

    # Filtrage par produit
    if produit_query:
        ventes = ventes.filter(lignevente__id_produit__nom_produit__icontains=produit_query)

    ventes = ventes.distinct()

    # Statistiques
    total_ventes = ventes.aggregate(total=Sum('montanttotal'))['total'] or 0
    total_clients = ventes.values('id_client').distinct().count()
    total_produits = LigneVente.objects.filter(id_vente__in=ventes).aggregate(qte=Sum('quantite'))['qte'] or 0

    # Calcul des bénéfices
    lignes = LigneVente.objects.filter(id_vente__in=ventes).annotate(
        benefice=F('prix_unitaire') - F('id_produit__prix_achat'),
        gain=F('quantite') * (F('prix_unitaire') - F('id_produit__prix_achat'))
    )
    total_benefices = lignes.aggregate(total=Sum('gain'))['total'] or 0

    #  SPARKLINES
    # ventes
    sparkline_ventes = ventes.annotate(jour=TruncDay('date_vente')) \
    .values('jour') \
    .annotate(total=Sum('montanttotal')) \
    .order_by('jour')

    sparkline_ventes_data = [float(item['total']) for item in sparkline_ventes]
    # CLIENTS
    sparkline_clients = ventes.annotate(jour=TruncDay('date_vente')) \
    .values('jour') \
    .annotate(count=Count('id_client', distinct=True)) \
    .order_by('jour')

    sparkline_clients_data = [int(item['count']) for item in sparkline_clients]
    #produits
    lignes_filtrees = LigneVente.objects.filter(id_vente__in=ventes)

    sparkline_produits = lignes_filtrees.annotate(jour=TruncDay('id_vente__date_vente')) \
    .values('jour') \
    .annotate(qte=Sum('quantite')) \
    .order_by('jour')

    sparkline_produits_data = [int(item['qte']) for item in sparkline_produits]
    #Benefices
    sparkline_benefices = lignes.annotate(jour=TruncDay('id_vente__date_vente')) \
    .values('jour') \
    .annotate(total=Sum('gain')) \
    .order_by('jour')

    sparkline_benefices_data = [float(item['total']) for item in sparkline_benefices]




    # Histogramme des ventes par date
    histogramme = ventes.values('date_vente__date').annotate(total=Sum('montanttotal')).order_by('date_vente__date')
    histogramme_data = [
        {
            'date': entry['date_vente__date'].strftime('%Y-%m-%d'),
            'total': float(entry['total']) if isinstance(entry['total'], Decimal) else entry['total']
        }
        for entry in histogramme
    ]

    # Top produits
    top_produits = LigneVente.objects.filter(id_vente__in=ventes).values(
        'id_produit__nom_produit'
    ).annotate(
        quantite=Sum('quantite')
    ).order_by('-quantite')[:5]
    top_produits_data = [
        {
            'nom_produit': entry['id_produit__nom_produit'],
            'quantite': float(entry['quantite']) if isinstance(entry['quantite'], Decimal) else entry['quantite']
        }
        for entry in top_produits
    ]

    # Ventes par caissier
    ventes_par_caissier = ventes.values(
        'id_utilisateur__username'
    ).annotate(total=Sum('montanttotal'))
    ventes_par_caissier_data = [
    {
        'caissier': entry['id_utilisateur__username'],
        'total': float(entry['total']) if entry['total'] else 0
    }
    for entry in ventes_par_caissier
]


    # Liste des caissiers pour le filtre
    caissiers = Utilisateur.objects.filter(role='caissier')

    context = {
        'nom' : nom,
        'prenom': prenom,
        'ventes': ventes,
        'total_ventes': total_ventes,
        'total_clients': total_clients,
        'total_produits': total_produits,
        'total_benefices': total_benefices,
        'histogramme': json.dumps(histogramme_data),
        'top_produits': json.dumps(top_produits_data),
        'ventes_par_caissier': json.dumps(ventes_par_caissier_data),
        'sparkline_ventes': sparkline_ventes_data,
        'sparkline_clients': sparkline_clients_data,
        'sparkline_produits': sparkline_produits_data,
        'sparkline_benefices': sparkline_benefices_data,
        'caissiers': caissiers,
    }
    
    return render(request, 'Vente/templates/rapport.html', context)

def export_rapport_pdf(request):
    date1 = request.GET.get('date1')
    date2 = request.GET.get('date2')
    caissier_id = request.GET.get('caissier')
    produit_query = request.GET.get('produit')
    nom = request.user.first_name
    prenom = request.user.last_name
    ventes = Vente.objects.all()

    # Filtrage identique à la vue principale
    if date1 and date2:
        dt1 = parse_datetime(date1)
        dt2 = parse_datetime(date2)
        if dt1 and dt2:
            ventes = ventes.filter(date_vente__range=[dt1, dt2])

    if caissier_id:
        ventes = ventes.filter(id_utilisateur__id_utilisateur=caissier_id)

    if produit_query:
        ventes = ventes.filter(lignevente__id_produit__nom_produit__icontains=produit_query)

    ventes = ventes.distinct()

    # Statistiques
    total_ventes = ventes.aggregate(total=Sum('montanttotal'))['total'] or 0
    total_produits = sum(v.lignevente_set.aggregate(total=Sum('quantite'))['total'] or 0 for v in ventes)
    total_clients = ventes.values('id_client').distinct().count()

    # Template HTML spécifique au PDF
    template = get_template('rapport_pdf.html')
    context = {
        'ventes': ventes,
        'total_ventes': total_ventes,
        'total_produits': total_produits,
        'total_clients': total_clients,
        'nom': nom,
        'prenom' : prenom,
    }

    html = template.render(context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="rapport_ventes.pdf"'

    pisa.CreatePDF(html, dest=response)
    return response


######## =======**///////  RETOUR PRODUIT =====/////***######
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from baseSQL.models import Facture, LigneVente  # adapte selon ton import

def retour_produit_page(request):
    return render(request, 'Vente/templates/retour_produit.html')

@api_view(['GET'])
def facture_detail(request, code_facture):
    try:
        facture = Facture.objects.get(code_facture=code_facture)
    except Facture.DoesNotExist:
        return Response({"error": "Facture non trouvée."}, status=status.HTTP_404_NOT_FOUND)
    
    vente = facture.id_vente  # C'est l'objet Vente lié à la facture

    # Récupérer toutes les lignes de vente associées à cette vente
    lignes_vente = LigneVente.objects.filter(id_vente=vente)

    produits_data = []
    for ligne in lignes_vente:
        produit = ligne.id_produit
        produits_data.append({
            "id": produit.id_produit,
            "nom": produit.nom_produit,
            "image": produit.image.url if produit.image else "",
            "qte_achetee": ligne.quantite,
            "prix_unitaire": float(ligne.prix_unitaire),
            "sous_total": float(ligne.sous_total),
            "qte_retournee": ligne.quantite_retournee if hasattr(ligne, "quantite_retournee") else 0,
        })

    data = {
        "numero": facture.code_facture,
        "date_emission": facture.date_emission.strftime("%Y-%m-%d %H:%M:%S"),
        "date_paiement": facture.date_paiement.strftime("%Y-%m-%d %H:%M:%S") if facture.date_paiement else None,
        "montant_ht": float(facture.montant_ht),
        "montant_ttc": float(facture.montant_ttc),
        "montant_net": float(facture.montant_net),
        "mode_paiement": facture.mode_paiement,
        "client": {
            "id": vente.id_client.id_client,
            "nom": vente.id_client.nom_client,
            "contact": vente.id_client.contact,
            "email": vente.id_client.email,
            "adresse": vente.id_client.adresse,
        },
        "produits": produits_data,
    }

    return Response(data)




@api_view(['POST'])
def valider_retour(request):
    data = request.data
    code_facture = data.get('code_facture')
    produits = data.get('produits', [])
    motif_global = data.get('motif_global', '')


      # Récupération des objets
    facture = get_object_or_404(Facture, code_facture=code_facture)
    vente = facture.id_vente
    utilisateur = request.user  # si tu utilises Django authentication et que le user est un Utilisateur


    total_rembourse = Decimal('0.00')

    lignes_retour = []

    for p in produits:
        produit_id = p.get('id')
        qte_retour = int(p.get('qte_a_retourner', 0))
        motif = p.get('motif', '')

        if not produit_id or qte_retour <= 0:
            continue

        try:
            ligne_vente = LigneVente.objects.get(id_vente=vente, id_produit_id=produit_id)
        except LigneVente.DoesNotExist:
            continue

        prix_unitaire = ligne_vente.prix_unitaire
        sous_total_retour = prix_unitaire * qte_retour
        total_rembourse += sous_total_retour

        lignes_retour.append({
            'produit_id': produit_id,
            'quantite': qte_retour,
            'prix_rembourse_unitaire': prix_unitaire,
            'motif': motif
        })

        # Mettre à jour la quantité retournée dans LigneVente
        ligne_vente.quantite_retournee += qte_retour  # ✅ Correct
        ligne_vente.save()

        # Réintégrer le produit dans le stock
        produit = ligne_vente.id_produit
        produit.quantite += qte_retour
        produit.save()

    # Création du retour principal
    retour = RetourProduit.objects.create(
        vente=vente,
        utilisateur=utilisateur,
        raison=motif_global,
        montant_total_rembourse=total_rembourse
    )
     
    # Création des lignes de retour
    for ligne in lignes_retour:
        LigneRetour.objects.create(
            retour=retour,
            produit_id=ligne['produit_id'],
            quantite=ligne['quantite'],
            prix_rembourse_unitaire=ligne['prix_rembourse_unitaire']
        )

    MouvementStock.objects.create(
                    utilisateur = request.user,
                    produit = produit,
                    type_mouvement = 'Retour',
                    quantite=ligne['quantite'],
                    date_mouvement = timezone.now()
        ) 

    return Response({"message": "Retour enregistré avec succès."}, status=status.HTTP_201_CREATED)
