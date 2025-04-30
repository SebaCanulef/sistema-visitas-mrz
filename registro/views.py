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

from datetime import date
from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

import pandas as pd
from io import BytesIO

from .models import Visita, TipoVisita, Empresa, Colaborador, Ubicacion

def generar_informe(request):
    hoy = date.today()
    filtros = {'fecha': hoy}
    exportar = False

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

    if fecha_inicio and fecha_fin:
        filtros['fecha__range'] = [fecha_inicio, fecha_fin]
    elif fecha_inicio:
        filtros['fecha__gte'] = fecha_inicio
    elif fecha_fin:
        filtros['fecha__lte'] = fecha_fin

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

            # Formatear horas a HH:MM
            df['Hora Entrada'] = df['Hora Entrada'].apply(lambda x: x.strftime('%H:%M') if pd.notnull(x) and x != '-' else '-')
            df['Hora Salida'] = df['Hora Salida'].apply(lambda x: x.strftime('%H:%M') if pd.notnull(x) and x != '-' else '-')


            with BytesIO() as b:
                with pd.ExcelWriter(b, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Visitas')
                    worksheet = writer.sheets['Visitas']

                    # Autoajustar ancho de columnas
                    for column_cells in worksheet.columns:
                        max_length = 0
                        column = column_cells[0].column_letter
                        for cell in column_cells:
                            try:
                                if cell.value:
                                    max_length = max(max_length, len(str(cell.value)))
                            except:
                                pass
                        adjusted_width = max_length + 2
                        worksheet.column_dimensions[column].width = adjusted_width

                response = HttpResponse(
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = 'attachment; filename="informe_visitas.xlsx"'
                response.write(b.getvalue())
                return response

        elif formato == 'pdf':
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="informe_visitas.pdf"'

            from reportlab.lib.pagesizes import letter, landscape
            from reportlab.platypus import Paragraph, Spacer, SimpleDocTemplate, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
            from reportlab.lib import colors
            from reportlab.lib.units import cm

            doc = SimpleDocTemplate(
                response,
                pagesize=landscape(letter),
                leftMargin=30,
                rightMargin=30,
                topMargin=40,
                bottomMargin=30
            )

            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(name='CenterTitle', alignment=TA_CENTER, fontSize=16, spaceAfter=12, fontName="Helvetica-Bold"))
            styles.add(ParagraphStyle(name='TableCell', alignment=TA_LEFT, fontSize=10, spaceAfter=4))
            styles.add(ParagraphStyle(name='HeaderCell', alignment=TA_CENTER, fontSize=11, fontName="Helvetica-Bold", textColor=colors.white))

            elements = []

            # Título
            elements.append(Paragraph("Informe de Visitas", styles['CenterTitle']))
            elements.append(Spacer(1, 12))

            # Encabezados
            encabezados = ['Visitante', 'RUT', 'Tipo Visita', 'Colaborador', 'Ubicación', 'Fecha', 'Horario']
            tabla_data = [[Paragraph(h, styles['HeaderCell']) for h in encabezados]]

            # Filas de datos
            for v in visitas_qs:
                visitante = f"{v.visitante.nombre} {v.visitante.apellido1} {v.visitante.apellido2}"
                colaborador = v.colaborador.nombre if v.colaborador else '-'
                horario = '-'
                if v.hora_entrada:
                    hora_entrada = v.hora_entrada.strftime('%H:%M')
                    hora_salida = v.hora_salida.strftime('%H:%M') if v.hora_salida else '-'
                    horario = f"{hora_entrada} - {hora_salida}"

                fecha_formateada = v.fecha.strftime('%d-%m-%Y')  # Formato Día-Mes-Año

                fila = [
                    Paragraph(visitante, styles['TableCell']),
                    Paragraph(v.visitante.rut, styles['TableCell']),
                    Paragraph(v.tipo_visita.nombre, styles['TableCell']),
                    Paragraph(colaborador, styles['TableCell']),
                    Paragraph(v.ubicacion.nombre if v.ubicacion else '-', styles['TableCell']),
                    Paragraph(fecha_formateada, styles['TableCell']),
                    Paragraph(horario, styles['TableCell'])
                ]
                tabla_data.append(fila)

            # Anchos personalizados
            col_widths = [4.5*cm, 3*cm, 3*cm, 5*cm, 3.5*cm, 3*cm, 4*cm]

            table = Table(tabla_data, repeatRows=1, colWidths=col_widths)

            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F81BD')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),

                ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),

                ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))

            elements.append(table)
            doc.build(elements)
            return response





    paginator = Paginator(visitas_qs, 10)
    page_number = request.GET.get('page')
    visitas = paginator.get_page(page_number)

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