import pytest
from fastapi.testclient import TestClient


def test_open_shift_success(client: TestClient, owner_token: str):
    response = client.post(
        "/cash-shifts/open",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"opening_balance": "100.00"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "open"
    assert data["opening_balance"] == "100.00"


def test_open_shift_unauthenticated(client: TestClient):
    response = client.post("/cash-shifts/open", json={"opening_balance": "50.00"})
    assert response.status_code == 401


def test_open_shift_negative_balance_rejected(client: TestClient, owner_token: str):
    response = client.post(
        "/cash-shifts/open",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"opening_balance": "-10.00"},
    )
    assert response.status_code == 422


def test_cannot_open_two_shifts(client: TestClient, owner_token: str):
    client.post(
        "/cash-shifts/open",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"opening_balance": "50.00"},
    )
    response = client.post(
        "/cash-shifts/open",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"opening_balance": "50.00"},
    )
    assert response.status_code == 400


def test_get_active_shift(client: TestClient, owner_token: str):
    client.post(
        "/cash-shifts/open",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"opening_balance": "200.00"},
    )
    response = client.get("/cash-shifts/active", headers={"Authorization": f"Bearer {owner_token}"})
    assert response.status_code == 200
    assert response.json()["status"] == "open"


def test_get_active_shift_when_none(client: TestClient, owner_token: str):
    response = client.get("/cash-shifts/active", headers={"Authorization": f"Bearer {owner_token}"})
    assert response.status_code == 404


def test_close_shift_success(client: TestClient, owner_token: str):
    client.post(
        "/cash-shifts/open",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"opening_balance": "150.00"},
    )
    response = client.post(
        "/cash-shifts/close",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"closing_balance": "320.00", "observations": "Todo bien"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "closed"
    assert data["closing_balance"] == "320.00"
    assert data["observations"] == "Todo bien"


def test_close_shift_when_none_open(client: TestClient, owner_token: str):
    response = client.post(
        "/cash-shifts/close",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"closing_balance": "100.00"},
    )
    assert response.status_code == 404


def test_close_shift_by_staff(client: TestClient, staff_token: str):
    client.post(
        "/cash-shifts/open",
        headers={"Authorization": f"Bearer {staff_token}"},
        json={"opening_balance": "75.00"},
    )
    response = client.post(
        "/cash-shifts/close",
        headers={"Authorization": f"Bearer {staff_token}"},
        json={"closing_balance": "75.00"},
    )
    assert response.status_code == 200
