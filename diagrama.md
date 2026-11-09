```mermaid
graph TD
    A[Leer fila de pedidos.csv] --> B{¿Fila idéntica a una anterior? - R5}
    
    %% Alertas tempranas
    B -- Sí --> C[Agregar Alerta: POSIBLE_DUPLICADO]
    B -- No --> D
    C --> D[Iniciar lista vacía de ERRORES]

    %% Válvulas de Validación (R8 exige pasar por TODAS)
    D --> E{¿Plato en Catálogo? - R1}
    E -- No --> E1[Añadir: PLATO_DESCONOCIDO]
    E -- Sí --> F
    E1 --> F{¿Cantidad > 0? - R2}
    
    F -- No --> F1[Añadir: CANTIDAD_INVALIDA]
    F -- Sí --> G
    F1 --> G{¿Fecha hábil y formato OK? - R3}
    
    G -- No --> G1[Añadir: FECHA/DIA_INVALIDO]
    G -- Sí --> H
    G1 --> H{¿Precio cobrado != Catálogo? - R4}

    %% Alertas tardías
    H -- Sí --> H1[Agregar Alerta: PRECIO_DISTINTO]
    H -- No --> I
    H1 --> I{¿Pagado está vacío? - R6}
    
    I -- Sí --> I1[Agregar Alerta: PAGO_SIN_INFORMAR]
    I -- No --> J
    I1 --> J{¿Lista de ERRORES tiene elementos? - R8}

    %% Separador final de flujo
    J -- Sí (Tiene errores) --> K[Descartar fila y guardar en 'rechazos' con todos sus motivos]
    J -- No (Válida) --> L[Sumar a total_vendido, ventas_por_dia y platos]
    
    L --> M{¿Tiene Empresa y está pendiente? - R7}
    M -- Sí --> N[Sumar a deuda_por_empresa]
    M -- No --> O[Ignorar deuda]

    K --> P[Siguiente fila]
    N --> P
    O --> P
    
    P --> Q[Fin archivo: Ordenar JSON y exportar]
    ```