import unittest
from unittest.mock import patch

from app import app


class OrderValidationTests(unittest.TestCase):
    def test_missing_idempotency_key_is_rejected(self) -> None:
        response = app.test_client().post("/orders", json={"sku": "book-1", "quantity": 1})
        self.assertEqual(response.status_code, 400)

    @patch("app.valkey")
    def test_cached_order_is_returned(self, valkey: object) -> None:
        valkey.get.return_value = b'{"order_id":"existing","status":"accepted"}'
        response = app.test_client().post(
            "/orders",
            json={"sku": "book-1", "quantity": 1},
            headers={"Idempotency-Key": "repeat"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["order_id"], "existing")
