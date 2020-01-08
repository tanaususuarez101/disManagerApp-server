"""empty message

Revision ID: 7a1e8462c648
Revises: 7b67b4edcbc0
Create Date: 2019-09-16 21:22:18.756824

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7a1e8462c648'
down_revision = '7b67b4edcbc0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('responsible_conflict',
    sa.Column('area_cod', sa.String(length=64), nullable=False),
    sa.Column('subject_cod', sa.String(length=64), nullable=False),
    sa.Column('teacher_dni', sa.String(length=64), nullable=False),
    sa.ForeignKeyConstraint(['subject_cod', 'area_cod'], ['subject.subject_cod', 'subject.area_cod'], ),
    sa.ForeignKeyConstraint(['teacher_dni'], ['teacher.dni'], ),
    sa.PrimaryKeyConstraint('area_cod', 'subject_cod', 'teacher_dni')
    )
    op.drop_table('responsibleConflict')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('responsibleConflict',
    sa.Column('area_cod', sa.VARCHAR(length=64), nullable=False),
    sa.Column('subject_cod', sa.VARCHAR(length=64), nullable=False),
    sa.Column('teacher_dni', sa.VARCHAR(length=64), nullable=False),
    sa.ForeignKeyConstraint(['subject_cod', 'area_cod'], ['subject.subject_cod', 'subject.area_cod'], ),
    sa.ForeignKeyConstraint(['teacher_dni'], ['teacher.dni'], ),
    sa.PrimaryKeyConstraint('area_cod', 'subject_cod', 'teacher_dni')
    )
    op.drop_table('responsible_conflict')
    # ### end Alembic commands ###