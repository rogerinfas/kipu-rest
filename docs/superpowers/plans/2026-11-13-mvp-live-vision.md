# KipuRest Live Vision MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Pantalla de demo que reproduce un video de un salón y, con YOLO en vivo, muestra qué mesas están ocupadas, sus cronómetros, sus alertas y los KPIs.

**Architecture:** Un backend FastAPI corre un hilo de lectura del video (a velocidad real) y un hilo de inferencia YOLO sobre el último frame. Un `SalonTracker` puro convierte detecciones en estados de mesa. El estado se emite por WebSocket y los frames anotados por MJPEG. Un frontend React (layout B) consume ambos. En la feria, FastAPI sirve el frontend compilado en un solo puerto.

**Tech Stack:** Python 3.12 (uv), FastAPI, Uvicorn, Ultralytics, OpenCV, pytest · React 19, Vite, TypeScript, TanStack Router, Tailwind v4, pnpm.

**Spec:** `docs/superpowers/specs/2026-11-13-mvp-live-vision-design.md`

## Global Constraints

- Backend: puerto 5000. Frontend en desarrollo: puerto 3001 (Vite proxy de `/api`, `/ws` y `/video` hacia 5000).
- Sin base de datos ni Docker. Estado en memoria.
- Usar CUDA si `torch.cuda.is_available()`; si no, CPU. Nunca fallar por falta de GPU.
- Video por defecto: `backend/media/flow-salon-v1.mp4`, configurable con `KIPU_VIDEO`. `media/` no se versiona.
- Umbral de alerta: 10 minutos mostrados (`KIPU_ALERT_MIN=10`). Factor de tiempo de demo ×20 (`KIPU_TIME_FACTOR=20`).
- Histéresis: ocupar tras 2 s reales con al menos 1 persona; liberar tras 5 s reales sin personas. `ATENCIÓN` dura menos de 3 min mostrados.
- Privacidad: no guardar frames ni recortes; solo cajas y conteos.
- Textos de interfaz en español. Tema oscuro. Pensado para 1920×1080.
- Multiplataforma: Windows y Linux. Rutas con `pathlib`; nada específico de bash dentro de Python.

## Review Focus

1. Video corto (3,9 s) en bucle: el reinicio no debe dejar mesas "fantasma" ocupadas ni romper el MJPEG. Prueba en Task 2: `test_loop_reset_clears_tables_keeps_kpis`.
2. Detecciones intermitentes (una persona desaparece 1 frame): la mesa no debe parpadear. Prueba en Task 2: `test_brief_dropout_does_not_free_table`.
3. Archivo de zonas inexistente o vacío: el sistema arranca, muestra el video sin mesas e indica "calibrar". Prueba en Task 4: `test_missing_zones_file_returns_empty`.
4. Video inexistente: el backend arranca y `/api/health` reporta `video_ok=false`, sin excepción. Prueba en Task 5: `test_health_without_video`.
5. El cliente WebSocket se cae y reconecta: el servidor no se cae y el hook reconecta cada 1 s. Prueba en Task 5: `test_ws_disconnect_is_harmless`; el hook se revisa manualmente en Task 7.

---

## File Structure

```
backend/
  pyproject.toml
  app/config.py        # Settings (env vars)
  app/models.py        # dataclasses / pydantic: Zone, Detection, TableState, SalonState
  app/geometry.py      # foot_point, point_in_polygon
  app/simulation.py    # TableScript: etapa y monto simulados, deterministas
  app/tracker.py       # SalonTracker: lógica pura de estados
  app/zones.py         # load_zones / save_zones (JSON)
  app/detector.py      # Detector (YOLO, device auto)
  app/pipeline.py      # VideoPipeline: hilos de lectura e inferencia, frame anotado
  app/main.py          # FastAPI: rutas, WS, MJPEG, estáticos
  zones/salon.json
  tests/...
frontend/              # Vite React TS
  src/routes/__root.tsx, index.tsx, calibrar.tsx
  src/hooks/useSalonState.ts
  src/components/TopBar.tsx, VideoStage.tsx, TableStrip.tsx, AiHint.tsx
  src/lib/types.ts, format.ts
scripts/start.sh, start.bat, check_env.py
docs/instalacion-laptop-feria.md
```

