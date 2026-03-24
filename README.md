# 📊 Inventario Dashboard

Dashboard web de inventario conectado a Excel, publicado en GitHub Pages con actualización automática.

## 🚀 Deploy en 5 pasos

### 1. Crear repositorio en GitHub
```
Nuevo repo → nombre: inventario-dashboard → Público ✓ → Crear
```

### 2. Subir archivos
Sube todos estos archivos al repositorio:
```
inventario-dashboard/
├── index.html            ← dashboard web
├── data.json             ← datos generados desde Excel
├── build_data.py         ← script de transformación
├── inventario.xlsx       ← tu archivo Excel (renombrado)
└── .github/
    └── workflows/
        └── update-dashboard.yml  ← automatización CI/CD
```

### 3. Activar GitHub Pages
```
Repositorio → Settings → Pages
Source: Deploy from a branch
Branch: gh-pages → / (root) → Save
```

### 4. Tu URL queda disponible en:
```
https://TU_USUARIO.github.io/inventario-dashboard/
```

### 5. Actualizar el dashboard
Cada vez que subas un nuevo `inventario.xlsx`:
- GitHub Actions corre automáticamente `build_data.py`
- Genera `data.json` actualizado
- Hace deploy del dashboard en ~2 minutos

---

## 🔄 Flujo de actualización

```
Tu Excel (inventario.xlsx)
        ↓  git push / GitHub UI
    GitHub Repository
        ↓  GitHub Actions (automático)
    build_data.py  →  data.json
        ↓  peaceiris/actions-gh-pages
    gh-pages branch
        ↓
    Dashboard URL actualizado ✓
```

## 📁 Estructura del proyecto

```
inventario-dashboard/
│
├── index.html              # Dashboard HTML/CSS/JS puro (sin dependencias externas excepto Chart.js CDN)
├── data.json               # Datos procesados del Excel — generado automáticamente
├── build_data.py           # Script Python: Excel → JSON
├── inventario.xlsx         # Fuente de datos (actualizar este archivo)
├── requirements.txt        # pandas, openpyxl
│
└── .github/
    └── workflows/
        └── update-dashboard.yml  # Pipeline CI/CD
```

## 🛠 Ejecutar localmente

```bash
# Instalar dependencias
pip install pandas openpyxl

# Generar data.json desde tu Excel
python build_data.py inventario.xlsx

# Abrir dashboard en navegador
open index.html   # macOS
start index.html  # Windows
```

## ⚙️ Personalización

### Cambiar columnas del Excel
En `build_data.py` ajusta los nombres de columna según tu archivo:
```python
SHEET = "Sheet1"   # nombre de la hoja
# Columnas esperadas:
# Material | Texto breve de material | Centro | Almacén | Libre utilización
```

### Cambiar frecuencia de actualización automática
En `.github/workflows/update-dashboard.yml`:
```yaml
schedule:
  - cron: '0 6 * * 1-5'   # Lunes-Viernes 6am UTC
  # Más opciones:
  # '0 */4 * * *'           → cada 4 horas
  # '0 8,12,17 * * 1-5'    → 3 veces al día laboral
```

## 📦 Tecnologías

| Componente | Tecnología | Razón |
|---|---|---|
| Frontend | HTML/CSS/JS puro | Sin build tools, deploy directo |
| Gráficos | Chart.js 4 (CDN) | Ligero, bien documentado |
| Datos | JSON estático | Rápido, sin servidor |
| Procesamiento | Python + pandas | Robusto para Excel |
| CI/CD | GitHub Actions | Gratuito, integrado |
| Hosting | GitHub Pages | Gratuito, HTTPS automático |
