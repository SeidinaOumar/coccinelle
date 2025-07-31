from django.urls import path
from . import views

urlpatterns  = [
    path('', views.liste_produits, name='produits'),
    path('ajouter/', views.ajouter_produit, name='ajouter_produit'),
    path('produits/modifier/<int:pk>/', views.modifier_produit, name='modifier_produit'),
    path('produits/supprimer/<int:pk>/', views.supprimer_produit, name='supprimer_produit'),

    path('liste/produit/', views.all_produit, name='all_produit'),

    path('scan/produit/', views.scan_produit, name='scan_produit'),


    path('produits/modifier/<int:pk>/', views.edit_product, name='edit_product'),
    path('produits/supprimer/<int:pk>/', views.delete_product, name='delete_product'),
    # urls.py du projet

]
