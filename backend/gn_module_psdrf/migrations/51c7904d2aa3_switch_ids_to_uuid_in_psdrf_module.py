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

schema = 'pr_psdrf'

def upgrade():
    # Repere
    # Step 1: Add new UUID column (if not already added)
    op.add_column('t_reperes', sa.Column('new_id_repere', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True), schema=schema)
    # Step 2: Populate new UUID column
    t_reperes = sa.table('t_reperes', 
                         sa.column('id_repere', sa.Integer), 
                         sa.column('new_id_repere', sa.dialects.postgresql.UUID(as_uuid=True)),
                         schema=schema)
    connection = op.get_bind()
    connection.execute(t_reperes.update().values(new_id_repere=sa.func.uuid_generate_v4()))
    # Step 3: Alter new_id_repere column to NOT NULL
    op.alter_column('t_reperes', 'new_id_repere', existing_type=sa.dialects.postgresql.UUID(as_uuid=True), nullable=False, schema=schema)
    # Step 4: Drop old primary key column
    op.drop_column('t_reperes', 'id_repere', schema=schema)
    # Step 5: Rename the new UUID column
    op.alter_column('t_reperes', 'new_id_repere', new_column_name='id_repere', schema=schema)
    op.create_primary_key('pk_t_reperes', 't_reperes', ['id_repere'], schema=schema)


    # Arbre
    # Drop the dependent view
    op.execute("DROP VIEW IF EXISTS pr_psdrf.v_arbres_geom")

    # Step 10: Drop the old foreign key constraint in t_arbres_mesures
    op.drop_constraint('fk_t_arbres_mesures_t_arbres', 't_arbres_mesures', type_='foreignkey', schema=schema)

    # Step 1: Add new UUID column (if not already added) and allow NULL temporarily
    op.add_column('t_arbres', sa.Column('new_id_arbre', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True), schema=schema)

    # Step 2: Populate new UUID column with unique values
    t_arbres = sa.table('t_arbres', 
                        sa.column('id_arbre', sa.Integer), 
                        sa.column('new_id_arbre', sa.dialects.postgresql.UUID(as_uuid=True)),
                        schema=schema)
    connection = op.get_bind()
    connection.execute(t_arbres.update().values(new_id_arbre=sa.func.uuid_generate_v4()))

    # Step 3: Alter new_id_arbre column to NOT NULL
    op.alter_column('t_arbres', 'new_id_arbre', existing_type=sa.dialects.postgresql.UUID(as_uuid=True), nullable=False, schema=schema)

    # Step 4: Add new UUID column to t_arbres_mesures for foreign key
    op.add_column('t_arbres_mesures', sa.Column('temp_id_arbre', sa.dialects.postgresql.UUID(as_uuid=True)), schema=schema)

    # Step 5: Populate new UUID column in t_arbres_mesures
    connection.execute("""
    UPDATE {schema}.t_arbres_mesures
    SET temp_id_arbre = t_arbres.new_id_arbre
    FROM {schema}.t_arbres
    WHERE t_arbres_mesures.id_arbre = t_arbres.id_arbre
    """.format(schema=schema))

    # Step 6: Drop old foreign key column in t_arbres_mesures
    op.drop_column('t_arbres_mesures', 'id_arbre', schema=schema)

    # Step 7: Rename the new UUID foreign key column in t_arbres_mesures
    op.alter_column('t_arbres_mesures', 'temp_id_arbre', new_column_name='id_arbre', schema=schema)

    # Step 8: Drop old primary key column in t_arbres
    op.drop_column('t_arbres', 'id_arbre', schema=schema)

    # Step 9: Rename the new UUID primary key column in t_arbres
    op.alter_column('t_arbres', 'new_id_arbre', new_column_name='id_arbre', schema=schema)
    op.create_primary_key('pk_t_arbres', 't_arbres', ['id_arbre'], schema=schema)

    # Step 11: Create the new foreign key constraint in t_arbres_mesures
    op.create_foreign_key('fk_t_arbres_mesures_t_arbres', 't_arbres_mesures', 't_arbres', ['id_arbre'], ['id_arbre'], ondelete='CASCADE', source_schema=schema, referent_schema=schema)

    # Recreate the view after modifications
    op.execute("""
        CREATE VIEW pr_psdrf.v_arbres_geom AS
        SELECT a.id_arbre,
            a.id_placette,
            a.code_essence,
            a.azimut,
            a.distance,
            a.taillis,
            a.observation,
            a.id_arbre_orig,
            st_setsrid(st_point(st_x(p.geom) + a.distance * sin(a.azimut * pi() / 200), st_y(p.geom) + a.distance * cos(a.azimut * pi() / 200)), 2154)::geometry(Point,2154) AS g
        FROM pr_psdrf.t_arbres a
            JOIN pr_psdrf.t_placettes p ON a.id_placette = p.id_placette
        WHERE p.geom IS NOT NULL;
    """)


    # Arbres mesures
    # Step 1: Add new UUID column
    op.add_column('t_arbres_mesures', sa.Column('new_id_arbre_mesure', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True), schema=schema)

    # Step 2: Populate new UUID column
    t_arbres_mesures = sa.table('t_arbres_mesures', 
                                sa.column('id_arbre_mesure', sa.Integer), 
                                sa.column('new_id_arbre_mesure', sa.dialects.postgresql.UUID(as_uuid=True)),
                                schema=schema)
    connection = op.get_bind()
    connection.execute(t_arbres_mesures.update().values(new_id_arbre_mesure=sa.func.uuid_generate_v4()))

    # Step 3: Alter new_id_repere column to NOT NULL
    op.alter_column('t_arbres_mesures', 'new_id_arbre_mesure', existing_type=sa.dialects.postgresql.UUID(as_uuid=True), nullable=False, schema=schema)

    # Step 4: Drop old primary key column
    op.drop_column('t_arbres_mesures', 'id_arbre_mesure', schema=schema)

    # Step 5: Rename the new UUID column
    op.alter_column('t_arbres_mesures', 'new_id_arbre_mesure', new_column_name='id_arbre_mesure', schema=schema)
    op.create_primary_key('pk_t_arbres_mesures', 't_arbres_mesures', ['id_arbre_mesure'], schema=schema)

    # BMS
    # Step 10: Drop the old foreign key constraint in t_bm_sup_30_mesures
    op.drop_constraint('fk_t_bm_sup_30_mesures_t_bm_sup_30', 't_bm_sup_30_mesures', type_='foreignkey', schema=schema)

    # Step 1: Add new UUID column
    op.add_column('t_bm_sup_30', sa.Column('new_id_bm_sup_30', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True), schema=schema)

    # Step 2: Populate new UUID column
    t_bm_sup_30 = sa.table('t_bm_sup_30', 
                        sa.column('id_bm_sup_30', sa.Integer), 
                        sa.column('new_id_bm_sup_30', sa.dialects.postgresql.UUID(as_uuid=True)),
                        schema=schema)
    connection = op.get_bind()
    connection.execute(t_bm_sup_30.update().values(new_id_bm_sup_30=sa.func.uuid_generate_v4()))

    # Step 3: Alter new_id_bm_sup_30 column to NOT NULL
    op.alter_column('t_bm_sup_30', 'new_id_bm_sup_30', existing_type=sa.dialects.postgresql.UUID(as_uuid=True), nullable=False, schema=schema)

    # Step 4: Add new UUID column to t_bm_sup_30_mesures for foreign key
    op.add_column('t_bm_sup_30_mesures', sa.Column('temp_id_bm_sup_30', sa.dialects.postgresql.UUID(as_uuid=True)), schema=schema)

    # Step 5: Populate new UUID column in t_bm_sup_30_mesures
    connection.execute("""
    UPDATE {schema}.t_bm_sup_30_mesures
    SET temp_id_bm_sup_30 = t_bm_sup_30.new_id_bm_sup_30
    FROM {schema}.t_bm_sup_30
    WHERE t_bm_sup_30_mesures.id_bm_sup_30 = t_bm_sup_30.id_bm_sup_30
    """.format(schema=schema))

    # Step 6: Drop old foreign key column in t_bm_sup_30_mesures
    op.drop_column('t_bm_sup_30_mesures', 'id_bm_sup_30', schema=schema)

    # Step 7: Rename the new UUID foreign key column in t_bm_sup_30_mesures
    op.alter_column('t_bm_sup_30_mesures', 'temp_id_bm_sup_30', new_column_name='id_bm_sup_30', schema=schema)

    # Step 8: Drop old primary key column in t_bm_sup_30
    op.drop_column('t_bm_sup_30', 'id_bm_sup_30', schema=schema)

    # Step 9: Rename the new UUID primary key column in t_bm_sup_30
    op.alter_column('t_bm_sup_30', 'new_id_bm_sup_30', new_column_name='id_bm_sup_30', schema=schema)
    op.create_primary_key('pk_t_bm_sup_30', 't_bm_sup_30', ['id_bm_sup_30'], schema=schema)

    # Step 11: Create the new foreign key constraint in t_bm_sup_30_mesures
    op.create_foreign_key('fk_t_bm_sup_30_mesures_t_bm_sup_30', 't_bm_sup_30_mesures', 't_bm_sup_30', ['id_bm_sup_30'], ['id_bm_sup_30'], ondelete='CASCADE', source_schema=schema, referent_schema=schema)


    # BMS mesures
    # Step 1: Add new UUID column
    op.add_column('t_bm_sup_30_mesures', sa.Column('new_id_bm_sup_30_mesure', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True), schema=schema)

    # Step 2: Populate new UUID column
    t_bm_sup_30_mesures = sa.table('t_bm_sup_30_mesures', 
                                sa.column('id_bm_sup_30_mesure', sa.Integer), 
                                sa.column('new_id_bm_sup_30_mesure', sa.dialects.postgresql.UUID(as_uuid=True)),
                                schema=schema)
    connection = op.get_bind()
    connection.execute(t_bm_sup_30_mesures.update().values(new_id_bm_sup_30_mesure=sa.func.uuid_generate_v4()))

    # Step 3: Alter new_id_bm_sup_30_mesure column to NOT NULL
    op.alter_column('t_bm_sup_30_mesures', 'new_id_bm_sup_30_mesure', existing_type=sa.dialects.postgresql.UUID(as_uuid=True), nullable=False, schema=schema)

    # Step 4: Drop old primary key column
    op.drop_column('t_bm_sup_30_mesures', 'id_bm_sup_30_mesure', schema=schema)

    # Step 5: Rename the new UUID column
    op.alter_column('t_bm_sup_30_mesures', 'new_id_bm_sup_30_mesure', new_column_name='id_bm_sup_30_mesure', schema=schema)
    op.create_primary_key('pk_t_bm_sup_30_mesures', 't_bm_sup_30_mesures', ['id_bm_sup_30_mesure'], schema=schema)


    # Cor_cycle_placette
    # Step 10: Drop the old foreign key constraint in t_regenerations and t_transects
    op.drop_constraint('fk_t_regenerations_cor_cycles_placettes', 't_regenerations', type_='foreignkey', schema=schema)
    op.drop_constraint('fk_t_transects_cor_cycles_placettes', 't_transects', type_='foreignkey', schema=schema)

    # Step 1: Add new UUID column
    op.add_column('cor_cycles_placettes', sa.Column('new_id_cycle_placette', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True), schema=schema)

    # Step 2: Populate new UUID column
    cor_cycles_placettes = sa.table('cor_cycles_placettes', 
                                    sa.column('id_cycle_placette', sa.Integer), 
                                    sa.column('new_id_cycle_placette', sa.dialects.postgresql.UUID(as_uuid=True)),
                                    schema=schema)
    connection = op.get_bind()
    connection.execute(cor_cycles_placettes.update().values(new_id_cycle_placette=sa.func.uuid_generate_v4()))

    # Step 3: Alter new_id_cycle_placette column to NOT NULL
    op.alter_column('cor_cycles_placettes', 'new_id_cycle_placette', existing_type=sa.dialects.postgresql.UUID(as_uuid=True), nullable=False, schema=schema)

    # Step 4: Add new UUID column to t_regenerations and t_transects for foreign key
    op.add_column('t_regenerations', sa.Column('temp_id_cycle_placette', sa.dialects.postgresql.UUID(as_uuid=True)), schema=schema)
    op.add_column('t_transects', sa.Column('temp_id_cycle_placette', sa.dialects.postgresql.UUID(as_uuid=True)), schema=schema)

    # Step 5: Populate new UUID column in t_regenerations and t_transects
    connection.execute("""
    UPDATE {schema}.t_regenerations
    SET temp_id_cycle_placette = cor_cycles_placettes.new_id_cycle_placette
    FROM {schema}.cor_cycles_placettes
    WHERE t_regenerations.id_cycle_placette = cor_cycles_placettes.id_cycle_placette
    """.format(schema=schema))
    connection.execute("""
    UPDATE {schema}.t_transects
    SET temp_id_cycle_placette = cor_cycles_placettes.new_id_cycle_placette
    FROM {schema}.cor_cycles_placettes
    WHERE t_transects.id_cycle_placette = cor_cycles_placettes.id_cycle_placette
    """.format(schema=schema))

    # Step 6: Drop old foreign key column in t_regenerations and t_transects
    op.drop_column('t_regenerations', 'id_cycle_placette', schema=schema)
    op.drop_column('t_transects', 'id_cycle_placette', schema=schema)

    # Step 7: Rename the new UUID foreign key column in t_regenerations and t_transects
    op.alter_column('t_regenerations', 'temp_id_cycle_placette', new_column_name='id_cycle_placette', schema=schema)
    op.alter_column('t_transects', 'temp_id_cycle_placette', new_column_name='id_cycle_placette', schema=schema)

    # Step 8: Drop old primary key column in cor_cycles_placettes
    op.drop_column('cor_cycles_placettes', 'id_cycle_placette', schema=schema)

    # Step 9: Rename the new UUID primary key column in cor_cycles_placettes
    op.alter_column('cor_cycles_placettes', 'new_id_cycle_placette', new_column_name='id_cycle_placette', schema=schema)
    op.create_primary_key('pk_cor_cycles_placettes', 'cor_cycles_placettes', ['id_cycle_placette'], schema=schema)

    # Step 11: Create the new foreign key constraint in t_regenerations and t_transects
    op.create_foreign_key('fk_t_regenerations_cor_cycles_placettes', 't_regenerations', 'cor_cycles_placettes', ['id_cycle_placette'], ['id_cycle_placette'], ondelete='CASCADE', source_schema=schema, referent_schema=schema)
    op.create_foreign_key('fk_t_transects_cor_cycles_placettes', 't_transects', 'cor_cycles_placettes', ['id_cycle_placette'], ['id_cycle_placette'], ondelete='CASCADE', source_schema=schema, referent_schema=schema)


    # Regeneration
    # Step 1: Add new UUID column
    op.add_column('t_regenerations', sa.Column('new_id_regeneration', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True), schema=schema)
    # Step 2: Populate new UUID column
    t_regenerations = sa.table('t_regenerations', 
                            sa.column('id_regeneration', sa.Integer), 
                            sa.column('new_id_regeneration', sa.dialects.postgresql.UUID(as_uuid=True)),
                            schema=schema)
    connection = op.get_bind()
    connection.execute(t_regenerations.update().values(new_id_regeneration=sa.func.uuid_generate_v4()))
    # Step 3: Alter new_id_regeneration column to NOT NULL
    op.alter_column('t_regenerations', 'new_id_regeneration', existing_type=sa.dialects.postgresql.UUID(as_uuid=True), nullable=False, schema=schema)
    # Step 4: Drop old primary key column
    op.drop_column('t_regenerations', 'id_regeneration', schema=schema)
    # Step 5: Rename the new UUID column
    op.alter_column('t_regenerations', 'new_id_regeneration', new_column_name='id_regeneration', schema=schema)
    op.create_primary_key('pk_t_regenerations', 't_regenerations', ['id_regeneration'], schema=schema)

    # Transect
    # Step 1: Add new UUID column
    op.add_column('t_transects', sa.Column('new_id_transect', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True), schema=schema)
    # Step 2: Populate new UUID column
    t_transects = sa.table('t_transects', 
                        sa.column('id_transect', sa.Integer), 
                        sa.column('new_id_transect', sa.dialects.postgresql.UUID(as_uuid=True)),
                        schema=schema)
    connection = op.get_bind()
    connection.execute(t_transects.update().values(new_id_transect=sa.func.uuid_generate_v4()))
    # Step 3: Alter new_id_transect column to NOT NULL
    op.alter_column('t_transects', 'new_id_transect', existing_type=sa.dialects.postgresql.UUID(as_uuid=True), nullable=False, schema=schema)
    # Step 4: Drop old primary key column
    op.drop_column('t_transects', 'id_transect', schema=schema)
    # Step 5: Rename the new UUID column
    op.alter_column('t_transects', 'new_id_transect', new_column_name='id_transect', schema=schema)
    op.create_primary_key('pk_t_transects', 't_transects', ['id_transect'], schema=schema)


