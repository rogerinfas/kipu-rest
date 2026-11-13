# KipuRest MVP: Live Vision (demo de feria)

Fecha: 2026-11-13. Estado: borrador para revisión.

## 1. Intención

Vender la idea de KipuRest en la Feria de Emprendimiento 2026. Quien se acerque al stand debe ver cómo una cámara instalada en el salón de cualquier restaurante detecta sola qué mesas están ocupadas y cuánto tiempo llevan sentados los clientes, sin que nadie marque nada a mano.

Lo que importa es que se vea llamativo y convincente. No es un ERP. Los CRUDs (comandas, inventario, caja) quedan fuera.

**Éxito:** un visitante mira la pantalla de 30 a 60 segundos y entiende sin explicación que las mesas cambian de estado solas, que hay cronómetros reales por mesa y que el sistema alerta demoras.

## 2. Alcance

### Incluido
- Reproducción en bucle de un video grabado de un salón real (cámara fija), analizado en vivo con YOLO.
- Mesas definidas como zonas (polígonos) sobre el video, dibujadas una vez en un modo de calibración y guardadas en un archivo JSON.
- Estado por mesa: `LIBRE`, `ATENCIÓN` (recién ocupada), `ÓPTIMO`, `ALERTA` (más de 10 minutos de espera; el umbral es configurable).
- Cronómetro por mesa desde que se ocupa.
- Indicadores: ocupación del salón (%), tiempo promedio de ocupación y rotación (mesas liberadas desde el arranque).
- "Sugerencia IA": un texto generado por reglas a partir del estado (por ejemplo, "Priorizar pase de Mesa 01 en cocina").
- Datos simulados de negocio por mesa: monto en soles y etapa ("esperando plato fuerte", "consumiendo"). Son coherentes con el tiempo de ocupación, pero no se detectan.
- Privacidad: solo se muestran cajas y conteos; no se guardan imágenes ni se identifican rostros.

### Fuera (no-goals)
- Comandas, recetas, inventario, caja, login y usuarios.
- Base de datos. El estado vive en memoria y se reinicia en cada arranque.
- Detección real de platos.
- Cámara en vivo por RTSP. Queda preparado (la fuente de video es configurable), pero no se prueba.
- Despliegue en la nube.

### Anti-goals
- Que la demo se congele, se vea entrecortada o falle frente al público.
- Que los estados parpadeen de ocupada a libre cada segundo por ruido de detección.
- Que dependa de internet en el stand.

## 3. Restricciones
- **Hardware de la feria:** una sola laptop con GTX 1650, probablemente Windows (puede ser Linux). No hay internet garantizado.
- **Desarrollo:** se hace en este PC Arch Linux sin GPU, así que todo debe correr también en CPU (más lento).
- **Puertos** (según `AGENTS.md`, verificados el 2026-11-13): frontend **3001** (el 3000 está ocupado) y backend **5000**.
- Sin Docker en el MVP: no hay servicio de Postgres que levantar.

## 4. Decisiones tomadas

### Stack
- **Backend:** Python 3.11+, FastAPI, Uvicorn, Ultralytics YOLO (modelo `yolo11n` o `yolov8n`, clase `person`), OpenCV para leer el video y Shapely (o una prueba simple de punto en polígono) para asignar personas a mesas. Usa CUDA si existe y CPU si no.
- **Frontend:** React, Vite, TypeScript, TanStack Router y Tailwind. Gestor de paquetes: pnpm.
- **Comunicación:**
  - WebSocket `/ws/state`: el estado del salón, unas 5 veces por segundo.
  - Stream MJPEG `/video`: los frames ya anotados.
  - REST: `/api/zones` (GET y PUT de las zonas) y `/api/health`.

### Layout de pantalla (elegido: B)
- Barra superior: marca "KipuRest Live Vision", ocupación, tiempo promedio e indicador "● EN VIVO".
- Video protagonista grande con las zonas de mesa coloreadas según su estado, la etiqueta `M01 14:20` y las cajas de personas. La "Sugerencia IA" va superpuesta en una esquina, y una marca "CAM-01 · sin rostros".
- Tira inferior con una tarjeta por mesa (color de estado y cronómetro).
- Colores: rojo para alerta, verde para óptimo, ámbar para atención y gris punteado para libre. Tema oscuro.
- Pensado para pantalla completa a 1920×1080.

