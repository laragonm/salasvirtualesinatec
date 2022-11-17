from django.urls import path, include
from .views import SalasView, SalasSyncView, SalaUpdateView, AreasView, AreasSyncView, CentrosView, CentrosSyncView

app_name = 'catalogos'
urlpatterns = [
    path('salas/', include([
        path('', SalasView.as_view(), name='salas'),
        path('sync', SalasSyncView.as_view(), name='salas_sync'),
        path('update/<int:pk>', SalaUpdateView.as_view(), name='salas_update'),
    ])),
    path('areas/', include([
        path('', AreasView.as_view(), name='areas'),
        path('sync', AreasSyncView.as_view(), name='areas_sync')
    ])),
    path('centros/', include([
        path('', CentrosView.as_view(), name='centros'),
        path('sync', CentrosSyncView.as_view(), name='centros_sync')
    ])),
]
