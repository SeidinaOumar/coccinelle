from django.shortcuts import render, redirect, get_object_or_404
from baseSQL.models import Utilisateur, Vente , Produit , Approvisionnement, LigneVente, Facture
from .forms import LoginForm , CaissierCreationForm , CaissierForm,PhotoProfilForm, InfosProfilForm
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import authenticate , login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta,datetime, time
from .forms import ProfilForm
from django.utils.timezone import now
from django.db.models import Sum,Count, Q, F
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.template.loader import render_to_string
from datetime import date
from django.db import models
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from django.utils.formats import date_format
import json
from django.utils.dateformat import DateFormat
from django.db.models import Prefetch




# Create your views here.
def login_view(request):
    if request.method =='POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not user.is_active:
                messages.error(request, "Ce compte est desactivé.")
                return render (request ,'login.html') 
              
            login(request, user)
            # si l'utilisateur a un profil caissier
            if hasattr(user, 'profilcaissier') and user.role == 'caissier':
                if user.profilcaissier.first_login:
                   return redirect('changer_mot_de_passe_caissier')
                return redirect('dashboard_caissier')

            ### Si l'utilisateur est admin
            elif user.role == 'admin':
                return redirect('dashboard_admin')
           
            else :
                messages.error(request, "Rôle non reconnu")

        else:
            try:
                utilisateur = Utilisateur.objects.get(username=username)
                if not utilisateur.is_active:
                 messages.error(request, "Ce compte est desactivé.")
                else:
                 messages.error(request, "Nom d'utilisateur ou mot de passe incorrect")
            except Utilisateur.DoesNotExist:
               messages.error(request, "Nom d'utilisateur ou mot de passe incorrect") 

    return render (request ,'login.html')                      
from django.contrib.auth.decorators import user_passes_test

def is_admin(user):
    return user.is_authenticated and hasattr(user, 'role') and user.role == 'admin'

@user_passes_test(is_admin, login_url='login')        
@login_required(login_url='login')
def dashboard_admin(request):

    print("✅ Vue stock_alertes appelée")
    # Produits en dessous du seuil minimum
    donut_data = get_donut_data() 
    produits_seuil = Produit.objects.filter(quantite__lte=models.F('stock_min'))

    # Approvisionnements proches de la date d'expiration (7 jours)
    approv_proche_expiration = Approvisionnement.objects.filter(
        date_expiration__isnull=False,
        date_expiration__gt=date.today(),
        date_expiration__lte=date.today() + timedelta(days=7)
    )

    # Approvisionnements expirés
    approv_expire = Approvisionnement.objects.filter(
        date_expiration__lt=date.today(),
        ### tableaus des ventes
    )
    ventes_recent = Vente.objects.select_related('id_utilisateur')\
      .prefetch_related('facture_set')\
      .order_by('-date_vente')[:30]

    

    context = {
        'donut_data': donut_data,
        'donut_series': json.dumps(donut_data['series']),
        'donut_labels': json.dumps(donut_data['labels']),
        'donut_colors': json.dumps(donut_data['colors']),
        'produits_seuil': produits_seuil,
        'approv_proche_expiration': approv_proche_expiration,
        'approv_expire': approv_expire,
        'ventes_recent': ventes_recent,

    }
    return render(request, 'accounts/templates/dashboard_admin.html', context)


@login_required
def dashboard_caissier(request):
    return render(request, 'accounts/templates/dashboard_caissier.html') 
@user_passes_test(is_admin, login_url='login')

def gestion_caissiers(request):
    caissiers = Utilisateur.objects.filter(role='caissier')
    return render(request, 'accounts/templates/gestion_caissier.html', {'caissiers': caissiers})
@user_passes_test(is_admin, login_url='login')
          
@login_required
def ajouter_caissier(request):
    if not request.user.role == 'admin':
        return redirect('unauthorized')
    
    if request.method == 'POST':
        form = CaissierCreationForm(request.POST)
        if form.is_valid():
            caissier = form.save(commit=False)
            caissier.role = 'caissier'
            caissier.set_password(form.cleaned_data['password'])
            caissier.save()
            return redirect('gestion_caissier')##### redirection sur la page liste de caissier apres le formualire

    else:
        form = CaissierCreationForm()

    return render(request, 'accounts/templates/ajouter_caissier.html', {'form':form} )        

##### lamodification d'un caisier

