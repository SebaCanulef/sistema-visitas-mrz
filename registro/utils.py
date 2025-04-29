import re
from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

def parse_mrz(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    mrz_lines = []
    for i in range(len(lines) - 2):
        if re.match(r'.*CHL\d{8,9}.*', lines[i + 1]):
            if re.match(r'.*<<.*', lines[i + 2]):
                mrz_lines = lines[i:i + 3]
                break
    
    if not mrz_lines or len(mrz_lines) < 3:
        return None
    
    
    rut_match = re.search(r'CHL(\d{8,9})', mrz_lines[1])
    if not rut_match:
        return None
    rut = rut_match.group(1)

    tercera_linea = mrz_lines[2]
    
    secciones = tercera_linea.split('<<')
    if len(secciones) < 2:
        return None
    
    apellidos_raw = secciones[0].strip()
    apellidos = apellidos_raw.split('<')
    apellido1 = apellidos[0].strip()
    apellido2 = apellidos[1].strip() if len(apellidos) > 1 else ""

    nombres_raw = secciones[1].strip()
    nombres = nombres_raw.split('<')
    nombre = nombres[0].strip()

    
    return {
        'rut': rut,
        'nombre': nombre,
        'apellido1': apellido1,
        'apellido2': apellido2
    }