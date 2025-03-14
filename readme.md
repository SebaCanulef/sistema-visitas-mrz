# Sistema de Registro de Visitas con MRZ

Este proyecto es un sistema web desarrollado con Django que permite registrar entradas y salidas de visitantes mediante el escaneo de códigos MRZ (Machine Readable Zone) en documentos de identidad. Incluye funcionalidades para gestionar tipos de visitas, generar informes filtrados y visualizar visitas activas, todo con una interfaz visual profesional y ordenada.

## Características

- **Captura de MRZ**: Escanea documentos con una cámara web para extraer datos como RUT, nombre y apellidos.
- **Registro de Entrada**: Clasifica visitas por tipo (contratista, apoderado, candidato a entrevista, otros) con campos dinámicos (empresa, colaborador, ubicación).
- **Registro de Salida**: Finaliza visitas automáticamente al reescanear el documento o manualmente desde una lista de visitas activas.
- **Informes**: Genera reportes filtrados por RUT, tipo de visita, empresa, colaborador, ubicación y rango de fechas, descargables en Excel y PDF.
- **Visitas Activas**: Lista las visitas en curso con opción de finalizarlas manualmente.
- **Interfaz Profesional**: Diseño limpio con tablas ordenadas, títulos centrados y navegación intuitiva.

## Requisitos

- **Python**: 3.8 o superior
- **Dependencias**:
  - Django (`pip install django`)
  - OpenCV (`pip install opencv-python`)
  - Pytesseract (`pip install pytesseract`) + Tesseract-OCR instalado en el sistema
  - Pandas (`pip install pandas`)
  - Openpyxl (`pip install openpyxl`)
  - ReportLab (`pip install reportlab`)
  - Pillow (`pip install pillow`)

### Instalación de Tesseract-OCR
- **Windows**: Descarga e instala desde [Tesseract en GitHub](https://github.com/UB-Mannheim/tesseract/wiki). Añade el ejecutable al PATH.
- **Linux**: `sudo apt-get install tesseract-ocr`
- **MacOS**: `brew install tesseract`

## Instalación

1. **Clona el repositorio**:
   ```bash
   git clone https://github.com/SebaCanulef/sistema-visitas-mrz.git
   cd sistema-visitas-mrz
   ```

2. **Crea un entorno virtual** (opcional pero recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Instala las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura la base de datos**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Carga datos iniciales**:
   ```bash
   python load_initial_data.py
   ```

6. **Crea un superusuario** (para acceder al admin):
   ```bash
   python manage.py createsuperuser
   ```

7. **Recolecta archivos estáticos**:
   ```bash
   python manage.py collectstatic
   ```

## Estructura del Proyecto

```
sistema-visitas-mrz/
├── registro/
│   ├── migrations/
│   ├── static/
│   │   └── css/
│   │       └── style.css
│   ├── templates/
│   │   └── registro/
│   │       ├── index.html
│   │       ├── registro_entrada.html
│   │       ├── seleccion_empresa.html
│   │       ├── seleccion_colaborador.html
│   │       ├── entrada_exitosa.html
│   │       ├── salida_exitosa.html
│   │       ├── generar_informe.html
│   │       └── visitas_activas.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── utils.py
│   └── views.py
├── visita_mrz/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── load_initial_data.py
├── README.md
├── requirements.txt
└── .gitignore
```

- **`registro/models.py`**: Define los modelos (`Visitante`, `Visita`, `TipoVisita`, `Empresa`, `Colaborador`, `Ubicacion`).
- **`registro/utils.py`**: Contiene la lógica para procesar imágenes MRZ con OpenCV y Pytesseract.
- **`registro/views.py`**: Maneja las vistas y la lógica del sistema.
- **`static/css/style.css`**: Estilos CSS para una interfaz profesional.

## Uso

1. **Inicia el servidor**:
   ```bash
   python manage.py runserver
   ```

2. **Accede al sistema**:
   - Abre `http://127.0.0.1:8000/` en tu navegador.
   - Usa la cámara para escanear un documento con MRZ (o presiona la barra espaciadora para capturar).

3. **Flujo principal**:
   - **Captura**: Escanea el documento en la página inicial.
   - **Selección de Tipo**: Elige el tipo de visita en "Datos del Visitante".
   - **Datos Adicionales**: Completa empresa/colaborador/ubicación según el tipo.
   - **Registro**: Confirma la entrada o salida.
   - **Informes**: Filtra y descarga reportes desde "Generar Informe".
   - **Visitas Activas**: Revisa y finaliza visitas en curso.

4. **Admin**:
   - Accede a `http://127.0.0.1:8000/admin/` con el superusuario para gestionar datos.

## Detalles de la Interfaz

- **Páginas**:
  - **Inicio**: Cámara y botones para informes/visitas activas.
  - **Datos del Visitante**: Tabla con datos y selección de tipo de visita.
  - **Seleccione Empresa/Colaborador**: Tablas con opciones dinámicas y botón "Regresar" a "Datos del Visitante".
  - **Entrada/Salida Exitosa**: Confirmaciones en tablas.
  - **Generar Informe**: Formulario de filtros en tabla y descarga.
  - **Visitas Activas**: Lista con opción de finalizar.


## Personalización

- **Datos Iniciales**: Edita `load_initial_data.py` para añadir más tipos de visita, empresas, etc.
- **Estilos**: Modifica `static/css/style.css` para ajustar colores o diseño.
- **Validaciones**: Agrega lógica en `utils.py` o `models.py` (ej. validar RUT).

## Notas

- Asegúrate de que la cámara esté habilitada en el navegador.
- Si el MRZ no se detecta, verifica la instalación de Tesseract y la calidad de la imagen.
- Los filtros de informes son opcionales excepto las fechas.

## Contribuciones

Si deseas contribuir, crea un *fork*, implementa cambios y envía un *pull request*. ¡Toda mejora es bienvenida!

