from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView
from .forms import SalaForm
from .helpers import sincronizar_salas, sincronizar_areas, sincronizar_centros
from .models import Sala, Area, Centro
from ..usuarios.mixins import PermisoAdministradorRedirectMixin


class SalasView(LoginRequiredMixin, PermisoAdministradorRedirectMixin, TemplateView):
    template_name = 'catalogos/salas.html'
    model = Sala

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            data = []
            for el in self.model.objects.all():
                obj = el.to_json()
                obj['usuarios'] = el.usuarios_display()
                obj['privada_display'] = 'Si' if el.privada else 'No'
                obj['url_update'] = reverse_lazy('catalogos:salas_update', kwargs={'pk': el.pk})
                data.append(obj)
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)


class SalasSyncView(TemplateView):
    template_name = 'catalogos/salas_sync.html'

    def get_context_data(self, **kwargs):
        context = super(SalasSyncView, self).get_context_data(**kwargs)
        context['modal_title'] = 'Sincronización'
        context['form_url'] = reverse_lazy('catalogos:salas_sync')
        return context

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            sincronizar_salas()
            data['success'] = 'Sincronización Realizada'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)


class SalaUpdateView(UpdateView):
    model = Sala
    form_class = SalaForm
    template_name = 'catalogos/salas_update_form.html'

    def get_context_data(self, **kwargs):
        context = super(SalaUpdateView, self).get_context_data(**kwargs)
        context['modal_title'] = 'Asignación de Areas'
        context['form_url'] = reverse_lazy('catalogos:salas_update', kwargs={'pk': self.kwargs.get('pk')})
        return context

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.object = self.get_object()
            form = self.get_form()
            if form.is_valid():
                form.save()
                data['success'] = 'Registro actulizado correctamente'
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)


class AreasView(LoginRequiredMixin, PermisoAdministradorRedirectMixin, TemplateView):
    template_name = 'catalogos/areas.html'
    model = Area

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            data = []
            for el in self.model.objects.all():
                obj = el.to_json()
                data.append(obj)
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)


class AreasSyncView(TemplateView):
    template_name = 'catalogos/areas_sync.html'

    def get_context_data(self, **kwargs):
        context = super(AreasSyncView, self).get_context_data(**kwargs)
        context['modal_title'] = 'Sincronización'
        context['form_url'] = reverse_lazy('catalogos:areas_sync')
        return context

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            sincronizar_areas()
            data['success'] = 'Sincronización Realizada'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)


class CentrosView(LoginRequiredMixin, PermisoAdministradorRedirectMixin, TemplateView):
    template_name = 'catalogos/centros.html'
    model = Centro

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            data = []
            for el in self.model.objects.all().order_by('id_centro'):
                obj = el.to_json()
                data.append(obj)
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)


class CentrosSyncView(TemplateView):
    template_name = 'catalogos/centros_sync.html'

    def get_context_data(self, **kwargs):
        context = super(CentrosSyncView, self).get_context_data(**kwargs)
        context['modal_title'] = 'Sincronización'
        context['form_url'] = reverse_lazy('catalogos:centros_sync')
        return context

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            sincronizar_centros()
            data['success'] = 'Sincronización Realizada'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)
