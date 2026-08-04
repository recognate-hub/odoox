import asyncio
import contextvars
from fastapi import FastAPI, Depends, Request
import uvicorn
import threading
import httpx

cv = contextvars.ContextVar("cv", default=None)
app = FastAPI()

async def auth_dep(request: Request):
    cv.set("TOKEN_123")

@app.get("/test", dependencies=[Depends(auth_dep)])
async def test_route():
    return {"token": cv.get()}

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=9998, log_level="error")

async def run_client():
    async with httpx.AsyncClient() as client:
        r = await client.get("http://127.0.0.1:9998/test")
        print(r.json())

if __name__ == "__main__":
    t = threading.Thread(target=run_server, daemon=True)
    t.start()
    import time
    time.sleep(1)
    asyncio.run(run_client())
