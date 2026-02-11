from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ProfilUtilisateur, RoleUtilisateur

User = get_user_model()


@receiver(post_save, sender=User)
def creer_profil_utilisateur(sender, instance: User, created: bool, **kwargs) -> None:
    """Crée automatiquement un ProfilUtilisateur minimal à la création du user."""
    if not created:
        return
    ProfilUtilisateur.objects.create(
        user=instance,
        role=RoleUtilisateur.MEMBER,
    )
