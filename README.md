# FastAPI Multi-Tenant SaaS

**Proyecto personal enfocado en explorar arquitectura backend, diseño de aplicaciones SaaS y buenas prácticas de desarrollo.**

El proyecto toma como caso de estudio un sistema POS multi-tenant para experimentar con modelado de datos, autenticación, autorización y organización de aplicaciones backend escalables.

Su objetivo principal no es replicar un sistema POS comercial ni aprender un framework en particular, sino utilizar un dominio de negocio real para experimentar con decisiones de arquitectura y comprender cómo diseñar aplicaciones backend que puedan evolucionar de forma ordenada a medida que aumentan su complejidad.

Cada nueva funcionalidad se incorpora únicamente cuando permite explorar un nuevo concepto técnico o validar una decisión de diseño.

Actualmente utiliza **FastAPI**, **SQLAlchemy 2.0**, **PostgreSQL**, **Alembic**, **JWT** y **pytest**.

Implementa una arquitectura modular con soporte para multi-tenancy a nivel aplicación, RBAC dual (plataforma y tenant) y autenticación JWT con selección de tenant posterior al inicio de sesión.

Como dominio de negocio incorpora funcionalidades propias de un sistema POS, incluyendo productos, categorías, órdenes, turnos de caja, descuentos y métricas.

---

## ¿Por qué existe este proyecto?

Este proyecto nace para profundizar en conceptos de arquitectura backend que difícilmente se pueden explorar en aplicaciones pequeñas.

**Más que implementar funcionalidades, el objetivo fue entender cómo las decisiones de diseño influyen en la mantenibilidad, escalabilidad y evolución de una aplicación backend.**

Los principales objetivos fueron:

- Diseñar una arquitectura preparada para crecer de forma incremental, incorporando nuevas funcionalidades sin comprometer la mantenibilidad del sistema.
- Aprender a diseñar una arquitectura basada en separación de responsabilidades, desacoplando lógica de negocio, acceso a datos y capa de presentación.
- Diseñar una organización modular del código que facilite el mantenimiento y la incorporación de nuevos dominios de negocio.
- Explorar patrones utilizados en aplicaciones SaaS multi-tenant.
- Profundizar en el uso de ORMs (SQLAlchemy) para modelar entidades, gestionar relaciones y simplificar el acceso a datos mediante consultas parametrizadas.
- Gestionar la evolución del esquema de base de datos mediante migraciones versionadas con Alembic.
- Diseñar e implementar mecanismos de autenticación, autorización y control de acceso utilizando JWT y RBAC.

El proyecto continúa evolucionando como un espacio para validar nuevas decisiones de diseño, incorporar funcionalidades y seguir profundizando en conceptos de arquitectura e ingeniería de software.

---

## Preguntas que buscaba responder

Durante el desarrollo del proyecto me propuse responder preguntas como:

- ¿Cómo organizar un backend para que sea fácil de mantener a medida que crece?
- ¿Cuándo conviene utilizar un ORM y cuándo SQL nativo?
- ¿Cómo modelar relaciones complejas sin aumentar el acoplamiento entre entidades?
- ¿Cómo mantener bajo el acoplamiento entre módulos a medida que crece la aplicación?
- ¿Qué responsabilidades deberían pertenecer al dominio y cuáles a la infraestructura?
- ¿Cómo estructurar un proyecto para facilitar su evolución y mantenimiento a largo plazo?

---

## Enfoque del proyecto

Aunque el dominio funcional elegido es un sistema POS, el foco principal del proyecto está en la arquitectura backend y no en la implementación de funcionalidades específicas.

Cada nueva funcionalidad se incorpora únicamente cuando permite explorar un nuevo concepto técnico, validar una decisión de diseño o mejorar la arquitectura existente.

---

## Principios del proyecto

Durante el desarrollo intento mantener algunas decisiones constantes:

- Favorecer soluciones simples antes que abstracciones innecesarias.
- Favorecer código legible antes que soluciones complejas.
- Separar responsabilidades para reducir el acoplamiento.
- Priorizar mantenibilidad sobre optimizaciones prematuras.
- Incorporar nuevas tecnologías únicamente cuando aportan una mejora real al diseño.

---

## Índice

