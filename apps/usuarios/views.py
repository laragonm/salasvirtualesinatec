from http import HTTPStatus
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, ListView, UpdateView
from .forms import UsuarioForm
from .helpers import verificar_permiso_login, obtener_usuarios, obtener_roles
from .mixins import PermisoAdministradorRedirectMixin


class LoginView(TemplateView):
    template_name = 'usuarios/login.html'

    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            next_url = self.request.GET.get('next')
            if next_url is None:
                next_url = reverse_lazy('core:home')
            return HttpResponseRedirect(next_url)
        return super(LoginView, self).dispatch(*args, **kwargs)

    def post(self, *args, **kwargs):
        status = HTTPStatus.OK
        if self.request.POST:
            form = AuthenticationForm(data=self.request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                user = authenticate(username=username, password=password)
                if user is not None:
                    if verificar_permiso_login(user):
                        login(self.request, user)
                        data = {'type': 'success', 'msg': 'Login Correcto'}
                    else:
                        data = {'type': 'error', 'msg': 'No tiene permiso para acceder'}
                        status = HTTPStatus.UNAUTHORIZED
                else:
                    data = {'type': 'error', 'msg': 'Credenciales Incorrectas'}
                    status = HTTPStatus.UNAUTHORIZED
            else:
                data = {'type': 'error', 'msg': 'Credenciales Incorrectas'}
                status = HTTPStatus.UNAUTHORIZED
        else:
            data = {'type': 'error', 'msg': 'Metodo no permitido'}
            status = HTTPStatus.METHOD_NOT_ALLOWED
        return JsonResponse(data=data, status=status)


class LogoutView(LoginRequiredMixin, View):
    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            logout(self.request)
            next_url = self.request.GET.get('next')
            if next_url is None:
                next_url = reverse_lazy('core:home')
            return HttpResponseRedirect(next_url)
        return super(LogoutView, self).dispatch(*args, **kwargs)


class UsuarioListView(LoginRequiredMixin, PermisoAdministradorRedirectMixin, ListView):
    model = User
    template_name = 'usuarios/usuario_list.html'

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            data = []
            for el in obtener_usuarios():
                obj = {}
                obj['usuario'] = el.username
                obj['nombre_completo'] = f'{el.first_name} {el.last_name}'
                obj['correo'] = el.email
                obj['roles'] = obtener_roles(el)
                obj['estado'] = ''
                obj['url_update'] = reverse_lazy('usuarios:update_usuario', kwargs={'pk': el.pk})
                data.append(obj)
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)


class UsuarioUpdateView(UpdateView):
    model = User
    form_class = UsuarioForm
    template_name = 'usuarios/usuario_update_form.html'

    def get_context_data(self, **kwargs):
        context = super(UsuarioUpdateView, self).get_context_data(**kwargs)
        context['modal_title'] = 'Asignación de Roles'
        context['form_url'] = reverse_lazy('usuarios:update_usuario', kwargs={'pk': self.kwargs.get('pk')})
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
