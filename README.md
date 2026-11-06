# Sistema ETL - Cocina Doña Rosa
Repositorio para la prueba técnica de Avostech.

## Parte 1 - Análisis del problema

### 1. Problemas de fondo vs. Síntomas
Para diagnosticar el estado del negocio, es necesario separar el dolor diario de Rosa (síntomas) de las fallas en sus procesos (problemas de fondo).

**Síntomas (Las consecuencias visibles):**
*   **Pérdida de información:** Se le pierden pedidos, especialmente en WhatsApp.
*   **Mermas y quiebres de stock:** Unos días sobra comida que debe botar, y otros días se queda corta.
*   **Incertidumbre financiera:** A fin de mes no sabe con exactitud cuánto le debe cada empresa.
*   **Barrera psicológica:** Siente vergüenza al cobrar, derivada de la inseguridad en sus registros.
*   **Ineficiencia logística:** El repartidor pierde mucho tiempo en la ruta.

**Problemas de Fondo (La causa raíz operativa):**
*   **Ingesta de datos multicanal desestructurada:** Los pedidos entran por tres vías informales (WhatsApp, Instagram, teléfono) y sufren un doble registro manual asíncrono (cuaderno y luego planilla). Esto rompe la trazabilidad.
*   **Producción a ciegas (Falta de forecasting):** Cocina un lote estático de 80 a 120 almuerzos sin basarse en demanda histórica ni establecer un horario de corte para confirmar pedidos. 
*   **Ausencia de conciliación y control de crédito B2B:** Las empresas acumulan deuda sin un sistema transaccional auditable que valide el consumo diario. 
*   **Ausencia de enrutamiento:** No hay consolidación de despachos por zona.

### 2. Preguntas antes de proponer una solución y supuestos
*(En redacción...)*