"""empty message

Revision ID: bc5603c98ce1
Revises: 393a81c5368c
Create Date: 2019-09-14 13:30:10.735363

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bc5603c98ce1'
down_revision = '393a81c5368c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('teacher', sa.Column('doctorate', sa.String(length=64), nullable=True))
    op.add_column('teacher', sa.Column('master', sa.String(length=64), nullable=True))
    op.add_column('teacher', sa.Column('practices', sa.String(length=64), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('teacher', 'practices')
    op.drop_column('teacher', 'master')
    op.drop_column('teacher', 'doctorate')
    # ### end Alembic commands ###
