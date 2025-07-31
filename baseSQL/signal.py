from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Utilisateur, ProfilCaissier


@receiver(post_save, sender=Utilisateur)
def create_profil_caissier(sender, instance, created, **kwargs):
    if created and instance.role == 'caissier':
        ProfilCaissier.objects.create(utilisateur=instance)