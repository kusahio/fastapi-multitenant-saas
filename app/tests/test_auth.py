from fastapi.testclient import TestClient
from app.modules.users.models import User
from app.modules.tenants.models import Tenant
from app.modules.user_tenants.models import UserTenant
from app.domain.enums.users_role import UserRole
from app.domain.enums.business_type import BusinessType
from app.core.security import hashed_password


def _create_user_with_tenant(db_session):
    """Helper: crea un user+tenant y devuelve (email, password, tenant_id)."""
    tenant = Tenant(name="Auth Tenant", slug="auth-tenant", business_type=BusinessType.STORE)
    db_session.add(tenant)
    db_session.commit()

    user = User(
        name="Auth User",
        email="auth.user@test.com",
        hashed_password=hashed_password("correctpass"),
    )
    db_session.add(user)
    db_session.commit()

    user_tenant = UserTenant(user_id=user.id, tenant_id=tenant.id, role=UserRole.OWNER)
    db_session.add(user_tenant)
    db_session.commit()

    return "auth.user@test.com", "correctpass", tenant.id


def test_login_success_regular_user(client: TestClient, db_session):
    email, password, _ = _create_user_with_tenant(db_session)
    response = client.post("/auth/login", data={"username": email, "password": password})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user_id"] is not None
    assert isinstance(data["tenants"], list)
    assert len(data["tenants"]) == 1


def test_login_wrong_password(client: TestClient, db_session):
    _create_user_with_tenant(db_session)
    response = client.post("/auth/login", data={"username": "auth.user@test.com", "password": "wrongpass"})
    assert response.status_code == 401


def test_login_nonexistent_user(client: TestClient):
    response = client.post("/auth/login", data={"username": "noexiste@test.com", "password": "any"})
    assert response.status_code == 401


def test_login_platform_admin_returns_empty_tenants(client: TestClient, db_session):
    admin = User(
        name="Platform Admin",
        email="platform.login@test.com",
        hashed_password=hashed_password("adminpass"),
        is_platform_admin=True,
    )
    db_session.add(admin)
    db_session.commit()

    response = client.post("/auth/login", data={"username": "platform.login@test.com", "password": "adminpass"})
    assert response.status_code == 200
    data = response.json()
    assert data["tenants"] == []
    assert "access_token" in data


def test_login_inactive_user_rejected(client: TestClient, db_session):
    user = User(
        name="Inactive",
        email="inactive@test.com",
        hashed_password=hashed_password("pass123"),
        active=False,
    )
    db_session.add(user)
    db_session.commit()

    response = client.post("/auth/login", data={"username": "inactive@test.com", "password": "pass123"})
    assert response.status_code == 401


def test_select_tenant_success(client: TestClient, db_session):
    email, password, tenant_id = _create_user_with_tenant(db_session)

    login_resp = client.post("/auth/login", data={"username": email, "password": password})
    token = login_resp.json()["access_token"]

    response = client.post(
        "/auth/select-tenant",
        headers={"Authorization": f"Bearer {token}"},
        json={"tenant_id": tenant_id},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_select_tenant_invalid(client: TestClient, db_session):
    email, password, _ = _create_user_with_tenant(db_session)
    login_resp = client.post("/auth/login", data={"username": email, "password": password})
    token = login_resp.json()["access_token"]

    response = client.post(
        "/auth/select-tenant",
        headers={"Authorization": f"Bearer {token}"},
        json={"tenant_id": 99999},
    )
    assert response.status_code == 401


def test_get_me_authenticated(client: TestClient, owner_token: str):
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {owner_token}"})
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert "role" in data


def test_get_me_unauthenticated(client: TestClient):
    response = client.get("/auth/me")
    assert response.status_code == 401
