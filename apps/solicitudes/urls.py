from django.urls import path, include
from .views import SolicitudesView, SolicitudCreateView, SolicitudUpdateView, SolicitudStateView, SolicitudDetailView, \
    CalendarioView, obtener_reuniones, InstructivoView

app_name = 'solicitudes'
urlpatterns = [
    path('solicitudes/', include([
        path('', SolicitudesView.as_view(), name='solicitudes'),
        path('registrar', SolicitudCreateView.as_view(), name='solicitud_create'),
        path('actualizar/<int:pk>', SolicitudUpdateView.as_view(), name='solicitud_update'),
        path('cambiar-estado/<int:pk>/<slug:action>', SolicitudStateView.as_view(), name='solicitud_state'),
        path('detalle/<int:pk>', SolicitudDetailView.as_view(), name='solicitud_detail'),
        path('json', obtener_reuniones, name='solicitud_json'),
        path('instructivo', InstructivoView.as_view(), name='solicitud_instructivo'),
    ])),
    path('calendario/', CalendarioView.as_view(), name='calendario'),
]
