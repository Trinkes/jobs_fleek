"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}



def add_non_nullable_column(
    table_name: str,
    column: sa.Column,
    default_value: str | None = None,
    default_value_expression: str | None = None,
):
    op.add_column(table_name, column)
    if default_value is not None:
        op.execute(f"UPDATE {table_name} SET {column.name} = '{default_value}'")
    if default_value_expression is not None:
        op.execute(
            f"UPDATE {table_name} SET {column.name} = ({default_value_expression})"
        )
    op.alter_column(table_name, column.name, nullable=False)
