"""back_employee_management

Revision ID: 964d24aa9d64
Revises:
Create Date: 2024-08-12 14:08:37.868666

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '964d24aa9d64'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### adjusted by Ameni ###
    op.create_table('JWT_Blacklist',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('token', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_JWT_Blacklist_id'), 'JWT_Blacklist', ['id'], unique=True)
    op.create_table('company',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('last_employee_number', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_company_id'), 'company', ['id'], unique=False)
    op.create_table('errors',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('orig', sa.String(), nullable=False),
    sa.Column('params', sa.String(), nullable=False),
    sa.Column('statement', sa.String(), nullable=False),
    sa.Column('created_on', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('employees',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('firstname', sa.String(), nullable=False),
    sa.Column('lastname', sa.String(), nullable=False),
    sa.Column('number', sa.Integer(), nullable=False),
    sa.Column('phone_number', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('cnss_number', sa.String(), nullable=True),
    sa.Column('birth_date', sa.DateTime(), nullable=True),
    sa.Column('gender', sa.Enum('male', 'female', name='gender'), nullable=False),
    sa.Column('status', sa.Enum('active', 'inactive', name='accountstatus'), nullable=False),
    sa.Column('contract_type', sa.Enum('cdi', 'cdd', 'sivp', 'apprenti', name='contracttype'), nullable=False),
    sa.Column('password', sa.String(), nullable=True),
    sa.Column('company_id', sa.Integer(), nullable=False),
    sa.CheckConstraint("(contract_type IN ('cdi', 'cdd') AND cnss_number IS NOT NULL AND cnss_number ~ '^\\d{8}-\\d{2}$') OR (contract_type IN ('apprenti', 'sivp') AND (cnss_number IS NULL OR cnss_number ~ '^\\d{8}-\\d{2}$'))", name='check_contract_type_and_cnss_number'),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('cnss_number', name='unique_cnss_number'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('email', name='unique_email_constraint'),
    sa.UniqueConstraint('number')
    )
    op.create_index(op.f('ix_employees_id'), 'employees', ['id'], unique=False)
    op.create_table('account_activation',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('token', sa.String(), nullable=False),
    sa.Column('status', sa.Enum('used', 'pending', name='tokenstatus'), nullable=False),
    sa.Column('created_on', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('employee_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_account_activation_id'), 'account_activation', ['id'], unique=False)
    op.create_table('change_password',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('token', sa.String(), nullable=False),
    sa.Column('status', sa.Enum('used', 'pending', name='tokenstatus'), nullable=False),
    sa.Column('created_on', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('employee_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_change_password_id'), 'change_password', ['id'], unique=False)
    op.create_table('employee_role',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('employee_id', sa.Integer(), nullable=False),
    sa.Column('role', sa.Enum('admin', 'vendor', 'inventory_manager', 'super_user', name='role'), nullable=False),
    sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('employee_id'),
    sa.UniqueConstraint('employee_id', 'role', name='uix_employee_role')
    )
    op.create_index(op.f('ix_employee_role_id'), 'employee_role', ['id'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_employee_role_id'), table_name='employee_role')
    op.drop_table('employee_role')
    op.drop_index(op.f('ix_change_password_id'), table_name='change_password')
    op.drop_table('change_password')
    op.drop_index(op.f('ix_account_activation_id'), table_name='account_activation')
    op.drop_table('account_activation')
    op.drop_index(op.f('ix_employees_id'), table_name='employees')
    op.drop_table('employees')
    op.drop_table('errors')
    op.drop_index(op.f('ix_company_id'), table_name='company')
    op.drop_table('company')
    op.drop_index(op.f('ix_JWT_Blacklist_id'), table_name='JWT_Blacklist')
    op.drop_table('JWT_Blacklist')
    # ### end Alembic commands ###
