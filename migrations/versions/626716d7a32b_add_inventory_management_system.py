"""Add inventory management system

Revision ID: 626716d7a32b
Revises: 17ad8d3b052c
Create Date: 2025-09-21 18:35:11.573150

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '626716d7a32b'
down_revision = '17ad8d3b052c'
branch_labels = None
depends_on = None


def upgrade():
    # Create inventory_locations table
    op.create_table('inventory_locations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('manager_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['manager_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    
    # Create staff_location_assignments table
    op.create_table('staff_location_assignments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('staff_id', sa.Integer(), nullable=False),
        sa.Column('location_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=True),
        sa.Column('permissions', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('assigned_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['location_id'], ['inventory_locations.id'], ),
        sa.ForeignKeyConstraint(['staff_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create inventory_items table
    op.create_table('inventory_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('jewelry_item_id', sa.Integer(), nullable=True),
        sa.Column('automobile_id', sa.Integer(), nullable=True),
        sa.Column('location_id', sa.Integer(), nullable=False),
        sa.Column('current_stock', sa.Integer(), nullable=False),
        sa.Column('reserved_stock', sa.Integer(), nullable=True),
        sa.Column('available_stock', sa.Integer(), nullable=True),
        sa.Column('reorder_point', sa.Integer(), nullable=True),
        sa.Column('max_stock_level', sa.Integer(), nullable=True),
        sa.Column('unit_cost', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('total_value', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('last_counted', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['automobile_id'], ['vehicles.id'], ),
        sa.ForeignKeyConstraint(['jewelry_item_id'], ['jewelry_items.id'], ),
        sa.ForeignKeyConstraint(['location_id'], ['inventory_locations.id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create stock_movements table
    op.create_table('stock_movements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('inventory_item_id', sa.Integer(), nullable=False),
        sa.Column('location_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('movement_type', sa.String(length=20), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('reference_type', sa.String(length=50), nullable=True),
        sa.Column('reference_id', sa.String(length=50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('unit_cost', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('stock_before', sa.Integer(), nullable=True),
        sa.Column('stock_after', sa.Integer(), nullable=True),
        sa.Column('movement_date', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['inventory_item_id'], ['inventory_items.id'], ),
        sa.ForeignKeyConstraint(['location_id'], ['inventory_locations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create low_stock_alerts table
    op.create_table('low_stock_alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('inventory_item_id', sa.Integer(), nullable=False),
        sa.Column('alert_level', sa.String(length=20), nullable=True),
        sa.Column('current_stock', sa.Integer(), nullable=False),
        sa.Column('reorder_point', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('acknowledged_by_id', sa.Integer(), nullable=True),
        sa.Column('acknowledged_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['acknowledged_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['inventory_item_id'], ['inventory_items.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create inventory_audits table
    op.create_table('inventory_audits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('location_id', sa.Integer(), nullable=False),
        sa.Column('auditor_id', sa.Integer(), nullable=False),
        sa.Column('audit_type', sa.String(length=20), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('scheduled_date', sa.Date(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('total_items_counted', sa.Integer(), nullable=True),
        sa.Column('discrepancies_found', sa.Integer(), nullable=True),
        sa.Column('total_value_difference', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['auditor_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['location_id'], ['inventory_locations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create inventory_audit_items table
    op.create_table('inventory_audit_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('audit_id', sa.Integer(), nullable=False),
        sa.Column('inventory_item_id', sa.Integer(), nullable=False),
        sa.Column('system_count', sa.Integer(), nullable=False),
        sa.Column('physical_count', sa.Integer(), nullable=False),
        sa.Column('variance', sa.Integer(), nullable=False),
        sa.Column('unit_cost', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('value_variance', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('counted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['audit_id'], ['inventory_audits.id'], ),
        sa.ForeignKeyConstraint(['inventory_item_id'], ['inventory_items.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Update existing product tables to support low stock threshold of 2
    op.alter_column('products', 'low_stock_threshold',
                   existing_type=sa.INTEGER(),
                   type_=sa.Integer(),
                   existing_nullable=True,
                   server_default='2')
    
    # Add low_stock_threshold to jewelry_items if it doesn't exist
    try:
        op.add_column('jewelry_items', sa.Column('low_stock_threshold', sa.Integer(), default=2))
    except:
        # Column might already exist, ignore error
        pass


def downgrade():
    # Drop tables in reverse order
    op.drop_table('inventory_audit_items')
    op.drop_table('inventory_audits')
    op.drop_table('low_stock_alerts')
    op.drop_table('stock_movements')
    op.drop_table('inventory_items')
    op.drop_table('staff_location_assignments')
    op.drop_table('inventory_locations')
    
    # Revert product table changes
    op.alter_column('products', 'low_stock_threshold',
                   existing_type=sa.Integer(),
                   type_=sa.INTEGER(),
                   existing_nullable=True,
                   server_default='5')
    
    # Remove column from jewelry_items if it was added
    try:
        op.drop_column('jewelry_items', 'low_stock_threshold')
    except:
        # Column might not exist, ignore error
        pass
