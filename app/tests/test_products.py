import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def category_id(client: TestClient, owner_token: str):
    """Crea una categoría y devuelve su ID."""
    resp = client.post(
        "/categories/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"name": "Cat Productos", "discount": "0"},
    )
    assert resp.status_code == 201
    return resp.json()["id"]


def test_create_product_by_owner(client: TestClient, owner_token: str, category_id: int):
    response = client.post(
        "/products/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "name": "Coca Cola",
            "price": "1.50",
            "stock": "100",
            "category_id": category_id,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Coca Cola"
    assert data["tenant_id"] is not None


def test_create_product_by_admin(client: TestClient, admin_token: str):
    # Crear categoría con el mismo admin_token
    cat_resp = client.post(
        "/categories/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "Cat Admin Prod", "discount": "0"},
    )
    cat_id = cat_resp.json()["id"]

    response = client.post(
        "/products/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "Pepsi", "price": "1.20", "stock": "50", "category_id": cat_id},
    )
    assert response.status_code == 201


def test_create_product_by_staff_forbidden(client: TestClient, staff_token: str):
    response = client.post(
        "/products/",
        headers={"Authorization": f"Bearer {staff_token}"},
        json={"name": "Staff Prod", "price": "1.00", "stock": "10", "category_id": 1},
    )
    assert response.status_code == 403


def test_create_product_unauthenticated(client: TestClient):
    response = client.post(
        "/products/",
        json={"name": "Sin Auth", "price": "1.00", "stock": "10", "category_id": 1},
    )
    assert response.status_code == 401


def test_create_product_invalid_price(client: TestClient, owner_token: str, category_id: int):
    response = client.post(
        "/products/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"name": "Precio Cero", "price": "0", "stock": "10", "category_id": category_id},
    )
    assert response.status_code == 422


def test_create_product_duplicate_barcode(client: TestClient, owner_token: str, category_id: int):
    client.post(
        "/products/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"name": "Prod 1", "price": "1.00", "stock": "10", "category_id": category_id, "barcode": "BAR001"},
    )
    response = client.post(
        "/products/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"name": "Prod 2", "price": "2.00", "stock": "5", "category_id": category_id, "barcode": "BAR001"},
    )
    assert response.status_code == 400


def test_list_products(client: TestClient, owner_token: str, category_id: int):
    client.post(
        "/products/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"name": "Listable", "price": "3.00", "stock": "20", "category_id": category_id},
    )
    response = client.get("/products/", headers={"Authorization": f"Bearer {owner_token}"})
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert len(data["items"]) >= 1


def test_list_products_staff_allowed(client: TestClient, staff_token: str):
    response = client.get("/products/", headers={"Authorization": f"Bearer {staff_token}"})
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data   


def test_update_product(client: TestClient, owner_token: str, category_id: int):
    create_resp = client.post(
        "/products/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"name": "Antes Update", "price": "5.00", "stock": "10", "category_id": category_id},
    )
    prod_id = create_resp.json()["id"]

    response = client.patch(
        f"/products/{prod_id}",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"name": "Despues Update", "discount": "0"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Despues Update"


def test_delete_product(client: TestClient, owner_token: str, category_id: int):
    create_resp = client.post(
        "/products/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"name": "Para Eliminar", "price": "2.00", "stock": "5", "category_id": category_id},
    )
    prod_id = create_resp.json()["id"]

    response = client.delete(f"/products/{prod_id}", headers={"Authorization": f"Bearer {owner_token}"})
    assert response.status_code == 200


def test_search_products(client: TestClient, owner_token: str, category_id: int):
    client.post(
        "/products/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"name": "Agua Mineral", "price": "0.80", "stock": "200", "category_id": category_id},
    )
    response = client.get("/products/search?q=Agua", headers={"Authorization": f"Bearer {owner_token}"})
    assert response.status_code == 200
    names = [p["name"] for p in response.json()]
    assert any("Agua" in n for n in names)


def test_search_products_by_barcode(client: TestClient, owner_token: str, category_id: int):
    client.post(
        "/products/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"name": "Producto Barcode", "price": "1.00", "stock": "10", "category_id": category_id, "barcode": "SEARCHBAR"},
    )
    response = client.get("/products/search?q=SEARCHBAR", headers={"Authorization": f"Bearer {owner_token}"})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["barcode"] == "SEARCHBAR"


def test_get_unit_types(client: TestClient, owner_token: str):
    response = client.get("/products/unit-types", headers={"Authorization": f"Bearer {owner_token}"})
    assert response.status_code == 200
    assert "unit" in response.json()
