import argparse
import os
from pathlib import Path
import shutil

def get_parser():
    """
    Configura y retorna el parser de argumentos.
    
    Returns:
        argparse.ArgumentParser: Parser configurado
    """
    parser = argparse.ArgumentParser(
        description='Busca archivos .pptx y .pdf en un directorio. Los PDF se copian y los PPTX se convierten a PDF.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python script.py -i /ruta/entrada -o /ruta/salida
  python script.py -i /ruta/entrada -o /ruta/salida --recursive
  python script.py --input /ruta/entrada --output /ruta/salida --verbose
  
Nota: Requiere LibreOffice instalado y la librería 'sh' (pip install sh)
        """
    )
    
    # Argumentos requeridos
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Directorio de entrada donde buscar archivos'
    )
    
    parser.add_argument(
        '-o', '--output',
        required=True,
        help='Directorio de salida donde guardar los archivos'
    )
    
    # Argumentos opcionales
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Buscar recursivamente en subdirectorios'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Mostrar información detallada'
    )
    
    parser.add_argument(
        '--libreoffice-path',
        default='libreoffice',
        help='Ruta al ejecutable de LibreOffice (por defecto: libreoffice)'
    )
    
    return parser

def verificar_libreoffice(libreoffice_path):
    """
    Verifica si LibreOffice está disponible.
    
    Args:
        libreoffice_path (str): Ruta al ejecutable de LibreOffice
    
    Returns:
        bool: True si LibreOffice está disponible, False en caso contrario
    """
    try:
        import sh
        
        # Crear comando de LibreOffice
        if '/' in libreoffice_path or '\\' in libreoffice_path:
            # Es una ruta completa
            libreoffice_cmd = sh.Command(libreoffice_path)
        else:
            # Es un comando en PATH
            libreoffice_cmd = getattr(sh, libreoffice_path.replace('-', '_'))
        
        # Verificar versión
        result = libreoffice_cmd('--version', _timeout=10)
        return True
        
    except ImportError:
        print("❌ Error: La librería 'sh' no está instalada. Instálala con: pip install sh")
        return False
    except (sh.CommandNotFound, sh.TimeoutException, Exception):
        return False

def buscar_archivos_pptx_pdf(directorio, recursive=False):
    """
    Busca todos los archivos .pptx y .pdf en un directorio.
    
    Args:
        directorio (str): Directorio donde buscar
        recursive (bool): Si True, busca recursivamente
    
    Returns:
        tuple: (lista_archivos_pdf, lista_archivos_pptx)
    """
    archivos_pdf = []
    archivos_pptx = []
    
    try:
        if not os.path.exists(directorio):
            print(f"El directorio '{directorio}' no existe")
            return archivos_pdf, archivos_pptx
        
        if recursive:
            directorio_path = Path(directorio)
            archivos_pdf = [str(archivo) for archivo in directorio_path.rglob("*.pdf")]
            archivos_pptx = [str(archivo) for archivo in directorio_path.rglob("*.pptx")]
        else:
            for archivo in os.listdir(directorio):
                ruta_completa = os.path.join(directorio, archivo)
                if archivo.lower().endswith('.pdf'):
                    archivos_pdf.append(ruta_completa)
                elif archivo.lower().endswith('.pptx'):
                    archivos_pptx.append(ruta_completa)
    
    except PermissionError:
        print(f"No tienes permisos para acceder al directorio '{directorio}'")
    except Exception as e:
        print(f"Error al buscar archivos: {e}")
    
    return archivos_pdf, archivos_pptx

def copiar_archivos_pdf(archivos_pdf, output_dir, verbose=False):
    """
    Copia archivos PDF al directorio de salida.
    
    Args:
        archivos_pdf (list): Lista de archivos PDF a copiar
        output_dir (str): Directorio de salida
        verbose (bool): Mostrar información detallada
    """
    if not archivos_pdf:
        return
    
    print(f"\n📄 Copiando {len(archivos_pdf)} archivo(s) PDF:")
    
    for archivo in archivos_pdf:
        try:
            nombre_archivo = os.path.basename(archivo)
            destino = os.path.join(output_dir, nombre_archivo)
            
            # Si ya existe, agregar sufijo numérico
            contador = 1
            nombre_base, extension = os.path.splitext(nombre_archivo)
            while os.path.exists(destino):
                nuevo_nombre = f"{nombre_base}_{contador}{extension}"
                destino = os.path.join(output_dir, nuevo_nombre)
                contador += 1
            
            shutil.copy2(archivo, destino)
            
            if verbose:
                print(f"  ✓ Copiado: {nombre_archivo} -> {os.path.basename(destino)}")
            else:
                print(f"  ✓ {nombre_archivo}")
                
        except Exception as e:
            print(f"  ❌ Error copiando {archivo}: {e}")

def convertir_pptx_a_pdf(archivos_pptx, output_dir, libreoffice_path, verbose=False):
    """
    Convierte archivos PPTX a PDF usando LibreOffice con la librería sh.
    
    Args:
        archivos_pptx (list): Lista de archivos PPTX a convertir
        output_dir (str): Directorio de salida
        libreoffice_path (str): Ruta al ejecutable de LibreOffice
        verbose (bool): Mostrar información detallada
    """
    if not archivos_pptx:
        return
    
    try:
        import sh
        
        # Crear comando de LibreOffice
        if '/' in libreoffice_path or '\\' in libreoffice_path:
            # Es una ruta completa
            libreoffice_cmd = sh.Command(libreoffice_path)
        else:
            # Es un comando en PATH
            libreoffice_cmd = getattr(sh, libreoffice_path.replace('-', '_'))
        
    except ImportError:
        print("❌ Error: La librería 'sh' no está instalada. Instálala con: pip install sh")
        return
    except AttributeError:
        print(f"❌ Error: No se pudo crear el comando para '{libreoffice_path}'")
        return
    
    print(f"\n🔄 Convirtiendo {len(archivos_pptx)} archivo(s) PPTX a PDF:")
    
    for archivo in archivos_pptx:
        try:
            nombre_archivo = os.path.basename(archivo)
            nombre_sin_ext = os.path.splitext(nombre_archivo)[0]
            
            if verbose:
                print(f"  🔄 Convirtiendo: {nombre_archivo}")
            
            # Convertir usando sh
            result = libreoffice_cmd(
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', output_dir,
                archivo,
                _timeout=60  # Timeout de 60 segundos
            )
            
            # Verificar que se creó el archivo PDF
            archivo_pdf = os.path.join(output_dir, f"{nombre_sin_ext}.pdf")
            if os.path.exists(archivo_pdf):
                if verbose:
                    print(f"  ✓ Convertido: {nombre_archivo} -> {nombre_sin_ext}.pdf")
                else:
                    print(f"  ✓ {nombre_archivo} -> PDF")
            else:
                print(f"  ❌ Error: No se generó el PDF para {nombre_archivo}")
                
        except sh.TimeoutException:
            print(f"  ❌ Timeout convirtiendo {nombre_archivo}")
        except sh.ErrorReturnCode as e:
            print(f"  ❌ Error convirtiendo {nombre_archivo}: {e.stderr.decode() if e.stderr else 'Error desconocido'}")
        except Exception as e:
            print(f"  ❌ Error convirtiendo {nombre_archivo}: {e}")

def main():
    # Obtener parser y parsear argumentos
    parser = get_parser()
    args = parser.parse_args()
    
    # Validaciones
    if not os.path.exists(args.input):
        print(f"❌ Error: El directorio de entrada '{args.input}' no existe")
        return
    
    if not os.path.isdir(args.input):
        print(f"❌ Error: '{args.input}' no es un directorio")
        return
    
    # Verificar LibreOffice
    if not verificar_libreoffice(args.libreoffice_path):
        print(f"❌ Error: LibreOffice no está disponible en '{args.libreoffice_path}'")
        print("   Instala LibreOffice o especifica la ruta correcta con --libreoffice-path")
        print("   También asegúrate de tener instalada la librería 'sh': pip install sh")
        return
    
    # Crear directorio de salida
    try:
        os.makedirs(args.output, exist_ok=True)
    except Exception as e:
        print(f"❌ Error creando directorio de salida '{args.output}': {e}")
        return
    
    # Mostrar configuración si verbose está activado
    if args.verbose:
        print("=" * 60)
        print("CONFIGURACIÓN:")
        print(f"  📁 Directorio entrada: {args.input}")
        print(f"  📁 Directorio salida: {args.output}")
        print(f"  🔄 Búsqueda recursiva: {'Sí' if args.recursive else 'No'}")
        print(f"  🖥️  LibreOffice: {args.libreoffice_path}")
        print("=" * 60)
    
    # Buscar archivos
    archivos_pdf, archivos_pptx = buscar_archivos_pptx_pdf(args.input, args.recursive)
    
    total_archivos = len(archivos_pdf) + len(archivos_pptx)
    if total_archivos == 0:
        print("❌ No se encontraron archivos .pdf o .pptx")
        return
    
    print(f"📊 Archivos encontrados: {len(archivos_pdf)} PDF, {len(archivos_pptx)} PPTX")
    
    # Procesar archivos
    copiar_archivos_pdf(archivos_pdf, args.output, args.verbose)
    convertir_pptx_a_pdf(archivos_pptx, args.output, args.libreoffice_path, args.verbose)
    
    print(f"\n✅ Procesamiento completado. Archivos guardados en: {args.output}")

if __name__ == "__main__":
    main()
