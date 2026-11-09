from datetime import datetime

def validar_cantidad(cantidad_str):
    """R2: La cantidad debe ser un entero mayor que 0."""
    if cantidad_str is None: return 0, "CANTIDAD_INVALIDA"
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
    if fecha_str is None: return "", "DIA_NO_HABIL"
    fecha_str = str(fecha_str).strip()
    try:
        # Intenta parsear el formato estricto
        fecha_obj = datetime.strptime(fecha_str.strip(), "%Y-%m-%d").date()
        
        # .weekday() devuelve 0=Lunes ... 5=Sábado, 6=Domingo
        if fecha_obj.weekday() >= 5:
            return fecha_str, "DIA_NO_HABIL"
            
        return fecha_str, None
    except ValueError:
        return fecha_str, "FECHA_INVALIDA"

def evaluar_pago(pagado_str):
    """R6: 'si'=pagado, 'no'=pendiente, vacío=pendiente + alerta."""
    if pagado_str is None: return "pendiente", "PAGO_SIN_INFORMAR"
    pagado_str = str(pagado_str).strip().lower()
    val = pagado_str.strip().lower()
    if val == 'si':
        return 'pagado', None
    elif val == 'no':
        return 'pendiente', None
    else:
        # Si viene vacío o con basura, asumimos pendiente pero levantamos alerta
        return 'pendiente', "PAGO_SIN_INFORMAR"