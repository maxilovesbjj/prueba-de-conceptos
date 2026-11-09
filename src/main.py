import sys
import argparse
import logging
from pathlib import Path
import csv
import json

# --- INYECCIÓN DE RUTA RAÍZ ---
raiz_proyecto = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(raiz_proyecto))

from src.rules import validar_cantidad, validar_fecha, evaluar_pago

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def validar_archivos(rutas):
    """Verifica existencia de archivos (Criterio: terminar distinto de 0)."""
    for ruta in rutas:
        if not ruta.is_file():
            logger.error(f"Error crítico: El archivo '{ruta}' no existe o no es accesible.")
            sys.exit(1)

def cargar_catalogo(ruta_catalogo):
    """
    R1: Carga catálogo limpiando strings y manejando espacios iniciales.
    Devuelve diccionario con acceso O(1).
    """
    catalogo = {}
    try:
        with open(ruta_catalogo, mode='r', encoding='utf-8') as archivo:
            lector = csv.DictReader(archivo, delimiter=',', skipinitialspace=True)
            for fila in lector:
                nombre_oficial = fila.get('plato', '').strip()
                if not nombre_oficial: continue 
                
                llave_busqueda = nombre_oficial.lower()
                try: precio = int(fila.get('precio', 0))
                except ValueError: precio = 0
                
                catalogo[llave_busqueda] = {'nombre_oficial': nombre_oficial, 'precio': precio}
                
                alias_crudo = fila.get('alias', '')
                if alias_crudo:
                    alias_limpio = alias_crudo.strip().lower()
                    if alias_limpio:
                        catalogo[alias_limpio] = {'nombre_oficial': nombre_oficial, 'precio': precio}
        return catalogo
    except Exception as e:
        logger.error(f"Error al leer el catálogo '{ruta_catalogo}': {e}")
        sys.exit(1)

def procesar_pedidos(ruta_pedidos, catalogo):
    """
    Pipeline secuencial que evalúa R2-R8 acumulando errores.
    Implementa R9: Agrupa pedidos válidos y aplica 10% de descuento a empresas con >=4 almuerzos diarios.
    """
    resumen = {"filas_leidas": 0, "filas_validas": 0, "filas_rechazadas": 0, "total_vendido": 0}
    ventas_dict = {}
    platos_dict = {}
    deuda_dict = {}
    rechazos = []
    alertas = []
    filas_vistas = set() 
    
    # NUEVO: Estructuras en memoria para la Parte 3 (Regla R9)
    filas_validas_memoria = []
    conteo_diario_empresas = {} # Llave: (fecha, empresa), Valor: suma de unidades
    
    try:
        with open(ruta_pedidos, mode='r', encoding='utf-8') as archivo:
            lector = csv.DictReader(archivo, delimiter=',', skipinitialspace=True)
            
            columnas_esperadas = {'fecha', 'cliente', 'empresa', 'canal', 'plato', 'cantidad', 'precio_unitario', 'pagado'}
            if not columnas_esperadas.issubset(set(lector.fieldnames or [])):
                logger.error("Error crítico: Al archivo pedidos.csv le faltan columnas obligatorias.")
                sys.exit(1)
                
            for num_linea, fila in enumerate(lector, start=2):
                resumen["filas_leidas"] += 1
                errores_fila = []
                
                # R5: Duplicados exactos
                fila_str = str(fila)
                if fila_str in filas_vistas:
                    alertas.append({"linea": num_linea, "tipo": "POSIBLE_DUPLICADO"})
                filas_vistas.add(fila_str)
                
                # R1: Validar Plato
                plato_crudo = (fila.get('plato') or '').strip().lower()
                precio_oficial = 0
                nombre_oficial = ""
                if plato_crudo in catalogo:
                    precio_oficial = catalogo[plato_crudo]['precio']
                    nombre_oficial = catalogo[plato_crudo]['nombre_oficial']
                else:
                    errores_fila.append("PLATO_DESCONOCIDO")
                    
                # R2 y R3: Inyectar Motor Matemático
                cantidad, err_cant = validar_cantidad(fila.get('cantidad', ''))
                if err_cant: errores_fila.append(err_cant)
                
                fecha, err_fecha = validar_fecha(fila.get('fecha', ''))
                if err_fecha: errores_fila.append(err_fecha)
                
                # R4: Precio distinto o inválido
                precio_crudo = fila.get('precio_unitario', '0')
                if precio_crudo is None: precio_crudo = '0'
                try: 
                    precio_cobrado = int(str(precio_crudo).strip())
                except ValueError: 
                    errores_fila.append("PRECIO_INVALIDO")
                    precio_cobrado = 0
                
                # R6: Validar Pago
                estado_pago, err_pago = evaluar_pago(fila.get('pagado', ''))
                if err_pago:
                    alertas.append({"linea": num_linea, "tipo": err_pago})
                
                if not errores_fila and precio_cobrado != precio_oficial:
                    alertas.append({"linea": num_linea, "tipo": "PRECIO_DISTINTO"})

                # R8: Válvula de decisión final
                if errores_fila:
                    resumen["filas_rechazadas"] += 1
                    rechazos.append({"linea": num_linea, "motivos": errores_fila})
                else:
                    # NUEVO: Si es válida, contamos los almuerzos corporativos y enviamos a la sala de espera
                    resumen["filas_validas"] += 1
                    empresa = (fila.get('empresa') or '').strip()
                    
                    if empresa:
                        llave_agrupacion = (fecha, empresa)
                        conteo_diario_empresas[llave_agrupacion] = conteo_diario_empresas.get(llave_agrupacion, 0) + cantidad
                        
                    filas_validas_memoria.append({
                        "fecha": fecha,
                        "empresa": empresa,
                        "nombre_oficial": nombre_oficial,
                        "cantidad": cantidad,
                        "precio_cobrado": precio_cobrado,
                        "estado_pago": estado_pago
                    })
                    
        # NUEVO: --- FASE DE LIQUIDACIÓN FINANCIERA (R9) ---
        # Recorremos la sala de espera ahora que ya sabemos el total diario de cada empresa
        for item in filas_validas_memoria:
            precio_final = item["precio_cobrado"]
            
            # Evaluar R9: Descuento corporativo por volumen
            if item["empresa"]:
                llave = (item["fecha"], item["empresa"])
                if conteo_diario_empresas.get(llave, 0) >= 4:
                    # 10% de descuento redondeado al peso
                    precio_final = round(precio_final * 0.9)
            
            monto_linea = item["cantidad"] * precio_final
            
            # Sumas financieras globales (impactadas por el descuento si aplicó)
            resumen["total_vendido"] += monto_linea
            ventas_dict[item["fecha"]] = ventas_dict.get(item["fecha"], 0) + monto_linea
            
            if item["nombre_oficial"] not in platos_dict:
                platos_dict[item["nombre_oficial"]] = {"plato": item["nombre_oficial"], "unidades": 0, "total": 0}
            platos_dict[item["nombre_oficial"]]["unidades"] += item["cantidad"]
            platos_dict[item["nombre_oficial"]]["total"] += monto_linea
            
            # R7: Deuda por empresa
            if item["empresa"] and item["estado_pago"] == 'pendiente':
                deuda_dict[item["empresa"]] = deuda_dict.get(item["empresa"], 0) + monto_linea

        return resumen, ventas_dict, platos_dict, deuda_dict, rechazos, alertas
        
    except Exception as e:
        logger.error(f"Error procesando pedidos: {e}")
        sys.exit(1)
