from __future__ import annotations

import asyncio
import os
import subprocess

import httpx
import uvicorn
import websockets
from fastapi import Request, Response, WebSocket

from server.app import app


async def _proxy_http(request: Request, path: str) -> Response:
    upstream = f"http://127.0.0.1:8501/{path}"
    if request.url.query:
        upstream = f"{upstream}?{request.url.query}"
    body = await request.body()
    headers = dict(request.headers)
    headers.pop("host", None)
    
    async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
        try:
            r = await client.request(request.method, upstream, content=body, headers=headers)
            resp_headers = dict(r.headers)
            resp_headers.pop("content-encoding", None)
            resp_headers.pop("transfer-encoding", None)
            return Response(content=r.content, status_code=r.status_code, headers=resp_headers)
        except Exception as e:
            return Response(
                content=f"<h1>UI Loading...</h1><p>Streamlit is starting up. Please refresh in a few seconds.</p><p>Error: {str(e)}</p>",
                status_code=200,
                media_type="text/html"
            )


@app.api_route("/ui", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def ui_root(request: Request):
    return await _proxy_http(request, "")


@app.api_route("/ui/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def ui_proxy(path: str, request: Request):
    return await _proxy_http(request, path)


# Also proxy /static/* directly to Streamlit
@app.api_route("/static/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def static_proxy(path: str, request: Request):
    return await _proxy_http(request, f"static/{path}")


@app.websocket("/ui/_stcore/stream")
async def ui_ws(websocket: WebSocket):
    await websocket.accept()
    upstream = "ws://127.0.0.1:8501/_stcore/stream"
    async with websockets.connect(upstream) as upstream_ws:
        async def to_upstream():
            while True:
                msg = await websocket.receive()
                if msg.get("type") == "websocket.disconnect":
                    break
                if "bytes" in msg and msg["bytes"] is not None:
                    await upstream_ws.send(msg["bytes"])
                elif "text" in msg and msg["text"] is not None:
                    await upstream_ws.send(msg["text"])

        async def to_client():
            async for msg in upstream_ws:
                if isinstance(msg, bytes):
                    await websocket.send_bytes(msg)
                else:
                    await websocket.send_text(msg)

        await asyncio.gather(to_upstream(), to_client())


def main() -> None:
    os.environ.setdefault("STREAMLIT_SERVER_HEADLESS", "true")
    os.environ.setdefault("STREAMLIT_SERVER_ENABLE_CORS", "false")
    os.environ.setdefault("STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION", "false")
    os.environ.setdefault("STREAMLIT_SERVER_RUN_ON_SAVE", "false")
    os.environ.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")

    streamlit_cmd = [
        "python",
        "-m",
        "streamlit",
        "run",
        "ui/app.py",
        "--server.port",
        "8501",
        "--server.address",
        "127.0.0.1",
        "--server.headless",
        "true",
        "--server.enableCORS",
        "false",
        "--server.enableXsrfProtection",
        "false",
        "--browser.gatherUsageStats",
        "false",
    ]
    
    print("[STARTUP] Starting Streamlit UI server on port 8501...")
    subprocess.Popen(streamlit_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Give Streamlit time to start
    import time
    time.sleep(2)
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "7860"))
    print(f"[STARTUP] Starting FastAPI server on {host}:{port}...")
    print(f"[STARTUP] UI will be available at http://{host}:{port}/ui")
    print(f"[STARTUP] Health check at http://{host}:{port}/health")
    
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()

