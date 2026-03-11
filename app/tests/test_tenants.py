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
