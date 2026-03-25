# Configuración: OneDrive → Dashboard automático

Este documento explica cómo conectar el Excel de OneDrive para que el dashboard
se actualice automáticamente cada vez que guardas cambios.

---

## Arquitectura del flujo

```
Guardas el Excel en OneDrive
        ↓
Power Automate detecta el cambio (segundos)
        ↓
Power Automate llama a GitHub Actions via API
        ↓
GitHub Actions descarga el Excel desde OneDrive
        ↓
Procesa → data.json → deploya en GitHub Pages (~2-3 min)
```

---

## PASO 1 — Compartir el Excel en OneDrive

1. Abre **OneDrive** en el navegador (onedrive.live.com)
2. Haz clic derecho sobre `inventario.xlsx` → **Compartir**
3. Cambia el permiso a **"Cualquier persona con el vínculo puede ver"**
4. Copia el enlace. Se verá así:
   ```
   https://1drv.ms/x/s!AbCdEfGhIjKl...
   ```
5. Al final del enlace, agrega `&download=1`:
   ```
   https://1drv.ms/x/s!AbCdEfGhIjKl...&download=1
   ```
   Esta será tu **URL de descarga directa**.

---

## PASO 2 — Agregar el secret en GitHub

1. Ve a tu repositorio en GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. Clic en **"New repository secret"**
4. Nombre: `ONEDRIVE_DOWNLOAD_URL`
5. Valor: la URL de descarga directa del paso anterior
6. Guardar

---

## PASO 3 — Crear un Personal Access Token en GitHub

Power Automate necesita un token para poder activar el workflow de GitHub.

1. Ve a GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Clic en **"Generate new token (classic)"**
3. Nombre: `power-automate-dashboard`
4. Expiration: **No expiration** (o la que prefieras)
5. Selecciona el scope: ✅ **workflow**
6. Clic en **"Generate token"**
7. **Copia el token** (solo se muestra una vez). Se verá así:
   ```
   ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

---

## PASO 4 — Crear el flujo en Power Automate

1. Ve a **make.powerautomate.com**
2. Clic en **"Crear"** → **"Flujo automatizado de nube"**
3. Nombre del flujo: `Inventario Dashboard - Actualizar al guardar`

### Trigger (Desencadenador):
- Busca: **"Cuando se modifica un archivo (OneDrive)"**
- Carpeta: selecciona la carpeta donde está `inventario.xlsx`

### Acción:
- Clic en **"+ Nuevo paso"**
- Busca: **"HTTP"**
- Configura así:

| Campo | Valor |
|-------|-------|
| Método | `POST` |
| URI | `https://api.github.com/repos/THSUPER01/inventario-dashboardtest/actions/workflows/update-dashboard.yml/dispatches` |
| Encabezados | `Accept`: `application/vnd.github+json` |
| | `Authorization`: `Bearer ghp_TU_TOKEN_AQUI` |
| | `Content-Type`: `application/json` |
| | `X-GitHub-Api-Version`: `2022-11-28` |
| Cuerpo | `{"ref": "main"}` |

4. Guarda el flujo ✅

---

## PASO 5 — Probar

1. Abre el Excel en OneDrive y haz un cambio pequeño → Guardar
2. En unos segundos Power Automate dispara el flujo
3. Ve a GitHub → **Actions** → verás el workflow corriendo
4. En ~2-3 minutos el dashboard estará actualizado

---

## Notas

- El workflow también corre automáticamente de lunes a viernes a las 8am Colombia como respaldo
- Puedes dispararlo manualmente desde GitHub → Actions → "Update Dashboard Data" → "Run workflow"
- Si el Excel no ha cambiado, el workflow detecta que `data.json` no cambió y no hace commit innecesario
