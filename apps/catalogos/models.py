from django.contrib.auth.models import User
from django.db import models
from django.forms import model_to_dict
from .choices import ESTADOS_SALAS


class Area(models.Model):
    id_area = models.CharField(max_length=8, unique=True)
    id_direccion = models.CharField(max_length=4)
    id_centro = models.CharField(max_length=4)
    nombre = models.CharField(max_length=64)
    estado = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ['nombre', ]
        verbose_name_plural = 'areas'

    def __str__(self):
        return f'{self.id_area} - {self.nombre}'

    def to_json(self):
        return model_to_dict(self)


class Centro(models.Model):
    id_centro = models.CharField(max_length=4)
    nombre = models.CharField(max_length=128)
    estado = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ['id_centro', ]
        verbose_name_plural = 'centros'

    def __str__(self):
        return self.nombre

    def to_json(self):
        return model_to_dict(self)


class Sala(models.Model):
    zoom_id = models.SlugField(unique=True)
    nombre = models.CharField(max_length=64, blank=True)
    correo = models.EmailField(unique=True)
    estado = models.PositiveSmallIntegerField(choices=ESTADOS_SALAS, default=1)
    privada = models.BooleanField(default=False)
    usuarios = models.ManyToManyField(User)

    class Meta:
        ordering = ['nombre', ]
        verbose_name_plural = 'salas'

    def __str__(self):
        return self.nombre

    def to_json(self):
        return model_to_dict(self)

    def usuarios_display(self):
        usuarios = []
        for usuario in self.usuarios.all():
            usuarios.append(usuario.username)
        return usuarios
