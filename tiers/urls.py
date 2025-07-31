from django.urls import path
from . import views




urlpatterns = [
    path('clients', views.client, name='client'),
    path('clients/liste', views.client_list, name='client_list'),
    path('clients/ajouter/', views.add_client, name='add_client'),
    path('clients/modifier/<int:pk>/', views.edit_client, name='edit_client'),
    path('clients/supprimer/<int:pk>/', views.delete_client, name='delete_client'),
    path('clients/<int:pk>/historique/', views.historique_achats_client, name='historique_achats_client'),

    path('fournisseurs', views.frs_list, name='frs_list'),
    path('fournisseurs/ajouter/', views.add_frs, name='add_frs'),
    path('fournisseurs/modifier/<int:pk>/', views.edit_frs, name='edit_frs'),
    path('fournisseurs/supprimer/<int:pk>/', views.delete_frs, name='delete_frs'),


    path('api/top-clients/', views.top_clients, name='top_clients'),

    

]