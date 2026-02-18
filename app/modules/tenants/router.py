from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.tenants.schemas import TenantCreate, TenantRead, TenantUpdate
from app.modules.tenants.repository import TenantRepository
from app.modules.tenants.service import TenantService
from app.domain.errors.tenant import TenantAlreadyExistsError, TenantNotFoundError

router = APIRouter(prefix='/tenants', tags=['tenants'])

@router.post('/', status_code=status.HTTP_201_CREATED)
def create_tenant(tenant: TenantCreate, service: TenantService, db: Session = Depends(get_db)):

  new_tenant = service.create(db, tenant)

  return new_tenant