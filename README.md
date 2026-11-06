# Sistema ETL - Cocina Doña Rosa
Repositorio para la prueba técnica de Avostech.

## Parte 1 - Análisis del problema

### 1. Problemas de fondo vs. Síntomas
Para diagnosticar el estado del negocio, es necesario separar el dolor diario de Rosa (síntomas) de las fallas en sus procesos (problemas de fondo).

**Síntomas (Las consecuencias visibles):**
*   **Pérdida de información:** Se le pierden pedidos, especialmente en WhatsApp.
*   **Mermas y quiebres de stock:** Unos días sobra comida que debe botar, y otros días se queda corta[cite: 3].
*   **Incertidumbre financiera:** A fin de mes no sabe con exactitud cuánto le debe cada empresa[cite: 3].
*   **Barrera psicológica:** Siente vergüenza al cobrar[cite: 3], derivada de la inseguridad en sus propios registros.
*   **Ineficiencia logística:** El repartidor pierde mucho tiempo en la ruta[cite: 3].

**Problemas de Fondo (La causa raíz operativa):**
*   **Ingesta de datos multicanal desestructurada:** Los pedidos entran por tres vías informales (WhatsApp, Instagram, teléfono) y sufren un doble registro manual asíncrono (cuaderno en la mañana, planilla en la tarde)[cite: 2]. Esto rompe la trazabilidad y genera los pedidos perdidos.
*   **Producción a ciegas (Falta de forecasting):** Cocina un lote estático de 80 a 120 almuerzos[cite: 2] sin basarse en demanda histórica ni establecer un horario de corte para confirmar pedidos. Esto causa directamente la merma y los quiebres de stock.
*   **Ausencia de conciliación y control de crédito B2B:** Las empresas acumulan deuda[cite: 2] sin un sistema transaccional auditable que valide el consumo diario. La "vergüenza de cobrar" es el resultado de no tener comprobantes que respalden la deuda.
*   **Ausencia de enrutamiento:** No hay consolidación de despachos por zona ni planificación de última milla.