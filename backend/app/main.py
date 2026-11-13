import asyncio
import atexit
import logging
from contextlib import asynccontextmanager
from typing import Callable

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, Response, StreamingResponse

from app.config import BACKEND_DIR, Settings
from app.models import Zone
from app.pipeline import DetectorLike, VideoPipeline
from app.zones import save_zones

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
DIST = BACKEND_DIR.parent / "frontend" / "dist"
WS_PERIOD_S = 0.2
MJPEG_PERIOD_S = 1 / 25


def _yolo_factory(s: Settings) -> DetectorLike:
    from app.detector import Detector

    return Detector(s.model_name, s.conf, s.imgsz)


def create_app(
    settings: Settings | None = None,
    detector_factory: Callable[[Settings], DetectorLike] = _yolo_factory,
) -> FastAPI:
    settings = settings or Settings()
    pipeline = VideoPipeline(settings, detector_factory)
    # Si el apagado del lifespan se cancela (clientes MJPEG abiertos), detener los hilos igual
    # antes de que el intérprete finalice, para evitar abortos de OpenCV/torch.
    atexit.register(pipeline.stop)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        pipeline.start()
        yield
        pipeline.stop()

    app = FastAPI(title="KipuRest Live Vision", lifespan=lifespan)

    @app.get("/api/health")
    def health():
        return {
            "video_ok": pipeline.video_ok,
            "device": pipeline.device,
            "fps": round(pipeline.state().fps, 1),
            "zones": len(pipeline.zones),
        }

    @app.get("/api/zones", response_model=list[Zone])
    def get_zones():
        return pipeline.zones

    @app.put("/api/zones", response_model=list[Zone])
    def put_zones(zones: list[Zone]):
        save_zones(settings.zones_path, zones)
        pipeline.set_zones(zones)
        return zones

    @app.get("/api/frame.jpg")
    def frame():
        jpg = pipeline.clean_jpeg()
        if jpg is None:
            raise HTTPException(503, "video no disponible")
        return Response(jpg, media_type="image/jpeg", headers={"Cache-Control": "no-store"})

    @app.get("/video")
    async def video():
        async def gen():
            while not pipeline.stopped:
                jpg = pipeline.latest_jpeg()
                if jpg:
                    yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpg + b"\r\n"
                await asyncio.sleep(MJPEG_PERIOD_S)

        return StreamingResponse(gen(), media_type="multipart/x-mixed-replace; boundary=frame")

    @app.websocket("/ws/state")
    async def ws_state(ws: WebSocket):
        await ws.accept()
        try:
            while True:
                await ws.send_json(pipeline.state().model_dump())
                await asyncio.sleep(WS_PERIOD_S)
        except (WebSocketDisconnect, RuntimeError, asyncio.CancelledError):
            pass

    if DIST.exists():

        @app.get("/{path:path}")
        def spa(path: str):
            f = (DIST / path).resolve()
            if path and f.is_file() and DIST.resolve() in f.parents:
                return FileResponse(f)
            return FileResponse(DIST / "index.html")

    return app


app = create_app()
