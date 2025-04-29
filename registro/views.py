from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils import timezone
from django.core.paginator import Paginator

from registro.models import Visitante, Visita, TipoVisita, Empresa, Colaborador, Ubicacion
from registro.utils import parse_mrz

from io import BytesIO
import base64
import pandas as pd
from datetime import date

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors


def index(request):
    return render(request, 'registro/index.html')

def captura_imagen(request):
    if request.method == 'POST':
        imagen_data = request.POST.get('imagen')
        if not imagen_data:
            return redirect('index')
        imagen_data = imagen_data.split(',')[1]
        imagen_bytes = BytesIO(base64.b64decode(imagen_data))
        
        datos_mrz = parse_mrz(imagen_bytes)
        
        if datos_mrz:
            visitante, creado = Visitante.objects.get_or_create(
                rut=datos_mrz['rut'],
                defaults={
                    'nombre': datos_mrz['nombre'],
                    'apellido1': datos_mrz['apellido1'],
                    'apellido2': datos_mrz['apellido2']
                }
            )
            visita_activa = Visita.objects.filter(visitante=visitante, hora_salida__isnull=True).first()
            
            if visita_activa:
                visita_activa.hora_salida = timezone.now().time()
                visita_activa.save()
                return render(request, 'registro/salida_exitosa.html', {'visita': visita_activa})

            else:
                request.session['visitante_id'] = visitante.id
                context = {
                    'visitante': visitante,
                    'fecha': timezone.now().date(),
                    'hora': timezone.now().time(),
                    'tipos_visita': TipoVisita.objects.all()
                }
                return render(request, 'registro/registro_entrada.html', context)
    return redirect('index')

def registro_entrada(request):
    visitante_id = request.session.get('visitante_id')
    if not visitante_id:
        return redirect('index')
    visitante = Visitante.objects.get(id=visitante_id)

    if request.method == 'POST':
        tipo_visita_id = request.POST.get('tipo_visita')
        if not tipo_visita_id:
            return redirect('index')
        tipo_visita = TipoVisita.objects.get(id=tipo_visita_id)
        
        request.session['tipo_visita_id'] = tipo_visita.id
        
        if tipo_visita.nombre == 'contratista':
            context = {
                'visitante': visitante,
                'tipo_visita': tipo_visita,
                'empresas': Empresa.objects.all(),
                'colaboradores': Colaborador.objects.all(),
                'ubicaciones': Ubicacion.objects.all()
            }
            return render(request, 'registro/seleccion_empresa.html', context)
        else:
            context = {
                'visitante': visitante,
                'tipo_visita': tipo_visita,
                'colaboradores': Colaborador.objects.all(),
                'ubicaciones': Ubicacion.objects.all()
            }
            return render(request, 'registro/seleccion_colaborador.html', context)
    
    # Si es GET (como al regresar), muestra la página de selección de tipo de visita
    context = {
        'visitante': visitante,
        'fecha': timezone.now().date(),
        'hora': timezone.now().time(),
        'tipos_visita': TipoVisita.objects.all()
    }
    return render(request, 'registro/registro_entrada.html', context)

def guardar_visita(request):
    if request.method == 'POST':
        visitante_id = request.session.get('visitante_id')
        tipo_visita_id = request.session.get('tipo_visita_id')
        if not (visitante_id and tipo_visita_id):
            return redirect('index')
        
        visitante = Visitante.objects.get(id=visitante_id)
        tipo_visita = TipoVisita.objects.get(id=tipo_visita_id)
        empresa_id = request.POST.get('empresa')
        colaborador_id = request.POST.get('colaborador')
        ubicacion_id = request.POST.get('ubicacion')
        
        if tipo_visita.nombre != 'contratista' and not colaborador_id:
            return redirect('index')
        
        visita = Visita(
            visitante=visitante,
            tipo_visita=tipo_visita,
            fecha=timezone.now().date(),
            hora_entrada=timezone.now().time(),
            empresa=Empresa.objects.get(id=empresa_id) if empresa_id else None,
            colaborador=Colaborador.objects.get(id=colaborador_id) if colaborador_id else None,
            ubicacion=Ubicacion.objects.get(id=ubicacion_id) if ubicacion_id else None
        )
        visita.save()
        
        del request.session['visitante_id']
        del request.session['tipo_visita_id']
        
        return render(request, 'registro/entrada_exitosa.html', {'visita': visita})
    return redirect('index')


