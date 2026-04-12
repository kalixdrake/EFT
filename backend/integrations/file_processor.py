"""
Módulo de procesamiento de archivos para extracción de contenido
Soporta: PDF (con OCR), Excel, CSV, Imágenes
"""

import os
import pandas as pd
from pathlib import Path
from typing import Tuple, Optional


def procesar_archivo(archivo_path: str) -> Tuple[bool, str]:
    """
    Procesa un archivo y extrae su contenido en formato legible para la IA
    
    Args:
        archivo_path: Ruta completa al archivo
    
    Returns:
        Tuple (éxito: bool, contenido: str)
        - Si éxito=True: contenido procesado
        - Si éxito=False: mensaje de error
    
    Ejemplo:
        exito, contenido = procesar_archivo('/ruta/to/archivo.xlsx')
        if exito:
            print(contenido)  # Datos procesados
        else:
            print(f"Error: {contenido}")
    """
    try:
        archivo_path = Path(archivo_path)
        
        if not archivo_path.exists():
            return False, f"El archivo no existe: {archivo_path}"
        
        nombre = archivo_path.name.lower()
        
        # Detectar tipo de archivo y procesarlo
        if nombre.endswith(('.pdf',)):
            return True, _procesar_pdf(str(archivo_path))
        
        elif nombre.endswith(('.xlsx', '.xls')):
            return True, _procesar_excel(str(archivo_path))
        
        elif nombre.endswith('.csv'):
            return True, _procesar_csv(str(archivo_path))
        
        elif nombre.endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
            return True, _procesar_imagen(str(archivo_path))
        
        else:
            return False, f"Formato de archivo no soportado: {nombre}"
    
    except Exception as e:
        return False, f"Error al procesar archivo: {str(e)}"


def _procesar_pdf(ruta: str) -> str:
    """
    Extrae texto de un PDF usando PyMuPDF (fitz)
    Incluye OCR para imágenes dentro del PDF
    
    Args:
        ruta: Ruta al archivo PDF
    
    Returns:
        str: Texto extraído del PDF
    """
    try:
        import fitz  # pymupdf
    except ImportError:
        return "⚠️ PyMuPDF no está instalado. Instala: pip install pymupdf\n"
    
    try:
        texto = ""
        pdf = fitz.open(ruta)
        
        for num_pagina, pagina in enumerate(pdf, 1):
            # Extraer texto de la página
            texto_pagina = pagina.get_text()
            
            if texto_pagina.strip():
                texto += f"\n--- Página {num_pagina} ---\n{texto_pagina}"
            
            # Si la página tiene poco texto, podría ser principalmente imágenes
            # Intentar OCR (nota: requiere instalación adicional de ocrmypdf o similar)
            if len(texto_pagina.strip()) < 100:
                # Intentar extraer imágenes como fallback
                imagenes = pagina.get_images()
                if imagenes:
                    texto += f"\n[Página {num_pagina} contiene {len(imagenes)} imagen(es)]"
        
        pdf.close()
        
        if not texto.strip():
            return f"[PDF vacío o solo con imágenes: {Path(ruta).name}]"
        
        return f"📄 CONTENIDO PDF: {Path(ruta).name}\n{texto}"
    
    except Exception as e:
        return f"Error al procesar PDF: {str(e)}"


def _procesar_excel(ruta: str) -> str:
    """
    Procesa archivos Excel y los convierte a formato legible
    Crea un resumen de datos útil para análisis
    
    Args:
        ruta: Ruta al archivo Excel (.xlsx o .xls)
    
    Returns:
        str: Resumen procesado de datos
    """
    try:
        # Leer todas las hojas
        excel_file = pd.ExcelFile(ruta)
        resumen = f"📊 DATOS EXCEL: {Path(ruta).name}\n"
        resumen += f"Hojas disponibles: {', '.join(excel_file.sheet_names)}\n\n"
        
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(ruta, sheet_name=sheet_name)
            resumen += f"--- Hoja: '{sheet_name}' ---\n"
            resumen += df.to_csv(index=False) + "\n\n"
        
        return resumen
    
    except Exception as e:
        return f"Error al procesar Excel: {str(e)}"


def _procesar_csv(ruta: str) -> str:
    """
    Procesa archivos CSV y los convierte a formato legible
    
    Args:
        ruta: Ruta al archivo CSV
    
    Returns:
        str: Resumen procesado de datos
    """
    try:
        # Detectar encoding
        encoding = _detectar_encoding(ruta)
        
        df = pd.read_csv(ruta, encoding=encoding)
        resumen = f"📋 DATOS CSV: {Path(ruta).name}\n\n"
        resumen += df.to_csv(index=False)
        
        return resumen
    
    except Exception as e:
        return f"Error al procesar CSV: {str(e)}"


