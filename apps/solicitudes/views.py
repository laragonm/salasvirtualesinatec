import uuid
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, DetailView, UpdateView

from .choices import MOTIVOS_RECHAZO, APLICA_APROBACION, APROBADO
from .forms import SolicitudForm, SolicitudUpdateForm
from .helpers import obtener_fecha_inicio, obtener_solicitudes, enviar_mensaje, crear_reunion, eliminar_reunion, \
    obtener_salas, notificar_nueva_solicitud, codigo_siguiente, obtener_fecha_fin, actualizar_reunion
from .models import Solicitud, Dia, Ocurrencia, Instructivo
from ..usuarios.helpers import verificar_permiso_administrador
from ..usuarios.mixins import PermisoAdministradorRedirectMixin


class SolicitudesView(LoginRequiredMixin, TemplateView):
    template_name = 'solicitudes/solicitudes.html'

    def get_context_data(self, **kwargs):
        context = super(SolicitudesView, self).get_context_data()
        context['instructivo'] = Instructivo.objects.first()
        return context

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            usuario = self.request.user
            if verificar_permiso_administrador(usuario):
                self.template_name = 'solicitudes/solicitudes_admin.html'
            if obtener_salas().count() == 0:
                self.template_name = 'solicitudes/sin_sala.html'
        return super(SolicitudesView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            data = []
            for el in obtener_solicitudes():
                obj = {
                    'codigo': el.__str__(),
                    'tema': el.tema,
                    'fecha_inicio': el.fecha_inicio,
                    'fecha_fin': el.fecha_fin if el.es_recurrente else el.fecha_inicio,
                    'fecha_rango': f'{el.fecha_inicio} - {el.fecha_fin}' if el.es_recurrente else el.fecha_inicio,
                    'horario': el.horario,
                    'sala': el.sala.__str__(),
                    'recurrente': 1 if el.es_recurrente else 0,
                    'recurrente_display': el.recurrente_display,
                    'estado_display': el.get_estado_display(),
                    'estado': el.estado,
                    'solicitante': el.solicitante,
                    'centros': el.centros_display,
                    'zoom_start_url': el.zoom_start_url,
                    'zoom_join_url': el.zoom_join_url,
                    'join_url_display': el.join_url_display,
                    'url_aprobar': reverse_lazy('solicitudes:solicitud_state',
                                                kwargs={'pk': el.pk, 'action': 'aprobar'}),
                    'url_rechazar': reverse_lazy('solicitudes:solicitud_state',
                                                 kwargs={'pk': el.pk, 'action': 'rechazar'}),
                    'url_anular': reverse_lazy('solicitudes:solicitud_state', kwargs={'pk': el.pk, 'action': 'anular'}),
                    'url_detalle': reverse_lazy('solicitudes:solicitud_detail', kwargs={'pk': el.pk}),
                    'url_actualizar': reverse_lazy('solicitudes:solicitud_update', kwargs={'pk': el.pk}),
                }
                data.append(obj)
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)


class SolicitudCreateView(CreateView):
    model = Solicitud
    form_class = SolicitudForm

    def get_context_data(self, **kwargs):
        context = super(SolicitudCreateView, self).get_context_data(**kwargs)
        context['modal_title'] = 'Nueva Solicitud'
        context['form_url'] = reverse_lazy('solicitudes:solicitud_create')
        context['fecha_inicio'] = obtener_fecha_inicio()
        context['fecha_fin'] = obtener_fecha_fin()
        context['aplica_aprobacion'] = APLICA_APROBACION
        context['aprobado'] = APROBADO
        return context

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            form = self.get_form()
            if form.is_valid():
                cleaned_data = form.cleaned_data
                form.instance.codigo = codigo_siguiente()
                form.save()
                if cleaned_data['es_recurrente']:
                    if cleaned_data['dias'] and len(cleaned_data['dias']) > 0:
                        form.instance.dias.set(cleaned_data['dias'])
                    else:
                        form.instance.dias.set(Dia.objects.all())
                notificar_nueva_solicitud(form.instance)
                data['success'] = f'Registro guardado correctamente'
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)


