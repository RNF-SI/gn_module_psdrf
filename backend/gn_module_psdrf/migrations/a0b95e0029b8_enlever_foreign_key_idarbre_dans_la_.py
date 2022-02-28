"""Enlever foreign key idarbre dans la table bmsusp30

Revision ID: a0b95e0029b8
Revises: e04a349457e4
Create Date: 2022-02-28 10:03:58.157371

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a0b95e0029b8'
down_revision = 'e04a349457e4'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('fk_t_bm_sup_30_t_arbres', "t_bm_sup_30", type_='foreignkey', schema='pr_psdrf')
    pass


def downgrade():
    op.create_foreign_key('fk_t_bm_sup_30_t_arbres', "t_bm_sup_30", 't_arbres', ['id_arbre'], ['id_arbre'],  schema='pr_psdrf')
    pass