def _procesar_imagen(ruta: str) -> str:
    """
    Procesa imágenes e intenta extraer texto con OCR si está disponible
    
    Args:
        ruta: Ruta al archivo de imagen
    
    Returns:
        str: Texto extraído o descripción de la imagen
    """
    try:
        from PIL import Image
        
        img = Image.open(ruta)
        resumen = f"🖼️ IMAGEN: {Path(ruta).name}\n"
        resumen += f"Dimensiones: {img.width}x{img.height} px\n"
        resumen += f"Formato: {img.format}\n"
        
        # Intentar OCR con pytesseract
        try:
            import pytesseract
            texto = pytesseract.image_to_string(img, lang='spa+eng')
            if texto.strip():
                resumen += f"\n--- Texto Extraído (OCR) ---\n{texto}"
            else:
                resumen += "\n[No se detectó texto en la imagen]"
        except ImportError:
            resumen += "\n[OCR no disponible - instala: pip install pytesseract]"
            resumen += "\n[También requiere Tesseract instalado en el sistema]"
        except Exception as ocr_error:
            resumen += f"\n[Error en OCR: {str(ocr_error)}]"
        
        return resumen
    
    except ImportError:
        return "⚠️ PIL (Pillow) no está instalado. Instala: pip install pillow\n"
    except Exception as e:
        return f"Error al procesar imagen: {str(e)}"


def _obtener_resumen_datos(df: pd.DataFrame, nombre: str) -> str:
    """
    Crea un resumen legible de un DataFrame para la IA
    Incluye estadísticas, muestras de datos y análisis básicos
    
    Args:
        df: DataFrame procesado
        nombre: Nombre de la hoja o dataset
    
    Returns:
        str: Resumen formateado
    """
    resumen = f"📈 Hoja: '{nombre}'\n"
    resumen += f"   Filas: {len(df)}, Columnas: {len(df.columns)}\n"
    resumen += f"   Columnas: {', '.join(df.columns.tolist())}\n\n"
    
    # Tipos de datos
    resumen += "   Tipos de datos:\n"
    for col, dtype in df.dtypes.items():
        resumen += f"   - {col}: {dtype}\n"
    
    # Estadísticas para columnas numéricas
    columnas_numericas = df.select_dtypes(include=['number']).columns
    if len(columnas_numericas) > 0:
        resumen += "\n   ESTADÍSTICAS:\n"
        stats = df[columnas_numericas].describe().round(2)
        resumen += stats.to_string().replace('\n', '\n   ')
        resumen += "\n"
    
    # Valores únicos para columnas categóricas
    columnas_categoricas = df.select_dtypes(include=['object']).columns
    if len(columnas_categoricas) > 0:
        resumen += "\n   VALORES ÚNICOS:\n"
        for col in columnas_categoricas:
            n_unicos = df[col].nunique()
            if n_unicos <= 20:  # Solo mostrar si hay pocos valores únicos
                valores = df[col].value_counts()
                resumen += f"   - {col} ({n_unicos} únicos):\n"
                for val, count in valores.items():
                    resumen += f"     • {val}: {count}\n"
            else:
                resumen += f"   - {col}: {n_unicos} valores únicos\n"
    
    return resumen


def _detectar_encoding(ruta: str) -> str:
    """
    Detecta el encoding de un archivo CSV
    
    Args:
        ruta: Ruta al archivo
    
    Returns:
        str: Encoding detectado
    """
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    
    for encoding in encodings:
        try:
            with open(ruta, 'r', encoding=encoding) as f:
                f.read()
            return encoding
        except (UnicodeDecodeError, LookupError):
            continue
    
    return 'utf-8'  # Por defecto


def obtener_info_archivo(archivo_path: str) -> dict:
    """
    Obtiene información rápida del archivo sin procesar todo el contenido
    Útil para validar archivos antes de procesamiento pesado
    
    Args:
        archivo_path: Ruta al archivo
    
    Returns:
        dict: Información del archivo
    """
    try:
        path = Path(archivo_path)
        
        return {
            'existe': path.exists(),
            'nombre': path.name,
            'tamaño_mb': round(path.stat().st_size / (1024 * 1024), 2) if path.exists() else 0,
            'extension': path.suffix.lower(),
            'ruta_absoluta': str(path.absolute())
        }
    except Exception as e:
        return {
            'error': str(e),
            'ruta': archivo_path
        }


# Función para pruebas rápidas
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        archivo = sys.argv[1]
        exito, contenido = procesar_archivo(archivo)
        
        if exito:
            print(f"✅ Procesamiento exitoso:\n{contenido}")
        else:
            print(f"❌ Error: {contenido}")
    else:
        print("Uso: python file_processor.py <ruta_archivo>")
