"""Widen t_arbres_mesures.coupe (char(1) -> varchar)

La colonne `coupe` etait un `char(1)` : elle ne stockait que les codes courts
"C" (chablis) et "E" (exploite). L'app mobile dendro3 >= 1.1.0 a ajoute une
troisieme option de coupe "NR" (arbre non retrouve), qui fait 2 caracteres et
provoquait une erreur Postgres `StringDataRightTruncation` a la synchro
(-> HTTP 500 cote mobile). On elargit la colonne en `varchar` (non borne, comme
le modele SQLAlchemy `DB.Unicode`) pour accueillir "NR" et d'eventuels futurs
codes, sur le schema de production ET sur le schema de staging (cree via
`CREATE TABLE ... AS TABLE pr_psdrf.t_arbres_mesures`, il herite donc du meme
type char(1)).

Revision ID: a3f1c9e2b4d7
Revises: 2115ba146beb
Create Date: 2026-07-16 09:00:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'a3f1c9e2b4d7'
down_revision = '2115ba146beb'
branch_labels = None
depends_on = None


def upgrade():
    # Production : la table existe toujours.
    op.execute("""
        ALTER TABLE pr_psdrf.t_arbres_mesures
        ALTER COLUMN coupe TYPE varchar
        USING NULLIF(btrim(coupe), '');
    """)

    # Staging : le schema/table peut ne pas exister sur toutes les instances.
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'pr_psdrf_staging'
                  AND table_name = 't_arbres_mesures'
                  AND column_name = 'coupe'
            ) THEN
                ALTER TABLE pr_psdrf_staging.t_arbres_mesures
                ALTER COLUMN coupe TYPE varchar
                USING NULLIF(btrim(coupe), '');
            END IF;
        END $$;
    """)


def downgrade():
    # Retour a char(1) : tronque les valeurs > 1 caractere (ex. "NR" -> "N").
    # A n'utiliser qu'en connaissance de cause (perte d'information possible).
    op.execute("""
        ALTER TABLE pr_psdrf.t_arbres_mesures
        ALTER COLUMN coupe TYPE char(1)
        USING left(coupe, 1);
    """)

    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'pr_psdrf_staging'
                  AND table_name = 't_arbres_mesures'
                  AND column_name = 'coupe'
            ) THEN
                ALTER TABLE pr_psdrf_staging.t_arbres_mesures
                ALTER COLUMN coupe TYPE char(1)
                USING left(coupe, 1);
            END IF;
        END $$;
    """)
