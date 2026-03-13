from pydantic import BaseModel
from decimal import Decimal
from app.domain.enums.payment_type import PaymentType
from app.domain.enums.business_type import BusinessType

class CategoryCount(BaseModel):
    category_name: str
    total_products: int

class EmployeeOrderCount(BaseModel):
    employee_name: str
    total_orders: int

class PaymentTypeMetric(BaseModel):
    payment_type: PaymentType
    total_orders: int
    total_amount: Decimal

class MetricsSummary(BaseModel):
    total_products: int
    total_categories: int
    products_by_category: list[CategoryCount]
    total_orders: int
    orders_by_employee: list[EmployeeOrderCount]
    sales_by_payment_type: list[PaymentTypeMetric]

class TenantTypeCount(BaseModel):
    business_type: BusinessType
    total: int

class TopTenant(BaseModel):
    tenant_name: str
    total_orders: int
    total_sales: Decimal

class PlatformMetricsSummary(BaseModel):
    total_tenants: int
    active_tenants: int
    tenants_by_type: list[TenantTypeCount]
    total_users: int
    global_gmv: Decimal
    top_tenants: list[TopTenant]