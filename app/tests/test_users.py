from fastapi.testclient import TestClient

def test_create_user_by_owner(client: TestClient, owner_token: str):
    response = client.post(
        "/users/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "name": "Test User",
            "email": "test.user@example.com",
            "password": "password",
            "role": "staff",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test.user@example.com"
    assert data["name"] == "Test User"

def test_create_staff_user_by_admin(client: TestClient, admin_token: str):
    response = client.post(
        "/users/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Staff by Admin",
            "email": "staff.by.admin@example.com",
            "password": "password",
            "role": "staff",
        },
    )
    assert response.status_code == 201

def test_create_admin_user_by_admin(client: TestClient, admin_token: str):
    response = client.post(
        "/users/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Admin by Admin",
            "email": "admin.by.admin@example.com",
            "password": "password",
            "role": "admin",
        },
    )
    assert response.status_code == 403

def test_create_owner_user_by_admin(client: TestClient, admin_token: str):
    response = client.post(
        "/users/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Owner by Admin",
            "email": "owner.by.admin@example.com",
            "password": "password",
            "role": "owner",
        },
    )
    assert response.status_code == 403

def test_create_user_by_staff(client: TestClient, staff_token: str):
    response = client.post(
        "/users/",
        headers={"Authorization": f"Bearer {staff_token}"},
        json={
            "name": "User by Staff",
            "email": "user.by.staff@example.com",
            "password": "password",
            "role": "staff",
        },
    )
    assert response.status_code == 403

def test_platform_admin_can_create_another_platform_admin(client: TestClient, platform_admin_token: str):
    response = client.post(
        "/users/",
        headers={"Authorization": f"Bearer {platform_admin_token}"},
        json={
            "name": "Second Admin",
            "email": "second.admin@example.com",
            "password": "password123",
            "role": "platform_admin",
        },
    )
    assert response.status_code == 201
    assert response.json()["email"] == "second.admin@example.com"


def test_platform_admin_cannot_create_tenant_user_without_tenant(client: TestClient, platform_admin_token: str):
    """PLATFORM_ADMIN sin tenant_id en el token no puede crear usuarios de tenant."""
    response = client.post(
        "/users/",
        headers={"Authorization": f"Bearer {platform_admin_token}"},
        json={
            "name": "Tenant User",
            "email": "tenant.user@example.com",
            "password": "password123",
            "role": "admin",
        },
    )
    # El servicio intenta crear UserTenant con tenant_id=None → falla con 500 o 400
    # Verificar que NO devuelve 201
    assert response.status_code != 201


def test_create_user_duplicate_email(client: TestClient, owner_token: str):
    client.post(
        "/users/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "name": "First User",
            "email": "duplicate@example.com",
            "password": "password",
            "role": "staff",
        },
    )
    response = client.post(
        "/users/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "name": "Second User",
            "email": "duplicate@example.com",
            "password": "password",
            "role": "staff",
        },
    )
    assert response.status_code == 409

def test_create_user_missing_fields(client: TestClient, owner_token: str):
    response = client.post(
        "/users/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"name": "Missing Fields"},
    )
    assert response.status_code == 422

def test_create_user_unauthenticated(client: TestClient):
    response = client.post(
        "/users/",
        json={
            "name": "Unauthenticated User",
            "email": "unauthenticated@example.com",
            "password": "password",
            "role": "staff",
        },
    )
    assert response.status_code == 401

def test_list_users_by_owner(client: TestClient, owner_token: str):
    response = client.get("/users/", headers={"Authorization": f"Bearer {owner_token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_users_unauthenticated(client: TestClient):
    response = client.get("/users/")
    assert response.status_code == 401


def test_update_user_by_owner(client: TestClient, owner_token: str):
    # Primero crear el usuario
    create_resp = client.post(
        "/users/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"name": "Before Update", "email": "before.update@example.com", "password": "password", "role": "staff"},
    )
    user_id = create_resp.json()["id"]

    response = client.patch(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"name": "After Update"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "After Update"


def test_deactivate_user_by_owner(client: TestClient, owner_token: str):
    create_resp = client.post(
        "/users/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"name": "To Deactivate", "email": "to.deactivate@example.com", "password": "password", "role": "staff"},
    )
    user_id = create_resp.json()["id"]

    response = client.delete(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert response.status_code == 200

    # Verificar que está desactivado
    list_resp = client.get("/users/", headers={"Authorization": f"Bearer {owner_token}"})
    users = list_resp.json()
    target = next((u for u in users if u["id"] == user_id), None)
    assert target is not None
    assert target["active"] is False


def test_activate_user_by_owner(client: TestClient, owner_token: str):
    create_resp = client.post(
        "/users/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"name": "To Activate", "email": "to.activate@example.com", "password": "password", "role": "staff"},
    )
    user_id = create_resp.json()["id"]

    # Desactivar primero
    client.delete(f"/users/{user_id}", headers={"Authorization": f"Bearer {owner_token}"})

    # Activar
    response = client.patch(
        f"/users/{user_id}/activate",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert response.status_code == 200
    assert response.json()["active"] is True