def downgrade():

                                       
    # Repere
    # Reverse Step 4: Rename UUID column back to a temporary name
    op.alter_column('t_reperes', 'id_repere', new_column_name='new_id_repere', schema=schema)

    # Reverse Step 3: Recreate the original integer primary key column without a default value
    op.add_column('t_reperes', sa.Column('id_repere', sa.Integer, autoincrement=False, nullable=True), schema=schema)

    # Create an engine (or use an existing one)
    bind = op.get_bind()
    metadata = sa.MetaData(bind=bind)
    t_reperes = sa.Table('t_reperes', metadata, autoload=True, autoload_with=bind, schema=schema)

    # Check if the primary key constraint 'pk_t_reperes' exists and drop it if it does
    insp = sa.inspect(bind)
    pk_constraint = insp.get_pk_constraint('t_reperes', schema=schema)
    if pk_constraint and 'pk_t_reperes' in pk_constraint.get('name', []):
        op.drop_constraint('pk_t_reperes', 't_reperes', type_='primary', schema=schema)

    # Create a CTE that assigns row numbers to each row in t_reperes
    row_number_cte = sa.select([
        t_reperes.c.new_id_repere,
        sa.func.row_number().over(order_by=t_reperes.c.new_id_repere).label('rn')
    ]).cte('row_number_cte')

    # Update t_reperes by joining it with the CTE on new_id_repere
    update_stmt = t_reperes.update().values(
        id_repere=row_number_cte.c.rn
    ).where(
        t_reperes.c.new_id_repere == row_number_cte.c.new_id_repere
    )

    # Execute the update statement
    bind.execute(update_stmt)

    op.alter_column('t_reperes', 'id_repere', existing_type=sa.Integer, nullable=False, schema=schema)
    op.create_primary_key('pk_t_reperes', 't_reperes', ['id_repere'], schema=schema)

    # Drop the temporary UUID column
    op.drop_column('t_reperes', 'new_id_repere', schema=schema)





    # Arbres
    # Drop the dependent view
    op.execute("DROP VIEW IF EXISTS pr_psdrf.v_arbres_geom")

    # Reverse operations for t_arbres_mesures first
    # Step 10: Drop the new foreign key constraint
    op.drop_constraint('fk_t_arbres_mesures_t_arbres', 't_arbres_mesures', type_='foreignkey', schema=schema)

    # Step 6: Rename the UUID foreign key column back to a temporary name
    op.alter_column('t_arbres_mesures', 'id_arbre', new_column_name='temp_id_arbre', schema=schema)

    # Step 5: Recreate the original foreign key column with integer type
    op.add_column('t_arbres_mesures', sa.Column('id_arbre', sa.Integer, nullable=True), schema=schema)

    # Now, reverse operations for t_arbres
    # Get database connection and metadata
    connection = op.get_bind()
    metadata = sa.MetaData(bind=connection)

    # Step 8: Rename the UUID primary key column back to a temporary name
    op.alter_column('t_arbres', 'id_arbre', new_column_name='new_id_arbre', schema=schema)

    # Step 7: Recreate the original primary key column with integer type
    op.add_column('t_arbres', sa.Column('id_arbre', sa.Integer, primary_key=True, autoincrement=True, nullable=True), schema=schema)

    # Load t_arbres table
    t_arbres = sa.Table('t_arbres', metadata, autoload=True, autoload_with=connection, schema=schema)

    # Check if the primary key constraint 'pk_t_arbres' exists and drop it if it does
    insp = sa.inspect(bind)
    pk_constraint = insp.get_pk_constraint('t_arbres', schema=schema)
    if pk_constraint and 'pk_t_arbres' in pk_constraint.get('name', []):
        op.drop_constraint('pk_t_arbres', 't_arbres', type_='primary', schema=schema)

    # Create a CTE for row numbers
    row_number_cte = sa.select([
        t_arbres.c.new_id_arbre,
        sa.func.row_number().over(order_by=t_arbres.c.new_id_arbre).label('rn')
    ]).cte('row_number_cte')

    # Update statement
    update_stmt = t_arbres.update().values(
        id_arbre=row_number_cte.c.rn
    ).where(
        t_arbres.c.new_id_arbre == row_number_cte.c.new_id_arbre
    )

    # Execute the update
    connection.execute(update_stmt)

    # Set the column to NOT NULL and add primary key
    op.alter_column('t_arbres', 'id_arbre', existing_type=sa.Integer, nullable=False, schema=schema)
    op.create_primary_key('pk_t_arbres', 't_arbres', ['id_arbre'], schema=schema)


    # Step 4: Repopulate the integer foreign key column in t_arbres_mesures
    t_arbres_mesures = sa.Table('t_arbres_mesures', metadata, autoload=True, autoload_with=connection, schema=schema)

    # Update the foreign key in t_arbres_mesures
    connection.execute(
        t_arbres_mesures.update().values(
            id_arbre=sa.select([t_arbres.c.id_arbre]).where(t_arbres.c.new_id_arbre == t_arbres_mesures.c.temp_id_arbre)
        )
    )

    # Step 3: Drop the temporary UUID column in t_arbres_mesures
    op.drop_column('t_arbres_mesures', 'temp_id_arbre', schema=schema)

    # Recreate the original foreign key constraint
    op.create_foreign_key('fk_t_arbres_mesures_t_arbres', 't_arbres_mesures', 't_arbres', ['id_arbre'], ['id_arbre'], ondelete='CASCADE', source_schema=schema, referent_schema=schema)

    # Step 1: Drop the temporary UUID column in t_arbres
    op.drop_column('t_arbres', 'new_id_arbre', schema=schema)

    # Recreate the view after modifications
    op.execute("""
        CREATE VIEW pr_psdrf.v_arbres_geom AS
        SELECT a.id_arbre,
            a.id_placette,
            a.code_essence,
            a.azimut,
            a.distance,
            a.taillis,
            a.observation,
            a.id_arbre_orig,
            st_setsrid(st_point(st_x(p.geom) + a.distance * sin(a.azimut * pi() / 200), st_y(p.geom) + a.distance * cos(a.azimut * pi() / 200)), 2154)::geometry(Point,2154) AS g
        FROM pr_psdrf.t_arbres a
            JOIN pr_psdrf.t_placettes p ON a.id_placette = p.id_placette
        WHERE p.geom IS NOT NULL;
    """)


    # Arbres Mesures
    # Reverse Step 4: Rename UUID column back to a temporary name
    op.alter_column('t_arbres_mesures', 'id_arbre_mesure', new_column_name='new_id_arbre_mesure', schema=schema)

    # Reverse Step 3: Recreate the original integer primary key column without a default value
    op.add_column('t_arbres_mesures', sa.Column('id_arbre_mesure', sa.Integer, nullable=True), schema=schema)

    # Create an engine (or use an existing one)
    bind = op.get_bind()
    metadata = sa.MetaData(bind=bind)
    t_arbres_mesures = sa.Table('t_arbres_mesures', metadata, autoload=True, autoload_with=bind, schema=schema)

    # Check if the primary key constraint exists and drop it
    insp = sa.inspect(bind)
    pk_constraint = insp.get_pk_constraint('t_arbres_mesures', schema=schema)
    if pk_constraint and 'pk_t_arbres_mesures' in pk_constraint.get('name', []):
        op.drop_constraint('pk_t_arbres_mesures', 't_arbres_mesures', type_='primary', schema=schema)


    # Create a CTE for row numbers
    row_number_cte = sa.select([
        t_arbres_mesures.c.new_id_arbre_mesure,
        sa.func.row_number().over(order_by=t_arbres_mesures.c.new_id_arbre_mesure).label('rn')
    ]).cte('row_number_cte')

    # Update statement
    update_stmt = t_arbres_mesures.update().values(
        id_arbre_mesure=row_number_cte.c.rn
    ).where(
        t_arbres_mesures.c.new_id_arbre_mesure == row_number_cte.c.new_id_arbre_mesure
    )

    # Execute the update
    bind.execute(update_stmt)

    # Set the column to NOT NULL and add primary key
    op.alter_column('t_arbres_mesures', 'id_arbre_mesure', existing_type=sa.Integer, nullable=False, schema=schema)
    op.create_primary_key('pk_t_arbres_mesures', 't_arbres_mesures', ['id_arbre_mesure'], schema=schema)

    # Reverse Step 1: Drop the UUID column after successful repopulation of integer IDs
    op.drop_column('t_arbres_mesures', 'new_id_arbre_mesure', schema=schema)




    # BMS
    # Reverse operations for t_bm_sup_30_mesures first
    # Step 10: Drop the new foreign key constraint
    op.drop_constraint('fk_t_bm_sup_30_mesures_t_bm_sup_30', 't_bm_sup_30_mesures', type_='foreignkey', schema=schema)

    # Step 6: Rename the UUID foreign key column back to a temporary name
    op.alter_column('t_bm_sup_30_mesures', 'id_bm_sup_30', new_column_name='temp_id_bm_sup_30', schema=schema)

    # Step 5: Recreate the original foreign key column with integer type
    op.add_column('t_bm_sup_30_mesures', sa.Column('id_bm_sup_30', sa.Integer, nullable=True), schema=schema)

    # Now, reverse operations for t_bm_sup_30
    # Get database connection and metadata
    connection = op.get_bind()
    metadata = sa.MetaData(bind=connection)

    # Step 8: Rename the UUID primary key column back to a temporary name
    op.alter_column('t_bm_sup_30', 'id_bm_sup_30', new_column_name='new_id_bm_sup_30', schema=schema)

    # Step 7: Recreate the original primary key column with integer type
    op.add_column('t_bm_sup_30', sa.Column('id_bm_sup_30', sa.Integer, primary_key=True, autoincrement=True, nullable=True), schema=schema)

    # Load t_bm_sup_30 table
    t_bm_sup_30 = sa.Table('t_bm_sup_30', metadata, autoload=True, autoload_with=connection, schema=schema)

    # Check if the primary key constraint 'pk_t_bm_sup_30' exists and drop it if it does
    insp = sa.inspect(connection)
    pk_constraint = insp.get_pk_constraint('t_bm_sup_30', schema=schema)
    if pk_constraint and 'pk_t_bm_sup_30' in pk_constraint.get('name', []):
        op.drop_constraint('pk_t_bm_sup_30', 't_bm_sup_30', type_='primary', schema=schema)

    # Create a CTE for row numbers
    row_number_cte = sa.select([
        t_bm_sup_30.c.new_id_bm_sup_30,
        sa.func.row_number().over(order_by=t_bm_sup_30.c.new_id_bm_sup_30).label('rn')
    ]).cte('row_number_cte')

    # Update statement
    update_stmt = t_bm_sup_30.update().values(
        id_bm_sup_30=row_number_cte.c.rn
    ).where(
        t_bm_sup_30.c.new_id_bm_sup_30 == row_number_cte.c.new_id_bm_sup_30
    )

    # Execute the update
    connection.execute(update_stmt)

    # Set the column to NOT NULL and add primary key
    op.alter_column('t_bm_sup_30', 'id_bm_sup_30', existing_type=sa.Integer, nullable=False, schema=schema)
    op.create_primary_key('pk_t_bm_sup_30', 't_bm_sup_30', ['id_bm_sup_30'], schema=schema)

    # Step 4: Repopulate the integer foreign key column in t_bm_sup_30_mesures
    t_bm_sup_30_mesures = sa.Table('t_bm_sup_30_mesures', metadata, autoload=True, autoload_with=connection, schema=schema)

    # Update the foreign key in t_bm_sup_30_mesures
    connection.execute(
        t_bm_sup_30_mesures.update().values(
            id_bm_sup_30=sa.select([t_bm_sup_30.c.id_bm_sup_30]).where(t_bm_sup_30.c.new_id_bm_sup_30 == t_bm_sup_30_mesures.c.temp_id_bm_sup_30)
        )
    )

    # Step 3: Drop the temporary UUID column in t_bm_sup_30_mesures
    op.drop_column('t_bm_sup_30_mesures', 'temp_id_bm_sup_30', schema=schema)

    # Recreate the original foreign key constraint
    op.create_foreign_key('fk_t_bm_sup_30_mesures_t_bm_sup_30', 't_bm_sup_30_mesures', 't_bm_sup_30', ['id_bm_sup_30'], ['id_bm_sup_30'],ondelete='CASCADE', source_schema=schema, referent_schema=schema)

    # Step 1: Drop the temporary UUID column in t_bm_sup_30
    op.drop_column('t_bm_sup_30', 'new_id_bm_sup_30', schema=schema)






    # BMS Mesures
    # Reverse Step 4: Rename UUID column back to a temporary name
    op.alter_column('t_bm_sup_30_mesures', 'id_bm_sup_30_mesure', new_column_name='new_id_bm_sup_30_mesure', schema=schema)

    # Reverse Step 3: Recreate the original integer primary key column without a default value
    op.add_column('t_bm_sup_30_mesures', sa.Column('id_bm_sup_30_mesure', sa.Integer, autoincrement=False, nullable=True), schema=schema)

    # Create an engine (or use an existing one)
    bind = op.get_bind()
    metadata = sa.MetaData(bind=bind)
    t_bm_sup_30_mesures = sa.Table('t_bm_sup_30_mesures', metadata, autoload=True, autoload_with=bind, schema=schema)

    # Check if the primary key constraint 'pk_t_bm_sup_30_mesures' exists and drop it if it does
    insp = sa.inspect(bind)
    pk_constraint = insp.get_pk_constraint('t_bm_sup_30_mesures', schema=schema)
    if pk_constraint and 'pk_t_bm_sup_30_mesures' in pk_constraint.get('name', []):
        op.drop_constraint('pk_t_bm_sup_30_mesures', 't_bm_sup_30_mesures', type_='primary', schema=schema)

    # Create a CTE that assigns row numbers to each row in t_bm_sup_30_mesures
    row_number_cte = sa.select([
        t_bm_sup_30_mesures.c.new_id_bm_sup_30_mesure,
        sa.func.row_number().over(order_by=t_bm_sup_30_mesures.c.new_id_bm_sup_30_mesure).label('rn')
    ]).cte('row_number_cte')

    # Update t_bm_sup_30_mesures by joining it with the CTE on new_id_bm_sup_30_mesure
    update_stmt = t_bm_sup_30_mesures.update().values(
        id_bm_sup_30_mesure=row_number_cte.c.rn
    ).where(
        t_bm_sup_30_mesures.c.new_id_bm_sup_30_mesure == row_number_cte.c.new_id_bm_sup_30_mesure
    )

    # Execute the update statement
    bind.execute(update_stmt)

    op.alter_column('t_bm_sup_30_mesures', 'id_bm_sup_30_mesure', existing_type=sa.Integer, nullable=False, schema=schema)
    op.create_primary_key('pk_t_bm_sup_30_mesures', 't_bm_sup_30_mesures', ['id_bm_sup_30_mesure'], schema=schema)

    # Drop the temporary UUID column
    op.drop_column('t_bm_sup_30_mesures', 'new_id_bm_sup_30_mesure', schema=schema)




    # Cor_cycle_placette
    # Reverse operations for t_regenerations and t_transects first
    # Step 10: Drop the new foreign key constraint
    op.drop_constraint('fk_t_regenerations_cor_cycles_placettes', 't_regenerations', type_='foreignkey', schema=schema)
    op.drop_constraint('fk_t_transects_cor_cycles_placettes', 't_transects', type_='foreignkey', schema=schema)

    # Step 6: Rename the UUID foreign key column back to a temporary name
    op.alter_column('t_regenerations', 'id_cycle_placette', new_column_name='temp_id_cycle_placette', schema=schema)
    op.alter_column('t_transects', 'id_cycle_placette', new_column_name='temp_id_cycle_placette', schema=schema)

    # Step 5: Recreate the original foreign key column with integer type
    op.add_column('t_regenerations', sa.Column('id_cycle_placette', sa.Integer, nullable=True), schema=schema)
    op.add_column('t_transects', sa.Column('id_cycle_placette', sa.Integer, nullable=True), schema=schema)

    # Now, reverse operations for cor_cycles_placettes
    # Step 8: Rename the UUID primary key column back to a temporary name
    op.alter_column('cor_cycles_placettes', 'id_cycle_placette', new_column_name='new_id_cycle_placette', schema=schema)

    # Step 7: Recreate the original primary key column with integer type
    op.add_column('cor_cycles_placettes', sa.Column('id_cycle_placette', sa.Integer, autoincrement=False, nullable=True), schema=schema)

    # Get database connection and metadata
    connection = op.get_bind()
    metadata = sa.MetaData(bind=connection)

    # Load cor_cycles_placettes table
    cor_cycles_placettes = sa.Table('cor_cycles_placettes', metadata, autoload=True, autoload_with=connection, schema=schema)

    # Check if the primary key constraint 'pk_cor_cycles_placettes' exists and drop it if it does
    insp = sa.inspect(bind)
    pk_constraint = insp.get_pk_constraint('cor_cycles_placettes', schema=schema)
    if pk_constraint and 'pk_cor_cycles_placettes' in pk_constraint.get('name', []):
        op.drop_constraint('pk_cor_cycles_placettes', 'cor_cycles_placettes', type_='primary', schema=schema)

    # Create a CTE for row numbers
    row_number_cte = sa.select([
        cor_cycles_placettes.c.new_id_cycle_placette,
        sa.func.row_number().over(order_by=cor_cycles_placettes.c.new_id_cycle_placette).label('rn')
    ]).cte('row_number_cte')

    # Update statement
    update_stmt = cor_cycles_placettes.update().values(
        id_cycle_placette=row_number_cte.c.rn
    ).where(
        cor_cycles_placettes.c.new_id_cycle_placette == row_number_cte.c.new_id_cycle_placette
    )

    # Execute the update
    connection.execute(update_stmt)

    # Set the column to NOT NULL and add primary key
    op.alter_column('cor_cycles_placettes', 'id_cycle_placette', existing_type=sa.Integer, nullable=False, schema=schema)
    op.create_primary_key('pk_cor_cycles_placettes', 'cor_cycles_placettes', ['id_cycle_placette'], schema=schema)

    # Step 4: Repopulate the integer foreign key column in t_regenerations and t_transects
    t_regenerations = sa.Table('t_regenerations', metadata, autoload=True, autoload_with=connection, schema=schema)
    t_transects = sa.Table('t_transects', metadata, autoload=True, autoload_with=connection, schema=schema)

    # Update the foreign key in t_regenerations and t_transects
    connection.execute(
        t_regenerations.update().values(
            id_cycle_placette=sa.select([cor_cycles_placettes.c.id_cycle_placette]).where(cor_cycles_placettes.c.new_id_cycle_placette == t_regenerations.c.temp_id_cycle_placette)
        )
    )
    connection.execute(
        t_transects.update().values(
            id_cycle_placette=sa.select([cor_cycles_placettes.c.id_cycle_placette]).where(cor_cycles_placettes.c.new_id_cycle_placette == t_transects.c.temp_id_cycle_placette)
        )
    )

    # Step 3: Drop the temporary UUID column in t_regenerations and t_transects
    op.drop_column('t_regenerations', 'temp_id_cycle_placette', schema=schema)
    op.drop_column('t_transects', 'temp_id_cycle_placette', schema=schema)

    # Recreate the original foreign key constraint
    op.create_foreign_key('fk_t_regenerations_cor_cycles_placettes', 't_regenerations', 'cor_cycles_placettes', ['id_cycle_placette'], ['id_cycle_placette'],ondelete='CASCADE', source_schema=schema, referent_schema=schema)
    op.create_foreign_key('fk_t_transects_cor_cycles_placettes', 't_transects', 'cor_cycles_placettes', ['id_cycle_placette'], ['id_cycle_placette'],ondelete='CASCADE', source_schema=schema, referent_schema=schema)

    # Step 1: Drop the temporary UUID column in cor_cycles_placettes
    op.drop_column('cor_cycles_placettes', 'new_id_cycle_placette', schema=schema)





    # Regeneration
    # Reverse Step 4: Rename UUID column back to a temporary name
    op.alter_column('t_regenerations', 'id_regeneration', new_column_name='new_id_regeneration', schema=schema)

    # Reverse Step 3: Recreate the original integer primary key column without a default value
    op.add_column('t_regenerations', sa.Column('id_regeneration', sa.Integer, autoincrement=False, nullable=True), schema=schema)

    # Create an engine (or use an existing one)
    bind = op.get_bind()
    metadata = sa.MetaData(bind=bind)
    t_regenerations = sa.Table('t_regenerations', metadata, autoload=True, autoload_with=bind, schema=schema)

    # Check if the primary key constraint 'pk_t_regenerations' exists and drop it if it does
    insp = sa.inspect(bind)
    pk_constraint = insp.get_pk_constraint('t_regenerations', schema=schema)
    if pk_constraint and 'pk_t_regenerations' in pk_constraint.get('name', []):
        op.drop_constraint('pk_t_regenerations', 't_regenerations', type_='primary', schema=schema)

    # Create a CTE that assigns row numbers to each row in t_regenerations
    row_number_cte = sa.select([
        t_regenerations.c.new_id_regeneration,
        sa.func.row_number().over(order_by=t_regenerations.c.new_id_regeneration).label('rn')
    ]).cte('row_number_cte')

    # Update t_regenerations by joining it with the CTE on new_id_regeneration
    update_stmt = t_regenerations.update().values(
        id_regeneration=row_number_cte.c.rn
    ).where(
        t_regenerations.c.new_id_regeneration == row_number_cte.c.new_id_regeneration
    )

    # Execute the update statement
    bind.execute(update_stmt)

    op.alter_column('t_regenerations', 'id_regeneration', existing_type=sa.Integer, nullable=False, schema=schema)
    op.create_primary_key('pk_t_regenerations', 't_regenerations', ['id_regeneration'], schema=schema)

    # Drop the temporary UUID column
    op.drop_column('t_regenerations', 'new_id_regeneration', schema=schema)


    # Transect
    # Reverse Step 4: Rename UUID column back to a temporary name
    op.alter_column('t_transects', 'id_transect', new_column_name='new_id_transect', schema=schema)

    # Reverse Step 3: Recreate the original integer primary key column without a default value
    op.add_column('t_transects', sa.Column('id_transect', sa.Integer, autoincrement=False, nullable=True), schema=schema)

    # Create an engine (or use an existing one)
    bind = op.get_bind()
    metadata = sa.MetaData(bind=bind)
    t_transects = sa.Table('t_transects', metadata, autoload=True, autoload_with=bind, schema=schema)

    # Check if the primary key constraint 'pk_t_transects' exists and drop it if it does
    insp = sa.inspect(bind)
    pk_constraint = insp.get_pk_constraint('t_transects', schema=schema)
    if pk_constraint and 'pk_t_transects' in pk_constraint.get('name', []):
        op.drop_constraint('pk_t_transects', 't_transects', type_='primary', schema=schema)

    # Create a CTE that assigns row numbers to each row in t_transects
    row_number_cte = sa.select([
        t_transects.c.new_id_transect,
        sa.func.row_number().over(order_by=t_transects.c.new_id_transect).label('rn')
    ]).cte('row_number_cte')

    # Update t_transects by joining it with the CTE on new_id_transect
    update_stmt = t_transects.update().values(
        id_transect=row_number_cte.c.rn
    ).where(
        t_transects.c.new_id_transect == row_number_cte.c.new_id_transect
    )

    # Execute the update statement
    bind.execute(update_stmt)

    op.alter_column('t_transects', 'id_transect', existing_type=sa.Integer, nullable=False, schema=schema)
    op.create_primary_key('pk_t_transects', 't_transects', ['id_transect'], schema=schema)

    # Drop the temporary UUID column
    op.drop_column('t_transects', 'new_id_transect', schema=schema)


