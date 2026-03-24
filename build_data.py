#!/usr/bin/env python3
"""
build_data.py — Convierte el archivo Excel de inventario a data.json para el dashboard.
Uso:
    python build_data.py                        # usa inventario.xlsx en el mismo directorio
    python build_data.py ruta/al/archivo.xlsx   # ruta personalizada
"""
import sys
import json
import pandas as pd
from pathlib import Path
from datetime import date

# ─── CONFIG ───────────────────────────────────────────────────────────────────
SHEET = "Sheet1"
EXCEL_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "inventario.xlsx"
OUTPUT = Path(__file__).parent / "data.json"

# ─── READ ─────────────────────────────────────────────────────────────────────
df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET)
df = df.dropna(subset=["Centro"])

# Normalize types
df["Material"] = df["Material"].apply(lambda x: str(int(x)) if pd.notna(x) else "")
df["Almacén"] = df["Almacén"].apply(lambda x: str(int(x)) if pd.notna(x) else "")
df["Libre utilización"] = df["Libre utilización"].fillna(0).astype(int)

# ─── AGGREGATE ────────────────────────────────────────────────────────────────
por_centro = df.groupby("Centro")["Libre utilización"].sum().to_dict()
por_almacen = df.groupby("Almacén")["Libre utilización"].sum().to_dict()

top_mat = (
    df.groupby(["Material", "Texto breve de material"])["Libre utilización"]
    .sum()
    .sort_values(ascending=False)
    .head(15)
)
top_list = [
    {"material": m, "nombre": n, "stock": int(s)}
    for (m, n), s in top_mat.items()
]

# ─── NEW KPI AGGREGATIONS ────────────────────────────────────────────────────
total_registros = len(df)
total_stock = int(df["Libre utilización"].sum())
sin_stock = int((df["Libre utilización"] == 0).sum())
con_stock = int((df["Libre utilización"] > 0).sum())

# Zero stock rate as percentage
tasa_sin_stock = round(sin_stock / total_registros * 100, 1) if total_registros > 0 else 0

# Average stock per record (only for records with stock > 0)
con_stock_df = df[df["Libre utilización"] > 0]
stock_promedio = round(con_stock_df["Libre utilización"].mean(), 1) if len(con_stock_df) > 0 else 0

# Stock concentration in top 10 materials
top10_stock = (
    df.groupby("Material")["Libre utilización"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .sum()
)
concentracion_top10 = round(top10_stock / total_stock * 100, 1) if total_stock > 0 else 0

# Materials at risk: materials whose TOTAL stock across all centers is between 1 and 5
stock_por_material = df.groupby("Material")["Libre utilización"].sum()
materiales_en_riesgo = int(((stock_por_material > 0) & (stock_por_material <= 5)).sum())

# Coverage by center: count of unique materials with stock > 0 per center
cobertura_por_centro = (
    df[df["Libre utilización"] > 0]
    .groupby("Centro")["Material"]
    .nunique()
    .to_dict()
)

# ─── BUILD JSON ───────────────────────────────────────────────────────────────
data = {
    "generado": str(date.today()),
    "inventario": df.to_dict("records"),
    "por_centro": {k: int(v) for k, v in por_centro.items()},
    "por_almacen": {k: int(v) for k, v in por_almacen.items()},
    "top_materiales": top_list,
    "stats": {
        "total_registros": total_registros,
        "total_materiales": int(df["Material"].nunique()),
        "total_stock": total_stock,
        "sin_stock": sin_stock,
        "con_stock": con_stock,
        "centros": sorted(df["Centro"].unique().tolist()),
        "almacenes": sorted([a for a in df["Almacén"].unique().tolist() if a]),
        "tasa_sin_stock": tasa_sin_stock,
        "stock_promedio": stock_promedio,
        "concentracion_top10": concentracion_top10,
        "materiales_en_riesgo": materiales_en_riesgo,
        "cobertura_por_centro": {k: int(v) for k, v in cobertura_por_centro.items()},
    },
}

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✓ data.json generado: {len(df)} registros, {data['stats']['total_stock']} unidades en stock")
print(f"  Centros: {data['stats']['centros']}")
print(f"  Almacenes: {data['stats']['almacenes']}")
print(f"  Archivo: {OUTPUT}")