class SolicitudUpdateView(UpdateView):
    model = Solicitud
    form_class = SolicitudUpdateForm
    template_name = 'solicitudes/solicitud_update_form.html'

    def get_context_data(self, **kwargs):
        context = super(SolicitudUpdateView, self).get_context_data(**kwargs)
        context['aplica_aprobacion'] = APLICA_APROBACION
        context['aprobado'] = APROBADO
        context['modal_title'] = 'Actualizar Solicitud'
        context['form_url'] = reverse_lazy('solicitudes:solicitud_update', kwargs={'pk': self.kwargs.get('pk')})
        return context

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            form = self.get_form()
            if form.is_valid():
                cleaned_data = form.cleaned_data
                solicitud = Solicitud.objects.filter(pk=kwargs.get('pk')).first()
                solicitud.tema = cleaned_data['tema']
                solicitud.agenda = cleaned_data['agenda']
                solicitud.fecha_inicio = cleaned_data['fecha_inicio']
                solicitud.hora_inicio = cleaned_data['hora_inicio']
                solicitud.hora_fin = cleaned_data['hora_fin']
                solicitud.aplica_aprobacion = cleaned_data['aplica_aprobacion']
                solicitud.aprobado = cleaned_data['aprobado']
                solicitud.save()

                if solicitud.estado == 1:
                    data['success'] = f'Registro actualizado correctamente'
                else:
                    if actualizar_reunion(solicitud):
                        data['success'] = f'Registro actualizado correctamente'
                    else:
                        data['success'] = f'No se actulizo en Zoom'
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)


class SolicitudStateView(TemplateView):
    template_name = 'solicitudes/solicitud_state.html'

    def get_context_data(self, **kwargs):
        context = super(SolicitudStateView, self).get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        action = self.kwargs.get('action')
        if action == 'aprobar':
            context['modal_title'] = 'Aprobar Solicitud'
            context['btn_submit'] = 'btn-success'
        elif action == 'rechazar':
            context['modal_title'] = 'Rechazar Solicitud'
            context['motivos_rechazo'] = MOTIVOS_RECHAZO
            context['btn_submit'] = 'btn-danger'
        else:
            context['modal_title'] = 'Anular Solicitud'
            context['btn_submit'] = 'btn-danger'
        context['action'] = action
        context['form_url'] = reverse_lazy('solicitudes:solicitud_state', kwargs={'pk': pk, 'action': action})
        return context

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            pk = self.kwargs.get('pk')
            action = self.kwargs.get('action')
            solicitud = Solicitud.objects.filter(pk=pk).first()
            if solicitud:
                if action == 'aprobar':
                    solicitud.estado = 2
                    if solicitud.usa_codigo_acceso:
                        solicitud.codigo_acceso = uuid.uuid4().__str__()[:8]
                    solicitud.save()
                    crear_reunion(solicitud)
                    if solicitud.zoom_uuid:
                        enviar_mensaje(solicitud)
                        data['success'] = 'Solicitud aprobada correctamente'
                    else:
                        data['error'] = 'Error al crear al reunion en zoom'
                elif action == 'rechazar':
                    solicitud.estado = 3
                    solicitud.motivo_rechazo = request.POST['motivo_rechazo']
                    solicitud.save()
                    enviar_mensaje(solicitud)
                    data['success'] = 'Solicitud rechanzada correctamente'
                else:
                    if eliminar_reunion(solicitud):
                        solicitud.estado = 0
                        solicitud.save()
                        enviar_mensaje(solicitud)
                        data['success'] = 'Solicitud anulada correctamente'
                    else:
                        data['error'] = 'Error al anular la reunion en zoom'
            else:
                data['error'] = 'No se encontro la solicitud'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)


class SolicitudDetailView(DetailView):
    model = Solicitud
    template_name = 'solicitudes/solicitud_detail.html'


class CalendarioView(LoginRequiredMixin, TemplateView):
    template_name = 'solicitudes/calendario.html'

    def get_context_data(self, **kwargs):
        context = super(CalendarioView, self).get_context_data(**kwargs)
        context['salas'] = obtener_salas()
        return context


def obtener_reuniones(request):
    data = []
    sala = request.GET.get('id_sala')
    solicitudes = Solicitud.objects.filter(sala=int(sala), estado__in=[2]) if sala else None
    for sol in solicitudes:
        if sol.es_recurrente:
            ocurrencias = Ocurrencia.objects.filter(solicitud__estado__in=[2]).select_related('solicitud').all()
            for oc in ocurrencias:
                obj = {
                    'title': oc.solicitud.tema,
                    'start': oc.fecha_inicio_utc,
                    'end': oc.fecha_fin_utc,
                    'slug': f'{oc.solicitud.tema}-{oc.fecha_inicio_utc}-{oc.fecha_fin_utc}'
                }
                data.append(obj)
        else:
            obj = {
                'title': sol.tema,
                'start': sol.fecha_inicio_utc,
                'end': sol.fecha_fin_utc,
                'slug': f'{sol.tema}-{sol.fecha_inicio_utc}-{sol.fecha_fin_utc}'
            }
            data.append(obj)

    data = list({each['slug']: each for each in data}.values())
    return JsonResponse(data, safe=False)


class InstructivoView(TemplateView):
    template_name = 'solicitudes/instructivo.html'

    def get_context_data(self, **kwargs):
        context = super(InstructivoView, self).get_context_data(**kwargs)
        context['modal_title'] = 'Instructivo de Salas Virtuales'
        context['instructivo'] = Instructivo.objects.first()
        return context
