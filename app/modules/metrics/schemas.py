from pydantic import BaseModel

class CategoryCount(BaseModel):
    category_name: str
    total_products: int

class EmployeeOrderCount(BaseModel):
    employee_name: str
    total_orders: int

class MetricsSummary(BaseModel):
    total_products: int
    total_categories: int
    products_by_category: list[CategoryCount]
    total_orders: int
    orders_by_employee: list[EmployeeOrderCount]