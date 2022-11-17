from django.urls import path, include
from .views import LoginView, LogoutView, UsuarioListView, UsuarioUpdateView

app_name = 'usuarios'
urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('usuarios/', include([
        path('', UsuarioListView.as_view(), name='usuarios'),
        path('asignar-rol/<int:pk>', UsuarioUpdateView.as_view(), name='update_usuario'),
    ])),
]
