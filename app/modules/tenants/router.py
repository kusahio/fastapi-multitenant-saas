from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.tenants.schemas import TenantCreate, TenantRead, TenantUpdate
from app.modules.tenants.repository import TenantRepository
from app.modules.users.repository import UserRepository
from app.modules.user_tenants.repository import UserTenantRepository
from app.modules.tenants.service import TenantService
from app.domain.errors.tenant import TenantAlreadyExistsError, TenantNotFoundError
from app.core.dependencies import get_current_user
from app.core.guards.role_guard import RoleGuard
from app.domain.enums.users_role import UserRole

router = APIRouter(prefix='/tenants', tags=['tenants'])

def get_tenant_service() -> TenantService:
    tenant_repository = TenantRepository()
    user_repository = UserRepository()
    user_tenant_repository = UserTenantRepository()
    return TenantService(
        tenant_repository=tenant_repository,
        user_repository=user_repository,
        user_tenant_repository=user_tenant_repository
    )

@router.post('/', response_model=TenantRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RoleGuard(UserRole.PLATFORM_ADMIN))])
def create_tenant(
    tenant: TenantCreate,
    db: Session = Depends(get_db),
    service: TenantService = Depends(get_tenant_service)):

    try:
        return service.create(db, tenant)
    except TenantAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Ya existe un tenant con este slug'
        )

@router.get('/', response_model=list[TenantRead], status_code=status.HTTP_200_OK, dependencies=[Depends(RoleGuard(UserRole.PLATFORM_ADMIN))])
def list_tenants(
    db: Session = Depends(get_db), 
    service: TenantService = Depends(get_tenant_service)
):
    return service.get_list(db)

@router.get('/{tenant_id}', response_model=TenantRead, status_code=status.HTTP_200_OK, dependencies=[Depends(RoleGuard(UserRole.PLATFORM_ADMIN))])
def get_tenant_by_id(
    tenant_id: int,
    db: Session = Depends(get_db), 
    service: TenantService = Depends(get_tenant_service)
):
    try:
        return service.get_by_id(db, tenant_id)
    except TenantNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Tenant no encontrado'
        )

@router.get('/slug/{tenant_slug}', response_model=TenantRead, status_code=status.HTTP_200_OK, dependencies=[Depends(RoleGuard(UserRole.PLATFORM_ADMIN))])
def get_tenant_by_slug(
    tenant_slug: str,
    db: Session = Depends(get_db),
    service: TenantService = Depends(get_tenant_service)
):
    try:
        return service.get_by_slug(db, tenant_slug)
    except TenantNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Tenant no encontrado'
        )
  
@router.put('/{tenant_id}', response_model=TenantRead, status_code=status.HTTP_200_OK, dependencies=[Depends(RoleGuard(UserRole.PLATFORM_ADMIN))])
def update_tenant(
    tenant_id: int,
    data: TenantUpdate,
    db: Session = Depends(get_db),
    service: TenantService = Depends(get_tenant_service)
):
    try:
        return service.update(db, tenant_id, data)
    except TenantNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Tenant no encontrado'
        )

@router.patch('/{tenant_id}/activate', response_model=TenantRead, status_code=status.HTTP_200_OK, dependencies=[Depends(RoleGuard(UserRole.PLATFORM_ADMIN))])
def activate_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    service: TenantService = Depends(get_tenant_service)
    ):
    try:
        return service.update(db, tenant_id, TenantUpdate(active=True))
    except TenantNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Tenant no encontrado'
        )

@router.patch('/{tenant_id}/deactivate', response_model=TenantRead, status_code=status.HTTP_200_OK, dependencies=[Depends(RoleGuard(UserRole.PLATFORM_ADMIN))])
def deactivate_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    service: TenantService = Depends(get_tenant_service)
    ):
    try:
        return service.update(db, tenant_id, TenantUpdate(active=False))
    except TenantNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Tenant no encontrado'
        )
