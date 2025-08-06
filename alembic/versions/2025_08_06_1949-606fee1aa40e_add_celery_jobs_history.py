"""add celery jobs history

Revision ID: 606fee1aa40e
Revises: 57323af4b301
Create Date: 2025-08-06 19:49:20.868030

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "606fee1aa40e"
down_revision = "57323af4b301"
branch_labels = None
depends_on = None


def upgrade() -> None:
    add_non_nullable_column(
        "medias", sa.Column("celery_jobs", sa.ARRAY(sa.String())), "{}"
    )
    op.alter_column("medias", "job_id", existing_type=sa.UUID(), nullable=True)
    op.add_column(
        "medias",
        sa.Column(
            "next_run",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
    )
    op.drop_column("medias", "next_try")


def downgrade() -> None:
    op.drop_column("medias", "celery_jobs")
    op.execute("update medias set job_id = gen_random_uuid() where job_id is null")
    op.alter_column("medias", "job_id", existing_type=sa.UUID(), nullable=False)
    op.add_column(
        "medias",
        sa.Column(
            "next_try",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.drop_column("medias", "next_run")


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