1. [Arquitectura General](#arquitectura-general)
2. [Estructura Detallada del Proyecto](#estructura-detallada-del-proyecto)
3. [Modelo Multi-Tenant](#modelo-multi-tenant)
4. [Flujo de Autenticación y Autorización](#flujo-de-autenticación-y-autorización)
5. [Módulos Funcionales en Profundidad](#módulos-funcionales-en-profundidad)
6. [Lógica de Negocio Clave](#lógica-de-negocio-clave)
7. [Testing](#testing)
8. [Stack Tecnológico](#stack-tecnológico)
9. [Puesta en Marcha](#puesta-en-marcha)
10. [Migraciones Alembic](#migraciones-alembic)
11. [Decisiones de Diseño](#decisiones-de-diseño)
12. [Futuras Mejoras](#futuras-mejoras)
13. [Nuevas Funcionalidades Potenciales](#nuevas-funcionalidades-potenciales)

---

## Arquitectura General

El proyecto sigue una **arquitectura en capas con separación por dominios** (Domain-Driven Design ligero).  
Cada módulo funcional contiene su propio modelo, esquemas, repositorio, servicio y router.

### Capas del Sistema

```
┌──────────────────────────────────────────────────────┐
│                    FastAPI App                        │
│  (main.py: factory + middlewares + exception handlers)│
├──────────────────────────────────────────────────────┤
│                    core/                              │
│  settings  database  security  dependencies  limiter  │
│  middleware/  guards/  repositories/                  │
├──────────────────────────────────────────────────────┤
│                    domain/                            │
│  errors/ (excepciones tipadas por módulo)             │
│  enums/ (UserRole, TenantRole, BusinessType, ...)     │
├──────────────────────────────────────────────────────┤
│                    modules/                           │
│  auth │ users │ tenants │ user_tenants                │
│  categories │ products │ orders │ cash_shifts │ metrics│
├──────────────────────────────────────────────────────┤
│                    tests/                             │
│  pytest + TestClient + SQLite in-memory               │
└──────────────────────────────────────────────────────┘
```

### Patrón por Módulo (Repository + Service + Router)

Cada módulo funcional sigue estrictamente esta estructura:

```
modules/{modulo}/
├── models.py       # SQLAlchemy models (definición de tablas)
├── schemas.py      # Pydantic v2 schemas (validación request/response)
├── repository.py   # Acceso a datos (CRUD + queries específicas)
├── service.py      # Lógica de negocio, transacciones, validaciones de dominio
└── router.py       # Endpoints FastAPI + inyección de dependencias + guards
```

**Responsabilidades separadas:**
- **Router:** Solo serialización/validación HTTP, manejo de excepciones, guards de autorización.
- **Service:** Lógica de negocio, transacciones con commit/rollback, orquestación de repositorios.
- **Repository:** Queries SQLAlchemy, acceso a datos, filtros por tenant, soft delete.
- **Models:** Definición de tablas, relaciones, constraints.

---

## Estructura Detallada del Proyecto

```
fastapi-multitenant-saas/
│
├── app/
│   ├── main.py                           # Factory create_app(), middlewares, routers, exception handlers
│   │
│   ├── core/                             # Núcleo compartido
│   │   ├── settings.py                   # Pydantic BaseSettings con .env
│   │   ├── database.py                   # Engine SQLAlchemy + SessionLocal + Base + get_db()
│   │   ├── security.py                   # hashed_password() + verify_password() con bcrypt
│   │   ├── dependencies.py               # get_current_user() (decodifica JWT, devuelve dict)
│   │   ├── limiter.py                    # slowapi.Limiter (rate limiting global)
│   │   ├── middleware/
│   │   │   └── tenant_middleware.py       # Extrae tenant_id/user_id/role del JWT → request.state
│   │   ├── guards/
│   │   │   └── role_guard.py             # RoleGuard(*roles): valida rol del usuario en endpoint
│   │   └── repositories/
│   │       └── tenant_repository.py      # BaseTenantRepository: CRUD genérico filtrado por tenant_id
│   │
│   ├── domain/                           # Dominio puro (sin dependencias externas)
│   │   ├── errors/                       # Excepciones de dominio por módulo
│   │   │   ├── users.py                  # UserAlreadyExist, UserNotFound, InvalidCredentials, etc.
│   │   │   ├── tenant.py                 # TenantAlreadyExists, TenantNotFound, TenantInactive
│   │   │   ├── products.py               # ProductNotFound, ProductBarcodeAlreadyExists
│   │   │   ├── categories.py             # CategoryNotFound, CategoryHasProducts
│   │   │   ├── orders.py                 # NoActiveShift, OrderNotFound
│   │   │   ├── cash_shifts.py            # ShiftAlreadyOpen, NoOpenShift
│   │   │   └── auth.py                   # (reservado para errores de autenticación)
│   │   └── enums/                        # Enums de dominio (str Enum)
│   │       ├── users_role.py             # UserRole: PLATFORM_ADMIN, OWNER, ADMIN, STAFF
│   │       ├── tenant_role.py            # TenantRole: OWNER, ADMIN, STAFF
│   │       ├── business_type.py          # BusinessType: STORE, FOOD, RESTAURANT
│   │       ├── payment_type.py           # PaymentType: CASH, DEBIT_CARD, CREDIT_CARD, TRANSFER, VIRTUAL_WALLET
│   │       ├── unit_type.py              # UnitType: UNIT, KG, LITER, METER
│   │       └── cash_shift.py             # CashShiftStatus: OPEN, CLOSED
│   │
│   ├── modules/                          # Módulos funcionales
│   │   ├── auth/                         # Autenticación
│   │   ├── users/                        # Gestión de usuarios
│   │   ├── tenants/                      # Gestión de tenants
│   │   ├── user_tenants/                 # Relación muchos-a-muchos User ↔ Tenant
│   │   ├── categories/                   # Categorías de productos
│   │   ├── products/                     # Productos (inventario)
│   │   ├── orders/                       # Órdenes de venta (POS)
│   │   ├── cash_shifts/                  # Turnos de caja
│   │   └── metrics/                      # Métricas y estadísticas
│   │
│   └── tests/                            # Suite de tests
│       ├── conftest.py                   # Fixtures compartidas (db, client, tokens, datos pre-poblados)
│       ├── test_auth.py                  # Tests de login, refresh, select-tenant
│       ├── test_tenants.py               # CRUD de tenants
│       ├── test_users.py                 # CRUD de usuarios con roles
│       ├── test_categories.py            # CRUD de categorías
│       ├── test_products.py              # CRUD de productos
│       ├── test_orders.py                # Creación y consulta de órdenes
│       ├── test_cash_shifts.py           # Apertura/cierre de caja
│       └── test_metrics.py              # Métricas por tenant y plataforma
│
├── alembic/                              # Migraciones de base de datos
│   ├── env.py                            # Configuración de Alembic (importa todos los modelos)
│   ├── script.py.mako                    # Template para nuevas migraciones
│   └── versions/                         # Migraciones versionadas
│
├── pytest.ini                            # Configuración de pytest
├── requirements.txt                      # Dependencias del proyecto
├── alembic.ini                           # Configuración de conexión para Alembic
├── .env                                  # Variables de entorno (local, no commiteado)
└── .gitignore
```

---

## Modelo Multi-Tenant

### Estrategia: Shared Database, Shared Schema (columna discriminadora `tenant_id`)

**No se usa un schema de PostgreSQL por tenant ni una base de datos por tenant.**  
Todas las tablas de negocio residen en el mismo esquema y la separación se logra mediante la columna `tenant_id` como Foreign Key a `tenants.id`.

**Ventajas de esta estrategia:**
- Simple de implementar y mantener
- Facil de testear (una sola base de datos)
- Portable entre motores de base de datos
- Consultas cross-tenant para el admin de plataforma

**Riesgos:**
- Riesgo de fuga de datos si un desarrollador olvida filtrar por `tenant_id`

**Mitigación:** El `BaseTenantRepository` fuerza el filtro por `tenant_id` en todos los métodos CRUD base. Cada servicio debe pasar explícitamente el `tenant_id` obtenido del JWT.

### Diagrama de Entidades y Relaciones

```
┌─────────────────────┐
│       tenants       │
├─────────────────────┤
│ id (PK)             │
│ name (varchar 100)  │
│ slug (varchar 50, UK)│ ← Ej: "mi-tienda"
│ logo_url (varchar)  │
│ business_type (enum)│ ← STORE | FOOD | RESTAURANT
│ active (boolean)    │
│ created_at (timestmp)│
└─────────┬───────────┘
          │ 1
          │
    ┌─────┴─────┐ (user_tenants)
    │           │
    ▼           ▼
┌──────────┐ ┌──────────────────────┐
│  users   │ │    user_tenants      │← Tabla pivote (muchos-a-muchos)
├──────────┤ ├──────────────────────┤
│ id (PK)  │ │ id (PK)              │
│ name     │ │ user_id (FK)         │
│ email(UK)│ │ tenant_id (FK)       │
│ password │ │ role (TenantRole)    │← OWNER | ADMIN | STAFF
│ document │ │ created_at           │
│ is_plat. │ │ UNIQUE(user_id,tenant_id)
│ admin    │ └──────────────────────┘
│ active   │
│ deleted  │
│ created  │
└────┬─────┘
     │ 1
     │
     ▼
┌──────────────────────────────────────────┐
│          Entidades de negocio            │
│  (todas con tenant_id como FK)           │
├──────────────────────────────────────────┤
│                                          │
│  ┌────────────┐  ┌──────────┐           │
│  │ categories │  │ products │           │
│  │────────────│  │──────────│           │
│  │ tenant_id  │  │ tenant_id│           │
│  │ name       │  │ barcode  │           │
│  │ discount   │  │ name     │           │
│  │ is_cumulat.│  │ price    │           │
│  │ is_active  │  │ discount │           │
│  └──────┬─────┘  │ is_active│           │
│         │        │ stock    │           │
│         │        │ unit_type│           │
│         │        │ category │           │
│         │        │ active   │           │
│         │        │ deleted  │           │
│         │        └────┬─────┘           │
│         │             │                 │
│         ▼             ▼                 │
│  ┌─────────────────────────┐            │
│  │        orders           │            │
│  │─────────────────────────│            │
│  │ tenant_id               │            │
│  │ user_id  (FK)           │            │
│  │ cash_shift_id (FK)      │            │
│  │ payment_type (enum)     │            │
│  │ total (Numeric)         │            │
│  │ created_at              │            │
│  └───────────┬─────────────┘            │
│              │ 1                        │
│              ▼                          │
│  ┌─────────────────────────┐            │
│  │      order_items        │            │
│  │─────────────────────────│            │
│  │ order_id (FK)           │            │
│  │ product_id (FK,nullable)│            │
│  │ product_name *          │← Snapshot   │
│  │ product_sku *           │← histórico  │
│  │ product_barcode *       │← inmutable  │
│  │ category_name *         │             │
│  │ quantity                │             │
│  │ unit_price *            │← precio al  │
│  │ discount *              │← momento de │
│  │ total_price *           │← la venta   │
│  └─────────────────────────┘            │
│                                          │
│  ┌─────────────────────────┐            │
│  │      cash_shifts        │            │
│  │─────────────────────────│            │
│  │ tenant_id               │            │
│  │ user_id (FK)            │            │
│  │ opening_balance         │            │
│  │ closing_balance         │            │
│  │ expected_balance        │            │
│  │ status (OPEN/CLOSED)    │            │
│  │ opened_at               │            │
│  │ closed_at               │            │
│  │ observations            │            │
│  └─────────────────────────┘            │
│                                          │
└──────────────────────────────────────────┘
```

### Jerarquía de Roles y Permisos

El sistema tiene **dos niveles de roles** que conviven:

#### Nivel 1: UserRole (global, asignado al usuario en la tabla `users`)

| Rol | `users.is_platform_admin` | Acceso |
|-----|--------------------------|--------|
| `PLATFORM_ADMIN` | `true` | Acceso total a todos los tenants. Endpoints de administración global. No tiene `tenant_id` en el JWT. |

#### Nivel 2: TenantRole (por tenant, asignado en `user_tenants`)

| Rol | Nivel de acceso dentro del tenant | Categorías | Productos | Órdenes | Caja | Usuarios |
|-----|----------------------------------|:-----------:|:---------:|:-------:|:----:|:--------:|
| `OWNER` | Control total del tenant | CRUD | CRUD | CRUD | Apertura/cierre | Crear ADMIN y STAFF |
| `ADMIN` | Administración (sin dueño) | CRUD | CRUD | Lectura + creación | Apertura/cierre | Crear solo STAFF |
| `STAFF` | Operación diaria | Lectura | Lectura | Lectura + creación | Apertura/cierre | <span style="color:red">🗙</span> |

**Reglas de negocio validadas en `UserService._validate_role_creation()`:**
- `PLATFORM_ADMIN` puede crear cualquier rol, incluyendo otros `PLATFORM_ADMIN`
- `OWNER` puede crear `ADMIN` y `STAFF`
- `ADMIN` solo puede crear `STAFF`
- `STAFF` no puede crear usuarios

---

## Flujo de Autenticación y Autorización

### 1. Registro inicial

Los tenants son creados por `PLATFORM_ADMIN` via `POST /tenants/`.  
Al crear un tenant, se especifica `owner_name`, `owner_email`, `owner_password`: si el usuario no existe, se crea automáticamente con rol `OWNER` dentro del nuevo tenant.

### 2. Login (`POST /auth/login`)

```
Request:  { "username": "email", "password": "..." }  (OAuth2PasswordRequestForm)
Response: {
  "user_id": 1,
  "name": "Juan Pérez",
  "tenants": [
    { "tenant_id": 1, "name": "Mi Tienda", "slug": "mi-tienda", "role": "owner" }
  ],
  "access_token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

**Lógica:**
- Busca usuario por email
- Verifica contraseña con bcrypt
- Verifica `user.active == true`
- Si es `PLATFORM_ADMIN` → genera token sin `tenant_id`, tenants vacío
- Si es usuario normal → consulta `UserTenant` con JOIN a `Tenant`, genera token temporal (solo `sub`) + devuelve lista de tenants

### 3. Selección de Tenant (`POST /auth/select-tenant`)

```
Request:  { "tenant_id": 1 }
Response: { "access_token": "eyJ...", "refresh_token": "eyJ..." }
```

**Lógica:**
- Verifica que exista `UserTenant` para ese usuario + tenant
- Genera nuevo JWT con `sub` (user_id), `tenant_id` y `role` (TenantRole)
- A partir de este punto, el JWT trae el contexto completo del tenant

### 4. Refresh Token (`POST /auth/refresh`)

```
Request:  { "refresh_token": "eyJ..." }  (opcional, puede venir en cookie)
Response: { "access_token": "eyJ...", "refresh_token": "eyJ..." }
```

- El refresh token se distingue por `"type": "refresh"` en el payload
- Rota ambos tokens (access + refresh) manteniendo el payload original

### 5. Requests Autenticados

**TenantMiddleware** (se ejecuta en cada request):

```python
# Decodifica el JWT y extrae:
request.state.user_id    = payload.get("sub")
request.state.tenant_id  = payload.get("tenant_id")
request.state.role       = payload.get("role")
```

**get_current_user()** (dependency):

```python
# Retorna dict con:
{ "user_id": int, "tenant_id": int | None, "role": str | None }
```

**RoleGuard(*roles)** (dependency):

```python
# Valida que current_user["role"] esté en los roles permitidos
# Si no → HTTP 403 Forbidden
# PLATFORM_ADMIN pasa cualquier guard (por diseño actual)
```

### 6. Soporte para Web (HttpOnly Cookies)

El router de auth soporta un flag `web: bool = False` en los endpoints de login, select-tenant y refresh.  
Cuando está activado:
- El `refresh_token` se guarda en una cookie HttpOnly (no accesible desde JavaScript)
- El `refresh_token` se elimina del body de la respuesta
- En refresh, primero busca el token en la cookie, luego en el body

Esto permite que aplicaciones web (React, Angular, etc.) manejen el refresh token de forma segura.

---

## Módulos Funcionales en Profundidad

### auth

| Método | Endpoint | Auth | Guard |
|--------|----------|------|-------|
| Login | `POST /auth/login` | No | `5/min` rate limit |
| Select Tenant | `POST /auth/select-tenant` | JWT | `get_current_user` |
| Refresh | `POST /auth/refresh` | <span style="color:red">🗙</span>* | <span style="color:red">🗙</span> |
| Me | `GET /auth/me` | JWT | `get_current_user` |
| Logout | `POST /auth/logout` | <span style="color:red">🗙</span> | <span style="color:red">🗙</span> |

**`GET /auth/me`**: Retorna el contexto actual del usuario. Si tiene `tenant_id`, hace lookup del tenant y retorna `active_tenant` con id, name, slug y role. Verifica que el tenant esté activo.

### users

| Método | Endpoint | Roles permitidos |
|--------|----------|-----------------|
| `POST` | `/users` | PLATFORM_ADMIN, OWNER, ADMIN |
| `GET` | `/users` | PLATFORM_ADMIN, OWNER, ADMIN, STAFF |
| `GET` | `/users/me/tenants` | Cualquiera autenticado |
| `PATCH` | `/users/{id}` | PLATFORM_ADMIN, OWNER, ADMIN |
| `DELETE` | `/users/{id}` | PLATFORM_ADMIN, OWNER, ADMIN |
| `PATCH` | `/users/{id}/activate` | PLATFORM_ADMIN, OWNER, ADMIN |

**Características:**
- Soft delete (marca `deleted_at` + `active = false`)
- Validación: no se puede desactivar un usuario con caja abierta (`UserHasOpenShiftError`)
- Paginación: `skip` / `limit` (default 100)
- Los usuarios normales solo ven usuarios de su propio tenant (filtro por `tenant_id`)
- El `PLATFORM_ADMIN` ve todos los usuarios del sistema

### tenants

| Método | Endpoint | Roles permitidos |
|--------|----------|-----------------|
| `POST` | `/tenants/` | PLATFORM_ADMIN |
| `GET` | `/tenants/` | PLATFORM_ADMIN |
| `GET` | `/tenants/{id}` | PLATFORM_ADMIN |
| `GET` | `/tenants/slug/{slug}` | PLATFORM_ADMIN |
| `PUT` | `/tenants/{id}` | PLATFORM_ADMIN |
| `PATCH` | `/tenants/{id}/activate` | PLATFORM_ADMIN |
| `PATCH` | `/tenants/{id}/deactivate` | PLATFORM_ADMIN |

**Creación de tenant** (`POST /tenants/`):
- Crea el tenant con `name`, `slug` (único, validated con regex `^[a-z0-9]+(-[a-z0-9]+)*$`), `business_type`
- Busca si el `owner_email` ya existe como usuario
  - Si no existe → crea el usuario con contraseña hasheada
  - Si existe → lo reutiliza
- Crea `UserTenant` con rol `OWNER`
- Transacción: si falla `IntegrityError` (slug duplicado) → rollback + `TenantAlreadyExistsError`

### categories

| Método | Endpoint | Roles permitidos |
|--------|----------|-----------------|
| `POST` | `/categories` | OWNER, ADMIN |
| `GET` | `/categories` | OWNER, ADMIN, STAFF |
| `GET` | `/categories/summary` | OWNER, ADMIN, STAFF |
| `PATCH` | `/categories/{id}` | OWNER, ADMIN |
| `DELETE` | `/categories/{id}` | OWNER, ADMIN |
| `PATCH` | `/categories/{id}/activate` | OWNER, ADMIN |
| `PATCH` | `/categories/{id}/deactivate` | OWNER, ADMIN |

**Características:**
- Paginación con filtros: `search` (por nombre), `is_active`
- Soft delete + validación: no se puede eliminar categoría con productos activos (`CategoryHasProductsError`)
- `GET /categories/summary`: retorna cada categoría con conteo de productos activos (query con `LEFT JOIN` y `GROUP BY`)

### products

| Método | Endpoint | Roles permitidos |
|--------|----------|-----------------|
| `POST` | `/products` | OWNER, ADMIN |
| `GET` | `/products` | OWNER, ADMIN, STAFF |
| `GET` | `/products/search?q=` | OWNER, ADMIN, STAFF |
| `GET` | `/products/unit-types` | OWNER, ADMIN, STAFF |
| `PATCH` | `/products/{id}` | OWNER, ADMIN |
| `DELETE` | `/products/{id}` | OWNER, ADMIN |
| `PATCH` | `/products/{id}/activate` | OWNER, ADMIN |
| `PATCH` | `/products/{id}/deactivate` | OWNER, ADMIN |

**Características:**
- Código de barras único por tenant (`UNIQUE(tenant_id, barcode)`)
- Paginación con filtros: `search` (por nombre), `category_id`, `is_active`
- `GET /products/search`: busca por término, prioriza coincidencia exacta de código de barras (útil para POS con escáner)
- Soft delete (`deleted_at`) + campo `active` para desactivación temporal
- `get_by_id_for_update()`: bloqueo pesimista (`SELECT ... FOR UPDATE`) para evitar condiciones de carrera en stock

### orders (POS)

| Método | Endpoint | Roles permitidos |
|--------|----------|-----------------|
| `POST` | `/orders` | OWNER, ADMIN, STAFF |
| `GET` | `/orders` | OWNER, ADMIN, STAFF |
| `GET` | `/orders/{id}` | OWNER, ADMIN, STAFF |

**Proceso de creación de orden (lógica completa en `OrderService.create_order()`):**

```
1. Validar que la orden tenga al menos 1 item
2. Validar que el usuario tenga una caja abierta (cash_shift activo)
3. Por cada item en la orden:
   a. Buscar producto con bloqueo pesimista (FOR UPDATE)
   b. Validar que el producto exista y esté activo
   c. Validar stock suficiente
   d. Calcular descuento:
      - discount_product si is_discount_active
      - discount_category si is_discount_active
      - Si is_discount_cumulative → suma
      - Si no → el mayor de los dos
      - Cap: 100%
   e. Calcular precio unitario y total con descuento
   f. Descontar del stock
   g. Crear OrderItem con SNAPSHOT de datos del producto
4. Calcular total de la orden
5. Crear Order con:
   - tenant_id, user_id, cash_shift_id (de la caja activa)
   - payment_type, total
   - Items creados
6. Commit (con rollback en caso de error)
```

**Snapshot en OrderItem:** Los campos `product_name`, `product_barcode`, `category_name`, `unit_price`, `discount` se copian al momento de la venta. Esto asegura que el histórico de ventas permanezca inmutable aunque después se modifique el producto o categoría.

### cash_shifts (Turnos de Caja)

| Método | Endpoint | Roles permitidos |
|--------|----------|-----------------|
| `POST` | `/cash-shifts/open` | OWNER, ADMIN, STAFF |
| `POST` | `/cash-shifts/close` | OWNER, ADMIN, STAFF |
| `GET` | `/cash-shifts/active` | OWNER, ADMIN, STAFF |

**Flujo:**
1. **Apertura:** El usuario registra `opening_balance` (dinero inicial en caja). Se valida que no tenga otra caja abierta (`ShiftAlreadyOpenError`).
2. **Operación:** El usuario puede crear órdenes de venta (valida que tenga caja abierta en `OrderService`).
3. **Cierre:** El usuario registra `closing_balance` (dinero real en caja). El sistema calcula `expected_balance = opening_balance + total_ventas_de_la_caja`. La diferencia se registra implícitamente para arqueo.

### metrics

| Método | Endpoint | Roles permitidos |
|--------|----------|-----------------|
| `GET` | `/metrics/summary` | OWNER, ADMIN, STAFF |
| `GET` | `/metrics/platform-summary` | PLATFORM_ADMIN |

**Métricas por tenant (`/metrics/summary`):**
- `total_products`: productos activos
- `total_categories`: categorías activas
- `products_by_category`: desglose por categoría
- `total_orders`: total de órdenes
- `orders_by_employee`: órdenes agrupadas por usuario (empleado)
- `sales_by_payment_type`: órdenes y montos por tipo de pago (efectivo, tarjeta, etc.)

**Métricas globales (`/metrics/platform-summary`):**
- `total_tenants`: todos los tenants
- `active_tenants`: tenants activos
- `tenants_by_type`: desglose por tipo de negocio
- `total_users`: usuarios del sistema
- `global_gmv`: Gross Merchandise Value (suma total de todas las órdenes)
- `top_tenants`: top 10 tenants por ventas totales

---

## Lógica de Negocio Clave

### Cálculo de Descuentos en Órdenes

```python
# Descuento del producto
prod_discount = product.discount if product.is_discount_active else 0.00

# Descuento de la categoría
cat_discount = product.category.discount if product.category.is_discount_active else 0.00

# Combinación
if product.category.is_discount_cumulative:
    final_discount = prod_discount + cat_discount    # Se acumulan
else:
    final_discount = max(prod_discount, cat_discount) # Se queda con el mayor

# Cap al 100%
final_discount = min(final_discount, 100.00)

# Precio final
item_total = (unit_price * quantity) * ((100 - final_discount) / 100)
```

### Soft Delete y Filtrado

Varias entidades (`users`, `products`, `categories`) usan **soft delete**:
- `deleted_at = DateTime(timezone=True, nullable=True)` — timestamp del borrado
- `active = Boolean(default=True)` — para desactivación temporal sin borrar

Los repositorios filtran `WHERE deleted_at IS NULL` en todas las queries de listado.
El soft delete permite recuperación ante desactivaciones accidentales.

### Validación de Permisos Jerárquicos

`UserService._validate_role_creation()` y `_validate_user_management_permissions()` implementan la escalera de permisos:

```
PLATFORM_ADMIN → puede: crear usuarios con cualquier rol (incluso PLATFORM_ADMIN)
                                    modificar usuarios de cualquier tenant
                                    activar/desactivar en cualquier tenant
OWNER          → puede: crear ADMIN y STAFF en su tenant
                                    modificar ADMIN y STAFF en su tenant
                                    activar/desactivar ADMIN y STAFF
ADMIN          → puede: crear SOLO STAFF en su tenant
                                    modificar SOLO STAFF en su tenant
                                    activar/desactivar SOLO STAFF
STAFF          → no puede gestionar usuarios
```

### Bloqueo Pesimista en Stock

`ProductRepository.get_by_id_for_update()` usa `SELECT ... FOR UPDATE` para evitar **condiciones de carrera** cuando dos empleados venden el mismo producto simultáneamente. El bloqueo se mantiene hasta que la transacción hace commit o rollback.

### Arqueo de Caja

Al cerrar la caja:
```python
total_sales = SUM(Order.total) WHERE cash_shift_id == shift.id
expected_balance = opening_balance + total_sales
difference = closing_balance - expected_balance  # implícito, el usuario ve la diferencia
```

Esto permite al dueño/administrador ver si hay diferencias entre lo que debería haber en caja y lo que realmente hay.

---

## Testing

### Configuración

- **Framework:** `pytest`
- **Cliente HTTP:** `fastapi.testclient.TestClient`
- **Base de datos:** SQLite en memoria (`sqlite:///:memory:`) con `StaticPool`
- **Rate limiting:** Deshabilitado durante tests (`limiter.enabled = False`)
- **Inicialización:** La app se crea una vez con `create_app()`, se sobrescribe `get_db` con la sesión de prueba

### Fixtures (`conftest.py`)

| Fixture | Scope | Descripción |
|---------|-------|-------------|
| `db_session` | function | Sesión limpia por test (truncado de todas las tablas) |
| `client` | function | TestClient con `db_session` inyectado |
| `platform_admin_token` | function | JWT de usuario PLATFORM_ADMIN |
| `owner_token` | function | JWT de usuario OWNER (con tenant creado) |
| `admin_token` | function | JWT de usuario ADMIN (con tenant creado) |
| `staff_token` | function | JWT de usuario STAFF (con tenant creado) |
| `tenant_and_owner` | function | Tupla `(tenant, user, token)` para tests que necesitan datos reales |
| `staff_in_tenant` | function | Tupla `(tenant, staff_user, staff_token)` en el mismo tenant que `tenant_and_owner` |

### Archivos de Test

| Archivo | Lo que testea |
|---------|---------------|
| `test_auth.py` | Login exitoso, login con credenciales inválidas, refresh token, select-tenant |
| `test_tenants.py` | CRUD de tenants, creación con owner, slug duplicado, activación/desactivación |
| `test_users.py` | Creación de usuarios por rol, validación de permisos, soft delete, caja abierta bloquea borrado |
| `test_categories.py` | CRUD de categorías, paginación, eliminación con productos asociados |
| `test_products.py` | CRUD de productos, código de barras único, búsqueda, descuento |
| `test_orders.py` | Creación de orden, cálculo de totales, validación de stock, descuentos acumulativos |
| `test_cash_shifts.py` | Apertura/cierre de caja, doble apertura, cierre con ventas |
| `test_metrics.py` | Métricas de tenant y plataforma |

### Comandos

```bash
# Ejecutar todos los tests
pytest -v

# Con reporte de coverage
pytest --cov=app --cov-report=term-missing

# Test específico
pytest app/tests/test_orders.py -v -k "test_create_order"
```

---

## Stack Tecnológico

| Capa | Tecnología | Versión | Propósito |
|------|-----------|---------|-----------|
| Framework | **FastAPI** | 0.135.x | API REST asíncrona con validación automática y docs |
| ASGI Server | **Uvicorn** | 0.42.x | Servidor ASGI para producción/desarrollo |
| ORM | **SQLAlchemy** | 2.0.x | ORM moderno con DeclarativeBase y session |
| DB Prod | **PostgreSQL** | 14+ | Base de datos relacional principal |
| DB Tests | **SQLite** | - | Base de datos en memoria para tests |
| Migraciones | **Alembic** | 1.18.x | Versionado de esquema de base de datos |
| Auth | **python-jose** | 3.5.x | JWTs (access + refresh) |
| Passwords | **bcrypt** | 5.0.x | Hash y verificación de contraseñas |
| Rate Limiting | **slowapi** | 0.1.x | Límite de requests por IP |
| Config | **pydantic-settings** | 2.13.x | Variables de entorno tipadas |
| Validación | **pydantic** | 2.12.x | Schemas de request/response |
| Testing | **pytest** | 9.0.x | Suite de tests |
| Testing | **httpx** | 0.28.x | Cliente HTTP para TestClient |
| Email | **email-validator** | 2.3.x | Validación de emails |
| Multipart | **python-multipart** | 0.0.x | Soporte para formularios OAuth2 |

---

## Puesta en Marcha

### 1. Requisitos
- Python 3.11+
- PostgreSQL 14+ (producción)

### 2. Variables de entorno (`.env`)

```env
# Base de datos
DB_USER=postgres
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=saas_db

# JWT
JWT_SECRET=super-secret-key-cambiar-en-produccion
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=240
REFRESH_TOKEN_EXPIRE_DAYS=30

# CORS (separados por coma)
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:4200
```

### 3. Instalación y ejecución

```bash
# Crear y activar entorno virtual
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar migraciones
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload --port 8000
```

### 4. Documentación interactiva

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Migraciones Alembic

### Historial de migraciones

| Revisión | Descripción |
|----------|-------------|
| `16e2cdcfea3f` | Creación de tabla `tenants` |
| *(siguientes)* | Tablas `users`, `user_tenants`, `categories`, `products`, `orders`, `order_items`, `cash_shifts` |
| `2f24a7a15039` | Lógica completa de descuentos en productos + `is_discount_active`, `is_discount_cumulative` en categorías |
| `32f2445c0056` | Agregar `payment_type` a tabla `orders` |
| `f4ce807585f3` | Agregar `cash_shift_id` como FK en `orders` (relación orden ↔ caja) |
| `24932b4da6ab` | Agregar `product_name` a `order_items` (snapshot histórico del nombre del producto) |

### Crear nueva migración

```bash
alembic revision --autogenerate -m "descripcion_de_la_migracion"
alembic upgrade head
```

**Nota:** Alembic autogenerate funciona correctamente porque `env.py` importa explícitamente todos los modelos (`User`, `Tenant`, `UserTenant`, `Category`, `Product`, `Order`, `CashShift`) y usa `Base.metadata` como `target_metadata`.

---

## Decisiones de Diseño

### 1. Multi-tenancy a nivel aplicación (no RLS de PostgreSQL)

Se optó por filtrar explícitamente por `tenant_id` en cada query en lugar de usar Row-Level Security de PostgreSQL.  
**Razones:**
- Portabilidad entre motores de BD (SQLite en tests funciona igual)
- Simplicidad: no requiere configurar políticas RLS ni roles de BD
- Transparencia: el filtro es explícito en el código, no mágico

**Mitigación de riesgo:** `BaseTenantRepository` obliga a pasar `tenant_id` en todos los métodos. Los servicios también reciben `tenant_id` desde el JWT.

### 2. JWT Stateless con tenant_id embebido

El JWT contiene `sub` (user_id), `tenant_id` y `role`.  
**Ventajas:**
- El middleware puede extraer el contexto sin consultar la BD
- Escalable horizontalmente (sin sesiones en servidor)
- Refresh token rota ambas credenciales periódicamente

### 3. RBAC Dual

Dos dimensiones de roles que se combinan:
- **UserRole.PLATFORM_ADMIN** para operaciones de plataforma (crear tenants, ver todos los datos)
- **TenantRole (OWNER/ADMIN/STAFF)** para operaciones dentro de un tenant

`RoleGuard` valida el rol en el endpoint. La lógica de negocio en servicios valida permisos más finos.

### 4. Repository Pattern + Service Layer

**Repository:**
- `BaseTenantRepository`: CRUD genérico con filtro por `tenant_id`
- Repositorios específicos extienden la base y agregan queries particulares

**Service:**
- Contiene la lógica de negocio: validaciones, cálculos, transacciones
- Orquesta múltiples repositorios cuando es necesario
- Maneja commit/rollback

**Router:**
- Solo serialización (schemas), inyección de dependencias, guards
- Traduce excepciones de dominio a HTTP errors

### 5. Domain Errors (Excepciones tipadas)

Cada módulo define sus propias excepciones en `domain/errors/`.  
Los servicios lanzan estas excepciones. Los routers las atrapan y devuelven HTTP responses con `raise HTTPException`.

**Excepción especial:** `InsufficientPermissionsError` extiende `HTTPException` directamente porque se usa en multiples servicios y siempre debe devolver 403.

### 6. Soft Delete

`deleted_at` (timestamp del borrado) + `active` (desactivación temporal).  
**Ventajas:**
- Recuperación ante desactivaciones accidentales
- Historial de cambios
- Las órdenes referencian productos que pueden haber sido "eliminados"

### 7. Snapshot de Precios en OrderItem

Los campos `product_name`, `product_barcode`, `category_name`, `unit_price`, `discount` se copian al crear la orden.  
**Razón:** El ticket de venta debe reflejar los precios y nombres del momento de la venta, incluso si después el producto cambia de precio o nombre.

### 8. Bloqueo Pesimista en Stock

`ProductRepository.get_by_id_for_update()` usa `SELECT ... FOR UPDATE` para evitar que dos ventas concurrentes descuenten del mismo stock y generen inventario negativo.

### 9. Rate Limiting Global

`slowapi` con límite de 5 intentos/minuto en el endpoint de login (mitigación de fuerza bruta).  
Deshabilitado automáticamente en tests para no interferir.

### 10. Transacciones con Rollback Explícito

En servicios con múltiples operaciones (crear orden, crear tenant con owner), se maneja `try/except` con `db.rollback()` explícito ante cualquier error para mantener consistencia.

---

## Aprendizajes obtenidos

El desarrollo del proyecto me permitió profundizar especialmente en:

- Diseño de arquitecturas backend preparadas para crecer de forma incremental.
- Modelado de entidades y relaciones utilizando SQLAlchemy.
- Organización del código mediante separación de responsabilidades y arquitectura por capas.
- Gestión de la evolución del esquema de base de datos con Alembic.
- Diseño de APIs desacopladas, mantenibles y fáciles de extender.

---

## Futuras Mejoras

Secciones de mejora identificadas durante el desarrollo del proyecto:

### Mejoras Técnicas

- [ ] **Tipado completo:** Migrar de `Column` + type hints a `mapped_column()` de SQLAlchemy 2.0 para mejor integración con mypy
- [ ] **Paginación unificada:** Crear una clase base `PaginatedResponse[T]` genérica con Pydantic para evitar repetir el patrón `{"total": int, "items": list[T]}`
- [ ] **Repositorio abstracto:** Convertir `BaseTenantRepository` en ABC con métodos abstractos para garantizar implementación consistente
- [ ] **DTOs de dominio:** Separar completamente los schemas Pydantic de API de los objetos de dominio internos
- [ ] **Logging estructurado:** Implementar logging con `structlog` o formato JSON para mejor trazabilidad
- [ ] **Health check mejorado:** Agregar verificación de conexión a BD, migraciones pendientes y latencia
- [ ] **Pre-commit hooks:** Agregar `pre-commit` con ruff, mypy, y formateo automático
- [ ] **Dockerizar:** Agregar `Dockerfile` y `docker-compose.yml` con PostgreSQL + app
- [ ] **CI/CD:** Agregar pipeline GitHub Actions para lint, test y build
- [ ] **Gestión de secretos:** Migrar a variables de entorno con fallback a `.env` solo en desarrollo
- [ ] **Async:** Evaluar migración a endpoints asíncronos con `AsyncSession` de SQLAlchemy para operaciones I/O bound

### Mejoras de Seguridad

- [ ] **Refresh token rotation con invalidación:** Marcar refresh tokens como usados (tabla `refresh_tokens`) para detectar robo
- [ ] **Rate limiting por endpoint:** Extender slowapi a endpoints sensibles adicionales (crear usuario, crear tenant)
- [ ] **Auditoría de acciones:** Tabla `audit_log` para registrar operaciones críticas (creación de usuarios, cambios de rol, apertura/cierre de caja)
- [ ] **2FA / MFA:** Autenticación de dos factores para PLATFORM_ADMIN y OWNER
- [ ] **Políticas de contraseñas:** Validar complejidad (mayúsculas, números, símbolos) en backend
- [ ] **CSRF Protection:** Para endpoints que usan cookies HttpOnly

### Mejoras de Testing

- [ ] **Fábricas de test data:** Crear `factories.py` con builders para generar tenants, usuarios, productos, etc. de forma declarativa
- [ ] **Tests de integración con PostgreSQL:** Usar `testcontainers` o BD real para tests que requieren features específicas de PG
- [ ] **Property-based testing:** Usar `hypothesis` para probar cálculo de descuentos con valores extremos
- [ ] **Cobertura mínima:** Configurar `pytest-cov` con umbral mínimo (80%+)

---

## Nuevas Funcionalidades Potenciales

Funcionalidades que podrían agregarse al proyecto para expandir su alcance:

### Módulos de Negocio

- [ ] **Clientes (CRM):** Tabla `customers` con historial de compras, crédito, dirección. Asociar órdenes a clientes.
- [ ] **Proveedores y Compras:** Módulo de abastecimiento: órdenes de compra, recepción de mercadería, actualización automática de stock.
- [ ] **Múltiples sucursales:** Cada tenant podría tener múltiples `branches` con su propio stock, caja y empleados.
- [ ] **Gestión de inventario avanzado:** Transferencias entre sucursales, ajustes de inventario, conteo cíclico.
- [ ] **Facturación electrónica:** Integración con SII (Chile), SUNAT (Perú), AFIP (Argentina) según el país.
- [ ] **Comandas (restaurantes):** Mesas, mozos, comandas abiertas, división de cuentas, impresión en cocina.
- [ ] **Suscripciones y Planes:** Modelo de planes (Gratuito, Básico, Premium) con límites por feature (max productos, max usuarios, etc.).
- [ ] **Módulo de Gastos:** Registro de gastos operacionales, categorización, reportes de pérdidas y ganancias.

### Infraestructura

- [ ] **Webhooks:** Sistema de webhooks para notificar eventos (nueva orden, cierre de caja) a integraciones externas.
- [ ] **Exportación de datos:** Reportes en PDF/CSV/Excel descargables (ventas diarias, inventario, arqueo).
- [ ] **Cache con Redis:** Cachear consultas frecuentes (lista de productos activos, métricas del dashboard) con Redis.
- [ ] **Background tasks:** Usar Celery o FastAPI BackgroundTasks para tareas pesadas (generar reportes, enviar emails).
- [ ] **Notificaciones en tiempo real:** WebSockets o Server-Sent Events para actualizaciones del dashboard en vivo.
- [ ] **Backup automático:** Script de backup de BD con rotación y subida a cloud (S3, Google Cloud Storage).

### Experiencia de Usuario

- [ ] **Onboarding multi-paso:** Flujo guiado para nuevo tenant: crear primer producto, abrir caja, hacer primera venta.
- [ ] **Dashboard interactivo:** Endpoints de métricas optimizados para gráficos (ventas por hora/día/mes, top productos, tendencias).
- [ ] **Búsqueda avanzada de productos:** Búsqueda por código de barras parcial, nombre, categoría, precio, con autocomplete.
- [ ] **Historial de precios:** Tabla `price_history` para tracking de cambios de precio con fecha efectiva.
- [ ] **Múltiples monedas:** Soporte para transacciones en distintas monedas con tasa de cambio configurable.
- [ ] **Impresión de tickets:** Endpoint que genere HTML/PDF de ticket para impresión térmica (ESC/POS).

### API y Developer Experience

- [ ] **API Keys:** Soporte para API keys de integración (para conectar apps de terceros al POS).
- [ ] **Documentación interactiva mejorada:** Ejemplos de requests/responses en Swagger, schemas de error documentados.
- [ ] **Versionado de API:** Prefijo `/api/v1/` para permitir evolución del API sin romper clientes existentes.
- [ ] **SDK Client:** Generar cliente Python/TypeScript automáticamente desde OpenAPI spec.
- [ ] **Sandbox / Modo demo:** Entorno de pruebas con datos ficticios para demostraciones y testing de integraciones.

---

## Licencia

Proyecto personal desarrollado con fines de aprendizaje, experimentación y referencia.

Actualmente no cuenta con una licencia de código abierto específica.