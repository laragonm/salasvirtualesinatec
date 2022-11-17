from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import View
from .helpers import verificar_permiso_administrador


class PermisoAdministradorRedirectMixin(View):
    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            if not verificar_permiso_administrador(self.request.user):
                next_url = reverse_lazy('core:home')
                return HttpResponseRedirect(next_url)
        return super(PermisoAdministradorRedirectMixin, self).dispatch(*args, **kwargs)
