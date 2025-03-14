from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('captura/', views.captura_imagen, name='captura_imagen'),
    path('registro/', views.registro_entrada, name='registro_entrada'),
    path('guardar/', views.guardar_visita, name='guardar_visita'),
    path('informe/', views.generar_informe, name='generar_informe'),
    path('visitas-activas/', views.visitas_activas, name='visitas_activas'),
]