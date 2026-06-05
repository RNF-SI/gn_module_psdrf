"""create pr_psdrf_staging.t_dendro3_sync_log

Journal de synchronisation dendro3 : trace, par placette synchronisée, quel
appareil (device) et quel utilisateur (id_role) ont saisi, et quand (synced_at).
Alimente la traçabilité « 1 mobile = 1 placette » et la route d'état des
placettes (GET /psdrf/dispositif-placettes-state/<id_dispositif>).

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-05

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None

SCHEMA_STAGING = "pr_psdrf_staging"


def upgrade():
    # Le schéma pr_psdrf_staging est normalement créé hors Alembic par
    # create_pr_psdrf_staging_schema.sql. Garde-fou pour rendre cette migration
    # autonome : la table de log n'a aucune FK vers les tables miroir staging.
    op.execute("CREATE SCHEMA IF NOT EXISTS " + SCHEMA_STAGING)
    op.create_table(
        "t_dendro3_sync_log",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_dispositif", sa.Integer(), nullable=True),
        sa.Column("id_placette", sa.Integer(), nullable=True),
        sa.Column("device", sa.Text(), nullable=True),
        sa.Column("id_role", sa.Integer(), nullable=True),
        sa.Column("synced_at", sa.DateTime(), nullable=True),
        schema=SCHEMA_STAGING,
    )
    # Index pour la route d'état des placettes (dernier log par placette).
    op.create_index(
        "ix_dendro3_sync_log_disp_placette",
        "t_dendro3_sync_log",
        ["id_dispositif", "id_placette"],
        schema=SCHEMA_STAGING,
    )


def downgrade():
    op.drop_index(
        "ix_dendro3_sync_log_disp_placette",
        table_name="t_dendro3_sync_log",
        schema=SCHEMA_STAGING,
    )
    op.drop_table("t_dendro3_sync_log", schema=SCHEMA_STAGING)
