import locale
from datetime import datetime
from dateutil import tz
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.forms import model_to_dict
from django_currentuser.middleware import get_current_authenticated_user
from solo.models import SingletonModel
from .choices import ESTADOS_SOLICITUDES, MOTIVOS_RECHAZO, APLICA_APROBACION, APROBADO
from ..catalogos.models import Sala, Centro


class Dia(models.Model):
    codigo = models.PositiveSmallIntegerField()
    nombre = models.CharField(max_length=16)

    class Meta:
        verbose_name_plural = 'dias'

    def __str__(self):
        return self.nombre.capitalize()


class Solicitud(models.Model):
    codigo = models.PositiveSmallIntegerField(unique=True)
    tema = models.CharField(max_length=256)
    agenda = models.TextField(max_length=2000, blank=True, null=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(blank=True, null=True)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    zoom_uuid = models.CharField(max_length=64, blank=True, null=True)
    zoom_id = models.PositiveBigIntegerField(blank=True, null=True)
    zoom_start_url = models.URLField(max_length=1024, blank=True, null=True)
    zoom_join_url = models.URLField(blank=True, null=True)
    usa_codigo_acceso = models.BooleanField(default=False)
    usa_sala_espera = models.BooleanField(default=True)
    codigo_acceso = models.CharField(max_length=8, blank=True)
    es_recurrente = models.BooleanField(default=False)
    dias = models.ManyToManyField(Dia)
    sala = models.ForeignKey(Sala, on_delete=models.PROTECT)
    centros = models.ManyToManyField(Centro)
    observacion = models.TextField(blank=True, null=True)
    estado = models.PositiveSmallIntegerField(choices=ESTADOS_SOLICITUDES, default=1)
    motivo_rechazo = models.PositiveSmallIntegerField(choices=MOTIVOS_RECHAZO, blank=True, null=True)
    aplica_aprobacion = models.PositiveSmallIntegerField(choices=APLICA_APROBACION, blank=False, null=True)
    aprobado = models.PositiveSmallIntegerField(choices=APROBADO, blank=True, null=True)
    usuario_grabacion = models.ForeignKey(User, on_delete=models.PROTECT, related_name='usuario_grabacion')
    fecha_grabacion = models.DateTimeField(auto_now_add=True)
    usuario_modificacion = models.ForeignKey(User, on_delete=models.PROTECT, related_name='usuario_modificacion')
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-codigo', ]
        verbose_name_plural = 'solicitudes'

    def __str__(self):
        return f'{self.codigo:06}'

    def save(self, *args, **kwargs):
        user = get_current_authenticated_user()
        if not self.pk:
            self.usuario_grabacion = user
        self.usuario_modificacion = user
        super(Solicitud, self).save(*args, **kwargs)

    def to_json(self):
        return model_to_dict(self)

    @property
    def solicitante(self):
        return f'{self.usuario_grabacion.first_name} {self.usuario_grabacion.last_name}'

    @property
    def duracion(self):
        inicio = datetime.strptime(self.hora_inicio.strftime('%H:%M'), '%H:%M')
        fin = datetime.strptime(self.hora_fin.strftime('%H:%M'), '%H:%M')
        result = fin - inicio
        return int(result.total_seconds() / 60)

    @property
    def hora_inicio_formato(self):
        locale.setlocale(locale.LC_TIME, settings.LC_EN)
        return self.hora_inicio.strftime('%I:%M %p')

    @property
    def hora_fin_formato(self):
        locale.setlocale(locale.LC_TIME, settings.LC_EN)
        return self.hora_fin.strftime('%I:%M %p')

    @property
    def horario(self):
        return f'{self.hora_inicio_formato} - {self.hora_fin_formato}'

    @property
    def fecha_inicio_formato(self):
        locale.setlocale(locale.LC_TIME, settings.LC_ES)
        return self.fecha_inicio.strftime('%A %d de %B %Y').capitalize()

    @property
    def fecha_fin_formato(self):
        locale.setlocale(locale.LC_TIME, settings.LC_ES)
        fecha_fin = self.fecha_fin if self.fecha_fin else self.fecha_inicio
        return fecha_fin.strftime('%A %d de %B %Y').capitalize()

    @property
    def fecha_inicio_utc(self):
        utc_zone = tz.tzutc()
        fecha = f'{self.fecha_inicio.strftime("%Y-%m-%d")} {self.hora_inicio.strftime("%H:%M:%S")}'
        fecha = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S')
        return fecha.astimezone(utc_zone)

    @property
    def fecha_fin_utc(self):
        utc_zone = tz.tzutc()
        fecha_fin = self.fecha_fin if self.fecha_fin else self.fecha_inicio
        fecha = f'{fecha_fin.strftime("%Y-%m-%d")} {self.hora_fin.strftime("%H:%M:%S")}'
        fecha = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S')
        return fecha.astimezone(utc_zone).strftime('%Y-%m-%dT%H:%M:%SZ')

    @property
    def centros_display(self):
        centros = []
        for centro in self.centros.all():
            centros.append(centro.nombre)
        return centros

    @property
    def join_url_display(self):
        if self.usa_codigo_acceso:
            return f'https://zoom.us/j/{self.zoom_id}'
        else:
            return self.zoom_join_url

    @property
    def recurrente_display(self):
        return 'Si' if self.es_recurrente else 'No'

    @property
    def dias_display(self):
        dias = ''
        for dia in self.dias.all():
            dias += f'{dia.codigo},'
        return dias[:-1]

    @property
    def aplica(self):
        return 'Aplica' if self.aplica_aprobacion==1 else 'No Aplica'

    @property
    def autorizacion(self):
        return 'Autorizado' if self.aprobado==1 else 'No Autorizado'

    @property
    def aplica_cod(self):
        return self.aplica_aprobacion

    @property
    def autorizacion_cod(self):
        return self.aprobado


class Ocurrencia(models.Model):
    zoom_id = models.PositiveBigIntegerField()
    fecha = models.DateField()
    duracion = models.PositiveSmallIntegerField()
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'ocurrencias'

    def __str__(self):
        return f'{self.solicitud} - {self.fecha}'

    @property
    def horario(self):
        return self.solicitud.horario

    @property
    def fecha_formato(self):
        locale.setlocale(locale.LC_TIME, settings.LC_ES)
        return self.fecha.strftime('%A %d de %B %Y').capitalize()

    @property
    def fecha_inicio_utc(self):
        utc_zone = tz.tzutc()
        fecha = f'{self.fecha.strftime("%Y-%m-%d")} {self.solicitud.hora_inicio.strftime("%H:%M:%S")}'
        fecha = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S')
        return fecha.astimezone(utc_zone)

    @property
    def fecha_fin_utc(self):
        utc_zone = tz.tzutc()
        fecha_fin = self.fecha
        fecha = f'{fecha_fin.strftime("%Y-%m-%d")} {self.solicitud.hora_fin.strftime("%H:%M:%S")}'
        fecha = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S')
        return fecha.astimezone(utc_zone).strftime('%Y-%m-%dT%H:%M:%SZ')


class Instructivo(SingletonModel):
    visible = models.BooleanField(default=False)
    archivo = models.FileField()

    class Meta:
        verbose_name = 'instructivo'
