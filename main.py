import os
import asyncio
from fastapi import FastAPI, Header, HTTPException
from kasa import SmartStrip

app = FastAPI()

API_KEY = os.getenv("API_KEY")

# Cache: one SmartStrip per IP address
strip_cache = {}


async def get_strip(ip: str):
    """
    Cache SmartStrip instances PER IP so calls do not overload the device,
    but different strips can still be used.
    """
    if ip not in strip_cache:
        strip_cache[ip] = SmartStrip(ip)
        await strip_cache[ip].update()
    return strip_cache[ip]


async def safe(fn, retries=3, delay=0.25):
    """
    Retry wrapper: handles Kasa intermittent failures (0-byte response, timeouts).
    """
    for attempt in range(retries):
        try:
            return await fn()
        except Exception:
            if attempt == retries - 1:
                raise
            await asyncio.sleep(delay)


async def turn_on(ip: str, plug_number: int):
    async def action():
        strip = await get_strip(ip)
        await strip.update()

        if plug_number < 1 or plug_number > len(strip.children):
            raise HTTPException(status_code=400, detail="Invalid plug number")

        plug = strip.children[plug_number - 1]
        await plug.turn_on()

        return {
            "ip": ip,
            "alias": plug.alias,
            "plug_number": plug_number,
            "state": "on"
        }

    return await safe(action)


async def turn_off(ip: str, plug_number: int):
    async def action():
        strip = await get_strip(ip)
        await strip.update()

        if plug_number < 1 or plug_number > len(strip.children):
            raise HTTPException(status_code=400, detail="Invalid plug number")

        plug = strip.children[plug_number - 1]
        await plug.turn_off()

        return {
            "ip": ip,
            "alias": plug.alias,
            "plug_number": plug_number,
            "state": "off"
        }

    return await safe(action)


@app.post("/power/on/{ip}/{plug_number}")
async def power_on(ip: str, plug_number: int, x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        result = await turn_on(ip, plug_number)
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/power/off/{ip}/{plug_number}")
async def power_off(ip: str, plug_number: int, x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        result = await turn_off(ip, plug_number)
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok"}
