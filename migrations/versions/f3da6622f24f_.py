"""empty message

Revision ID: f3da6622f24f
Revises: 
Create Date: 2022-04-12 17:40:52.316485

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f3da6622f24f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('country',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('person',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('show',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('show_type', sa.String(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('date_added', sa.DateTime(), nullable=True),
    sa.Column('release_year', sa.Integer(), nullable=True),
    sa.Column('rating', sa.String(), nullable=True),
    sa.Column('duration', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('show')
    op.drop_table('person')
    op.drop_table('country')
    op.drop_table('category')
    # ### end Alembic commands ###
