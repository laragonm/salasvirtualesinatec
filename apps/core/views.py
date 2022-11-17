from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'core/home.html'

    def dispatch(self, request, *args, **kwargs):
        next_url = reverse_lazy('solicitudes:solicitudes')
        return HttpResponseRedirect(next_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_name'] = 'Home View'
        return context