---

### Task 1: Esqueleto del backend, modelos y geometría

**Files:**
- Create: `backend/pyproject.toml`, `backend/app/__init__.py`, `backend/app/config.py`, `backend/app/models.py`, `backend/app/geometry.py`
- Test: `backend/tests/test_geometry.py`

**Interfaces:**
- Produces:
  - `Detection(x1: float, y1: float, x2: float, y2: float, conf: float)`.
  - `Zone(id: str, name: str, polygon: list[tuple[float, float]])`, con coordenadas **normalizadas 0..1**.
  - `foot_point(d: Detection, w: int, h: int) -> tuple[float, float]`: punto inferior-centro normalizado.
  - `point_in_polygon(p, poly) -> bool`: ray casting.
  - `Settings`: `video_path`, `zones_path`, `model_name="yolo11n.pt"`, `alert_min=10`, `time_factor=20`, `occupy_s=2.0`, `release_s=5.0`, `attention_min=3`, `conf=0.35`, `imgsz=960`, `port=5000`. Se lee de variables `KIPU_*`.

- [ ] **Step 1:** `uv init --python 3.12` en `backend/`. Agregar dependencias: `fastapi uvicorn[standard] ultralytics opencv-python-headless numpy pydantic`; para desarrollo, `pytest httpx`.
- [ ] **Step 2: Tests**
  - `test_foot_point`: con la caja (100, 100, 300, 500) en un frame de 1000×1000, el resultado es `(0.2, 0.5)`.
  - `test_point_in_square`: (0.5, 0.5) está dentro de [(0,0), (1,0), (1,1), (0,1)]. (1.5, 0.5) está fuera.
  - `test_point_in_concave`: un polígono en forma de L excluye el hueco.
- [ ] **Step 3:** Correr `uv run pytest -q` y confirmar que falla. Implementar. Confirmar que pasa.
- [ ] **Step 4:** Commit con el mensaje `feat(backend): esqueleto, modelos y geometría`.

### Task 2: SalonTracker y simulación

**Files:**
- Create: `backend/app/simulation.py`, `backend/app/tracker.py`
- Test: `backend/tests/test_tracker.py`, `backend/tests/test_simulation.py`

**Interfaces:**
- Consumes: `Zone`, `Detection`, `foot_point`, `point_in_polygon`, `Settings`.
- Produces:
  - `TableScript(seed: int)`, con `.stage(elapsed_shown_s: float) -> Literal["sentados","esperando","consumiendo"]` y `.amount(elapsed_shown_s) -> float` en soles. El monto es 0 hasta "consumiendo" y después llega a un valor de entre 40 y 180, según la semilla.
    - Duraciones (en tiempo mostrado): "sentados" de 1 a 3 min; "esperando" de 4 a 14 min (así algunas mesas cruzan el umbral de 10); el resto, "consumiendo".
    - Usar `random.Random(seed)`.
  - `TableState` (pydantic): `id`, `name`, `status: Literal["LIBRE","ATENCION","OPTIMO","ALERTA"]`, `people: int`, `elapsed_s: float` (mostrados), `stage: str | None`, `amount: float`, `stage_note: str`.
  - `SalonState`: `tables: list[TableState]`, `occupancy_pct: int`, `avg_occupancy_s: float` (mostrados, de mesas liberadas), `rotations: int`, `hint: str`, `fps: float`, `device: str`.
  - `SalonTracker(zones, settings)`:
    - `.update(dets: list[Detection], w: int, h: int, now: float) -> None` (`now` es el reloj real en segundos).
    - `.snapshot(now: float) -> SalonState`.
    - `.reset_tables() -> None`.
  - Semilla de cada mesa: `hash` estable de `zone.id` + número de ocupación.
