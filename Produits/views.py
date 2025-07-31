from django.shortcuts import render,redirect
from baseSQL.models import Produit , CategorieProduit
from django.db.models import Q, F
from .forms import ProduitForm
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import ProtectedError

# Create your views here.

# vue Pour AFFICHER LES PRODUITS
def liste_produits(request):
    query = request.GET.get('search', '')
    categorie = request.GET.get('categorie', '')

    produits = Produit.objects.all().order_by('-id_produit')
    total_prod = Produit.objects.count()
    if query:
        produits = produits.filter(
            Q(nom_produit__icontains=query)|
            Q(reference__icontains=query)|
            Q(description__icontains=query)
        ) 

    if categorie :
        produits = produits.filter(id_categorie = categorie)

   ## produits = produits.order_by('-id_produit')[:6] ### les 6 derniers ajoutées

    categories = CategorieProduit.objects.all()

    
    total_categories = CategorieProduit.objects.count()
    stock_global = sum(p.stock_actuel for p in Produit.objects.all())
    produits_stock_faible = Produit.objects.filter(stock_actuel__lte=F('stock_min')).count()           

    context ={

        'produits' : produits ,
        'categories' :categories ,
        'total_prod ':total_prod ,  
        'total_categories': total_categories ,
        'stock_global'  :stock_global,
        'produits_stock_faible': produits_stock_faible  ,          



    }



    return render(request, 'Produits/templates/produits.html', context)
########### C R U D SUR LES PRODUITS

def ajouter_produit(request):
    if request.method == 'POST':
        form = ProduitForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect('produits')
    else : 
        form =ProduitForm()

    return render(request, 'Produits/templates/ajouter_produit.html',{'form': form})  

def modifier_produit(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    form = ProduitForm(request.POST or None, instance=produit)
    if form.is_valid():
       form.save()
       return redirect('produits')
    return render(request, 'Produits/templates/ajouter_produit.html', {'form': form})

def supprimer_produit(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    if request.method == 'POST':
        # Vérifie si le produit est lié à une ligne de vente
        if produit.lignevente_set.exists():
           messages.error(request, "❌ Impossible de supprimer ce produit car il est utilisé dans des ventes.")
           return redirect('produits') 
        elif produit.ligneappro_set.exists():   
           messages.error(request, "❌ Impossible de supprimer ce produit car il est utilisé dans des Appprovisionnement.")
           return redirect('produits')  # redirige vers la liste des produits
        produit.delete()
        return redirect('produits')
    return render(request, 'Produits/templates/produits.html', {'produit': produit}) 

   
##### liste complete des produits et crud sur cette ligne
def all_produit(request):
    produits = Produit.objects.all()
    return render(request, 'Produits/templates/liste_produit.html', {'produits': produits})

def edit_product(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    form = ProduitForm(request.POST or None, instance=produit)
    
    if form.is_valid():
       form.save()
       return redirect('liste_produit')
       
    return render(request, 'Produits/templates/liste_produit.html', {'form': form})

def delete_product(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    if request.method == 'POST':
        produit.delete()
        return redirect('all_produit')
    return render(request, 'Produits/templates/liste_produit.html', {'produit': produit}) 
    

def scan_produit(request):
    code = request.GET.get('code')
    try:
        produit = Produit.objects.get(codes_barres=code)
        data = {
            "found": True,
            "nom": produit.nom_produit,
            "reference": produit.reference,
            "prix_vente": produit.prix_vente,
            "stock_actuel": produit.stock_actuel,
            "categorie": produit.categorie.nom if produit.categorie else "Non défini",
            "image": produit.image.url if produit.image else ""
        }
    except Produit.DoesNotExist:
        data = { "found": False }

    return JsonResponse(data)