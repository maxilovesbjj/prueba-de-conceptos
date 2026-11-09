from datetime import datetime

def validar_cantidad(cantidad_str):
    """R2: La cantidad debe ser un entero mayor que 0."""
    if cantidad_str is None:
        return 0, "CANTIDAD_INVALIDA"
    cantidad_str = str(cantidad_str).strip()
    try:
        cant = int(cantidad_str)
        if cant > 0:
            return cant, None
        return 0, "CANTIDAD_INVALIDA"
    except ValueError:
        return 0, "CANTIDAD_INVALIDA"

def validar_fecha(fecha_str):
    """R3: La fecha (AAAA-MM-DD) debe ser válida y de lunes a viernes."""
    if not fecha_str or not str(fecha_str).strip():
        return "", "FECHA_INVALIDA"
    fecha_str = str(fecha_str).strip()
    try:
        dt = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        if dt.weekday() >= 5:
            return fecha_str, "DIA_NO_HABIL"
        return fecha_str, None
    except ValueError:
        return fecha_str, "FECHA_INVALIDA"

def evaluar_pago(pagado_str):
    """R6: 'si'=pagado, 'no'=pendiente, vacío=pendiente + alerta."""
    if pagado_str is None:
        return "pendiente", "PAGO_SIN_INFORMAR"
    val = str(pagado_str).strip().lower()
    if val in ("si", "sí"):
        return "pagado", None
    elif val == "no":
        return "pendiente", None
    else:
        return "pendiente", "PAGO_SIN_INFORMAR"