from datetime import date
import pandas as pd
from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

from .models import Visita, TipoVisita, Empresa, Colaborador, Ubicacion

def generar_informe(request):
    hoy = date.today()
    filtros = {'fecha': hoy}  # Mostrar visitas del día actual por defecto
    exportar = False

    # Leer filtros desde GET (o POST si es exportar)
    data = request.POST if request.method == 'POST' else request.GET

    fecha_inicio = data.get('fecha_inicio')
    fecha_fin = data.get('fecha_fin')
    rut = data.get('rut')
    tipo_visita_id = data.get('tipo_visita')
    empresa_id = data.get('empresa')
    colaborador_id = data.get('colaborador')
    ubicacion_id = data.get('ubicacion')
    formato = data.get('formato')

    filtros = {}

    # Filtros de fechas mejorados
    if fecha_inicio and fecha_fin:
        filtros['fecha__range'] = [fecha_inicio, fecha_fin]
    elif fecha_inicio:
        filtros['fecha__gte'] = fecha_inicio
    elif fecha_fin:
        filtros['fecha__lte'] = fecha_fin

    # Otros filtros
    if rut:
        filtros['visitante__rut__icontains'] = rut
    if tipo_visita_id:
        filtros['tipo_visita_id'] = tipo_visita_id
    if empresa_id:
        filtros['empresa_id'] = empresa_id
    if colaborador_id:
        filtros['colaborador_id'] = colaborador_id
    if ubicacion_id:
        filtros['ubicacion_id'] = ubicacion_id

    visitas_qs = Visita.objects.filter(**filtros).order_by('fecha')

    # Exportar Excel o PDF si corresponde
    if formato in ['excel', 'pdf']:
        exportar = True
        data_export = [{
            'Visitante': f"{v.visitante.nombre} {v.visitante.apellido1} {v.visitante.apellido2}",
            'RUT': v.visitante.rut,
            'Tipo Visita': v.tipo_visita.nombre,
            'Empresa': v.empresa.nombre if v.empresa else '-',
            'Colaborador': f"{v.colaborador.nombre} ({v.colaborador.rut})" if v.colaborador else '-',
            'Ubicación': v.ubicacion.nombre if v.ubicacion else '-',
            'Fecha': v.fecha,
            'Hora Entrada': v.hora_entrada,
            'Hora Salida': v.hora_salida if v.hora_salida else '-'
        } for v in visitas_qs]

        if formato == 'excel':
            df = pd.DataFrame(data_export)
            response = HttpResponse(content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="informe_visitas.xlsx"'
            df.to_excel(response, index=False)
            return response

        elif formato == 'pdf':
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="informe_visitas.pdf"'
            doc = SimpleDocTemplate(response, pagesize=letter)
            table_data = [['Visitante', 'RUT', 'Tipo Visita', 'Empresa', 'Colaborador', 'Ubicación', 'Fecha', 'Hora Entrada', 'Hora Salida']]
            table_data.extend([list(d.values()) for d in data_export])
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            doc.build([table])
            return response

    # Paginación
    paginator = Paginator(visitas_qs, 10)  # 10 visitas por página
    page_number = request.GET.get('page')
    visitas = paginator.get_page(page_number)

    # Filtros actuales (para mantener en la paginación)
    filtros_actuales = request.GET.copy()
    filtros_actuales.pop('page', None)
    filtros_actuales.pop('formato', None)

    context = {
        'tipos_visita': TipoVisita.objects.all(),
        'empresas': Empresa.objects.all(),
        'colaboradores': Colaborador.objects.all(),
        'ubicaciones': Ubicacion.objects.all(),
        'visitas': visitas,
        'filtros_actuales': filtros_actuales,
    }
    return render(request, 'registro/generar_informe.html', context)


def visitas_activas(request):
    if request.method == 'POST':
        visita_id = request.POST.get('visita_id')
        if visita_id:
            visita = Visita.objects.get(id=visita_id)
            visita.hora_salida = timezone.now().time()
            visita.save()
            return redirect('visitas_activas')
    
    visitas = Visita.objects.filter(hora_salida__isnull=True)
    return render(request, 'registro/visitas_activas.html', {'visitas': visitas})