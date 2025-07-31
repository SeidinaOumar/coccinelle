from django.urls import path
from . import views


 

urlpatterns = [
    
    path('', views.nouvelle_vente, name='vente'),
    path('enregistrer_vente/', views.enregistrer_vente, name='enregistrer_vente'),
    path('rechercher_client/', views.rechercher_client, name='rechercher_client'),
    path('rechercher_produit/', views.rechercher_produit, name='rechercher_produit'),
    path('nouvelle_vente/', views.nouvelle_vente, name='nouvelle_vente'),
     #path('facture/<int:id_facture>/', views.facture_view1, name='facture'),
   # path('fact/<int:id_vente>/', views.facture_view, name='fact'),
    
    path('client/', views.chercher_ou_creer_client, name='chercher_ou_creer_client'),
    path('api/produit/', views.api_produit, name='api_produit'),
    path('scan-produit/', views.chercher_produit_par_code_barres, name='scan_produit'),
    path('valider/', views.valider_vente, name='valider_vente'),

    path('latest-factures/', views.latest_factures, name='latest_factures'),
    path('facture/<str:code_facture>/', views.imprimer_facture, name='imprimer_facture'),

        path('rapport/', views.rapport, name='rapport'),

     path('rapport/export-pdf/',  views.export_rapport_pdf, name='export_pdf'),

  path('retour-produit/', views.retour_produit_page, name='retour_produit'),

    path('api/factures/<str:code_facture>/', views.facture_detail, name='facture-detail'),
    path('api/retour-valider/', views.valider_retour, name='valider-retour'),
        path("ajouter_client/", views.ajouter_client, name="ajouter_client"),



]