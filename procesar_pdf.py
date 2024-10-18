import pdfplumber
import re
import os
import pandas as pd

def extraer_datos(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        texto_completo = ""
        
        # Lee todas las páginas del PDF
        for pagina in pdf.pages:
            texto_pagina = pagina.extract_text()
            print(f"Contenido de la página:\n{texto_pagina}\n{'-'*80}")
            texto_completo += texto_pagina


        # Buscar el Total a Pagar
        total_boleta = re.search(r'Total a pagar\s+\$(\d{1,3}(?:\.\d{3})*,\d{2})', texto_completo)
        
        # Buscar la Electricidad Consumida en kWh
        consumo_boleta = re.search(r'Electricidad consumida\s+\((\d+)\s?kWh\)', texto_completo)
        
        # Buscar el monto de Electricidad consumida (precio de la electricidad)
        monto_boleta = re.search(r'Electricidad consumida.*\s+\$(\d{1,3}(?:\.\d{3})*,\d{2})', texto_completo)
        
        # Buscar las lecturas actuales y anteriores del medidor
        lecturas = re.search(r'Actual\s+(\d{1,3}(?:\.\d{3})*)\s+kWh\s+-\s+Anterior\s+(\d{1,3}(?:\.\d{3})*)', texto_completo)
        
        # Buscar la fecha de medición (período de lectura)
        fecha_medicion = re.search(r'Período de lectura:\s+(\d{2}/\d{2}/\d{4})\s+-\s+(\d{2}/\d{2}/\d{4})', texto_completo)

        # Convierte los datos extraídos
        total = total_boleta.group(1) if total_boleta else "No encontrado"
        consumo = consumo_boleta.group(1) if consumo_boleta else "No encontrado"
        monto = monto_boleta.group(1) if monto_boleta else "No encontrado"
        lectura_actual = lecturas.group(1) if lecturas else "No encontrado"
        lectura_anterior = lecturas.group(2) if lecturas else "No encontrado"
        fecha_inicio = fecha_medicion.group(1) if fecha_medicion else "No encontrado"
        fecha_fin = fecha_medicion.group(2) if fecha_medicion else "No encontrado"

        # Calcular el precio por kWh
        if consumo != "No encontrado" and monto != "No encontrado":
            consumo_val = int(consumo.replace(".", ""))
            monto_val = float(monto.replace(".", "").replace(",", "."))
            precio_kwh = monto_val / consumo_val
        else:
            precio_kwh = "No encontrado"

        # Devuelve los datos en forma de diccionario
        return {
            "Archivo": os.path.basename(pdf_path),
            "Total a pagar": total,
            "Consumo (kWh)": consumo,
            "Monto electricidad consumida": monto,
            "Lectura actual": lectura_actual,
            "Lectura anterior": lectura_anterior,
            "Precio por kWh": round(precio_kwh, 4) if isinstance(precio_kwh, float) else precio_kwh,
            "Fecha de inicio de medición": fecha_inicio,
            "Fecha de fin de medición": fecha_fin
        }

# Ruta de la carpeta donde están los PDF
carpeta_pdf = "D:\Leonardo\Proyecto en python\PDFs"

# Lista para almacenar todos los datos
datos_lista = []

# Itera sobre cada archivo PDF en la carpeta
for archivo in os.listdir(carpeta_pdf):
    if archivo.endswith(".pdf"):
        ruta_pdf = os.path.join(carpeta_pdf, archivo)
        print(f"\nProcesando archivo: {archivo}")
        datos = extraer_datos(ruta_pdf)
        
        # Agrega los datos a la lista
        datos_lista.append(datos)

# Crea un DataFrame de pandas con la lista de datos
df = pd.DataFrame(datos_lista)

# Guarda el DataFrame en un archivo Excel
df.to_excel("cuentas_luz.xlsx", index=False)

print("Datos guardados en 'cuentas_luz.xlsx'")