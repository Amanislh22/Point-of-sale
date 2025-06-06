"""session_management_without_pricelist_and_programs

Revision ID: bdbc7e84b071
Revises: aa51a5fb038d
Create Date: 2024-07-25 11:06:48.244087

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bdbc7e84b071'
down_revision: Union[str, None] = '964d24aa9d64'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### adjusted by Ameni ###
    op.create_table('category',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('icon_name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('customer',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email', name='unique_email_constraint'),
    )
    op.create_index(op.f('ix_customer_id'), 'customer', ['id'], unique=False)
    op.create_table('product',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('unit_price', sa.Float(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('image_link', sa.String(), nullable=True),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_product_id'), 'product', ['id'], unique=False)
    op.create_table('session',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('opened_at', sa.DateTime(), nullable=False),
    sa.Column('closed_at', sa.DateTime(), nullable=True),
    sa.Column('employee_id', sa.Integer(), nullable=False),
    sa.Column('session_status', sa.Enum('open', 'closed', name='sessionstatus'), nullable=True),
    sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('order',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('number', sa.String(), nullable=False),
    sa.Column('created_on', sa.DateTime(), nullable=False),
    sa.Column('total_price', sa.Float(), nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=True),
    sa.Column('session_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['customer_id'], ['customer.id'], ),
    sa.ForeignKeyConstraint(['session_id'], ['session.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_id'), 'order', ['id'], unique=False)
    op.create_table('order_line',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('unit_price', sa.Float(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('total_price', sa.Float(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_unique_constraint(None, 'employee_role', ['employee_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'employee_role', type_='unique')
    op.drop_table('order_line')
    op.drop_index(op.f('ix_order_id'), table_name='order')
    op.drop_table('order')
    op.drop_table('session')
    op.drop_index(op.f('ix_product_id'), table_name='product')
    op.drop_table('product')
    op.drop_index(op.f('ix_customer_id'), table_name='customer')
    op.drop_table('customer')
    op.drop_table('category')
    # ### end Alembic commands ###
