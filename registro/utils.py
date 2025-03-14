import re
from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

def parse_mrz(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    print("Texto extraído por Tesseract:")
    print(text)
    
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    print("Líneas procesadas:", lines)
    
    mrz_lines = []
    for i in range(len(lines) - 2):
        if re.match(r'.*CHL\d{8,9}.*', lines[i + 1]):
            if re.match(r'.*<<.*', lines[i + 2]):
                mrz_lines = lines[i:i + 3]
                break
    
    if not mrz_lines or len(mrz_lines) < 3:
        print("Error: No se encontraron las líneas del MRZ")
        return None
    
    print("Líneas MRZ detectadas:", mrz_lines)
    
    rut_match = re.search(r'CHL(\d{8,9})', mrz_lines[1])
    if not rut_match:
        print("Error: No se encontró el RUT")
        return None
    rut = rut_match.group(1)

    tercera_linea = mrz_lines[2]
    print("Tercera línea original:", tercera_linea)
    
    secciones = tercera_linea.split('<<')
    print("Secciones después de split('<<'):", secciones)
    if len(secciones) < 2:
        print("Error: No se pudo separar apellidos y nombres")
        return None
    
    apellidos_raw = secciones[0].strip()
    apellidos = apellidos_raw.split('<')
    print("Apellidos antes de split:", apellidos_raw)
    print("Apellidos procesados:", apellidos)
    apellido1 = apellidos[0].strip()
    apellido2 = apellidos[1].strip() if len(apellidos) > 1 else ""

    nombres_raw = secciones[1].strip()
    nombres = nombres_raw.split('<')
    print("Nombres antes de split:", nombres_raw)
    print("Nombres procesados:", nombres)
    nombre = nombres[0].strip()

    print("Partes procesadas:", [apellido1, apellido2, nombre])
    
    return {
        'rut': rut,
        'nombre': nombre,
        'apellido1': apellido1,
        'apellido2': apellido2
    }