"""Indexer les cles etrangeres ON DELETE CASCADE de pr_psdrf

Postgres n'indexe pas automatiquement le cote *enfant* d'une cle etrangere.
Tant que ces colonnes n'ont pas d'index, chaque suppression d'une ligne parente
force un parcours sequentiel complet de la table enfant.

L'import d'un dispositif (`data_integration`) commence par
`DELETE FROM pr_psdrf.t_placettes WHERE id_dispositif = :id`. Pour un gros
dispositif (834 placettes, ~29 000 arbres), cela declenchait :
  - un seq scan de `t_placettes` (pas d'index sur `id_dispositif`) ;
  - puis, pour CHAQUE placette supprimee, un seq scan de `t_arbres`,
    `t_reperes`, `t_bm_sup_30`, `cor_cycles_placettes` ;
  - puis, pour CHAQUE arbre supprime en cascade, un seq scan de
    `t_arbres_mesures`.
Le cout depend du volume *total* des tables, tous dispositifs confondus : il a
donc grossi au fil des campagnes jusqu'a depasser le timeout gunicorn de 300 s
(constate en production le 2026-08-26 sur le dispositif 30 : `DELETE` toujours
actif apres 5 min, worker tue, import impossible).

Les index sont crees en CONCURRENTLY : la production continue de servir pendant
la creation, au prix d'une execution hors transaction (autocommit_block).

Revision ID: b7c2d5e91a04
Revises: a3f1c9e2b4d7
Create Date: 2026-08-26 15:30:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'b7c2d5e91a04'
down_revision = 'a3f1c9e2b4d7'
branch_labels = None
depends_on = None


# (nom de l'index, table, colonne) — toutes les FK ON DELETE CASCADE internes
# au schema qui n'etaient pas indexees cote enfant.
INDEXES = [
    # Chemin de suppression de l'import : t_placettes -> enfants -> petits-enfants
    ("idx_psdrf_t_placettes_id_dispositif", "t_placettes", "id_dispositif"),
    ("idx_psdrf_t_arbres_id_placette", "t_arbres", "id_placette"),
    ("idx_psdrf_t_arbres_mesures_id_arbre", "t_arbres_mesures", "id_arbre"),
    ("idx_psdrf_t_reperes_id_placette", "t_reperes", "id_placette"),
    ("idx_psdrf_t_bm_sup_30_id_placette", "t_bm_sup_30", "id_placette"),
    ("idx_psdrf_t_bm_sup_30_mesures_id_bm_sup_30", "t_bm_sup_30_mesures", "id_bm_sup_30"),
    ("idx_psdrf_cor_cycles_placettes_id_placette", "cor_cycles_placettes", "id_placette"),
    ("idx_psdrf_t_regenerations_id_cycle_placette", "t_regenerations", "id_cycle_placette"),
    ("idx_psdrf_t_transects_id_cycle_placette", "t_transects", "id_cycle_placette"),
    # Autres cascades du schema, moins volumineuses mais meme defaut
    ("idx_psdrf_t_bm_sup_30_mesures_id_cycle", "t_bm_sup_30_mesures", "id_cycle"),
    ("idx_psdrf_t_categories_id_dispositif", "t_categories", "id_dispositif"),
    ("idx_psdrf_t_tarifs_id_dispositif", "t_tarifs", "id_dispositif"),
]


def upgrade():
    # CREATE INDEX CONCURRENTLY est interdit dans une transaction.
    with op.get_context().autocommit_block():
        for index_name, table, column in INDEXES:
            op.execute(
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS {index} "
                "ON pr_psdrf.{table} ({column})".format(
                    index=index_name, table=table, column=column
                )
            )


def downgrade():
    with op.get_context().autocommit_block():
        for index_name, _table, _column in reversed(INDEXES):
            op.execute(
                "DROP INDEX CONCURRENTLY IF EXISTS pr_psdrf.{index}".format(
                    index=index_name
                )
            )
