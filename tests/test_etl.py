import pytest
from src.rules import validar_cantidad, validar_fecha, evaluar_pago

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