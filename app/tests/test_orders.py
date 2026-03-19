import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def order_setup(client: TestClient, owner_token: str):
    """
    Prepara el entorno completo para crear una orden:
    - Categoría creada
    - Producto con stock creado
    - Caja abierta
    Devuelve product_id y el token.
    """
    # Crear categoría
    cat_resp = client.post(
        "/categories/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"name": "Cat Orders", "discount": "0"},
    )
    cat_id = cat_resp.json()["id"]

    # Crear producto
    prod_resp = client.post(
        "/products/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"name": "Producto Orden", "price": "10.00", "stock": "50", "category_id": cat_id},
    )
    prod_id = prod_resp.json()["id"]

    # Abrir caja
    client.post(
        "/cash-shifts/open",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"opening_balance": "100.00"},
    )

    return prod_id


def test_create_order_success(client: TestClient, owner_token: str, order_setup: int):
    prod_id = order_setup
    response = client.post(
        "/orders/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "payment_type": "cash",
            "items": [{"product_id": prod_id, "quantity": "2"}],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert len(data["items"]) == 1
    assert data["total"] == "20.00"


def test_create_order_without_open_shift(client: TestClient, owner_token: str):
    # Sin abrir caja primero
    response = client.post(
        "/orders/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "payment_type": "cash",
            "items": [{"product_id": 1, "quantity": "1"}],
        },
    )
    assert response.status_code == 403


def test_create_order_unauthenticated(client: TestClient):
    response = client.post(
        "/orders/",
        json={"payment_type": "cash", "items": [{"product_id": 1, "quantity": "1"}]},
    )
    assert response.status_code == 401


def test_create_order_product_not_found(client: TestClient, owner_token: str):
    # Abrir caja
    client.post(
        "/cash-shifts/open",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"opening_balance": "0"},
    )
    response = client.post(
        "/orders/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"payment_type": "cash", "items": [{"product_id": 99999, "quantity": "1"}]},
    )
    assert response.status_code == 404


def test_create_order_insufficient_stock(client: TestClient, owner_token: str):
    cat_resp = client.post(
        "/categories/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"name": "Cat Stock Test", "discount": "0"},
    )
    cat_id = cat_resp.json()["id"]

    prod_resp = client.post(
        "/products/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"name": "Poca Existencia", "price": "5.00", "stock": "2", "category_id": cat_id},
    )
    prod_id = prod_resp.json()["id"]

    client.post(
        "/cash-shifts/open",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"opening_balance": "0"},
    )
    response = client.post(
        "/orders/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"payment_type": "cash", "items": [{"product_id": prod_id, "quantity": "100"}]},
    )
    assert response.status_code == 400


def test_create_order_empty_items_rejected(client: TestClient, owner_token: str):
    client.post(
        "/cash-shifts/open",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"opening_balance": "0"},
    )
    response = client.post(
        "/orders/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"payment_type": "cash", "items": []},
    )
    assert response.status_code == 422


def test_create_order_reduces_stock(client: TestClient, owner_token: str, order_setup: int):
    prod_id = order_setup

    products_before = client.get("/products/", headers={"Authorization": f"Bearer {owner_token}"}).json()
    stock_before = next(p["stock"] for p in products_before["items"] if p["id"] == prod_id)

    client.post(
        "/orders/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"payment_type": "cash", "items": [{"product_id": prod_id, "quantity": "3"}]},
    )

    products_after = client.get("/products/", headers={"Authorization": f"Bearer {owner_token}"}).json()
    stock_after = next(p["stock"] for p in products_after["items"] if p["id"] == prod_id)

    assert float(stock_after) == float(stock_before) - 3


def test_list_orders(client: TestClient, owner_token: str, order_setup: int):
    prod_id = order_setup
    client.post(
        "/orders/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"payment_type": "cash", "items": [{"product_id": prod_id, "quantity": "1"}]},
    )
    response = client.get("/orders/", headers={"Authorization": f"Bearer {owner_token}"})
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert len(data["items"]) >= 1


def test_get_order_by_id(client: TestClient, owner_token: str, order_setup: int):
    prod_id = order_setup
    create_resp = client.post(
        "/orders/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"payment_type": "debit_card", "items": [{"product_id": prod_id, "quantity": "1"}]},
    )
    order_id = create_resp.json()["id"]

    response = client.get(f"/orders/{order_id}", headers={"Authorization": f"Bearer {owner_token}"})
    assert response.status_code == 200
    assert response.json()["id"] == order_id


def test_get_order_not_found(client: TestClient, owner_token: str):
    response = client.get("/orders/99999", headers={"Authorization": f"Bearer {owner_token}"})
    assert response.status_code == 404


def test_create_order_with_multiple_items(client: TestClient, owner_token: str):
    cat_resp = client.post(
        "/categories/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"name": "Multi Item Cat", "discount": "0"},
    )
    cat_id = cat_resp.json()["id"]

    prod1 = client.post(
        "/products/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"name": "Prod A", "price": "5.00", "stock": "10", "category_id": cat_id},
    ).json()["id"]

    prod2 = client.post(
        "/products/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"name": "Prod B", "price": "3.00", "stock": "10", "category_id": cat_id},
    ).json()["id"]

    client.post(
        "/cash-shifts/open",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"opening_balance": "0"},
    )

    response = client.post(
        "/orders/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "payment_type": "cash",
            "items": [
                {"product_id": prod1, "quantity": "2"},
                {"product_id": prod2, "quantity": "1"},
            ],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert len(data["items"]) == 2
    assert float(data["total"]) == 13.00  # 5*2 + 3*1
