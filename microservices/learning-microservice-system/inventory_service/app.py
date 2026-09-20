import os
from typing import Any

import redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Learning Inventory Service", version="1.0.0")
valkey = redis.from_url(os.getenv("VALKEY_URL", "redis://localhost:6379/0"))


class Reservation(BaseModel):
    sku: str = Field(min_length=1)
    quantity: int = Field(gt=0)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/inventory/{sku}")
def get_inventory(sku: str) -> dict[str, Any]:
    key = f"inventory:stock:{sku}"
    if not valkey.exists(key):
        valkey.set(key, 10)
    return {"sku": sku, "available": int(valkey.get(key) or 0)}


@app.post("/reserve")
def reserve(item: Reservation) -> dict[str, Any]:
    key = f"inventory:stock:{item.sku}"
    if not valkey.exists(key):
        valkey.set(key, 10)
    remaining = valkey.decrby(key, item.quantity)
    if remaining < 0:
        valkey.incrby(key, item.quantity)
        raise HTTPException(status_code=409, detail="insufficient stock")
    return {"sku": item.sku, "reserved": item.quantity, "remaining": remaining}
