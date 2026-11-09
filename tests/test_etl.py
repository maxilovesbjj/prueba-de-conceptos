import pytest
import tempfile
import os
import json
from src.rules import validar_cantidad, validar_fecha, evaluar_pago
from src.main import procesar_pedidos, cargar_catalogo

# --- Tests Unitarios (Lógica Atómica) ---

def test_validar_cantidad():
    assert validar_cantidad("3") == (3, None)
    assert validar_cantidad("0") == (0, "CANTIDAD_INVALIDA")
    assert validar_cantidad("-1") == (0, "CANTIDAD_INVALIDA")
    assert validar_cantidad("abc") == (0, "CANTIDAD_INVALIDA")
    assert validar_cantidad(None) == (0, "CANTIDAD_INVALIDA")

def test_validar_fecha():
    assert validar_fecha("2026-11-04") == ("2026-11-04", None)
    assert validar_fecha("2026-11-07") == ("2026-11-07", "DIA_NO_HABIL")
    assert validar_fecha("fecha-invalida") == ("fecha-invalida", "FECHA_INVALIDA")
    assert validar_fecha(None) == ("", "FECHA_INVALIDA")
    assert validar_fecha("   ") == ("", "FECHA_INVALIDA")

def test_evaluar_pago():
    assert evaluar_pago("SI") == ("pagado", None)
    assert evaluar_pago("si") == ("pagado", None)
    assert evaluar_pago("NO") == ("pendiente", None)
    assert evaluar_pago("no") == ("pendiente", None)
    assert evaluar_pago("otro") == ("pendiente", "PAGO_SIN_INFORMAR")
    assert evaluar_pago(None) == ("pendiente", "PAGO_SIN_INFORMAR")

# --- Tests de Integración (Pipeline Completo y R9) ---

def test_pipeline_descuento_r9_y_catalogo(tmp_path):
    f_cat = tmp_path / "catalogo.csv"
    f_cat.write_text(
        "plato,precio,alias\n"
        "cazuela,5500,cazuela de ave|cazuela vacuna\n",
        encoding="utf-8"
    )

    f_ped = tmp_path / "pedidos.csv"
    f_ped.write_text(
        "fecha,cliente,empresa,canal,plato,cantidad,precio_unitario,pagado\n"
        "2026-11-04,Marta G.,Clinica Dental,whatsapp,cazuela,4,5500,si\n",
        encoding="utf-8"
    )

    cat = cargar_catalogo(str(f_cat))
    resumen, ventas_dict, platos_dict, deuda_dict, rechazos, alertas = procesar_pedidos(str(f_ped), cat)

    # Validaciones sobre el resumen (R9 aplicado correctamente)
    assert resumen["filas_leidas"] == 1
    assert resumen["filas_validas"] == 1
    assert resumen["filas_rechazadas"] == 0
    assert resumen["total_vendido"] == 19800