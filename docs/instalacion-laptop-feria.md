# Instalación en la laptop de la feria (GTX 1650)

Haz todo esto **antes** de la feria y **con internet**. El día del evento no hace falta conexión.

## 1. Requisitos comunes

1. **Driver de NVIDIA** actualizado:
   - Windows: GeForce Experience o https://www.nvidia.com/drivers (versión 560 o superior).
   - Linux: driver propietario 580 o superior. En Arch: `sudo pacman -S nvidia nvidia-utils`; en Ubuntu: `sudo ubuntu-drivers install`.
   - Compruébalo con `nvidia-smi`: debe mostrar la GTX 1650 y, arriba a la derecha, la versión del driver.
   - **Importante en Linux:** el torch que se instala necesita CUDA 13, es decir, un driver **580 o superior**. Con un driver más viejo, la detección cae a la CPU sin error (solo un `[AVISO]` en `check_env`) y va mucho más lenta.
2. **uv** (gestor de Python):
   - Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
   - Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
3. **Node.js 20 o superior y pnpm**. Solo se usan para compilar el frontend: `npm install -g pnpm`.
4. **Git**, para clonar el repositorio.

## 2. Preparar el proyecto

```bash
git clone https://github.com/rogerinfas/kipu-rest.git
cd kipu-rest
```

Copia el video del salón a `backend/media/flow-salon-v1.mp4`. No está en el repositorio. Si usas otro nombre, define `KIPU_VIDEO` con su ruta.

```bash
cd backend
uv sync                                        # en Windows instala torch con CUDA 12.6
uv run python ../scripts/check_env.py --prepare  # descarga el modelo YOLO
cd ../frontend
pnpm install
pnpm build
```

`check_env` debe mostrar `[OK]` en todo, incluida la línea **GPU CUDA: NVIDIA GeForce GTX 1650**. Si dice "Sin CUDA", revisa el driver (paso 1).

## 3. Arrancar la demo

- Windows: haz doble clic en `scripts\start.bat`.
- Linux: `./scripts/start.sh`

Se abre el navegador en http://localhost:5000.

| Tecla | Acción |
|---|---|
| `F` | Pantalla completa |
| `C` | Calibrar mesas (`Esc` vuelve) |
| `Ctrl+C` en la terminal | Detener la demo |

## 4. Calibrar las mesas (solo si cambias de video)

1. Pulsa `C`.
2. Haz clic alrededor de cada mesa, **incluyendo sus sillas**: el sistema ubica a cada persona por la posición de sus pies.
3. `Enter` cierra la mesa. Al final, pulsa **Guardar**.

## 5. Ensayo general (obligatorio)

1. Deja la demo corriendo **10 minutos** en pantalla completa.
2. Comprueba que el video no se traba, que los cronómetros avanzan, que aparecen alertas rojas y que cada ~75 s el salón "rota".
3. Desactiva la suspensión de pantalla y el ahorro de energía. Conecta la laptop a la corriente: la GPU rinde menos con batería.

## Ajustes opcionales (variables de entorno)

| Variable | Por defecto | Qué hace |
|---|---|---|
| `KIPU_VIDEO` | `backend/media/flow-salon-v1.mp4` | Video a reproducir |
| `KIPU_TIME_FACTOR` | `20` | Aceleración del cronómetro mostrado |
| `KIPU_ALERT_MIN` | `10` | Minutos (mostrados) para la alerta |
| `KIPU_CYCLE_S` | `75` | Segundos reales entre "rotaciones" del salón |
| `KIPU_CONF` | `0.35` | Confianza mínima de detección |
| `KIPU_PORT` | `5000` | Puerto |