def modifier_caissier(request, pk):
    caissier = get_object_or_404(Utilisateur, pk=pk, role = 'caissier')

    if request.method == 'POST':
        form = CaissierForm(request.POST, instance = caissier)

        ### SUPRRIMER UN CAISSIER
        if 'supprimer' in request.POST:
            caissier.delete()
            messages.success(request, " Caissier supprimer avec succès.")
            return redirect('gestion_caissier')
        
        #### Activation et desactivation

        elif 'changer_statut' in request.POST:
            caissier.statut = 'inactif' if caissier.statut == 'actif' else 'actif'
            if caissier.statut == 'inactif':
                caissier.is_active ='0'
            else :
                caissier.is_active = '1'    
            caissier.save()
            messages.success(request, f"Caissier {'desactiver' if caissier.statut == 'inactif' else 'activé'} avec succès")
            return redirect('modifier_caissier', pk=pk)
        
        ##### modification
        elif form.is_valid():
            form.save()
            messages.success(request, "Informations misa à jour !")
            return redirect('modifier_caissier',pk=pk)
        
    else:
        form = CaissierForm(instance= caissier)
    return render(request, 'accounts/templates/modifier_caissier.html', {
        'form' : form,
        'caissier': caissier
    })    


class CaissierChangePasswordView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'accounts/templates/caissier_change_password.html'
    success_url = reverse_lazy('dashboard_caissier')


    def form_valid(self, form):
        response = super().form_valid(form)

        #### mise a jour du champ first login
        if hasattr(self.request.user, 'profilcaissier'):
            self.request.user.profilcaissier.first_login = False
            self.request.user.profilcaissier.save()
       
        messages.success(self.request, "Mot de passe modifier avec succès.")
        return response
    

                ######-STATISTIQUES-####### 
            ####                           ####
####### #                                  #
                 

  

def ventes_semaine(request):
    aujourd_hui = timezone.now().date()
    debut_semaine = aujourd_hui - timedelta(days=aujourd_hui.weekday())  # lundi

    # dictionnaire initial pour chaque jour de la semaine
    jours = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    ventes_par_jour = {jour: 0 for jour in jours}

    ventes = Vente.objects.filter(date_vente__date__gte=debut_semaine)

    for vente in ventes:
        jour_index = vente.date_vente.weekday()  # 0 = Lundi, ..., 6 = Dimanche
        jour_nom = jours[jour_index]
        ventes_par_jour[jour_nom] += 1

    return JsonResponse({'labels': list(ventes_par_jour.keys()), 'data': list(ventes_par_jour.values())})               
##### ventes 7 dernirs jours

def ventes_7_derniers_jours(request):
    aujourd_hui = timezone.now().date()
    date_debut = aujourd_hui - timedelta(days=6)

    ventes = Vente.objects.filter(date_vente__date__gte=date_debut)

    # dictionnaire avec les 7 derniers jours
    ventes_par_jour = {}
    for i in range(7):
        jour = date_debut + timedelta(days=i)
        ventes_par_jour[jour.strftime("%d/%m")] = 0  # clé au format JJ/MM

    for vente in ventes:
        cle = vente.date_vente.date().strftime("%d/%m")
        if cle in ventes_par_jour:
            ventes_par_jour[cle] += 1

    return JsonResponse({
        'labels': list(ventes_par_jour.keys()),
        'data': list(ventes_par_jour.values())
    })
               

##### vue pour modifer les informations
@login_required
def modifier_profil(request):
    user = request.user
    if request.method == 'POST':
        form = ProfilForm(request.POST, request.FILES, instance=user)
        print("FILES:", request.FILES)  # Voir si un fichier est bien envoyé

        if form.is_valid():
            form.save()
            return redirect('profil_utilisateur')  # Redirection vers la page de profil
    else:
        form = ProfilForm(instance=user)
    return render(request, 'accounts/templates/modifier_profil.html', {'form': form})


##### ventes par caissiers


@login_required
def gestion_caissiers(request):
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())  # lundi

    start_of_today = datetime.combine(today, time.min).replace(tzinfo=timezone.get_current_timezone())
    end_of_today = datetime.combine(today, time.max).replace(tzinfo=timezone.get_current_timezone())

    #### comptes des ventes de 8h a 0h
    ##start_of_day = datetime.combine(today, time(hour=8, minute=0)).replace(tzinfo=timezone.get_current_timezone())
    ##end_of_day = datetime.combine(today + timedelta(days=1), time(0, 0)).replace(tzinfo=timezone.get_current_timezone())


    caissiers = Utilisateur.objects.filter(role='caissier').annotate(
    total_ventes=Count('ventes', filter=Q(ventes__date_vente__gte=start_of_week)),
    ventes_jour=Count('ventes', filter=Q(ventes__date_vente__range=(start_of_today, end_of_today))) 
    )

    
    context = {
        'caissiers': caissiers,
    }
   

    return render(request, 'accounts/templates/gestion_caissier.html', context)






