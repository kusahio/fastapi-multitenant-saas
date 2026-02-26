from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.tenants.schemas import TenantCreate, TenantRead, TenantUpdate
from app.modules.tenants.repository import TenantRepository
from app.modules.tenants.service import TenantService
from app.domain.errors.tenant import TenantAlreadyExistsError, TenantNotFoundError

router = APIRouter(prefix='/tenants', tags=['tenants'])

def get_tenant_service() -> TenantService:
    repository = TenantRepository()
    return TenantService(repository)

@router.post('/', response_model=TenantRead, status_code=status.HTTP_201_CREATED)
def create_tenant(
  tenant: TenantCreate,
  db: Session = Depends(get_db),
  service: TenantService = Depends(get_tenant_service)):

  try:
    return service.create(db, tenant)
  except TenantAlreadyExistsError:
    raise HTTPException(
      status_code=status.HTTP_409_CONFLICT,
      detail='Tenant with this slug already exists'
    )

@router.get('/', response_model=list[TenantRead], status_code=status.HTTP_200_OK)
def list_tenants(
  db: Session = Depends(get_db), 
  service: TenantService = Depends(get_tenant_service)
):
  return service.get_list(db)

@router.get('/{tenant_id}', response_model=TenantRead, status_code=status.HTTP_200_OK)
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
      detail='Tenant not found'
    )

@router.get('/slug/{tenant_slug}', response_model=TenantRead, status_code=status.HTTP_200_OK)
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
      detail='Tenant not found'
    )
  
@router.put('/tenant/{tenant_id}', response_model=TenantRead, status_code=status.HTTP_200_OK)
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
      detail='Tenant not found'
    )

@router.patch('/{tenant_id}/activate', response_model=TenantRead, status_code=status.HTTP_200_OK)
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
      detail='Tenant not found'
    )

@router.patch('/{tenant_id}/deactivate', response_model=TenantRead, status_code=status.HTTP_200_OK)
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
      detail='Tenant not found'
    )