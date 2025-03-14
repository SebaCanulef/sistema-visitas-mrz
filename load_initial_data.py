import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'visita_mrz.settings')
django.setup()

from registro.models import TipoVisita, Empresa, Colaborador, Ubicacion

def load_initial_data():
    # Tipos de Visita
    tipos_visita = [
        {'nombre': 'contratista'},
        {'nombre': 'apoderado'},
        {'nombre': 'candidato a entrevista'},
        {'nombre': 'otro'},
    ]
    for tipo in tipos_visita:
        if not TipoVisita.objects.filter(nombre=tipo['nombre']).exists():
            TipoVisita.objects.create(**tipo)
    print("Tipos de Visita cargados.")

    # Empresas
    empresas = [
        {'nombre': 'Empresa A'},
        {'nombre': 'Empresa B'},
        {'nombre': 'Empresa C'},
    ]
    for empresa in empresas:
        if not Empresa.objects.filter(nombre=empresa['nombre']).exists():
            Empresa.objects.create(**empresa)
    print("Empresas cargadas.")

    # Colaboradores
    colaboradores = [
        {'nombre': 'Juan Pérez', 'rut': '12345678'},
        {'nombre': 'María López', 'rut': '98765432'},
        {'nombre': 'Carlos Gómez', 'rut': '56789012'},
    ]
    for colab in colaboradores:
        if not Colaborador.objects.filter(rut=colab['rut']).exists():
            Colaborador.objects.create(**colab)
    print("Colaboradores cargados.")

    # Ubicaciones
    ubicaciones = [
        {'nombre': 'Oficina Principal'},
        {'nombre': 'Sucursal Norte'},
        {'nombre': 'Sucursal Sur'},
    ]
    for ubicacion in ubicaciones:
        if not Ubicacion.objects.filter(nombre=ubicacion['nombre']).exists():
            Ubicacion.objects.create(**ubicacion)
    print("Ubicaciones cargadas.")

if __name__ == "__main__":
    load_initial_data()