"""add access policy table

Revision ID: 8f492d45d2a7
Revises: edc43a5c39c4
Create Date: 2019-09-01 17:12:41.135413

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8f492d45d2a7'
down_revision = 'edc43a5c39c4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('access_policy',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.Column('note', sa.String(length=250), nullable=True),
    sa.Column('denied_before', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_access_policy_denied_before'), 'access_policy', ['denied_before'], unique=False)
    op.create_index(op.f('ix_access_policy_role_id'), 'access_policy', ['role_id'], unique=False)
    op.create_index(op.f('ix_access_policy_user_id'), 'access_policy', ['user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_access_policy_user_id'), table_name='access_policy')
    op.drop_index(op.f('ix_access_policy_role_id'), table_name='access_policy')
    op.drop_index(op.f('ix_access_policy_denied_before'), table_name='access_policy')
    op.drop_table('access_policy')
    # ### end Alembic commands ###
