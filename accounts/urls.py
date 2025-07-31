from django.urls import path
from . import views
from .views import CaissierChangePasswordView


urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('caissier/changer-mot-de-passe/', CaissierChangePasswordView.as_view(), name='changer_mot_de_passe_caissier'),
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard/caissier/', views.dashboard_caissier, name='dashboard_caissier'),
    path('utilisateurs/', views.gestion_caissiers, name='gestion_caissier'),
    path('utilisateurs/ajouter/', views.ajouter_caissier, name='ajouter_caissier'),
    path('utilisateurs/<int:pk>/modifier/', views.modifier_caissier, name='modifier_caissier'),
    path('api/ventes-semaine/', views.ventes_semaine, name='ventes_semaine'),
    path('mon_profil/', views.modifier_profil, name='profil_utilisateur'),


    path('modifier-infos/', views.modifier_infos, name='modifier_infos'),
    path('profil/', views.profil_utilisateur0, name='profil'),

    # urls.py
path('changer-photo/', views.changer_photo, name='changer_photo'),

    path('modifier-mot-de-passe/', views.modifier_mot_de_passe, name='modifier_mot_de_passe'),

# Exemple dans urls.py
path("alertes-stock/", views.stock_alertes, name="stock_alertes"),

    path('ventes-7-jours/', views.ventes_7_derniers_jours, name='ventes_7_derniers_jours'),


    path('api/revenus/', views.api_revenus, name='api_revenus'),

    path('api/stats/', views.stats_data, name='stats_data'),
path('details/<int:id_vente>/', views.details_vente_ajax, name='details_vente_ajax'),
path(' liste_ventes/', views.liste_ventes, name='liste_ventes'),
    path('facture/<str:code_facture>/', views.imprimer_facture, name='imprimer_facture'),


]
