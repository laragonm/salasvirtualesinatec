import time

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Count
from .helpers import obtener_salas, codigo_siguiente
from .models import Solicitud, Dia
from .choices import APLICA_APROBACION, APROBADO


class SolicitudForm(forms.ModelForm):
    todos_centros = forms.BooleanField(label='Todos los Centros', required=False)
    dias = forms.ModelMultipleChoiceField(queryset=Dia.objects.all(), widget=forms.CheckboxSelectMultiple(),
                                          required=False)

    class Meta:
        model = Solicitud
        fields = ['codigo', 'tema', 'agenda', 'fecha_inicio', 'fecha_fin', 'hora_inicio', 'hora_fin', 'sala', 'centros',
                  'usa_codigo_acceso', 'es_recurrente', 'aplica_aprobacion', 'aprobado']
        labels = {
            'agenda': 'Agenda',
            'fecha_inicio': 'Fecha de Inicio',
            'fecha_fin': 'Fecha de Fin',
            'usa_codigo_acceso': 'Código Seguridad',
            'es_recurrente': 'Recurrente'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for element in self.visible_fields():
            element.field.widget.attrs.update({'class': 'form-control', 'autocomplete': 'off'})
        self.fields['sala'].queryset = obtener_salas()
        self.fields['codigo'].initial = codigo_siguiente()
        self.fields['centros'].widget.attrs['class'] = 'form-select select-two'
        self.fields['usa_codigo_acceso'].widget.attrs['class'] = 'form-check-input'
        self.fields['es_recurrente'].widget.attrs['class'] = 'form-check-input'
        self.fields['todos_centros'].widget.attrs['class'] = 'form-check-input'
        self.fields['aplica_aprobacion'].widget.attrs['class'] = 'form-select select-two'
        self.fields['aprobado'].widget.attrs['class'] = 'form-select select-two'

    def clean(self):
        cleaned_data = super(SolicitudForm, self).clean()
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        es_recurrente = cleaned_data.get('es_recurrente')
        sala = cleaned_data.get('sala')
        centros = cleaned_data.get('centros')
        aplica_aprobacion = cleaned_data.get('aplica_aprobacion')
        aprobado = cleaned_data.get('aprobado')
        if hora_inicio >= hora_fin:
            raise ValidationError('La hora de fin debe ser mayor a la de inicio')

        flag_inicio = Solicitud.objects.filter(fecha_inicio=fecha_inicio, sala=sala, hora_inicio__lt=hora_inicio,
                                               hora_fin__gt=hora_inicio, estado__in=[1, 2]).count()
        flag_fin = Solicitud.objects.filter(fecha_inicio=fecha_inicio, sala=sala, hora_inicio__lt=hora_fin,
                                            hora_fin__gt=hora_fin, estado__in=[1, 2]).count()
        if flag_inicio + flag_fin > 0:
            raise ValidationError('Existe una reunion programada en ese horario')

        if not centros.filter(id_centro='1000').exists():
            raise ValidationError('La Sede Central debe estar incluida')

        solicitudes = Solicitud.objects.filter(fecha_inicio=fecha_inicio, hora_inicio__lt=hora_inicio,
                                               hora_fin__gt=hora_inicio, estado__in=[1, 2]).values(
            'centros__id_centro').annotate(
            total_centro=Count('centros__id_centro')).order_by('centros__id_centro')
        for centro in centros:
            for solicitud in solicitudes:
                if centro.id_centro == '1000':
                    continue
                if solicitud['centros__id_centro'] == centro.id_centro and solicitud['total_centro'] >= 2:
                    raise ValidationError(
                        f'El centro {centro.nombre} no puede atender la reunion programada en ese horario')

        solicitudes = Solicitud.objects.filter(fecha_inicio=fecha_inicio, hora_inicio__lt=hora_fin,
                                               hora_fin__gt=hora_fin, estado__in=[1, 2]).values(
            'centros__id_centro').annotate(total_centro=Count('centros__id_centro')).order_by('centros__id_centro')

        for centro in centros:
            for solicitud in solicitudes:
                if centro.id_centro == '1000':
                    continue
                if solicitud['centros__id_centro'] == centro.id_centro and solicitud['total_centro'] >= 2:
                    raise ValidationError(
                        f'El centro {centro.nombre} no puede atender la reunion programada en ese horario')

        if es_recurrente:
            if fecha_fin < fecha_inicio:
                raise ValidationError('La fecha de fin debe ser mayor a la de inicio')


class SolicitudUpdateForm(forms.ModelForm):
    class Meta:
        model = Solicitud
        fields = ['tema', 'agenda', 'fecha_inicio', 'hora_inicio', 'hora_fin', 'aplica_aprobacion', 'aprobado']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for element in self.visible_fields():
            element.field.widget.attrs.update({'class': 'form-control', 'autocomplete': 'off'})

    def clean(self):
        cleaned_data = super(SolicitudUpdateForm, self).clean()
        tema = cleaned_data.get('tema')
        agenda = cleaned_data.get('agenda')
        fecha_inicio = cleaned_data.get('hora_inicio')
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')
        aplica_aprobacion = cleaned_data.get('aplica_aprobacion')
        aprobado = cleaned_data.get('aprobado')
        id = self.data.get('id')
        solicitud = Solicitud.objects.filter(id=id).first()

        if hora_inicio >= hora_fin:
            raise ValidationError('La hora de fin debe ser mayor a la de inicio')

        flag_inicio = Solicitud.objects.filter(fecha_inicio=solicitud.fecha_inicio, sala=solicitud.sala,
                                               hora_inicio__lt=hora_inicio, hora_fin__gt=hora_inicio,
                                               estado__in=[1, 2]).exclude(id__in=[id, ]).count()
        flag_fin = Solicitud.objects.filter(fecha_inicio=solicitud.fecha_inicio, sala=solicitud.sala,
                                            hora_inicio__lt=hora_fin, hora_fin__gt=hora_fin,
                                            estado__in=[1, 2]).exclude(id__in=[id, ]).count()
        if flag_inicio + flag_fin > 0:
            raise ValidationError('Existe una reunion programada en ese horario')
