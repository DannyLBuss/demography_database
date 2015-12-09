"""empty message

Revision ID: 24588efadc8e
Revises: 25cd9d8d4e43
Create Date: 2015-12-09 13:57:24.304089

"""

# revision identifiers, used by Alembic.
revision = '24588efadc8e'
down_revision = '25cd9d8d4e43'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    pass
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_index('species_ibfk_2', 'species', ['iucn_status_id'], unique=False)
    op.create_index('species_ibfk_1', 'species', ['esa_status_id'], unique=False)
    op.drop_column(u'source_types', 'database_id')
    op.create_index('ix_seasons_name', 'seasons', ['name'], unique=False)
    op.drop_index('ix_seasons_season_name', 'seasons')
    op.add_column(u'seasons', sa.Column('name', mysql.VARCHAR(length=64), nullable=True))
    op.drop_column(u'seasons', 'season_name')
    op.drop_index('ix_databases_database_name', 'databases')
    op.drop_table('databases')
    ### end Alembic commands ###