- Reglas de la "Sugerencia IA" (`hint`):
  - Si hay mesas en ALERTA: `"Priorizar pase de {Mesa X} en cocina"`, tomando la de mayor tiempo.
  - Si no, si la ocupación pasa del 80%: `"Salón casi lleno: preparar rotación"`.
  - Si no: `"Servicio fluido"`.
- `stage_note`: "Comensales recién sentados", "Esperando plato fuerte", "Consumiendo · S/ {amount:.0f}" o "Lista para nuevos clientes".

- [ ] **Step 1: Tests** (con un reloj `now` inyectado y dos zonas cuadradas):
  - `test_occupies_after_2s`: 1 persona dentro durante 1,9 s da LIBRE; a los 2,1 s da ATENCION.
  - `test_brief_dropout_does_not_free_table`: ocupada, luego 1 s sin detecciones y vuelve la persona; sigue ocupada y el cronómetro no se reinicia.
  - `test_frees_after_5s_counts_rotation`: ocupada 30 s reales y luego 5,1 s vacía. Resultado: LIBRE, `rotations == 1` y `avg_occupancy_s` cerca de 30×20.
  - `test_elapsed_uses_time_factor`: tras 30 s reales, `elapsed_s` es 600 ± 1.
  - `test_alert_when_waiting_over_threshold`: usar una semilla cuyo guion dé "esperando" por más de 10 min y avanzar hasta 10,5 min mostrados. Resultado: ALERTA y `hint` menciona esa mesa.
  - `test_loop_reset_clears_tables_keeps_kpis`: tras `reset_tables()` todas quedan LIBRE con `elapsed_s == 0`, y `rotations` se mantiene.
  - `test_occupancy_pct`: con 1 de 2 mesas ocupadas, da 50.
  - `test_script_deterministic`: el mismo seed da las mismas etapas.
- [ ] **Step 2:** Confirmar que los tests fallan. Implementar. Confirmar que pasan.
- [ ] **Step 3:** Commit con el mensaje `feat(backend): tracker de mesas con histéresis y simulación`.

### Task 3: Detector YOLO

**Files:**
- Create: `backend/app/detector.py`
- Test: `backend/tests/test_detector.py` (marcado `slow`)

**Interfaces:**
- Produces: `Detector(model_name, conf, imgsz)`, con `.device: str` ("cuda:0" o "cpu") y `.detect(frame_bgr: np.ndarray) -> list[Detection]`. Solo la clase 0 (person). Usa `half=True` solo en CUDA.

- [ ] **Step 1:** Test `test_detects_people_in_salon`: sobre el frame a 3,5 s de `media/flow-salon-v1.mp4`, debe detectar al menos 8 personas. Se salta si el video no existe.
- [ ] **Step 2:** Confirmar que falla, implementar y confirmar que pasa con `uv run pytest -m slow`. Medir el tiempo por frame en CPU y anotarlo en el commit.
- [ ] **Step 3:** Commit con el mensaje `feat(backend): detector YOLO con selección de dispositivo`.

### Task 4: Zonas (JSON) y API de zonas

**Files:**
- Create: `backend/app/zones.py`, `backend/zones/salon.json` (inicialmente `[]`)
- Test: `backend/tests/test_zones.py`

**Interfaces:**
- Produces:
  - `load_zones(path: Path) -> list[Zone]`: devuelve `[]` si el archivo no existe o es inválido, y lo registra con un warning.
  - `save_zones(path, zones) -> None`: escritura atómica (archivo temporal más reemplazo).

- [ ] **Step 1:** Tests:
  - `test_roundtrip`.
  - `test_missing_zones_file_returns_empty`.
  - `test_invalid_json_returns_empty`.
  - `test_rejects_polygon_under_3_points`: `save_zones` lanza `ValueError`.
- [ ] **Step 2:** Confirmar que fallan, implementar y confirmar que pasan.
- [ ] **Step 3:** Commit.

### Task 5: Pipeline de video y FastAPI

**Files:**
- Create: `backend/app/pipeline.py`, `backend/app/main.py`
- Test: `backend/tests/test_api.py`

