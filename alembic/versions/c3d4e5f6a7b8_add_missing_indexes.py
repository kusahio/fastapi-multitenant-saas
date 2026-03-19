"""add missing indexes

Revision ID: c3d4e5f6a7b8
Revises: daa1d5d898d6
Create Date: 2026-03-19 11:00:00.000000

"""
from typing import Sequence, Union
from alembic import op

revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, Sequence[str], None] = 'daa1d5d898d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # #8 — tenant_id en tablas principales
    op.create_index('ix_products_tenant_id', 'products', ['tenant_id'])
    op.create_index('ix_categories_tenant_id', 'categories', ['tenant_id'])
    op.create_index('ix_orders_tenant_id', 'orders', ['tenant_id'])
    op.create_index('ix_cash_shifts_tenant_id', 'cash_shifts', ['tenant_id'])

    # índice compuesto para orders — tenant + fecha es la query más común
    op.create_index('ix_orders_tenant_created', 'orders', ['tenant_id', 'created_at'])

    # #9 — status en cash_shifts — se filtra en cada venta
    op.create_index('ix_cash_shifts_status', 'cash_shifts', ['status'])

    # índice compuesto para cash_shifts — la query real filtra tenant+user+status juntos
    op.create_index(
        'ix_cash_shifts_tenant_user_status',
        'cash_shifts',
        ['tenant_id', 'user_id', 'status']
    )


def downgrade() -> None:
    op.drop_index('ix_cash_shifts_tenant_user_status', table_name='cash_shifts')
    op.drop_index('ix_cash_shifts_status', table_name='cash_shifts')
    op.drop_index('ix_orders_tenant_created', table_name='orders')
    op.drop_index('ix_cash_shifts_tenant_id', table_name='cash_shifts')
    op.drop_index('ix_orders_tenant_id', table_name='orders')
    op.drop_index('ix_categories_tenant_id', table_name='categories')
    op.drop_index('ix_products_tenant_id', table_name='products')