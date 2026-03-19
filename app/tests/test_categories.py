from fastapi.testclient import TestClient

def test_create_category_by_owner(client: TestClient, owner_token: str):
    response = client.post(
        "/categories/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"name": "Bebidas", "discount": "0", "active": True},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Bebidas"
    assert "id" in data
    assert "tenant_id" in data

def test_create_category_by_admin(client: TestClient, admin_token: str):
    response = client.post(
        "/categories/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "Comidas", "discount": "0"},
    )
    assert response.status_code == 201

def test_create_category_by_staff_forbidden(client: TestClient, staff_token: str):
    response = client.post(
        "/categories/",
        headers={"Authorization": f"Bearer {staff_token}"},
        json={"name": "Categoría Staff", "discount": "0"},
    )
    assert response.status_code == 403

def test_create_category_unauthenticated(client: TestClient):
    response = client.post("/categories/", json={"name": "Sin auth", "discount": "0"})
    assert response.status_code == 401

def test_create_category_name_too_short(client: TestClient, owner_token: str):
    response = client.post(
        "/categories/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"name": "X", "discount": "0"},
    )
    assert response.status_code == 422

def test_list_categories(client: TestClient, owner_token: str):
    client.post("/categories/", headers={"Authorization": f"Bearer {owner_token}"},
                json={"name": "Lista Cat", "discount": "0"})
    response = client.get("/categories/", headers={"Authorization": f"Bearer {owner_token}"})
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert len(data["items"]) >= 1

def test_list_categories_staff_allowed(client: TestClient, staff_token: str):
    response = client.get("/categories/", headers={"Authorization": f"Bearer {staff_token}"})
    assert response.status_code == 200

def test_update_category(client: TestClient, owner_token: str):
    create_resp = client.post(
        "/categories/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"name": "Para Actualizar", "discount": "0"},
    )
    cat_id = create_resp.json()["id"]

    response = client.patch(
        f"/categories/{cat_id}",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"name": "Actualizada"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Actualizada"

def test_update_category_not_found(client: TestClient, owner_token: str):
    response = client.patch(
        "/categories/99999",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"name": "No existe"},
    )
    assert response.status_code == 404

def test_delete_category(client: TestClient, owner_token: str):
    create_resp = client.post(
        "/categories/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"name": "Para Borrar", "discount": "0"},
    )
    cat_id = create_resp.json()["id"]

    response = client.delete(f"/categories/{cat_id}", headers={"Authorization": f"Bearer {owner_token}"})
    assert response.status_code == 200

    list_resp = client.get("/categories/", headers={"Authorization": f"Bearer {owner_token}"})
    ids = [c["id"] for c in list_resp.json()["items"]]  # ← "items"
    assert cat_id not in ids

def test_delete_category_not_found(client: TestClient, owner_token: str):
    response = client.delete("/categories/99999", headers={"Authorization": f"Bearer {owner_token}"})
    assert response.status_code == 404

def test_categories_are_tenant_isolated(client: TestClient, owner_token: str, admin_token: str):
    client.post(
        "/categories/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"name": "Solo en Owner Tenant", "discount": "0"},
    )
    response = client.get("/categories/", headers={"Authorization": f"Bearer {admin_token}"})
    names = [c["name"] for c in response.json()["items"]]  # ← "items"
    assert "Solo en Owner Tenant" not in names