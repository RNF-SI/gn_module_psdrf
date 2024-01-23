"""Switch IDs to UUID in PSDRF module

Revision ID: 51c7904d2aa3
Revises: e04a349457e4
Create Date: 2024-01-23 14:06:36.619649

"""
from alembic import op
import sqlalchemy as sa
import uuid
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '51c7904d2aa3'
down_revision = 'e04a349457e4'
branch_labels = None
depends_on = None

def upgrade():
    # Repere
    # Step 1: Add new UUID column (if not already added)
    op.add_column('t_reperes', sa.Column('new_id_repere', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False))
    # Step 2: Populate new UUID column
    t_reperes = sa.table('t_reperes', 
                         sa.column('id_repere', sa.Integer), 
                         sa.column('new_id_repere', sa.dialects.postgresql.UUID(as_uuid=True)))
    connection = op.get_bind()
    connection.execute(t_reperes.update().values(new_id_repere=sa.func.uuid_generate_v4()))
    # Step 3: Drop old primary key column
    op.drop_column('t_reperes', 'id_repere')
    # Step 4: Rename the new UUID column
    op.alter_column('t_reperes', 'new_id_repere', new_column_name='id_repere')


    # Arbre
    # Step 1: Add new UUID column (if not already added)
    op.add_column('t_arbres', sa.Column('new_id_arbre', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False))
    # Step 2: Populate new UUID column
    t_arbres = sa.table('t_arbres', 
                        sa.column('id_arbre', sa.Integer), 
                        sa.column('new_id_arbre', sa.dialects.postgresql.UUID(as_uuid=True)))
    connection = op.get_bind()
    connection.execute(t_arbres.update().values(new_id_arbre=sa.func.uuid_generate_v4()))

    # Step 3: Add new UUID column to t_arbres_mesures for foreign key
    op.add_column('t_arbres_mesures', sa.Column('temp_id_arbre', sa.dialects.postgresql.UUID(as_uuid=True)))
    # Step 4: Populate new UUID column in t_arbres_mesures
    # (Match UUIDs from t_arbres to t_arbres_mesures)
    connection.execute("""
    UPDATE t_arbres_mesures
    SET temp_id_arbre = t_arbres.new_id_arbre
    FROM t_arbres
    WHERE t_arbres_mesures.id_arbre = t_arbres.id_arbre
    """)
    # Step 5: Drop old foreign key column in t_arbres_mesures
    op.drop_column('t_arbres_mesures', 'id_arbre')
    # Step 6: Rename the new UUID foreign key column in t_arbres_mesures
    op.alter_column('t_arbres_mesures', 'temp_id_arbre', new_column_name='id_arbre')

    # Step 7: Drop old primary key column in t_arbres
    op.drop_column('t_arbres', 'id_arbre')
    # Step 8: Rename the new UUID primary key column in t_arbres
    op.alter_column('t_arbres', 'new_id_arbre', new_column_name='id_arbre')

    # Step 9: Drop the old foreign key constraint in t_arbres_mesures
    op.drop_constraint('fk_t_arbres_mesures_t_arbres', 't_arbres_mesures', type_='foreignkey')

    # Step 10: Create the new foreign key constraint in t_arbres_mesures
    # Note: Ensure the referenced column 'id_arbre' in 't_arbres' has been correctly altered to UUID before this step
    op.create_foreign_key('fk_t_arbres_mesures_t_arbres', 't_arbres_mesures', 't_arbres', ['id_arbre'], ['id_arbre'])


    # Arbres mesures
    # Step 1: Add new UUID column (if not already added)
    op.add_column('t_arbres_mesures', sa.Column('new_id_arbre_mesure', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False))
    # Step 2: Populate new UUID column
    t_arbres_mesures = sa.table('t_arbres_mesures', 
                         sa.column('id_arbre_mesure', sa.Integer), 
                         sa.column('new_id_arbre_mesure', sa.dialects.postgresql.UUID(as_uuid=True)))
    connection = op.get_bind()
    connection.execute(t_arbres_mesures.update().values(new_id_arbre_mesure=sa.func.uuid_generate_v4()))
    # Step 3: Drop old primary key column
    op.drop_column('t_arbres_mesures', 'id_arbre_mesure')
    # Step 4: Rename the new UUID column
    op.alter_column('t_arbres_mesures', 'new_id_arbre_mesure', new_column_name='id_arbre_mesure')


    # BMS
    # Step 1: Add new UUID column (if not already added)
    op.add_column('t_bm_sup_30', sa.Column('new_id_bm_sup_30', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False))
    # Step 2: Populate new UUID column
    t_bm_sup_30 = sa.table('t_bm_sup_30', 
                     sa.column('id_bm_sup_30', sa.Integer), 
                     sa.column('new_id_bm_sup_30', sa.dialects.postgresql.UUID(as_uuid=True)))
    connection = op.get_bind()
    connection.execute(t_bm_sup_30.update().values(new_id_bm_sup_30=sa.func.uuid_generate_v4()))

    # Step 3: Add new UUID column to t_bm_sup_30_mesures for foreign key
    op.add_column('t_bm_sup_30_mesures', sa.Column('temp_id_bm_sup_30', sa.dialects.postgresql.UUID(as_uuid=True)))
    # Step 4: Populate new UUID column in t_bm_sup_30_mesures
    # (Match UUIDs from t_bm_sup_30 to t_bm_sup_30_mesures)
    connection.execute("""
    UPDATE t_bm_sup_30_mesures
    SET temp_id_bm_sup_30 = t_bm_sup_30.new_id_bm_sup_30
    FROM t_bm_sup_30
    WHERE t_bm_sup_30_mesures.id_bm_sup_30 = t_bm_sup_30.id_bm_sup_30
    """)
    # Step 5: Drop old foreign key column in t_bm_sup_30_mesures
    op.drop_column('t_bm_sup_30_mesures', 'id_bm_sup_30')
    # Step 6: Rename the new UUID foreign key column in t_bm_sup_30_mesures
    op.alter_column('t_bm_sup_30_mesures', 'temp_id_bm_sup_30', new_column_name='id_bm_sup_30')

    # Step 7: Drop old primary key column in t_bm_sup_30
    op.drop_column('t_bm_sup_30', 'id_bm_sup_30')
    # Step 8: Rename the new UUID primary key column in t_bm_sup_30
    op.alter_column('t_bm_sup_30', 'new_id_bm_sup_30', new_column_name='id_bm_sup_30')

    # Step 9: Drop the old foreign key constraint in t_bm_sup_30_mesures
    op.drop_constraint('fk_t_bm_sup_30_mesures_t_bm_sup_30', 't_bm_sup_30_mesures', type_='foreignkey')

    # Step 10: Create the new foreign key constraint in t_bm_sup_30_mesures
    # Note: Ensure the referenced column 'id_bm_sup_30' in 't_bm_sup_30' has been correctly altered to UUID before this step
    op.create_foreign_key('fk_t_bm_sup_30_mesures_t_bm_sup_30', 't_bm_sup_30_mesures', 't_bm_sup_30', ['id_bm_sup_30'], ['id_bm_sup_30'])

    # BMS mesures
    # Step 1: Add new UUID column (if not already added)
    op.add_column('t_bm_sup_30_mesures', sa.Column('new_id_bm_sup_30_mesure', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False))
    # Step 2: Populate new UUID column
    t_bm_sup_30_mesures = sa.table('t_bm_sup_30_mesures', 
                         sa.column('id_bm_sup_30_mesure', sa.Integer), 
                         sa.column('new_id_bm_sup_30_mesure', sa.dialects.postgresql.UUID(as_uuid=True)))
    connection = op.get_bind()
    connection.execute(t_bm_sup_30_mesures.update().values(new_id_bm_sup_30_mesure=sa.func.uuid_generate_v4()))
    # Step 3: Drop old primary key column
    op.drop_column('t_bm_sup_30_mesures', 't_bm_sup_30_mesures')
    # Step 4: Rename the new UUID column
    op.alter_column('t_bm_sup_30_mesures', 'new_id_bm_sup_30_mesure', new_column_name='t_bm_sup_30_mesures')


    # Cor_cycle_placette
    # Step 1: Add new UUID column (if not already added)
    op.add_column('cor_cycles_placettes', sa.Column('new_id_cycle_placette', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False))
    # Step 2: Populate new UUID column
    cor_cycles_placettes = sa.table('cor_cycles_placettes', 
                                    sa.column('id_cycle_placette', sa.Integer), 
                                    sa.column('new_id_cycle_placette', sa.dialects.postgresql.UUID(as_uuid=True)))
    connection = op.get_bind()
    connection.execute(cor_cycles_placettes.update().values(new_id_cycle_placette=sa.func.uuid_generate_v4()))

    # Step 3: Add new UUID column to t_regenerations and t_transects for foreign key
    op.add_column('t_regenerations', sa.Column('temp_id_cycle_placette', sa.dialects.postgresql.UUID(as_uuid=True)))
    op.add_column('t_transects', sa.Column('temp_id_cycle_placette', sa.dialects.postgresql.UUID(as_uuid=True)))
    # Step 4: Populate new UUID column in t_regenerations and t_transects
    # (Match UUIDs from cor_cycles_placettes to t_regenerations)
    connection.execute("""
    UPDATE t_regenerations
    SET temp_id_cycle_placette = cor_cycles_placettes.new_id_cycle_placette
    FROM cor_cycles_placettes
    WHERE t_regenerations.id_cycle_placette = cor_cycles_placettes.id_cycle_placette
    """)
    # (Match UUIDs from cor_cycles_placettes to t_transects)
    connection.execute("""
    UPDATE t_transects
    SET temp_id_cycle_placette = cor_cycles_placettes.new_id_cycle_placette
    FROM cor_cycles_placettes
    WHERE t_transects.id_cycle_placette = cor_cycles_placettes.id_cycle_placette
    """)
    # Step 5: Drop old foreign key column in t_regenerations and t_transects
    op.drop_column('t_regenerations', 'id_cycle_placette')
    op.drop_column('t_transects', 'id_cycle_placette')
    # Step 6: Rename the new UUID foreign key column in t_regenerations and t_transects
    op.alter_column('t_regenerations', 'temp_id_cycle_placette', new_column_name='id_cycle_placette')
    op.alter_column('t_transects', 'temp_id_cycle_placette', new_column_name='id_cycle_placette')

    # Step 7: Drop old primary key column in cor_cycles_placettes
    op.drop_column('cor_cycles_placettes', 'id_cycle_placette')
    # Step 8: Rename the new UUID primary key column in cor_cycles_placettes
    op.alter_column('cor_cycles_placettes', 'new_id_cycle_placette', new_column_name='id_cycle_placette')

    # Step 9: Drop the old foreign key constraint in t_regenerations and t_transects
    op.drop_constraint('fk_t_regenerations_cor_cycles_placettes', 't_regenerations', type_='foreignkey')
    op.drop_constraint('fk_t_transects_cor_cycles_placettes', 't_transects', type_='foreignkey')

    # Step 10: Create the new foreign key constraint in t_regenerations and t_transects
    # Note: Ensure the referenced column 'id_cycle_placette' in 'cor_cycles_placettes' has been correctly altered to UUID before this step
    op.create_foreign_key('fk_t_regenerations_cor_cycles_placettes', 't_regenerations', 'cor_cycles_placettes', ['id_cycle_placette'], ['id_cycle_placette'])
    op.create_foreign_key('fk_t_transects_cor_cycles_placettes', 't_transects', 'cor_cycles_placettes', ['id_cycle_placette'], ['id_cycle_placette'])


    # Regeneration
    # Step 1: Add new UUID column (if not already added)
    op.add_column('t_regenerations', sa.Column('new_id_regeneration', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False))
    # Step 2: Populate new UUID column
    t_regenerations = sa.table('t_regenerations', 
                               sa.column('id_regeneration', sa.Integer), 
                               sa.column('new_id_regeneration', sa.dialects.postgresql.UUID(as_uuid=True)))
    connection = op.get_bind()
    connection.execute(t_regenerations.update().values(new_id_regeneration=sa.func.uuid_generate_v4()))
    # Step 3: Drop old primary key column
    op.drop_column('t_regenerations', 'id_regeneration')
    # Step 4: Rename the new UUID column
    op.alter_column('t_regenerations', 'new_id_regeneration', new_column_name='id_regeneration')


    # Transect
    # Step 1: Add new UUID column (if not already added)
    op.add_column('t_transects', sa.Column('new_id_transect', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False))
    # Step 2: Populate new UUID column
    t_transects = sa.table('t_transects', 
                           sa.column('id_transect', sa.Integer), 
                           sa.column('new_id_transect', sa.dialects.postgresql.UUID(as_uuid=True)))
    connection = op.get_bind()
    connection.execute(t_transects.update().values(new_id_transect=sa.func.uuid_generate_v4()))
    # Step 3: Drop old primary key column
    op.drop_column('t_transects', 'id_transect')
    # Step 4: Rename the new UUID column
    op.alter_column('t_transects', 'new_id_transect', new_column_name='id_transect')



def downgrade():
    pass
