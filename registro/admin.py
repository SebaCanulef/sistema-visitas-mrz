from django.contrib import admin
from .models import Visitante, Visita, TipoVisita, Empresa, Colaborador, Ubicacion

admin.site.register(Visitante)
admin.site.register(Visita)
admin.site.register(TipoVisita)
admin.site.register(Empresa)
admin.site.register(Colaborador)
admin.site.register(Ubicacion)