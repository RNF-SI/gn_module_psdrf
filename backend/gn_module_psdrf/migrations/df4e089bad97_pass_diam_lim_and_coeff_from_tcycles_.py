"""Pass diam_lim and coeff from TCycles into CorCyclesPlacettes

Revision ID: df4e089bad97
Revises: 51c7904d2aa3
Create Date: 2024-02-22 14:56:02.069170

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'df4e089bad97'
down_revision = '51c7904d2aa3'
branch_labels = None
depends_on = None


def upgrade():
    # Step 1: Add new columns to CorCyclesPlacettes
    op.add_column('cor_cycles_placettes', sa.Column('coeff', sa.Integer, nullable=True), schema='pr_psdrf')
    op.add_column('cor_cycles_placettes', sa.Column('diam_lim', sa.Float, nullable=True), schema='pr_psdrf')

    # Step 2: Populate new columns with values from TCycles
    # Note: Adjust this SQL based on your actual database dialect
    op.execute("""
        UPDATE pr_psdrf.cor_cycles_placettes
        SET coeff = (SELECT coeff FROM pr_psdrf.t_cycles WHERE pr_psdrf.t_cycles.id_cycle = pr_psdrf.cor_cycles_placettes.id_cycle),
            diam_lim = (SELECT diam_lim FROM pr_psdrf.t_cycles WHERE pr_psdrf.t_cycles.id_cycle = pr_psdrf.cor_cycles_placettes.id_cycle)
    """)

    # Step 3: Remove columns from TCycles
    op.drop_column('t_cycles', 'coeff', schema='pr_psdrf')
    op.drop_column('t_cycles', 'diam_lim', schema='pr_psdrf')

def downgrade():
    # Add the columns back to TCycles with nullable set to True
    op.add_column('t_cycles', sa.Column('coeff', sa.Integer, nullable=True), schema='pr_psdrf')
    op.add_column('t_cycles', sa.Column('diam_lim', sa.Float, nullable=True), schema='pr_psdrf')

    # Populate the TCycles columns with the first CorCyclesPlacettes entry values for each cycle
    op.execute("""
        WITH FirstCorCycle AS (
            SELECT
                id_cycle,
                FIRST_VALUE(coeff) OVER(PARTITION BY id_cycle ORDER BY id_cycle_placette) AS first_coeff,
                FIRST_VALUE(diam_lim) OVER(PARTITION BY id_cycle ORDER BY id_cycle_placette) AS first_diam_lim,
                ROW_NUMBER() OVER(PARTITION BY id_cycle ORDER BY id_cycle_placette) AS rn
            FROM pr_psdrf.cor_cycles_placettes
        )
        UPDATE pr_psdrf.t_cycles
        SET
            coeff = (SELECT first_coeff FROM FirstCorCycle WHERE FirstCorCycle.id_cycle = t_cycles.id_cycle AND rn = 1),
            diam_lim = (SELECT first_diam_lim FROM FirstCorCycle WHERE FirstCorCycle.id_cycle = t_cycles.id_cycle AND rn = 1)
    """)

    # Remove the previously added columns from CorCyclesPlacettes
    op.drop_column('cor_cycles_placettes', 'coeff', schema='pr_psdrf')
    op.drop_column('cor_cycles_placettes', 'diam_lim', schema='pr_psdrf')

