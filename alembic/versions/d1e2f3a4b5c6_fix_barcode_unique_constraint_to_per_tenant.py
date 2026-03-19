"""fix barcode unique constraint to be per-tenant

Revision ID: d1e2f3a4b5c6
Revises: c3d4e5f6a7b8
Create Date: 2026-03-19 12:00:00.000000
"""
from alembic import op

revision = 'd1e2f3a4b5c6'
down_revision = 'c3d4e5f6a7b8'

def upgrade():
    # Eliminar el índice único global
    op.drop_index('ix_products_barcode', table_name='products')
    # Crear índice único compuesto por tenant
    op.create_index(
        'ix_products_tenant_barcode',
        'products',
        ['tenant_id', 'barcode'],
        unique=True
    )

def downgrade():
    op.drop_index('ix_products_tenant_barcode', table_name='products')
    op.create_index('ix_products_barcode', 'products', ['barcode'], unique=True)