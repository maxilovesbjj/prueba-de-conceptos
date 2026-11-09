# Decisiones Técnicas y Supuestos

## Parte 2: Arquitectura del CLI y ETL

### 1. Arquitectura de Procesamiento: Secuencial vs. Vectorizado
* **Decisión:** El pipeline procesará el CSV de forma secuencial (fila a fila) usando el módulo nativo `csv` de Python.
* **Alternativa descartada:** Uso de motores vectorizados (Pandas, Polars o DuckDB).
* **Por qué:** Aunque los motores vectorizados son el estándar en análisis de datos masivos, el caudal del negocio es mínimo (120 filas/día). La decisión se toma por la **Regla R8**, que exige recolectar *todos* los motivos de rechazo simultáneos en una sola fila. Tratar de hacer acumulación múltiple de errores por registro dinámicamente en Pandas obliga a usar `.apply()` o iterar el DataFrame, lo cual es un anti-patrón ineficiente. Un pipeline secuencial actúa como una serie de válvulas, evaluando cada condición y acumulando el residuo de forma limpia.

### 2. Separación de Responsabilidades (Modularidad)
* **Decisión:** Se aísla el motor matemático/lógico (Reglas R1 a R8) del pipeline de I/O (lectura y escritura de archivos). 
* **Por qué:** Evita el acoplamiento. Al estructurar las reglas como funciones puras independientes, se facilita la creación de tests unitarios aislados con `pytest` (cumpliendo el requisito de automatización de pruebas). Además, prepara el sistema para ser extensible sin romper el código base si cambian las lógicas de negocio en el futuro.

### 3. Manejo de Errores Críticos (stdout vs. stderr)
* **Decisión:** Cualquier error de validación de los archivos de entrada (ausencia de archivo, columnas faltantes) interrumpirá el programa con `sys.exit(1)` y el mensaje se imprimirá en `sys.stderr`.
* **Por qué:** El programa se ejecuta inyectando la salida en un archivo (`> reporte.json`). Si imprimimos mensajes de error o logs de depuración usando `print()` (que va por defecto a `stdout`), el JSON resultante se corromperá.

### 4. Supuestos sobre los Archivos de Entrada
* **Codificación y Delimitadores:** Se asume que los archivos `.csv` vendrán codificados en UTF-8 y separados estrictamente por comas (`,`). Esto evita fallos de parseo con caracteres especiales (ej. "Lasaña").
* **Catálogo (Regla R1):** Se asume que `catalogo.csv` siempre tendrá datos válidos en su estructura base. Se cargará en memoria como un Hash Map (diccionario) para lograr tiempos de acceso $O(1)$ en la validación de alias. Si un plato no tiene alias, el campo puede venir vacío.
* **Concepto "Sin Empresa" (Regla R7):** Se asume que un pedido "sin empresa" corresponde a un campo completamente vacío (`""`) o que contiene únicamente espacios en blanco (`"   "`). Ambos casos se normalizarán y excluirán del cálculo de deuda.
### 5. Manejo de Duplicados (R5)
Se decidió estrictamente sumar los montos de filas duplicadas a los totales y deudas, levantando únicamente la alerta. Aunque un auditor externo podría sugerir excluir los duplicados, el requerimiento de Avostech indica explícitamente "se cuenta igual (no sabemos si es error)".

### 6. Implementación de Descuento Corporativo (Regla R9 / Parte 3)
**Decisión:** Se refactorizó la función `procesar_pedidos` pasando de un modelo "Stream" (sumar al instante) a un modelo de "Agrupación en Memoria" (Sala de Espera).
**Por qué:** Para calcular si una empresa alcanza los 4 platos diarios, es imposible aplicar el cobro al leer la primera línea de la mañana. Ahora, las filas válidas se guardan en la memoria temporal `filas_validas_memoria`. Una vez que el archivo termina de leerse, se verifica el acumulador diario por empresa, se aplica el 10% si corresponde, y se consolida financieramente.