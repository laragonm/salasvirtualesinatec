from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.PROTECT, related_name='perfil')
    id_area = models.CharField(max_length=8, blank=True)
    id_direccion = models.CharField(max_length=4, blank=True)
    id_centro = models.CharField(max_length=4, blank=True)

    class Meta:
        ordering = ['usuario', ]
        verbose_name_plural = 'perfiles'

    def __str__(self):
        return self.usuario.username


@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(usuario=instance)
