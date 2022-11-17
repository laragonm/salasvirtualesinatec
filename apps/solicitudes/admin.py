from django.contrib import admin
from solo.admin import SingletonModelAdmin
from .models import Solicitud, Dia, Ocurrencia, Instructivo


@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    filter_horizontal = ['dias', 'centros']


@admin.register(Dia)
class DiaAdmin(admin.ModelAdmin):
    pass


@admin.register(Ocurrencia)
class OcurrenciaAdmin(admin.ModelAdmin):
    pass


admin.site.register(Instructivo, SingletonModelAdmin)
