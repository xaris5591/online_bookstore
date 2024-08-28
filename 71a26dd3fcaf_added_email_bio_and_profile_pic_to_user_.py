"""Added email, bio, and profile_pic to User model

Revision ID: 71a26dd3fcaf
Revises: 
Create Date: 2024-08-27 19:28:26.652926

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '71a26dd3fcaf'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email', sa.String(length=150), nullable=False))
        batch_op.add_column(sa.Column('bio', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('profile_pic', sa.String(length=150), nullable=True))
        batch_op.create_unique_constraint('uq_user_email', ['email'])




    # ### end Alembic commands ###


def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint('uq_user_email', type_='unique')
        batch_op.drop_column('profile_pic')
        batch_op.drop_column('bio')
        batch_op.drop_column('email')

    # ### end Alembic commands ###
