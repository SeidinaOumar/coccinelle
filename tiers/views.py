from django.shortcuts import render, redirect, get_object_or_404
from baseSQL.models import Client, Vente, LigneVente, Facture, Fournisseur
from .forms import ClientForm , FrsForm
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum,Count
from baseSQL.models import Vente
from django.utils import timezone
from django.db.models import Sum, Count
from django.http import JsonResponse

# Create your views here.

def client(request):
    clients = Client.objects.all()
   ## total_points = clients.aggregate(Sum('pont'))['pont__sum'] or 0
    return render(request , 'tiers/templates/client.html', {'clients': clients,  })

def client_list(request):
    clients = Client.objects.all()
   ## total_points = clients.aggregate(Sum('pont'))['pont__sum'] or 0
    return render(request , 'tiers/templates/client_list.html', {'clients': clients,  })

def add_client(request):
    if request.method == 'POST':
       form = ClientForm(request.POST)
       if form.is_valid():
           form.save()
           return redirect('client_list')
    else:
        form = ClientForm()
    return render(request, 'tiers/templates/client_form.html', {'form': form})    

def edit_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    form = ClientForm(request.POST or None, instance=client)
    if form.is_valid():
       form.save()
       return redirect('client_list')
    return render(request, 'tiers/templates/client_form.html', {'form': form})

def delete_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        if client.vente_set.exists():
           messages.error(request, "❌ Impossible de supprimer ce Fournisseur car il est utilisé dans approvinionnement.")
           return redirect('client_list') 
        client.delete()
        return redirect('client_list')
    return render(request, 'tiers/templates/client_list.html', {'client': client})    


    #### Historique des achats CLients


def historique_achats_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    ventes = Vente.objects.filter(id_client = client).order_by('-date_vente')   
   
    historiques = []
    for vente in ventes:
        lignes = LigneVente.objects.filter(id_vente=vente).select_related('id_produit')
        facture = Facture.objects.filter(id_vente=vente).first() # une seule facture par vente
        
        historiques.append({
            'vente': vente,
            'lignes' : lignes,
            'facture': facture,
           
        })

    return render(request, 'tiers/templates/historique_achats.html',{
        'client': client,
        'historiques' :historiques,
         
    })    

#### vue  pour la partie fournisseurs
####listes des fournisseurs
def frs_list(request):
    frs = Fournisseur.objects.all()
    return render(request , 'tiers/templates/frs_list.html', {'frs': frs}) ### frs = Fournisseurs

##### ajout d'un frs

def add_frs(request):
    if request.method =='POST':
       form = FrsForm(request.POST)
       if form.is_valid():
           form.save()
           return redirect('frs_list')
    else:
        form = FrsForm()
    return render(request, 'tiers/templates/frs_form.html', {'form': form})    

##### Modification et suppression
def edit_frs(request, pk):
    frs = get_object_or_404(Fournisseur, pk=pk)
    form = FrsForm(request.POST or None, instance=frs)
    if form.is_valid():
       form.save()
       return redirect('frs_list')
    return render(request, 'tiers/templates/frs_form.html', {'form': form})

def delete_frs(request, pk):
    frs = get_object_or_404(Fournisseur, pk=pk)
    if request.method == 'POST':
        if frs.approvisionnement_set.exists():
           messages.error(request, "❌ Impossible de supprimer ce Fournisseur car il est utilisé dans approvinionnement.")
           return redirect('frs_list') 
        frs.delete()
        return redirect('frs_list')
    return render(request, 'tiers/templates/frs_list.html', {'frs': frs})   










############ place des graphiques   !!!!!: oh que jai ssommeil 25/05§2025/14:35 kati koko




def top_clients(request):
    now = timezone.now()
    ventes_du_mois = Vente.objects.filter(
       date_vente__year=now.year,
       date_vente__month=now.month
    )

    top_clients = (
        ventes_du_mois
        .values('id_client__nom_client')
        .annotate(
            total_achats=Sum('montanttotal'),
            nombre_passages=Count('id_vente')  # Chaque vente = 1 passage
        )
        .order_by('-total_achats')[:10]
    )

    labels = [entry['id_client__nom_client'] for entry in top_clients]
    montants = [float(entry['total_achats']) for entry in top_clients]
    passages = [entry['nombre_passages'] for entry in top_clients]

    return JsonResponse({
        'labels': labels,
        'montants': montants,
        'passages': passages
    })

