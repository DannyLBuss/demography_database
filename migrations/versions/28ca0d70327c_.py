"""empty message

Revision ID: 28ca0d70327c
Revises: 2b69dec6f1b0
Create Date: 2015-12-16 13:36:45.820124

"""

# revision identifiers, used by Alembic.
revision = '28ca0d70327c'
down_revision = '2b69dec6f1b0'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    pass
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('stage_class_info_bussys')
    op.drop_index('ix_bussys_vector_str', 'bussys')
    op.drop_table('bussys')
    op.drop_index('ix_smalls_small_name', 'smalls')
    op.drop_table('smalls')
    op.drop_index('ix_vector_availabilities_availability_name', 'vector_availabilities')
    op.drop_table('vector_availabilities')
    op.drop_index('ix_stage_class_infos_info_code', 'stage_class_infos')
    op.drop_table('stage_class_infos')
    ### end Alembic commands ###
