from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.limiter import limiter
from app.core.middleware.tenant_middleware import TenantMiddleware
from app.core.settings import settings
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.tenants.router import router as tenants_router
from app.modules.categories.router import router as categories_router
from app.modules.products.router import router as products_router
from app.modules.metrics.router import router as metrics_router
from app.modules.orders.router import router as orders_router
from app.modules.cash_shifts.router import router as cash_shifts_router
from app.domain.errors.users import InvalidCredentialsError

def create_app() -> FastAPI:

    app = FastAPI(
        title="SaaS API",
        version="1.0.0"
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(InvalidCredentialsError)
    async def invalid_credentials_exception_handler(request: Request, exc: InvalidCredentialsError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"message": "Invalid credentials"},
        )

    app.add_middleware(TenantMiddleware)

    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(tenants_router)
    app.include_router(categories_router)
    app.include_router(products_router)
    app.include_router(metrics_router)
    app.include_router(orders_router)
    app.include_router(cash_shifts_router)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app

app = create_app()