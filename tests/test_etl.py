from src.rules import validar_cantidad, validar_fecha, evaluar_pago

def test_r2_cantidad():
    # Caso feliz
    assert validar_cantidad("2") == (2, None)
    # Rechazos
    assert validar_cantidad("0") == (0, "CANTIDAD_INVALIDA")
    assert validar_cantidad("-5") == (0, "CANTIDAD_INVALIDA")
    assert validar_cantidad("texto") == (0, "CANTIDAD_INVALIDA")

def test_r3_fecha():
    # Caso feliz (Miércoles)
    assert validar_fecha("2026-11-04") == ("2026-11-04", None)
    # Fin de semana (Sábado)
    assert validar_fecha("2026-11-07") == ("2026-11-07", "DIA_NO_HABIL")
    # Formato inválido
    assert validar_fecha("04-11-2026")[1] == "FECHA_INVALIDA"

def test_r6_pago():
    assert evaluar_pago("si") == ("pagado", None)
    assert evaluar_pago("no") == ("pendiente", None)
    # Vacío genera alerta
    assert evaluar_pago("") == ("pendiente", "PAGO_SIN_INFORMAR")