from __future__ import annotations

import os

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse

from env.environment import Action, Observation, WorkplaceEnv

app = FastAPI(title="workplace-simulator", version="1.0")

_ENV: WorkplaceEnv | None = None


def _get_env() -> WorkplaceEnv:
    global _ENV
    if _ENV is None:
        _ENV = WorkplaceEnv()
    return _ENV


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/")
async def root():
    """Root endpoint - redirects to UI."""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Workplace Failure Simulator</title>
        <meta http-equiv="refresh" content="0;url=/ui">
        <script>
            window.location.href = '/ui';
        </script>
    </head>
    <body>
        <p>Loading UI... <a href="/ui">Click here if not redirected</a></p>
    </body>
    </html>
    """)


@app.post("/reset")
def reset() -> Observation:
    env = _get_env()
    return env.reset()


@app.get("/state")
def state() -> dict:
    env = _get_env()
    return env.state()


@app.post("/step")
def step(action: Action):
    env = _get_env()
    obs, reward, done, info = env.step(action)
    return {"observation": obs, "reward": float(reward), "done": bool(done), "info": info}


def main() -> None:
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "7860"))
    uvicorn.run("server.app:app", host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()

