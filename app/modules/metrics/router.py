from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.guards.role_guard import RoleGuard
from app.domain.enums.users_role import UserRole
from app.modules.metrics.schemas import MetricsSummary, PlatformMetricsSummary
from app.modules.metrics.service import MetricsService

router = APIRouter(prefix="/metrics", tags=["Metrics"])
metrics_service = MetricsService()

@router.get(
    "/summary",
    response_model=MetricsSummary,
    dependencies=[
        Depends(RoleGuard(UserRole.OWNER, UserRole.ADMIN, UserRole.STAFF))
    ]
)
def get_metrics_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return metrics_service.get_summary(db, current_user.get("tenant_id"))

@router.get(
    "/platform-summary", 
    response_model=PlatformMetricsSummary, 
    dependencies=[Depends(RoleGuard(UserRole.PLATFORM_ADMIN))]
)
def get_platform_summary(db: Session = Depends(get_db)):
    return metrics_service.get_platform_summary(db)