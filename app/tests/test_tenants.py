from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.modules.users.models import User
from app.modules.tenants.models import Tenant

def test_create_tenant_success(client: TestClient, platform_admin_token: str):
    response = client.post(
        "/tenants/",
        headers={"Authorization": f"Bearer {platform_admin_token}"},
        json={
            "name": "New Tenant",
            "slug": "new-tenant",
            "business_type": "store",
            "owner_name": "Tenant Owner",
            "owner_email": "new.owner@test.com",
            "owner_password": "password",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Tenant"
    assert data["slug"] == "new-tenant"

def test_create_tenant_owner_auto_created(client: TestClient, platform_admin_token: str, db_session: Session):
    client.post(
        "/tenants/",
        headers={"Authorization": f"Bearer {platform_admin_token}"},
        json={
            "name": "Another Tenant",
            "slug": "another-tenant",
            "business_type": "food",
            "owner_name": "Another Owner",
            "owner_email": "another.owner@test.com",
            "owner_password": "password",
        },
    )
    user = db_session.query(User).filter(User.email == "another.owner@test.com").first()
    assert user is not None
    assert user.name == "Another Owner"

def test_create_tenant_by_non_platform_admin(client: TestClient, owner_token: str):
    response = client.post(
        "/tenants/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"name": "Tenant by owner", "slug": "tenant-by-owner", "business_type": "store", "owner_name": "owner", "owner_email": "owner@owner.com", "owner_password": "password"},
    )
    assert response.status_code == 403

def test_create_tenant_unauthenticated(client: TestClient):
    response = client.post(
        "/tenants/",
        json={"name": "Unauthenticated Tenant", "slug": "unauthenticated-tenant", "business_type": "store", "owner_name": "owner", "owner_email": "owner@owner.com", "owner_password": "password"},
    )
    assert response.status_code == 401

def test_create_tenant_duplicate_slug(client: TestClient, platform_admin_token: str):
    client.post(
        "/tenants/",
        headers={"Authorization": f"Bearer {platform_admin_token}"},
        json={
            "name": "Duplicate Slug Tenant",
            "slug": "duplicate-slug",
            "business_type": "store",
            "owner_name": "owner",
            "owner_email": "owner1@test.com",
            "owner_password": "password",
        },
    )
    response = client.post(
        "/tenants/",
        headers={"Authorization": f"Bearer {platform_admin_token}"},
        json={
            "name": "Another Duplicate",
            "slug": "duplicate-slug",
            "business_type": "food",
            "owner_name": "owner2",
            "owner_email": "owner2@test.com",
            "owner_password": "password",
        },
    )
    assert response.status_code == 409

def test_create_tenant_missing_fields(client: TestClient, platform_admin_token: str):
    response = client.post(
        "/tenants/",
        headers={"Authorization": f"Bearer {platform_admin_token}"},
        json={"name": "Missing Fields"},
    )
    assert response.status_code == 422

def test_list_tenants_by_platform_admin(client: TestClient, platform_admin_token: str):
    response = client.get("/tenants/", headers={"Authorization": f"Bearer {platform_admin_token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_tenants_by_non_admin(client: TestClient, owner_token: str):
    response = client.get("/tenants/", headers={"Authorization": f"Bearer {owner_token}"})
    assert response.status_code == 403


def test_get_tenant_by_id(client: TestClient, platform_admin_token: str):
    # Crear un tenant
    create_resp = client.post(
        "/tenants/",
        headers={"Authorization": f"Bearer {platform_admin_token}"},
        json={
            "name": "Tenant For Get",
            "slug": "tenant-for-get",
            "business_type": "store",
            "owner_name": "owner",
            "owner_email": "owner.get@test.com",
            "owner_password": "password",
        },
    )
    tenant_id = create_resp.json()["id"]

    response = client.get(f"/tenants/{tenant_id}", headers={"Authorization": f"Bearer {platform_admin_token}"})
    assert response.status_code == 200
    assert response.json()["id"] == tenant_id


def test_get_tenant_by_slug(client: TestClient, platform_admin_token: str):
    client.post(
        "/tenants/",
        headers={"Authorization": f"Bearer {platform_admin_token}"},
        json={
            "name": "Slug Tenant",
            "slug": "slug-tenant",
            "business_type": "food",
            "owner_name": "owner",
            "owner_email": "owner.slug@test.com",
            "owner_password": "password",
        },
    )
    response = client.get("/tenants/slug/slug-tenant", headers={"Authorization": f"Bearer {platform_admin_token}"})
    assert response.status_code == 200
    assert response.json()["slug"] == "slug-tenant"


def test_update_tenant(client: TestClient, platform_admin_token: str):
    create_resp = client.post(
        "/tenants/",
        headers={"Authorization": f"Bearer {platform_admin_token}"},
        json={
            "name": "Update Me",
            "slug": "update-me",
            "business_type": "store",
            "owner_name": "owner",
            "owner_email": "owner.update@test.com",
            "owner_password": "password",
        },
    )
    tenant_id = create_resp.json()["id"]

    response = client.put(
        f"/tenants/{tenant_id}",
        headers={"Authorization": f"Bearer {platform_admin_token}"},
        json={"name": "Updated Name", "slug": "update-me", "business_type": "food"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"


def test_deactivate_and_activate_tenant(client: TestClient, platform_admin_token: str):
    create_resp = client.post(
        "/tenants/",
        headers={"Authorization": f"Bearer {platform_admin_token}"},
        json={
            "name": "Toggle Tenant",
            "slug": "toggle-tenant",
            "business_type": "store",
            "owner_name": "owner",
            "owner_email": "owner.toggle@test.com",
            "owner_password": "password",
        },
    )
    tenant_id = create_resp.json()["id"]

    deact = client.patch(f"/tenants/{tenant_id}/deactivate", headers={"Authorization": f"Bearer {platform_admin_token}"})
    assert deact.status_code == 200
    assert deact.json()["active"] is False

    act = client.patch(f"/tenants/{tenant_id}/activate", headers={"Authorization": f"Bearer {platform_admin_token}"})
    assert act.status_code == 200
    assert act.json()["active"] is True
