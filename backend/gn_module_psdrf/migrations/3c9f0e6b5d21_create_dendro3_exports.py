"""Journal des exports Dendro3 : pr_psdrf_staging.t_dendro3_exports

Une ligne par export recu depuis l'appli (POST /export_dispositif_from_dendro3) :
date de reception et de fin, statut (en_cours / succes / echec) et message
d'erreur, compteurs crees/modifies/supprimes, placettes et cycles touches, et
appareil / utilisateur quand l'appli les envoie. Sert la page admin
(« dernieres remontees », #69) et la fiche dispositif (#70) : sans lui, rien
ne permettait de savoir si un export avait abouti.

Distinct de t_dendro3_sync_log (une ligne par placette, branche
feature/dendro3-sync-staging, non integree).

Revision ID: 3c9f0e6b5d21
Revises: e7a7dcc4eb7f
Create Date: 2026-10-29 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = '3c9f0e6b5d21'
down_revision = 'e7a7dcc4eb7f'
branch_labels = None
depends_on = None

SCHEMA_STAGING = 'pr_psdrf_staging'


def upgrade():
    # Le schema staging est normalement cree hors Alembic
    # (create_pr_psdrf_staging_schema.sql) ; la table n'a aucune FK vers lui.
    op.execute('CREATE SCHEMA IF NOT EXISTS ' + SCHEMA_STAGING)
    op.create_table(
        't_dendro3_exports',
        sa.Column('id_export', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('task_id', sa.Text(), nullable=False, unique=True),
        sa.Column('id_dispositif', sa.Integer(), nullable=True),
        sa.Column('recu_le', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('termine_le', sa.DateTime(), nullable=True),
        sa.Column('statut', sa.Text(), nullable=False, server_default='en_cours'),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('device', sa.Text(), nullable=True),
        sa.Column('id_role', sa.Integer(), nullable=True),
        sa.Column('compteurs', JSONB(), nullable=True),
        sa.Column('placettes', JSONB(), nullable=True),
        schema=SCHEMA_STAGING,
    )
    op.create_index(
        'ix_dendro3_exports_disp_recu',
        't_dendro3_exports',
        ['id_dispositif', 'recu_le'],
        schema=SCHEMA_STAGING,
    )


def downgrade():
    op.drop_index('ix_dendro3_exports_disp_recu', table_name='t_dendro3_exports', schema=SCHEMA_STAGING)
    op.drop_table('t_dendro3_exports', schema=SCHEMA_STAGING)
