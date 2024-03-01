"""Migration pour la synchronicite (created_by, created_on)

Revision ID: 2115ba146beb
Revises: df4e089bad97
Create Date: 2024-03-01 10:30:38.199569

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2115ba146beb'
down_revision = 'df4e089bad97'
branch_labels = None
depends_on = None

schema = 'pr_psdrf'

def upgrade():
    # List of table names to add columns to
    tables = ["t_reperes", "cor_cycles_placettes", "t_arbres", "t_arbres_mesures", 
              "t_regenerations", "t_bm_sup_30", "t_bm_sup_30_mesures", 
              "t_transects"]
    
    for table_name in tables:
        op.add_column(table_name, sa.Column('created_by', sa.String(), nullable=True), schema=schema)
        op.add_column(table_name, sa.Column('created_on', sa.String(), nullable=True), schema=schema)
        op.add_column(table_name, sa.Column('created_at', sa.DateTime(), nullable=True), schema=schema)
        op.add_column(table_name, sa.Column('updated_by', sa.String(), nullable=True), schema=schema)
        op.add_column(table_name, sa.Column('updated_on', sa.String(), nullable=True), schema=schema)
        op.add_column(table_name, sa.Column('updated_at', sa.DateTime(), nullable=True), schema=schema)

def downgrade():
    # List of table names to remove columns from
    tables = ["t_reperes", "cor_cycles_placettes", "t_arbres", "t_arbres_mesures", 
              "t_regenerations", "t_bm_sup_30", "t_bm_sup_30_mesures", 
              "t_transects"]
    
    for table_name in tables:
        op.drop_column(table_name, 'created_by', schema=schema)
        op.drop_column(table_name, 'created_on', schema=schema)
        op.drop_column(table_name, 'created_at', schema=schema)
        op.drop_column(table_name, 'updated_by', schema=schema)
        op.drop_column(table_name, 'updated_on', schema=schema)
        op.drop_column(table_name, 'updated_at', schema=schema)