### Lógica de ocupación
- Una persona pertenece a una mesa si el punto inferior-centro de su caja cae dentro del polígono de esa mesa.
- **Histéresis contra parpadeo:**
  - La mesa pasa a ocupada tras N segundos seguidos con al menos 1 persona (por defecto 2 s).
  - Pasa a libre tras M segundos seguidos sin personas (por defecto 5 s).
- Cronómetro: arranca al confirmarse la ocupación y se reinicia al liberarse. Al liberarse, la mesa suma una rotación y su duración entra al promedio.
- Estados:
  - `ATENCIÓN`: menos de 3 minutos ocupada.
  - `ÓPTIMO`: ocupada y sin alerta.
  - `ALERTA`: la etapa simulada es "esperando" y supera el umbral.

### Aceleración de tiempo
Un video de stock dura de 30 segundos a pocos minutos, así que un cronómetro real nunca llegaría a 10 minutos. Se agrega un **factor de tiempo de demo** configurable (por ejemplo, ×20): el cronómetro mostrado avanza más rápido que el reloj real. Al reiniciarse el bucle del video, el estado se resetea de forma limpia.

### Video
- Primera tarea: conseguir de 5 a 8 candidatos en Pexels (API gratuita, se necesita una clave del usuario) en 1080p o 4K, con cámara fija, ángulo elevado, varias mesas y gente sentándose y levantándose. El usuario elige uno o dos.
- Los videos van en `backend/media/`, que está en `.gitignore`. El README documenta el origen y la licencia (Pexels License).

### Arranque en la feria
- Script `start.bat` (Windows) y `start.sh` (Linux): levantan el backend, sirven el frontend ya compilado desde el propio FastAPI y abren el navegador en pantalla completa. Así solo hay un proceso y un puerto (5000) en la feria. El puerto 3001 solo se usa en desarrollo con Vite.
- `docs/instalacion-laptop-feria.md`: instalación de drivers NVIDIA, PyTorch con CUDA y Node/pnpm (solo para compilar), en Windows y en Linux.
- El modelo YOLO se descarga antes de ir a la feria y queda en local.

### Decisiones cerradas tras la revisión
- **Inferencia en vivo de verdad** (decisión del usuario). No hay modo precalculado. Para evitar que se congele, el video siempre se reproduce a su velocidad normal: la inferencia corre en otro hilo sobre el frame más reciente y salta frames si va lenta (en CPU, menos detecciones por segundo; el video no se traba). Se muestran los FPS de inferencia en la pantalla de diagnóstico, no en la de demo.
- **Etapa simulada** (decisión del builder): guion fijo por ocupación, con "recién sentados", luego "esperando plato", luego "consumiendo". La duración de cada etapa sale de una semilla fija por mesa, así que es reproducible. `ALERTA` se activa si "esperando" supera el umbral y se apaga cuando pasa a "consumiendo". El monto en soles crece en "consumiendo".
- **Bucle del video** (decisión del builder): al reiniciarse, solo se reinician los cronómetros y estados de las mesas. La rotación y el promedio se acumulan desde el arranque del proceso.
- **Calibración** (decisión del builder): una pantalla web `/calibrar` donde se hace clic sobre un frame del video para marcar los vértices de cada mesa. Guarda las zonas con `PUT /api/zones`.
- **Clave de Pexels:** la entrega el usuario. Se usa solo en un script local y nunca se guarda en el repositorio.
- **Laptop de la feria:** posiblemente habrá acceso previo para probar (no confirmado). Por eso la guía de instalación debe ser paso a paso, con un script de verificación (`scripts/check_env`) que informe si CUDA, el modelo, el video y las zonas están listos.

## 5. Estructura propuesta
```
KipuRest/
  backend/   app/ (main.py, vision.py, tracker.py, simulation.py, config.py)
             zones/   media/ (ignorado)   tests/   pyproject.toml
  frontend/  src/ (routes/, components/, hooks/useSalonState.ts)
  scripts/   start.sh  start.bat
  docs/
```

## 6. Pruebas
- Unitarias en Python para la máquina de estados de las mesas (histéresis, cronómetro, rotación) con detecciones falsas.
- Prueba de humo: el backend procesa N frames del video en CPU sin errores.
- Comprobación manual: la pantalla corre 10 minutos en bucle sin congelarse.

## 7. A criterio del builder
- La librería exacta de UI y de animaciones.
- `yolo11n` o `yolov8n`, y el tamaño de inferencia, según los FPS medidos.
- El formato del JSON de zonas.
- Las reglas concretas de la "Sugerencia IA".
