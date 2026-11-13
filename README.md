# KipuRest

> **Cada segundo en mesa cuenta.**

KipuRest es el primer **ERP gastronómico con visión artificial e IoT**. Mide en vivo los tiempos de salón y cocina para sacar el máximo provecho de cada mesa.

*Idea de negocio presentada en la Feria de Emprendimiento 2026.*

---

## El problema

Los restaurantes tienen cuellos de botella en el salón y la cocina que nadie ve:

- **Tiempos muertos sin registro:** nadie mide cuánto espera el cliente sentado.
- **Desconexión entre cocina y salón:** los platos listos se enfrían antes de servirse.
- **Baja rotación en hora punta:** las mesas ocupadas sin consumo frenan las ventas.

## Oportunidad

La gastronomía lidera el comercio local, pero se gestiona a ciegas.

- **28%** de pérdida potencial de ingresos diarios por demoras en mesa.
- Los sistemas POS tradicionales registran los cobros, pero ignoran los tiempos reales del salón.

## Propuesta de valor

Un ERP integral conectado con visión artificial en el salón.

| Módulo | Qué hace |
|---|---|
| **Mapa vivo del salón** | Detecta la ocupación y los platos sin marcación manual. |
| **Alertas predictivas con IA** | Avisa de demoras críticas y proyecta los insumos por hora. |
| **Gestión de POS e inventario** | Controla comandas, recetas, stock y caja. |

## Cómo funciona en tiempo real

El registro de tiempos es automático desde que llega el cliente:

1. **Llega el comensal:** la cámara marca la mesa como ocupada y activa el cronómetro.
2. **Toma del pedido:** se registra cuánto tarda el mozo en atender.
3. **Plato en la mesa:** la visión artificial detecta la entrega y cierra el tiempo de cocina.
4. **Mesa libre:** se calcula la rotación y se lanza una alerta para limpiar rápido.

## Público objetivo

Segmentos gastronómicos de alto flujo en **Arequipa**:

- **Picanterías y restaurantes turísticos:** locales de 15 a 60 mesas con alta rotación al mediodía y necesidad de rapidez.
- **Restaurantes casuales y franquicias:** negocios con varios salones que buscan estandarizar sus tiempos de servicio.

## Modelo de negocio

Ingresos recurrentes B2B, compatibles con las cámaras que el local ya tiene.

- **Suscripción mensual por salón (SaaS):** planes desde **S/ 149 al mes**, según el número de mesas monitoreadas y los módulos del ERP activos.
- **Implementación (setup):** pago único por calibrar las cámaras actuales o venta de un nodo inteligente *plug-and-play* (kit Edge IoT).

## Producto mínimo viable (PMV)

Un prototipo visual del monitor en vivo de salón y cocina:

- **Visión YOLO en vivo:** detecta comensales y platos en la mesa.
- **Semáforo de tiempos:** alerta cuando una demora pasa de 10 minutos.
- **Privacidad garantizada:** procesa solo metadatos, sin grabar rostros.
- **Sincronización con el POS:** vincula cada mesa con su comanda.

Ejemplo de vista en el **KipuRest Live Vision, salón principal** (ocupación: 83%, tiempo promedio de atención: 03:40):

| Mesa | Estado | Tiempo | Detalle |
|---|---|---|---|
| 01 | Alerta | 14:20 | Esperando el plato fuerte |
| 02 | Óptimo | 04:15 | Platos servidos · S/ 118 |
| 03 | Atención | 02:10 | Comensales recién sentados |
| 04 | Óptimo | 18:05 | Consumiendo · S/ 84 |
| 05 | Libre | 00:00 | Lista para nuevos clientes |

> **Sugerencia de la IA:** priorizar el pase de la mesa 01 en cocina.

## Estrategia de validación

1. **Fase 1, 30 entrevistas a dueños:** diagnóstico de mermas y de la disposición a pagar en Arequipa.
2. **Fase 2, piloto en 3 restaurantes:** prueba gratuita de 30 días con sus propias cámaras.
3. **Fase 3, meta de impacto:** reducir la espera en **20%**, de forma medible en el tiempo de entrega y con mayor rotación de mesas.

## Equipo

Ingeniería, visión artificial y pasión por la gastronomía:

- Inteligencia artificial e IoT
- Desarrollo full-stack
- Gestión gastronómica
- UX/UI

## Cómo correr la demo (MVP Live Vision)

El MVP es un monitor en vivo del salón: YOLO detecta personas en un video del salón y el panel muestra qué mesas están ocupadas, cuánto tiempo llevan, las alertas de demora y una sugerencia de IA.

- **Backend:** Python, FastAPI, Ultralytics YOLO y OpenCV (`backend/`).
- **Frontend:** React, Vite, TanStack Router y Tailwind (`frontend/`).

Inicio rápido:

```bash
cd backend && uv sync && uv run python ../scripts/check_env.py --prepare
cd ../frontend && pnpm install && pnpm build
cd .. && ./scripts/start.sh      # en Windows: scripts\start.bat
```

Abre http://localhost:5000. Para desarrollar el frontend: `pnpm dev` en `frontend/` (puerto 3001), con el backend corriendo en el 5000.

La guía completa para la laptop de la feria está en [docs/instalacion-laptop-feria.md](docs/instalacion-laptop-feria.md).
