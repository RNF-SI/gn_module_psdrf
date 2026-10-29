"""Staging : renseigner l'annee des releves Dendro3 depuis date_releve

Dendro3 ne saisit pas l'annee d'un releve (le champ est desactive dans
l'appli, seule la date de releve est obligatoire). Les associations
cycle/placette envoyees en staging avaient donc `annee` NULL : la fiche
dispositif ne les comptait pas comme relevees (colonne staging a « — »), et
l'export Excel staging sortait avec une Annee vide (#68).

Le merge Dendro3 -> staging deduit desormais l'annee de date_releve ; cette
migration rattrape les lignes deja recues. La production n'est pas touchee :
elle n'est alimentee que par l'import Excel, qui exige l'annee.

Downgrade sans effet : on ne sait plus distinguer les annees deduites.

Revision ID: e7a7dcc4eb7f
Revises: b7c2d5e91a04
Create Date: 2026-10-29 10:00:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'e7a7dcc4eb7f'
down_revision = 'b7c2d5e91a04'
branch_labels = None
depends_on = None


def upgrade():
    # Le schema staging est cree hors Alembic : ne rien faire s'il est absent.
    op.execute("""
        DO $$
        BEGIN
            IF to_regclass('pr_psdrf_staging.cor_cycles_placettes') IS NOT NULL THEN
                UPDATE pr_psdrf_staging.cor_cycles_placettes
                   SET annee = extract(year FROM date_releve)::int
                 WHERE annee IS NULL
                   AND date_releve IS NOT NULL;
            END IF;
        END
        $$;
    """)


def downgrade():
    pass
