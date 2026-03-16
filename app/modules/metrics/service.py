from sqlalchemy.orm import Session
from sqlalchemy import func
from app.modules.products.models import Product
from app.modules.categories.models import Category
from app.modules.orders.models import Order
from app.modules.users.models import User
from app.modules.tenants.models import Tenant

class MetricsService:
    def get_summary(self, db: Session, tenant_id: int):
        total_products = db.query(func.count(Product.id)).filter(
            Product.tenant_id == tenant_id,
            Product.active == True
        ).scalar() or 0

        total_categories = db.query(func.count(Category.id)).filter(
            Category.tenant_id == tenant_id,
            Category.active == True
        ).scalar() or 0

        products_by_category_query = db.query(
            Category.name.label('category_name'),
            func.count(Product.id).label('total_products')
        ).outerjoin(
            Product,
            (Category.id == Product.category_id) & (Product.active == True)
        ).filter(
            Category.tenant_id == tenant_id,
            Category.active == True
        ).group_by(
            Category.id
        ).all()

        products_by_category = [
            {
                "category_name": row.category_name,
                "total_products": row.total_products
            }
            for row in products_by_category_query
        ]

        total_orders = db.query(func.count(Order.id)).filter(
            Order.tenant_id == tenant_id
        ).scalar() or 0

        orders_by_employee_query = db.query(
            User.name.label('employee_name'),
            func.count(Order.id).label('total_orders')
        ).join(
            Order,
            User.id == Order.user_id
        ).filter(
            Order.tenant_id == tenant_id
        ).group_by(
            User.id
        ).order_by(
            func.count(Order.id).desc()
        ).all()

        orders_by_employee = [
            {
                "employee_name": row.employee_name,
                "total_orders": row.total_orders
            }
            for row in orders_by_employee_query
        ]

        sales_by_payment_query = db.query(
            Order.payment_type.label('payment_type'),
            func.count(Order.id).label('total_orders'),
            func.sum(Order.total).label('total_amount')
        ).filter(
            Order.tenant_id == tenant_id
        ).group_by(
            Order.payment_type
        ).all()

        sales_by_payment_type = [
            {
                "payment_type": row.payment_type,
                "total_orders": row.total_orders,
                "total_amount": row.total_amount or 0 
            }
            for row in sales_by_payment_query
        ]

        return {
            "total_products": total_products,
            "total_categories": total_categories,
            "products_by_category": products_by_category,
            "total_orders": total_orders,
            "orders_by_employee": orders_by_employee,
            "sales_by_payment_type": sales_by_payment_type
        }
    
    def get_platform_summary(self, db: Session):
        total_tenants = db.query(func.count(Tenant.id)).scalar() or 0
        active_tenants = db.query(func.count(Tenant.id)).filter(Tenant.active == True).scalar() or 0

        tenants_by_type_query = db.query(
            Tenant.business_type,
            func.count(Tenant.id).label('total')
        ).group_by(Tenant.business_type).all()

        tenants_by_type = [
            {
                "business_type": row.business_type,
                "total": row.total
            }
            for row in tenants_by_type_query
        ]

        total_users = db.query(func.count(User.id)).scalar() or 0

        global_gmv = db.query(func.sum(Order.total)).scalar() or 0

        top_tenants_query = db.query(
            Tenant.name.label('tenant_name'),
            func.count(Order.id).label('total_orders'),
            func.sum(Order.total).label('total_sales')
        ).join(
            Order, Tenant.id == Order.tenant_id
        ).group_by(
            Tenant.id
        ).order_by(
            func.sum(Order.total).desc()
        ).limit(10).all()

        top_tenants = [
            {
                "tenant_name": row.tenant_name,
                "total_orders": row.total_orders,
                "total_sales": row.total_sales or 0
            }
            for row in top_tenants_query
        ]

        return {
            "total_tenants": total_tenants,
            "active_tenants": active_tenants,
            "tenants_by_type": tenants_by_type,
            "total_users": total_users,
            "global_gmv": global_gmv,
            "top_tenants": top_tenants
        }