from django.shortcuts import render
from baseSQL.models import Utilisateur
# Create your views here.
def home(request):
    return render(request, 'core/templates/intro_app.html')



######  ICI ON  gère les urls pour empecher le caissier d'acceder a des urls innappropriés

def some_view(request):
    
    context = {
        'is_admin': request.user.role == 'admin',
        'is_cashier': request.user.role == 'caissier'
    }
    return render(request,'core/templates/navig.html', context )

def some_view(request):
    context = {
        'is_admin': request.user.role == 'admin',
        'is_cashier': request.user.role == 'caissier'
    }
    return render(request,'core/templates/navig0.html', context )