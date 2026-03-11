"""fix platform admin and owner name

Revision ID: a1f36567e99a
Revises: 16e2cdcfea3f
Create Date: 2026-03-11 09:30:54.338096

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a1f36567e99a'
down_revision: Union[str, Sequence[str], None] = '16e2cdcfea3f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Fix business_type enum rename
    op.execute("CREATE TYPE businesstype AS ENUM ('STORE', 'FOOD', 'RESTAURANT')")
    op.execute("""
        ALTER TABLE tenants
        ALTER COLUMN business_type TYPE businesstype
        USING business_type::text::businesstype
    """)
    op.execute("DROP TYPE business_type_enum")

    op.alter_column('tenants', 'active',
               existing_type=sa.BOOLEAN(),
               nullable=True,
               existing_server_default=sa.text('false'))
    op.alter_column('tenants', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('now()'))


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('tenants', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('now()'))
    op.alter_column('tenants', 'active',
               existing_type=sa.BOOLEAN(),
               nullable=False,
               existing_server_default=sa.text('false'))

    # Revert business_type enum rename
    op.execute("CREATE TYPE business_type_enum AS ENUM ('STORE', 'FOOD', 'RESTAURANT')")
    op.execute("""
        ALTER TABLE tenants
        ALTER COLUMN business_type TYPE business_type_enum
        USING business_type::text::business_type_enum
    """)
    op.execute("DROP TYPE businesstype")