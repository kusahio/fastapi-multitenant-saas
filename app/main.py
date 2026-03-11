from fastapi import FastAPI
from app.core.middleware.tenant_middleware import TenantMiddleware
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.tenants.router import router as tenants_router

def create_app() -> FastAPI:

    app = FastAPI(
        title="SaaS API",
        version="1.0.0"
    )

    app.add_middleware(TenantMiddleware)

    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(tenants_router)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app

app = create_app()