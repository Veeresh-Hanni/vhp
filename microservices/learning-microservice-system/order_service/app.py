import json
import os
import uuid
from typing import Any

import httpx
import redis
from flask import Flask, jsonify, request
from kafka import KafkaProducer

app = Flask(__name__)
valkey = redis.from_url(os.getenv("VALKEY_URL", "redis://localhost:6379/1"))
producer: KafkaProducer | None = None


def get_producer() -> KafkaProducer:
    global producer
    if producer is None:
        producer = KafkaProducer(
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
            value_serializer=lambda value: json.dumps(value).encode("utf-8"),
        )
    return producer


@app.get("/health")
def health() -> tuple[Any, int]:
    return jsonify(status="ok"), 200


@app.get("/inventory/<sku>")
def inventory(sku: str) -> tuple[Any, int]:
    response = httpx.get(
        f"{os.getenv('INVENTORY_URL', 'http://localhost:8001')}/inventory/{sku}",
        timeout=3,
    )
    return jsonify(response.json()), response.status_code


@app.post("/orders")
def create_order() -> tuple[Any, int]:
    key = request.headers.get("Idempotency-Key")
    body = request.get_json(silent=True) or {}
    sku = body.get("sku")
    quantity = body.get("quantity")
    if not key or not isinstance(sku, str) or not isinstance(quantity, int) or quantity < 1:
        return jsonify(error="sku, positive integer quantity, and Idempotency-Key are required"), 400

    cached = valkey.get(f"order:idempotency:{key}")
    if cached:
        return jsonify(json.loads(cached)), 200

    response = httpx.post(
        f"{os.getenv('INVENTORY_URL', 'http://localhost:8001')}/reserve",
        json={"sku": sku, "quantity": quantity},
        timeout=3,
    )
    if response.status_code != 200:
        return jsonify(response.json()), response.status_code

    order = {"order_id": str(uuid.uuid4()), "status": "accepted", "sku": sku, "quantity": quantity}
    valkey.setex(f"order:idempotency:{key}", 86400, json.dumps(order))
    get_producer().send("order.created", order)
    get_producer().flush(timeout=3)
    return jsonify(order), 201
