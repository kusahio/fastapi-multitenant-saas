from pydantic import BaseModel

class CategoryCount(BaseModel):
    category_name: str
    total_products: int

class MetricsSummary(BaseModel):
    total_products: int
    total_categories: int
    products_by_category: list[CategoryCount]