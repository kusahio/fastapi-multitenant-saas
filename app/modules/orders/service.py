import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from decimal import Decimal
from app.modules.orders.repository import OrderRepository
from app.modules.products.repository import ProductRepository
from app.modules.orders.schemas import OrderCreate
from app.modules.orders.models import Order, OrderItem
from app.modules.cash_shifts.repository import CashShiftRepository

class OrderService:
    def __init__(self):
        self.order_repository = OrderRepository()
        self.product_repository = ProductRepository()

    def create_order(self, db: Session, tenant_id: int, user_id: int, data: OrderCreate):
        if not data.items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La venta debe contener al menos un producto."
            )

        active_shift = CashShiftRepository().get_active_shift(db, tenant_id, user_id)

        if not active_shift:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Debes abrir caja antes de realizar una venta."
            )
        
        total_order_amount = Decimal('0.00')
        order_items = []

        for item in data.items:
            product = self.product_repository.get_by_id_for_update(db, tenant_id, item.product_id)

            if not product or not product.active:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail=f"Producto con ID {item.product_id} no encontrado o inactivo."
                )

            if product.stock < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Stock insuficiente para '{product.name}'. Stock actual: {product.stock}"
                )
            
            prod_discount = product.discount if product.is_discount_active else Decimal('0.00')
            cat_discount = product.category.discount if product.category.is_discount_active else Decimal('0.00')
            
            if product.category.is_discount_cumulative:
                final_discount = prod_discount + cat_discount
            else:
                final_discount = max(prod_discount, cat_discount)
            
            final_discount = min(final_discount, Decimal('100.00'))

            discount_multiplier = Decimal('1') - (final_discount / Decimal('100'))
            unit_price = product.price

            item_total_price = (unit_price * item.quantity) * discount_multiplier

            product.stock -= item.quantity

            order_item = OrderItem(
                product_id=product.id,
                product_name=product.name,
                quantity=item.quantity,
                unit_price=unit_price,
                discount=final_discount,
                total_price=item_total_price
            )
            order_items.append(order_item)
            
            total_order_amount += item_total_price

        order = Order(
            tenant_id=tenant_id,
            user_id=user_id,
            cash_shift_id=active_shift.id,
            payment_type=data.payment_type,
            total=total_order_amount,
            items=order_items
        )

        try:
            self.order_repository.save(db, order)
            db.commit() 
            db.refresh(order)
            return order
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logging.error(f"Error al procesar la venta: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error crítico al procesar la venta. Revisa los logs del servidor."
            )

    def get_list(self, db: Session, tenant_id: int):
        return self.order_repository.get_all(db, tenant_id)

    def get_by_id(self, db: Session, tenant_id: int, order_id: int):
        order = self.order_repository.get_by_id(db, tenant_id, order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket no encontrado")
        return order