import pytest
from src.rules import validar_cantidad, validar_fecha, evaluar_pago
from src.main import cargar_catalogo, procesar_pedidos

# ==========================================
# TESTS UNITARIOS (Reglas Aisladas)
# ==========================================

def test_r2_validar_cantidad():
    """R2: La cantidad debe ser un entero mayor que 0."""
    assert validar_cantidad("3") == (3, None)
    assert validar_cantidad("0") == (0, "CANTIDAD_INVALIDA")
    assert validar_cantidad("-1") == (0, "CANTIDAD_INVALIDA")
    assert validar_cantidad("abc") == (0, "CANTIDAD_INVALIDA")

def test_r3_validar_fecha():
    """R3: Fecha válida y de lunes a viernes."""
    assert validar_fecha("2026-11-04") == ("2026-11-04", None) # Miércoles
    assert validar_fecha("2026-11-07") == ("2026-11-07", "DIA_NO_HABIL") # Sábado
    assert validar_fecha(None) == ("", "FECHA_INVALIDA")

def test_r6_evaluar_pago():
    """R6: Pagado vs Pendiente."""
    assert evaluar_pago("si") == ("pagado", None)
    assert evaluar_pago("no") == ("pendiente", None)
    assert evaluar_pago("") == ("pendiente", "PAGO_SIN_INFORMAR")

# ==========================================
# TESTS DE INTEGRACIÓN (Reglas del Pipeline)
# ==========================================

def test_r1_cargar_catalogo(tmp_path):
    """R1: Normalización de nombres en minúsculas y alias."""
    f_cat = tmp_path / "cat.csv"
    f_cat.write_text("plato,precio,alias\ncazuela,5500,Cazuela Ave|CAZUELA VACUNA\n", encoding="utf-8")
    
    cat = cargar_catalogo(str(f_cat))
    # Tu main.py agrupa los alias unidos por el pipe, verificamos esa estructura
    assert "cazuela ave|cazuela vacuna" in cat
    assert cat["cazuela ave|cazuela vacuna"]["nombre_oficial"] == "cazuela"

def test_r4_validar_precio(tmp_path):
    """R4: Discrepancia de precio genera alerta, precio alfanumérico genera rechazo."""
    f_cat = tmp_path / "cat.csv"
    f_cat.write_text("plato,precio,alias\ncazuela,5500,\n", encoding="utf-8")
    
    f_ped = tmp_path / "ped.csv"
    f_ped.write_text(
        "fecha,cliente,empresa,canal,plato,cantidad,precio_unitario,pagado\n"
        "2026-11-04,A,Empresa,web,cazuela,1,6000,si\n" # Discrepante
        "2026-11-04,B,Empresa,web,cazuela,1,abc,si\n", # Inválido
        encoding="utf-8"
    )
    
    cat = cargar_catalogo(str(f_cat))
    resumen, _, _, _, rechazos, alertas = procesar_pedidos(str(f_ped), cat)
    
    assert resumen["filas_validas"] == 1
    # Verificamos que se haya generado al menos una alerta por el precio de 6000
    assert len(alertas) >= 1
    assert any("PRECIO_INVALIDO" in str(r) for r in rechazos)

def test_r5_duplicados(tmp_path):
    """R5: Transacciones idénticas se cobran igual pero levantan alerta."""
    f_cat = tmp_path / "cat.csv"
    f_cat.write_text("plato,precio,alias\ncazuela,5500,\n", encoding="utf-8")
    
    f_ped = tmp_path / "ped.csv"
    f_ped.write_text(
        "fecha,cliente,empresa,canal,plato,cantidad,precio_unitario,pagado\n"
        "2026-11-04,Marta,Empresa,web,cazuela,1,5500,si\n"
        "2026-11-04,Marta,Empresa,web,cazuela,1,5500,si\n", # Duplicado exacto
        encoding="utf-8"
    )
    
    cat = cargar_catalogo(str(f_cat))
    resumen, _, _, _, _, alertas = procesar_pedidos(str(f_ped), cat)
    
    assert resumen["filas_validas"] == 2 # Se procesan ambas
    assert any("DUPLICADO" in str(a) for a in alertas)

def test_r7_campos_vacios(tmp_path):
    """R7: Faltan datos críticos, se rechaza la fila sin crashear."""
    f_cat = tmp_path / "cat.csv"
    f_cat.write_text("plato,precio,alias\ncazuela,5500,\n", encoding="utf-8")
    
    f_ped = tmp_path / "ped.csv"
    f_ped.write_text(
        "fecha,cliente,empresa,canal,plato,cantidad,precio_unitario,pagado\n"
        ",,Empresa,web,,,,,si\n", # Fila con datos críticos vacíos
        encoding="utf-8"
    )
    
    cat = cargar_catalogo(str(f_cat))
    resumen, _, _, _, rechazos, _ = procesar_pedidos(str(f_ped), cat)
    
    assert resumen["filas_rechazadas"] == 1
    # Debería rechazar por los validadores defensivos (fecha vacía, cantidad nula, etc.)
    assert any("FECHA_INVALIDA" in str(r) or "CANTIDAD_INVALIDA" in str(r) for r in rechazos)

def test_r8_acumulacion_errores(tmp_path):
    """R8: Una misma fila debe acumular múltiples errores si los tiene."""
    f_cat = tmp_path / "cat.csv"
    f_cat.write_text("plato,precio,alias\ncazuela,5500,\n", encoding="utf-8")
    
    f_ped = tmp_path / "ped.csv"
    f_ped.write_text(
        "fecha,cliente,empresa,canal,plato,cantidad,precio_unitario,pagado\n"
        "2026-11-07,Marta,Empresa,web,inventado,-1,5500,si\n", # Sábado, plato falso, cant negativa
        encoding="utf-8"
    )
    
    cat = cargar_catalogo(str(f_cat))
    _, _, _, _, rechazos, _ = procesar_pedidos(str(f_ped), cat)
    
    motivos = str(rechazos[0])
    assert "DIA_NO_HABIL" in motivos
    assert "PLATO_DESCONOCIDO" in motivos
    assert "CANTIDAD_INVALIDA" in motivos

def test_r9_descuento_corporativo(tmp_path):
    """R9: 10% de descuento si la empresa pide 4 o más almuerzos el mismo día."""
    f_cat = tmp_path / "cat.csv"
    f_cat.write_text("plato,precio,alias\ncazuela,5500,\n", encoding="utf-8")
    
    f_ped = tmp_path / "ped.csv"
    f_ped.write_text(
        "fecha,cliente,empresa,canal,plato,cantidad,precio_unitario,pagado\n"
        "2026-11-04,Marta,Clinica Dental,web,cazuela,4,5500,si\n",
        encoding="utf-8"
    )
    
    cat = cargar_catalogo(str(f_cat))
    resumen, _, _, _, _, _ = procesar_pedidos(str(f_ped), cat)
    
    assert resumen["total_vendido"] == 19800