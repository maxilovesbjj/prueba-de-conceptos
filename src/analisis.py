import json
import matplotlib.pyplot as plt
from pathlib import Path

# Cargar el reporte generado por el ETL
ruta_reporte = Path(__file__).resolve().parent.parent / 'data' / 'processed' / 'reporte.json'

with open(ruta_reporte, 'r', encoding='utf-8') as f:
    datos = json.load(f)

# 1. Gráfico de Ventas por Día (Línea)
fechas = [d['fecha'] for d in datos['ventas_por_dia']]
totales_dia = [d['total'] for d in datos['ventas_por_dia']]

plt.figure(figsize=(10, 4))
plt.plot(fechas, totales_dia, marker='o', color='#2ca02c', linewidth=2)
plt.title('Ingresos Diarios - Doña Rosa')
plt.ylabel('Pesos (CLP)')
plt.grid(True, linestyle='--', alpha=0.7)
plt.savefig(Path(__file__).resolve().parent.parent / 'data' / 'processed' / 'tendencia_ventas.png')
plt.close()

# 2. Gráfico de Platos (Barras - Ley de Pareto)
platos = [p['plato'] for p in datos['platos']]
unidades = [p['unidades'] for p in datos['platos']]

plt.figure(figsize=(8, 5))
plt.bar(platos, unidades, color='#1f77b4')
plt.title('Unidades Vendidas por Plato (Pareto)')
plt.ylabel('Cantidad')
plt.savefig(Path(__file__).resolve().parent.parent / 'data' / 'processed' / 'distribucion_platos.png')
plt.close()

print("Gráficos generados exitosamente en data/processed/")