**Interfaces:**
- Consumes: `Detector`, `SalonTracker`, `load_zones`, `save_zones`, `Settings`.
- Produces:
  - `VideoPipeline(settings, detector_factory)`, con estos métodos:
    - `.start()` y `.stop()`.
    - `.latest_jpeg() -> bytes | None`.
    - `.state() -> SalonState`.
    - `.set_zones(zones)`.
    - `.video_ok: bool`.
  - Hilo lector: lee con `cv2.VideoCapture` y espera `1/fps` entre frames. Al llegar al final, vuelve a 0 y llama a `tracker.reset_tables()`.
  - Hilo de inferencia: toma el último frame, detecta, llama a `tracker.update` y dibuja el frame anotado (cajas de personas en azul, polígonos coloreados por estado y etiqueta `M01 14:20`). Lo codifica en JPEG con calidad 80 y lo guarda. Las anotaciones se dibujan sobre el último frame del lector con las últimas detecciones, así el video fluye aunque la inferencia vaya lenta.
  - Rutas:
    - `GET /api/health` devuelve `{video_ok, device, fps, zones}`.
    - `GET /api/zones` y `PUT /api/zones` (lista de Zone).
    - `GET /api/frame.jpg`: un frame limpio sin anotar, para calibrar.
    - `GET /video`: MJPEG con `multipart/x-mixed-replace; boundary=frame`.
    - `WS /ws/state`: envía `SalonState.model_dump()` cada 200 ms.
    - Si existe `frontend/dist`, se monta como estático en `/`, con fallback a `index.html`.

- [ ] **Step 1:** Tests con `TestClient` y un detector falso (inyectado con `app.state` o con una fábrica):
  - `test_health_without_video`: con `KIPU_VIDEO` apuntando a una ruta inexistente, responde 200 y `video_ok` es false.
  - `test_zones_put_get`.
  - `test_ws_sends_state`: recibe un JSON con la clave `tables`.
  - `test_ws_disconnect_is_harmless`: abrir, cerrar y abrir otra vez funciona.
- [ ] **Step 2:** Confirmar que fallan, implementar y confirmar que pasan.
- [ ] **Step 3: Verificación manual.** Correr `uv run uvicorn app.main:app --port 5000` y abrir `http://localhost:5000/video`: el video se ve en bucle con cajas de personas. Detener el servidor.
- [ ] **Step 4:** Commit con el mensaje `feat(backend): pipeline en vivo, WS, MJPEG y API`.

### Task 6: Frontend, esqueleto y tipos

**Files:**
- Create: `frontend/` (Vite React TS), `src/lib/types.ts`, `src/lib/format.ts`, `src/hooks/useSalonState.ts`, `src/routes/__root.tsx`
- Test: `frontend/src/lib/format.test.ts` (vitest)

**Interfaces:**
- Produces:
  - `types.ts`: replica exacta de `TableState` y `SalonState`.
  - `fmtClock(s: number) -> "mm:ss"`, y `"hh:mm:ss"` desde 3600 s.
  - `useSalonState(): { state: SalonState | null; connected: boolean }`: WebSocket a `/ws/state` que reconecta cada 1 s.
  - `STATUS_COLOR`: LIBRE `#6e7681`, ATENCION `#f0b429`, OPTIMO `#3fb950`, ALERTA `#ff5c5c`.

- [ ] **Step 1:** Ejecutar `pnpm create vite frontend --template react-ts` y agregar `@tanstack/react-router @tanstack/router-plugin tailwindcss @tailwindcss/vite vitest`. Configurar Vite en el puerto 3001 con proxy de `/api`, `/video` y `/ws` (este con ws: true) hacia `http://localhost:5000`.
- [ ] **Step 2:** Tests de `fmtClock`: 0 da `"00:00"`, 860 da `"14:20"` y 3725 da `"01:02:05"`.
- [ ] **Step 3:** Confirmar que fallan, implementar y confirmar que pasan con `pnpm vitest run`.
- [ ] **Step 4:** Commit.

### Task 7: Pantalla de demo (layout B)

**Files:**
- Create: `src/routes/index.tsx`, `src/components/TopBar.tsx`, `VideoStage.tsx`, `TableStrip.tsx`, `AiHint.tsx`

