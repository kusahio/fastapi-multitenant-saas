import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
from app.main import create_app
from app.modules.auth.utils import create_access_token
from app.domain.enums.users_role import UserRole
from app.domain.enums.business_type import BusinessType
from app.modules.users.models import User
from app.modules.tenants.models import Tenant
from app.modules.user_tenants.models import UserTenant
from app.core.security import hashed_password

from app.modules.categories.models import Category
from app.modules.products.models import Product
from app.modules.orders.models import Order, OrderItem
from app.modules.cash_shifts.models import CashShift

from app.core.limiter import limiter
from slowapi.middleware import SlowAPIMiddleware

# In-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)

# Create the database tables
Base.metadata.create_all(bind=engine)

# Dependency override for database session


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Inicialización de la app (Una sola vez)
app = create_app()
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db_session():
    """
    Fixture for providing a clean database session for tests.
    """
    connection = engine.connect()
    session = TestingSessionLocal(bind=connection)

    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()

    yield session

    session.close()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """
    Fixture for providing a FastAPI TestClient.
    """
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    limiter.enabled = False
    yield TestClient(app)
    limiter.enabled = True
    del app.dependency_overrides[get_db]


@pytest.fixture(scope="function")
def platform_admin_token(db_session):
    user = User(
        name="Platform Admin",
        email="platform.admin@test.com",
        hashed_password=hashed_password("testpass123"),
        is_platform_admin=True,
    )
    db_session.add(user)
    db_session.commit()

    return create_access_token(
        {"sub": str(user.id), "role": UserRole.PLATFORM_ADMIN.value}
    )


@pytest.fixture(scope="function")
def owner_token(db_session):
    tenant = Tenant(name="Test Tenant", slug="test-tenant",
                    business_type=BusinessType.STORE)
    db_session.add(tenant)
    db_session.commit()

    user = User(
        name="Owner User",
        email="owner@test.com",
        hashed_password=hashed_password("testpass123"),
    )
    db_session.add(user)
    db_session.commit()

    user_tenant = UserTenant(
        user_id=user.id, tenant_id=tenant.id, role=UserRole.OWNER
    )
    db_session.add(user_tenant)
    db_session.commit()

    return create_access_token(
        {"sub": str(user.id), "tenant_id": tenant.id,
        "role": UserRole.OWNER.value}
    )


@pytest.fixture(scope="function")
def admin_token(db_session):
    tenant = Tenant(name="Test Tenant Admin",
                    slug="test-tenant-admin", business_type=BusinessType.STORE)
    db_session.add(tenant)
    db_session.commit()

    user = User(
        name="Admin User",
        email="admin@test.com",
        hashed_password=hashed_password("testpass123"),
    )
    db_session.add(user)
    db_session.commit()

    user_tenant = UserTenant(
        user_id=user.id, tenant_id=tenant.id, role=UserRole.ADMIN
    )
    db_session.add(user_tenant)
    db_session.commit()

    return create_access_token(
        {"sub": str(user.id), "tenant_id": tenant.id,
        "role": UserRole.ADMIN.value}
    )


@pytest.fixture(scope="function")
def staff_token(db_session):
    tenant = Tenant(name="Test Tenant Staff",
                    slug="test-tenant-staff", business_type=BusinessType.STORE)
    db_session.add(tenant)
    db_session.commit()

    user = User(
        name="Staff User",
        email="staff@test.com",
        hashed_password=hashed_password("testpass123"),
    )
    db_session.add(user)
    db_session.commit()

    user_tenant = UserTenant(
        user_id=user.id, tenant_id=tenant.id, role=UserRole.STAFF
    )
    db_session.add(user_tenant)
    db_session.commit()

    return create_access_token(
        {"sub": str(user.id), "tenant_id": tenant.id,
        "role": UserRole.STAFF.value}
    )


@pytest.fixture(scope="function")
def tenant_and_owner(db_session):
    """Devuelve (tenant, user, owner_token) para tests que necesitan un tenant real."""
    tenant = Tenant(name="Main Tenant", slug="main-tenant",
                    business_type=BusinessType.STORE)
    db_session.add(tenant)
    db_session.commit()

    user = User(
        name="Main Owner",
        email="main.owner@test.com",
        hashed_password=hashed_password("testpass123"),
    )
    db_session.add(user)
    db_session.commit()

    user_tenant = UserTenant(
        user_id=user.id, tenant_id=tenant.id, role=UserRole.OWNER)
    db_session.add(user_tenant)
    db_session.commit()

    token = create_access_token(
        {"sub": str(user.id), "tenant_id": tenant.id,
        "role": UserRole.OWNER.value}
    )
    return tenant, user, token


@pytest.fixture(scope="function")
def staff_in_tenant(db_session, tenant_and_owner):
    """Devuelve (tenant, staff_user, staff_token) en el mismo tenant que tenant_and_owner."""
    tenant, _, _ = tenant_and_owner

    staff_user = User(
        name="Staff Member",
        email="staff.member@test.com",
        hashed_password=hashed_password("testpass123"),
    )
    db_session.add(staff_user)
    db_session.commit()

    user_tenant = UserTenant(user_id=staff_user.id,
                            tenant_id=tenant.id, role=UserRole.STAFF)
    db_session.add(user_tenant)
    db_session.commit()

    token = create_access_token(
        {"sub": str(staff_user.id), "tenant_id": tenant.id,
        "role": UserRole.STAFF.value}
    )
    return tenant, staff_user, token
