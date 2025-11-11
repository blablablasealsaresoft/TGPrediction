"""HTTP probes for liveness/readiness (and optional Prometheus metrics)."""

from typing import Awaitable, Callable, Dict, Optional, Tuple

from aiohttp import web

try:
    from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
except Exception:  # pragma: no cover - optional dependency
    CONTENT_TYPE_LATEST = "text/plain; version=0.0.4"

    def generate_latest():  # type: ignore
        return b""


HealthCallable = Callable[[], Awaitable[Tuple[bool, Dict[str, Tuple[bool, str]]]]]


class ProbeServer:
    """Embeds aiohttp to serve /live, /ready, and optional /metrics endpoints."""

    def __init__(
        self,
        health_check: HealthCallable,
        host: str = "0.0.0.0",
        port: int = 8080,
        prometheus_enabled: bool = False,
    ):
        self._health_check = health_check
        self._host = host
        self._port = port
        self._prometheus_enabled = prometheus_enabled
        self._runner: Optional[web.AppRunner] = None
        self._site: Optional[web.TCPSite] = None

    async def start(self) -> None:
        app = web.Application()
        app.router.add_get("/live", self._live_handler)
        app.router.add_get("/ready", self._ready_handler)
        if self._prometheus_enabled:
            app.router.add_get("/metrics", self._metrics_handler)

        self._runner = web.AppRunner(app)
        await self._runner.setup()
        self._site = web.TCPSite(self._runner, self._host, self._port)
        await self._site.start()

    async def stop(self) -> None:
        if self._site:
            await self._site.stop()
            self._site = None
        if self._runner:
            await self._runner.cleanup()
            self._runner = None

    async def _live_handler(self, request: web.Request) -> web.Response:
        return web.json_response({"status": "alive"})

    async def _ready_handler(self, request: web.Request) -> web.Response:
        health_ok, details = await self._health_check()
        status = 200 if health_ok else 503
        payload = {
            "status": "ready" if health_ok else "starting",
            "checks": {name: {"ok": ok, "detail": msg} for name, (ok, msg) in details.items()},
        }
        return web.json_response(payload, status=status)

    async def _metrics_handler(self, request: web.Request) -> web.Response:
        payload = generate_latest()
        return web.Response(body=payload, content_type=CONTENT_TYPE_LATEST)


async def start_probe_server(health_check: HealthCallable, prometheus_enabled: bool) -> ProbeServer:
    server = ProbeServer(health_check, prometheus_enabled=prometheus_enabled)
    await server.start()
    return server
