"""replace userrole with tenанtrole in user_tenants

Revision ID: e2f3a4b5c6d7
Revises: d1e2f3a4b5c6
Create Date: 2026-03-19 13:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'e2f3a4b5c6d7'
down_revision = 'd1e2f3a4b5c6'

def upgrade():
    # Crear el nuevo enum solo con roles de tenant
    tenant_role_enum = sa.Enum('OWNER', 'ADMIN', 'STAFF', name='tenantrole')
    tenant_role_enum.create(op.get_bind(), checkfirst=True)

    # Cambiar la columna al nuevo tipo
    op.alter_column(
        'user_tenants',
        'role',
        type_=tenant_role_enum,
        existing_type=sa.Enum('PLATFORM_ADMIN', 'OWNER', 'ADMIN', 'STAFF', name='userrole'),
        postgresql_using="role::text::tenantrole"
    )

    # Eliminar el enum viejo (solo si no lo usa nadie más)
    # IMPORTANTE: userrole sigue usándose en la lógica de la app pero NO en ninguna
    # tabla de la DB — el JWT y los guards manejan UserRole en memoria.
    # Si PostgreSQL se queja de dependencias, omitir este drop.
    op.execute("DROP TYPE IF EXISTS userrole")

def downgrade():
    userrole_enum = sa.Enum('PLATFORM_ADMIN', 'OWNER', 'ADMIN', 'STAFF', name='userrole')
    userrole_enum.create(op.get_bind(), checkfirst=True)

    op.alter_column(
        'user_tenants',
        'role',
        type_=userrole_enum,
        existing_type=sa.Enum('OWNER', 'ADMIN', 'STAFF', name='tenantrole'),
        postgresql_using="role::text::userrole"
    )

    op.execute("DROP TYPE IF EXISTS tenantrole")