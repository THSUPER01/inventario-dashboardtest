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

# ─── BUILD JSON ───────────────────────────────────────────────────────────────
data = {
    "generado": str(date.today()),
    "inventario": df.to_dict("records"),
    "por_centro": {k: int(v) for k, v in por_centro.items()},
    "por_almacen": {k: int(v) for k, v in por_almacen.items()},
    "top_materiales": top_list,
    "stats": {
        "total_registros": len(df),
        "total_materiales": int(df["Material"].nunique()),
        "total_stock": int(df["Libre utilización"].sum()),
        "sin_stock": int((df["Libre utilización"] == 0).sum()),
        "con_stock": int((df["Libre utilización"] > 0).sum()),
        "centros": sorted(df["Centro"].unique().tolist()),
        "almacenes": sorted([a for a in df["Almacén"].unique().tolist() if a]),
    },
}

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✓ data.json generado: {len(df)} registros, {data['stats']['total_stock']} unidades en stock")
print(f"  Centros: {data['stats']['centros']}")
print(f"  Almacenes: {data['stats']['almacenes']}")
print(f"  Archivo: {OUTPUT}")