#### modification des informations personnelles
@login_required
def profil_utilisateur0(request):
    return render(request, 'accounts/templates/profil.html')
@login_required
def modifier_infos(request):
    if request.method == 'POST':
        form = InfosProfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            html_form = render_to_string("accounts/templates/frag/fragment.html", {'form': form}, request=request)
            return JsonResponse({'success': False, 'form_html': html_form})
    else:
        form = InfosProfilForm(instance=request.user)
        html_form = render_to_string("accounts/templates/frag/fragment.html", {'form': form}, request=request)
        return JsonResponse({'form_html': html_form})


@login_required
def changer_photo(request):
    if request.method == 'POST' and request.FILES.get('photo'):
        user = request.user
        user.photo = request.FILES['photo']
        user.save()
        messages.success(request, 'Photo de profil mise à jour avec succès.')
    else:
        messages.error(request, 'Erreur lors du téléchargement de la photo.')

    return redirect('profil')    

@login_required
def modifier_mot_de_passe(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)  # évite déconnexion
            return JsonResponse({'success': True})
        else:
            html_form = render_to_string("accounts/templates/frag/frag_mdp.html", {'form': form}, request=request)
            return JsonResponse({'success': False, 'form_html': html_form})
    else:
        form = PasswordChangeForm(user=request.user)
        html_form = render_to_string("accounts/templates/frag/frag_mdp.html", {'form': form}, request=request)
        return JsonResponse({'form_html': html_form})
    

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
    
    return render(request, 'accounts/templates/dashboard_admin.html', context)    


######  GRAPHIQUE  PAR REVENU 

def api_revenus(request):
    periode = request.GET.get('periode', 'semaine')

    if periode == 'jour':
        trunc = TruncDay('id_vente__date_vente')
        # Fonction pour afficher jour abrégé FR + date sans espace, ex: Lun01/05
        def format_label(d):
            jours_fr = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
            day_num = d["period"].weekday()  # 0 = Lundi
            jour = jours_fr[day_num]
            date_str = DateFormat(d["period"]).format("d/m")
            return f"{jour}{date_str}"
    elif periode == 'semaine':
        trunc = TruncWeek('id_vente__date_vente')
        def format_label(d):
            start = d["period"]
            end = start + timedelta(days=6)
            # Si le mois est le même, afficher "13 - 19 mai"
            if start.month == end.month:
                return f"{start.day} - {end.day} {DateFormat(start).format('M')}"
            else:
                # Sinon afficher "28 mai - 3 juin"
                return f"{start.day} {DateFormat(start).format('M')} - {end.day} {DateFormat(end).format('M')}"
    else:
        trunc = TruncMonth('id_vente__date_vente')
        format_label = lambda d: DateFormat(d["period"]).format("%b")

    data = (
        LigneVente.objects
        .annotate(period=trunc)
        .values('period')
        .annotate(
            revenu_brut=Sum(F('quantite') * F('id_produit__prix_vente')),
            revenu_net=Sum(F('quantite') * (F('id_produit__prix_vente') - F('id_produit__prix_achat'))),
            ventes=Count('id_ligne')
        )
        .order_by('period')
    )

    response = {
        "labels": [format_label(d) for d in data],
        "revenu_brut": [float(d["revenu_brut"] or 0) for d in data],
        "revenu_net": [float(d["revenu_net"] or 0) for d in data],
        "ventes": [d["ventes"] for d in data]
    }

    return JsonResponse(response)



    #### ===== carte statistique de la vente 
   
