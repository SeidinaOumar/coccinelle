from django.urls import path
from . import views
from django.urls import path, include

urlpatterns  = [
    path('', views.page_stock, name='stock'),

    ### indices alertes
    
    path('mouvements-stock/', views.api_mouvements_stock, name='api_mouvements_stock'),
    path('approvisionnement', views.Approvisionnement_view, name='approvisionnemment'),

    #### appro par scan
    
    path('api/produit/<str:codes_barres>/', views.get_product_by_barcode, name='get_product_by_barcode'),
     path('approv/', views.approvisionnement_view0, name='approv_scan'),

path('mouvements/', views.mouvements_page, name='mouvements'),
    path('ajouter-categorie/', views.ajouter_categorie, name='ajouter_categorie'),

   path('categorie/modifier/<int:pk>/', views.edit_categorie, name='edit_categorie'),
    path('categorie/supprimer/<int:pk>/', views.delete_categorie, name='delete_categorie'),

    
     path('produits/modifier/<int:pk>/', views.edit_product, name='edit_product'),
    path('produits/supprimer/<int:pk>/', views.delete_product, name='delete_product'),
        path('produits/', include('Produits.urls')),  # ou base_sql, ou autre app concernée

]
