import io

import qrcode
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from server.config import settings
from server.net import get_lan_ip

router = APIRouter(prefix="/network", tags=["network"])

_tunnel_url: str | None = None


@router.get("/qr")
def judge_qr_code():
    ip = get_lan_ip()
    url = f"http://{ip}:{settings.port}/judge"
    img = qrcode.make(url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


@router.get("/info")
def network_info():
    ip = get_lan_ip()
    return {
        "lan_ip": ip,
        "port": settings.port,
        "judge_url": f"http://{ip}:{settings.port}/judge",
        "tunnel_url": _tunnel_url,
    }


@router.post("/tunnel/start")
def start_tunnel():
    global _tunnel_url
    if _tunnel_url:
        return {"tunnel_url": _tunnel_url}
    if not settings.ngrok_auth_token:
        return {"error": "MCTS_NGROK_AUTH_TOKEN not configured"}
    try:
        from pyngrok import conf, ngrok
        conf.get_default().auth_token = settings.ngrok_auth_token
        tunnel = ngrok.connect(settings.port, "http")
        _tunnel_url = tunnel.public_url
        return {"tunnel_url": _tunnel_url}
    except Exception as e:
        return {"error": str(e)}


@router.post("/tunnel/stop")
def stop_tunnel():
    global _tunnel_url
    try:
        from pyngrok import ngrok
        ngrok.kill()
    except Exception:  # noqa: S110
        pass
    _tunnel_url = None
    return {"status": "stopped"}
