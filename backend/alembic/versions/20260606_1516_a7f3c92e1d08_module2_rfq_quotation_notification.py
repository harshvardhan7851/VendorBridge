"""module2_rfq_quotation_notification

Revision ID: a7f3c92e1d08
Revises: 1215389543b4
Create Date: 2026-06-06 15:16:00.000000+00:00

Module 2 tables:
  - rfqs
  - rfq_line_items
  - rfq_vendor_assignments
  - rfq_attachments
  - quotations
  - quotation_line_items
  - notifications

Foreign keys reference Module 1 tables: users, vendors.
No Module 1 tables are modified.

Strategy for ENUM types with asyncpg:
  - We use raw SQL via op.execute() for both CREATE and DROP.
  - Within create_table(), we reference the already-created enum type using
    postgresql.ENUM(..., create_type=False) which suppresses SQLAlchemy's
    automatic CREATE TYPE DDL.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'a7f3c92e1d08'
down_revision: Union[str, None] = '1215389543b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# ---------------------------------------------------------------------------
# Pre-built ENUM type references (create_type=False → no DDL auto-emitted)
# ---------------------------------------------------------------------------
rfqstatus_type = postgresql.ENUM(
    'DRAFT', 'SENT', 'UNDER_REVIEW', 'CLOSED', 'CANCELLED',
    name='rfqstatus',
    create_type=False,
)

assignmentstatus_type = postgresql.ENUM(
    'INVITED', 'VIEWED', 'SUBMITTED', 'DECLINED',
    name='assignmentstatus',
    create_type=False,
)

quotationstatus_type = postgresql.ENUM(
    'DRAFT', 'SUBMITTED', 'WITHDRAWN', 'SELECTED', 'REJECTED',
    name='quotationstatus',
    create_type=False,
)

notificationtype_type = postgresql.ENUM(
    'RFQ_INVITE', 'QUOTATION_RECEIVED', 'WINNER_SELECTED', 'APPROVAL_REQUIRED',
    name='notificationtype',
    create_type=False,
)


def upgrade() -> None:
    # ------------------------------------------------------------------
    # Step 1: Create ENUM types via raw SQL (idempotent with DO blocks)
    # ------------------------------------------------------------------
    op.execute(sa.text(
        "DO $$ BEGIN "
        "    CREATE TYPE rfqstatus AS ENUM ('DRAFT', 'SENT', 'UNDER_REVIEW', 'CLOSED', 'CANCELLED'); "
        "EXCEPTION WHEN duplicate_object THEN NULL; "
        "END $$;"
    ))
    op.execute(sa.text(
        "DO $$ BEGIN "
        "    CREATE TYPE assignmentstatus AS ENUM ('INVITED', 'VIEWED', 'SUBMITTED', 'DECLINED'); "
        "EXCEPTION WHEN duplicate_object THEN NULL; "
        "END $$;"
    ))
    op.execute(sa.text(
        "DO $$ BEGIN "
        "    CREATE TYPE quotationstatus AS ENUM ('DRAFT', 'SUBMITTED', 'WITHDRAWN', 'SELECTED', 'REJECTED'); "
        "EXCEPTION WHEN duplicate_object THEN NULL; "
        "END $$;"
    ))
    op.execute(sa.text(
        "DO $$ BEGIN "
        "    CREATE TYPE notificationtype AS ENUM ('RFQ_INVITE', 'QUOTATION_RECEIVED', 'WINNER_SELECTED', 'APPROVAL_REQUIRED'); "
        "EXCEPTION WHEN duplicate_object THEN NULL; "
        "END $$;"
    ))

    # ------------------------------------------------------------------
    # Step 2: Table: rfqs
    # ------------------------------------------------------------------
    op.create_table(
        'rfqs',
        sa.Column('rfq_number',   sa.String(length=100),           nullable=False),
        sa.Column('title',        sa.String(length=255),           nullable=False),
        sa.Column('description',  sa.Text(),                       nullable=True),
        sa.Column('status',       rfqstatus_type,                  nullable=False),
        sa.Column('deadline',     sa.DateTime(timezone=True),      nullable=True),
        sa.Column('created_by',   sa.UUID(),                       nullable=True),
        # TimestampMixin columns
        sa.Column('id',           sa.UUID(),                       nullable=False),
        sa.Column('created_at',   sa.DateTime(timezone=True),
                  server_default=sa.text('now()'),                 nullable=False),
        sa.Column('updated_at',   sa.DateTime(timezone=True),
                  server_default=sa.text('now()'),                 nullable=False),
        sa.Column('updated_by',   sa.UUID(),                       nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'],      ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('rfq_number'),
    )
    op.create_index(op.f('ix_rfqs_id'),         'rfqs', ['id'],         unique=False)
    op.create_index(op.f('ix_rfqs_rfq_number'), 'rfqs', ['rfq_number'], unique=True)
    op.create_index(op.f('ix_rfqs_status'),     'rfqs', ['status'],     unique=False)
    op.create_index(op.f('ix_rfqs_created_by'), 'rfqs', ['created_by'], unique=False)

    # ------------------------------------------------------------------
    # Step 3: Table: rfq_line_items
    # ------------------------------------------------------------------
    op.create_table(
        'rfq_line_items',
        sa.Column('rfq_id',       sa.UUID(),                       nullable=False),
        sa.Column('product_name', sa.String(length=255),           nullable=False),
        sa.Column('description',  sa.Text(),                       nullable=True),
        sa.Column('quantity',     sa.DECIMAL(precision=12, scale=2), nullable=False),
        sa.Column('unit',         sa.String(length=50),            nullable=True),
        # TimestampMixin columns
        sa.Column('id',           sa.UUID(),                       nullable=False),
        sa.Column('created_at',   sa.DateTime(timezone=True),
                  server_default=sa.text('now()'),                 nullable=False),
        sa.Column('updated_at',   sa.DateTime(timezone=True),
                  server_default=sa.text('now()'),                 nullable=False),
        sa.Column('updated_by',   sa.UUID(),                       nullable=True),
        sa.ForeignKeyConstraint(['rfq_id'], ['rfqs.id'],           ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_rfq_line_items_id'),     'rfq_line_items', ['id'],     unique=False)
    op.create_index(op.f('ix_rfq_line_items_rfq_id'), 'rfq_line_items', ['rfq_id'], unique=False)

    # ------------------------------------------------------------------
    # Step 4: Table: rfq_vendor_assignments
    # ------------------------------------------------------------------
    op.create_table(
        'rfq_vendor_assignments',
        sa.Column('id',         sa.UUID(),                         nullable=False),
        sa.Column('rfq_id',     sa.UUID(),                         nullable=False),
        sa.Column('vendor_id',  sa.UUID(),                         nullable=False),
        sa.Column('status',     assignmentstatus_type,             nullable=False),
        sa.Column('invited_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'),                 nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'),                 nullable=False),
        sa.ForeignKeyConstraint(['rfq_id'],    ['rfqs.id'],        ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'],     ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('rfq_id', 'vendor_id', name='uq_rfq_vendor'),
    )
    op.create_index(op.f('ix_rfq_vendor_assignments_id'),        'rfq_vendor_assignments', ['id'],        unique=False)
    op.create_index(op.f('ix_rfq_vendor_assignments_rfq_id'),    'rfq_vendor_assignments', ['rfq_id'],    unique=False)
    op.create_index(op.f('ix_rfq_vendor_assignments_vendor_id'), 'rfq_vendor_assignments', ['vendor_id'], unique=False)
    op.create_index(op.f('ix_rfq_vendor_assignments_status'),    'rfq_vendor_assignments', ['status'],    unique=False)

    # ------------------------------------------------------------------
    # Step 5: Table: rfq_attachments
    # ------------------------------------------------------------------
    op.create_table(
        'rfq_attachments',
        sa.Column('id',          sa.UUID(),                        nullable=False),
        sa.Column('rfq_id',      sa.UUID(),                        nullable=False),
        sa.Column('uploaded_by', sa.UUID(),                        nullable=True),
        sa.Column('filename',    sa.String(length=255),            nullable=False),
        sa.Column('file_path',   sa.String(length=500),            nullable=False),
        sa.Column('file_size',   sa.BigInteger(),                  nullable=True),
        sa.Column('uploaded_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'),                 nullable=False),
        sa.ForeignKeyConstraint(['rfq_id'],      ['rfqs.id'],      ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'],     ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_rfq_attachments_id'),          'rfq_attachments', ['id'],          unique=False)
    op.create_index(op.f('ix_rfq_attachments_rfq_id'),      'rfq_attachments', ['rfq_id'],      unique=False)
    op.create_index(op.f('ix_rfq_attachments_uploaded_by'), 'rfq_attachments', ['uploaded_by'], unique=False)

    # ------------------------------------------------------------------
    # Step 6: Table: quotations
    # ------------------------------------------------------------------
    op.create_table(
        'quotations',
        sa.Column('quotation_number', sa.String(length=100),       nullable=False),
        sa.Column('rfq_id',           sa.UUID(),                   nullable=False),
        sa.Column('vendor_id',        sa.UUID(),                   nullable=False),
        sa.Column('status',           quotationstatus_type,        nullable=False),
        sa.Column('validity_date',    sa.Date(),                   nullable=True),
        sa.Column('delivery_days',    sa.Integer(),                nullable=True),
        sa.Column('notes',            sa.Text(),                   nullable=True),
        sa.Column('total_amount',     sa.DECIMAL(precision=18, scale=2), nullable=True),
        sa.Column('submitted_at',     sa.DateTime(timezone=True),  nullable=True),
        # TimestampMixin columns
        sa.Column('id',               sa.UUID(),                   nullable=False),
        sa.Column('created_at',       sa.DateTime(timezone=True),
                  server_default=sa.text('now()'),                 nullable=False),
        sa.Column('updated_at',       sa.DateTime(timezone=True),
                  server_default=sa.text('now()'),                 nullable=False),
        sa.Column('updated_by',       sa.UUID(),                   nullable=True),
        sa.ForeignKeyConstraint(['rfq_id'],    ['rfqs.id'],        ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'],     ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('quotation_number'),
    )
    op.create_index(op.f('ix_quotations_id'),               'quotations', ['id'],               unique=False)
    op.create_index(op.f('ix_quotations_quotation_number'), 'quotations', ['quotation_number'], unique=True)
    op.create_index(op.f('ix_quotations_rfq_id'),           'quotations', ['rfq_id'],           unique=False)
    op.create_index(op.f('ix_quotations_vendor_id'),        'quotations', ['vendor_id'],        unique=False)
    op.create_index(op.f('ix_quotations_status'),           'quotations', ['status'],           unique=False)

    # ------------------------------------------------------------------
    # Step 7: Table: quotation_line_items
    # ------------------------------------------------------------------
    op.create_table(
        'quotation_line_items',
        sa.Column('id',               sa.UUID(),                   nullable=False),
        sa.Column('quotation_id',     sa.UUID(),                   nullable=False),
        sa.Column('rfq_line_item_id', sa.UUID(),                   nullable=True),
        sa.Column('unit_price',       sa.DECIMAL(precision=18, scale=2), nullable=False),
        sa.Column('quantity',         sa.DECIMAL(precision=12, scale=2), nullable=False),
        sa.Column('total_price',      sa.DECIMAL(precision=18, scale=2), nullable=True),
        sa.Column('notes',            sa.Text(),                   nullable=True),
        sa.Column('created_at',       sa.DateTime(timezone=True),
                  server_default=sa.text('now()'),                 nullable=False),
        sa.ForeignKeyConstraint(['quotation_id'],     ['quotations.id'],     ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['rfq_line_item_id'], ['rfq_line_items.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_quotation_line_items_id'),               'quotation_line_items', ['id'],               unique=False)
    op.create_index(op.f('ix_quotation_line_items_quotation_id'),     'quotation_line_items', ['quotation_id'],     unique=False)
    op.create_index(op.f('ix_quotation_line_items_rfq_line_item_id'), 'quotation_line_items', ['rfq_line_item_id'], unique=False)

    # ------------------------------------------------------------------
    # Step 8: Table: notifications
    # ------------------------------------------------------------------
    op.create_table(
        'notifications',
        sa.Column('id',          sa.UUID(),                        nullable=False),
        sa.Column('user_id',     sa.UUID(),                        nullable=False),
        sa.Column('type',        notificationtype_type,            nullable=False),
        sa.Column('message',     sa.Text(),                        nullable=False),
        sa.Column('is_read',     sa.Boolean(),                     nullable=False),
        sa.Column('entity_type', sa.String(length=50),             nullable=True),
        sa.Column('entity_id',   sa.UUID(),                        nullable=True),
        sa.Column('created_at',  sa.DateTime(timezone=True),
                  server_default=sa.text('now()'),                 nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'],         ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_notifications_id'),      'notifications', ['id'],      unique=False)
    op.create_index(op.f('ix_notifications_user_id'), 'notifications', ['user_id'], unique=False)
    op.create_index(op.f('ix_notifications_type'),    'notifications', ['type'],    unique=False)


def downgrade() -> None:
    # Drop tables in reverse dependency order
    op.drop_index(op.f('ix_notifications_type'),    table_name='notifications')
    op.drop_index(op.f('ix_notifications_user_id'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_id'),      table_name='notifications')
    op.drop_table('notifications')

    op.drop_index(op.f('ix_quotation_line_items_rfq_line_item_id'), table_name='quotation_line_items')
    op.drop_index(op.f('ix_quotation_line_items_quotation_id'),     table_name='quotation_line_items')
    op.drop_index(op.f('ix_quotation_line_items_id'),               table_name='quotation_line_items')
    op.drop_table('quotation_line_items')

    op.drop_index(op.f('ix_quotations_status'),           table_name='quotations')
    op.drop_index(op.f('ix_quotations_vendor_id'),        table_name='quotations')
    op.drop_index(op.f('ix_quotations_rfq_id'),           table_name='quotations')
    op.drop_index(op.f('ix_quotations_quotation_number'), table_name='quotations')
    op.drop_index(op.f('ix_quotations_id'),               table_name='quotations')
    op.drop_table('quotations')

    op.drop_index(op.f('ix_rfq_attachments_uploaded_by'), table_name='rfq_attachments')
    op.drop_index(op.f('ix_rfq_attachments_rfq_id'),      table_name='rfq_attachments')
    op.drop_index(op.f('ix_rfq_attachments_id'),          table_name='rfq_attachments')
    op.drop_table('rfq_attachments')

    op.drop_index(op.f('ix_rfq_vendor_assignments_status'),    table_name='rfq_vendor_assignments')
    op.drop_index(op.f('ix_rfq_vendor_assignments_vendor_id'), table_name='rfq_vendor_assignments')
    op.drop_index(op.f('ix_rfq_vendor_assignments_rfq_id'),    table_name='rfq_vendor_assignments')
    op.drop_index(op.f('ix_rfq_vendor_assignments_id'),        table_name='rfq_vendor_assignments')
    op.drop_table('rfq_vendor_assignments')

    op.drop_index(op.f('ix_rfq_line_items_rfq_id'), table_name='rfq_line_items')
    op.drop_index(op.f('ix_rfq_line_items_id'),     table_name='rfq_line_items')
    op.drop_table('rfq_line_items')

    op.drop_index(op.f('ix_rfqs_created_by'), table_name='rfqs')
    op.drop_index(op.f('ix_rfqs_status'),     table_name='rfqs')
    op.drop_index(op.f('ix_rfqs_rfq_number'), table_name='rfqs')
    op.drop_index(op.f('ix_rfqs_id'),         table_name='rfqs')
    op.drop_table('rfqs')

    # Drop ENUM types after all referencing tables are gone
    op.execute(sa.text("DROP TYPE IF EXISTS notificationtype"))
    op.execute(sa.text("DROP TYPE IF EXISTS quotationstatus"))
    op.execute(sa.text("DROP TYPE IF EXISTS assignmentstatus"))
    op.execute(sa.text("DROP TYPE IF EXISTS rfqstatus"))
