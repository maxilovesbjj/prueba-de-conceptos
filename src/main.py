import sys
import argparse
import logging
from pathlib import Path
import csv

# Configuración del logger
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

def validar_archivos(rutas):
    """Valida la existencia de los archivos críticos."""
    for ruta in rutas:
        if not ruta.is_file():
            logger.error(f"El archivo '{ruta}' no existe o no es accesible.")
            sys.exit(1)

def cargar_catalogo(ruta_catalogo):
    """
    Carga el catálogo en un diccionario para búsquedas O(1).
    Regla R1: Limpia strings (minúsculas, sin espacios al inicio/final).
    """
    catalogo = {}
    try:
        with open(ruta_catalogo, mode='r', encoding='utf-8') as archivo:
            # Asumimos separador por coma
            lector = csv.DictReader(archivo, delimiter=',')
            for fila in lector:
                # Obtenemos el nombre oficial, limpio
                nombre_oficial = fila.get('plato', '').strip()
                if not nombre_oficial:
                    continue # Saltamos filas vacías si las hay
                
                # Guardamos el plato con su nombre oficial
                # Usamos minúsculas para la llave de búsqueda
                llave_busqueda = nombre_oficial.lower()
                
                # Asumimos que el precio puede no ser un número válido en el catálogo
                try:
                    precio = int(fila.get('precio', 0))
                except ValueError:
                    precio = 0
                
                catalogo[llave_busqueda] = {
                    'nombre_oficial': nombre_oficial,
                    'precio': precio
                }
                
                # Procesamos el alias si existe
                alias_crudo = fila.get('alias', '')
                if alias_crudo:
                    # R1: Guardamos el alias limpio apuntando al mismo plato
                    alias_limpio = alias_crudo.strip().lower()
                    if alias_limpio:
                        catalogo[alias_limpio] = {
                            'nombre_oficial': nombre_oficial,
                            'precio': precio
                        }
        return catalogo
    except Exception as e:
        logger.error(f"Error al leer el catálogo '{ruta_catalogo}': {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="ETL de Reporte Semanal - Doña Rosa")
    parser.add_argument("pedidos", help="Ruta al CSV de pedidos")
    parser.add_argument("catalogo", help="Ruta al CSV de catálogo")
    args = parser.parse_args()

    rutas = [Path(args.pedidos), Path(args.catalogo)]
    
    # 1. Validación de archivos
    validar_archivos(rutas)
    
    # 2. Cargar Catálogo (Regla R1)
    catalogo_dict = cargar_catalogo(rutas[1])
    
    # Salida temporal para probar el flujo de lectura
    logger.info(f"Catálogo cargado con {len(catalogo_dict)} llaves (incluyendo alias).")
    print(catalogo_dict)

if __name__ == "__main__":
    main()