from django.contrib import admin
from .models import Sala, Area


@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    pass


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    pass