**Interfaces:**
- Consumes: `useSalonState`, `fmtClock`, `STATUS_COLOR`.

Layout B del spec:
- Barra superior: marca, ocupación %, promedio, rotaciones y "● EN VIVO". El punto rojo parpadea si hay conexión; si no, aparece "Reconectando…".
- `VideoStage`: `<img src="/video">` a todo el ancho, con relación 16:9. `AiHint` superpuesto abajo a la derecha y "CAM-01 · sin rostros" abajo a la izquierda.
- `TableStrip`: grilla con una tarjeta por mesa. Cada tarjeta lleva el nombre, el estado, el cronómetro grande y el `stage_note`. Las tarjetas en ALERTA tienen un pulso suave.
- Tecla `F`: pantalla completa. La ruta no hace scroll a 1920×1080.

- [ ] **Step 1:** Implementar.
- [ ] **Step 2: Verificación manual.** Con el backend en 5000 y `pnpm dev` en 3001, abrir `http://localhost:3001`: las mesas cambian de estado, los cronómetros avanzan y la reconexión funciona al reiniciar el backend. Detener ambos procesos.
- [ ] **Step 3:** Commit con el mensaje `feat(frontend): pantalla de demo Live Vision`.

### Task 8: Pantalla de calibración

**Files:**
- Create: `src/routes/calibrar.tsx`

**Behavior:**
- Muestra `/api/frame.jpg` con un `<svg>` superpuesto.
- Al hacer clic se agrega un vértice (normalizado); `Enter` cierra el polígono y pide el nombre ("Mesa 01" por defecto, con numeración automática).
- Hay una lista de mesas con la opción de borrar cada una, y los botones "Guardar" (`PUT /api/zones`) y "Cargar" (`GET`).
- Desde la demo se accede con la tecla `C`; desde la calibración, `Esc` vuelve.

- [ ] **Step 1:** Implementar.
- [ ] **Step 2: Verificación manual.** Dibujar las mesas del `flow-salon-v1.mp4`, guardar y volver a la demo: las zonas aparecen en el video. Hacer commit de `backend/zones/salon.json` con las zonas reales.
- [ ] **Step 3:** Commit con el mensaje `feat(frontend): calibración de zonas`.

### Task 9: Arranque de feria, verificación de entorno y documentación

**Files:**
- Create: `scripts/start.sh`, `scripts/start.bat`, `scripts/check_env.py`, `docs/instalacion-laptop-feria.md`
- Modify: `README.md` (sección "Cómo correr la demo")

**Behavior:**
- `check_env.py` imprime ✔ o ✘ para cada punto:
  - Versión de Python.
  - `torch` y `cuda` disponible, con el nombre de la GPU.
  - Modelo descargado (si falta, lo descarga con `--prepare`).
  - El video existe y se puede leer.
  - Las zonas tienen al menos 1 mesa.
  - Existe `frontend/dist`.
  - Devuelve código de salida distinto de 0 si algo crítico falla.
- `start.*` ejecuta `check_env`, levanta `uvicorn app.main:app --port 5000`, espera a `/api/health` y abre el navegador en `http://localhost:5000`.
- La guía de instalación cubre Windows y Linux:
  - Driver de NVIDIA.
  - uv, `uv sync` e instalación de torch con CUDA 12.x (`uv pip install torch --index-url https://download.pytorch.org/whl/cu124`).
  - `pnpm install && pnpm build`.
  - `check_env --prepare` con internet antes de la feria.
  - Ensayo de 10 minutos.

- [ ] **Step 1:** Implementar.
- [ ] **Step 2: Verificación.** Ejecutar `pnpm build`, luego `scripts/start.sh` y abrir `http://localhost:5000`. Dejar la demo corriendo 10 minutos y confirmar que no se congela, que la RAM se mantiene estable y que no hay errores en consola. Detener el servidor y verificar con `ss -ltn` que el puerto 5000 queda libre.
- [ ] **Step 3:** Commit con el mensaje `feat: arranque de feria, check_env y guía de instalación`.