def stats_data(request):
    ventes = Vente.objects.all()
    total_ventes = ventes.aggregate(Sum('montanttotal'))['montanttotal__sum'] or 0

    # Dates des 5 dernières semaines (lundi à dimanche)
    today = now().date()
    start_of_week = today - timedelta(days=today.weekday())  # Lundi de cette semaine
    weekly_data = []

    for i in range(5, 0, -1):  # Les 5 semaines précédentes
        start_date = start_of_week - timedelta(weeks=i)
        end_date = start_date + timedelta(days=6)
        total_week = ventes.filter(date_vente__date__gte=start_date, date_vente__date__lte=end_date)\
                           .aggregate(Sum('montanttotal'))['montanttotal__sum'] or 0
        weekly_data.append(round(total_week, 2))

    return JsonResponse({
        'total_ventes': round(total_ventes, 2),
        'ventes_sparkline': weekly_data
    })


#####  CARTES STAT POUR VENTES PAR CATEGORI

from django.db.models import Sum
from baseSQL.models import LigneVente, Produit, CategorieProduit

# Dictionnaire de couleurs fixes (optionnel)
COULEURS_FIXES = {
    'Alimentaires': '#e60000',
    'Cosmétiques': '#ffffff',
    
}

# Données pour le graphique
def ventes_par_categorie():
    categories = CategorieProduit.objects.all()
    data = []
    couleurs = []

    for categorie in categories:
        total = LigneVente.objects.filter(
            id_produit__categorie=categorie
        ).aggregate(
            total_vente=Sum('sous_total')
        )['total_vente'] or 0

        data.append({
            'categorie': categorie.nom,
            'total_vente': float(total)
        })

        # Définir couleur fixe si elle existe, sinon couleur aléatoire
        if categorie.nom in COULEURS_FIXES:
            couleurs.append(COULEURS_FIXES[categorie.nom])
        else:
            import random
            couleur = "#{:06x}".format(random.randint(0, 0xFFFFFF))
            couleurs.append(couleur)

    return data, couleurs
def get_donut_data():
    data, couleurs = ventes_par_categorie()
    labels = [item['categorie'] for item in data]
    series = [item['total_vente'] for item in data]

    return {
        'series': series,
        'labels': labels,
        'colors': couleurs,
    }

#########  DETAILS DES VENTES
def details_vente_ajax(request, id_vente):
    vente = get_object_or_404(Vente, id_vente=id_vente)
    lignes = LigneVente.objects.filter(id_vente=vente).select_related('id_produit')
    client = vente.id_client

    data = {
        'client': {
            'nom': client.nom_client,
            'telephone': client.contact,
        },
        'produits': [
            {
                'nom': ligne.id_produit.nom_produit,
                'quantite': ligne.quantite,
                'prix': ligne.prix_unitaire,
                'image': ligne.id_produit.image.url if ligne.id_produit.image else '',
                'total': ligne.quantite * ligne.prix_unitaire
            }
            for ligne in lignes
        ],
        'montant_total': vente.montanttotal,
        'remise': vente.remise,
        'date': vente.date_vente.strftime('%d %b %Y %H:%M')
    }

    return JsonResponse(data)

    #######""" pages touts les ventes
def liste_ventes(request):
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')

    user = request.user

    if user.role == 'admin':
        ventes = Vente.objects.select_related('id_utilisateur', 'id_client')\
                          .prefetch_related('facture_set')\
                          .order_by('-date_vente')
    elif user.role == 'caissier':
        ventes = Vente.objects.select_related('id_utilisateur', 'id_client')\
                          .prefetch_related('facture_set')\
                          .filter(id_utilisateur=user)\
                          .order_by('-date_vente')
    else:
        ventes = Vente.objects.none()  # Aucun droit d'accès


    if date_debut and date_fin:
        try:
            date_debut_parsed = datetime.strptime(date_debut, "%Y-%m-%d")
            date_fin_parsed = datetime.strptime(date_fin, "%Y-%m-%d")
            ventes = ventes.filter(date_vente__range=(date_debut_parsed, date_fin_parsed))
        except ValueError:
            pass  # ignore invalid input

    context = {
        'ventes': ventes,
        'date_debut': date_debut,
        'date_fin': date_fin,
    }
    return render(request, 'accounts/templates/liste_ventes.html', context)

####"# imprimer la facture depuis le dashboard
def imprimer_facture(request, code_facture):
    print("Vue imprimer_facture appelée avec code_facture =", code_facture)

    facture = get_object_or_404(Facture, code_facture=code_facture)
    vente = facture.id_vente
    print("Vente:", vente)

    lignes_vente = LigneVente.objects.filter(id_vente=vente)

    context = {
        'facture': facture,
        'vente': vente,
        'lignes_vente': lignes_vente,
    }

    return render(request, 'accounts/templates/fact.html', context)


