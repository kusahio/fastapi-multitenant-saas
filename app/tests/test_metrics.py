from fastapi.testclient import TestClient


def test_get_metrics_summary_owner(client: TestClient, owner_token: str):
    response = client.get("/metrics/summary", headers={"Authorization": f"Bearer {owner_token}"})
    assert response.status_code == 200
    data = response.json()
    assert "total_products" in data
    assert "total_categories" in data
    assert "total_orders" in data
    assert "products_by_category" in data
    assert "orders_by_employee" in data
    assert "sales_by_payment_type" in data


def test_get_metrics_summary_admin(client: TestClient, admin_token: str):
    response = client.get("/metrics/summary", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200


def test_get_metrics_summary_staff(client: TestClient, staff_token: str):
    response = client.get("/metrics/summary", headers={"Authorization": f"Bearer {staff_token}"})
    assert response.status_code == 200


def test_get_metrics_summary_unauthenticated(client: TestClient):
    response = client.get("/metrics/summary")
    assert response.status_code == 401


def test_get_platform_summary_platform_admin(client: TestClient, platform_admin_token: str):
    response = client.get("/metrics/platform-summary", headers={"Authorization": f"Bearer {platform_admin_token}"})
    assert response.status_code == 200
    data = response.json()
    assert "total_tenants" in data
    assert "active_tenants" in data
    assert "global_gmv" in data
    assert "top_tenants" in data
    assert "tenants_by_type" in data
    assert "total_users" in data


def test_get_platform_summary_forbidden_for_owner(client: TestClient, owner_token: str):
    response = client.get("/metrics/platform-summary", headers={"Authorization": f"Bearer {owner_token}"})
    assert response.status_code == 403


def test_get_platform_summary_forbidden_for_staff(client: TestClient, staff_token: str):
    response = client.get("/metrics/platform-summary", headers={"Authorization": f"Bearer {staff_token}"})
    assert response.status_code == 403


def test_metrics_summary_reflects_created_data(client: TestClient, owner_token: str):
    """Verificar que las métricas cuentan correctamente los datos creados."""
    # Crear categoría y producto
    cat_resp = client.post(
        "/categories/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"name": "Metrics Cat", "discount": "0"},
    )
    cat_id = cat_resp.json()["id"]

    client.post(
        "/products/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"name": "Metrics Prod", "price": "1.00", "stock": "10", "category_id": cat_id},
    )

    response = client.get("/metrics/summary", headers={"Authorization": f"Bearer {owner_token}"})
    data = response.json()
    assert data["total_products"] >= 1
    assert data["total_categories"] >= 1
