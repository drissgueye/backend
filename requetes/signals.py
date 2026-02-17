from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import DelegueSyndical, ProfilUtilisateur, RoleUtilisateur

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


@receiver(post_save, sender=ProfilUtilisateur)
def synchroniser_admin_avec_is_staff(sender, instance: ProfilUtilisateur, **kwargs) -> None:
    """
    Quand un utilisateur a le rôle « admin », on met à jour User.is_staff pour qu'il
    ait accès à toute l'application (API + admin Django). Si le rôle n'est plus admin,
    on retire is_staff (sauf pour les superusers).
    """
    user = instance.user
    if not user:
        return
    if user.is_superuser:
        return
    doit_etre_staff = instance.role == RoleUtilisateur.ADMIN
    if user.is_staff != doit_etre_staff:
        user.is_staff = doit_etre_staff
        user.save(update_fields=["is_staff"])


@receiver(post_delete, sender=DelegueSyndical)
def remettre_role_apres_suppression_delegue(sender, instance: DelegueSyndical, **kwargs) -> None:
    """
    Quand un délégué syndical est supprimé (admin Django ou API),
    remet le rôle du profil à « member » si l'utilisateur n'a plus aucun mandat.
    """
    user = instance.user
    if not user:
        return
    a_encore_un_mandat = DelegueSyndical.objects.filter(user=user).exists()
    if a_encore_un_mandat:
        return
    profil = getattr(user, "profil", None)
    if profil and profil.role == RoleUtilisateur.DELEGATE:
        profil.role = RoleUtilisateur.MEMBER
        profil.save(update_fields=["role"])
