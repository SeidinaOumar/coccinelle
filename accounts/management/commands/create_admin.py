from django.core.management.base import BaseCommand
from baseSQL.models import Utilisateur
from django.utils import timezone
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Creer un admin par default"

    def handle(self, *args, **options):
        Utilisateur = get_user_model()
        if not Utilisateur.objects.filter(username="admin").exists():
            Utilisateur.objects.create_superuser(
                username="admin",
                email="admin@coccinelle.ml",
                password="admin123",
                role = "admin",
                first_name = "Admin",
                last_name  ="admin",
                statut="actif",
                
            )
            self.stdout.write(self.style.SUCCESS("Admin creé avec succès !"))
        else:    
            self.stdout.write(self.style.WARNING("Admin déja existant !"))