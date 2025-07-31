from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


####### Backend personnalisé pour gerer les caissiers

Utilisateur = get_user_model()

class CaissierAuthBackend(ModelBackend):
    def authenticate(self, request, username =None, password =None, **kwargs):
        try:
            user = Utilisateur.objects.get(username=username)
            if user.check_password(password) and user.is_active:
                return user
            
        except Utilisateur.DoesNotExist:
            return None    
    