def formatear_json(resumen, ventas_dict, platos_dict, deuda_dict, rechazos, alertas):
    """
    Ensambla el objeto JSON final respetando los ordenamientos exactos de Avostech.
    """
    ventas_por_dia = [{"fecha": k, "total": v} for k, v in ventas_dict.items()]
    ventas_por_dia.sort(key=lambda x: x["fecha"])
    
    platos = list(platos_dict.values())
    platos.sort(key=lambda x: x["total"], reverse=True)
    
    deuda_por_empresa = [{"empresa": k, "deuda": v} for k, v in deuda_dict.items() if v > 0]
    deuda_por_empresa.sort(key=lambda x: x["deuda"], reverse=True)
    
    rechazos.sort(key=lambda x: x["linea"])
    alertas.sort(key=lambda x: x["linea"])
    
    return {
        "resumen": resumen,
        "ventas_por_dia": ventas_por_dia,
        "platos": platos,
        "deuda_por_empresa": deuda_por_empresa,
        "rechazos": rechazos,
        "alertas": alertas
    }

def main():
    parser = argparse.ArgumentParser(description="ETL de Reporte Semanal - Doña Rosa")
    parser.add_argument("pedidos", help="Ruta al CSV de pedidos")
    parser.add_argument("catalogo", help="Ruta al CSV de catálogo")
    parser.add_argument("salida", help="Ruta donde se guardará el JSON resultante")
    args = parser.parse_args()

    rutas_entrada = [Path(args.pedidos), Path(args.catalogo)]
    validar_archivos(rutas_entrada)
    
    catalogo = cargar_catalogo(rutas_entrada[1])
    
    resumen, ventas_dict, platos_dict, deuda_dict, rechazos, alertas = procesar_pedidos(rutas_entrada[0], catalogo)
    reporte_final = formatear_json(resumen, ventas_dict, platos_dict, deuda_dict, rechazos, alertas)
    
    # Ruteo y escritura del archivo final
    ruta_salida = Path(args.salida)
    # Se asegura de crear la carpeta processed si no existe
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    
    # Usamos ensure_ascii=False al escribir directamente el archivo en UTF-8
    # para preservar la "ñ". Esto reemplaza el enfoque fallido de imprimir a stdout
    # que corrompía caracteres en PowerShell.
    with open(ruta_salida, mode='w', encoding='utf-8') as archivo_salida:
        json.dump(reporte_final, archivo_salida, indent=2, ensure_ascii=False)
        
    logger.info(f"Reporte generado exitosamente en: {ruta_salida}")

if __name__ == "__main__":
    main()