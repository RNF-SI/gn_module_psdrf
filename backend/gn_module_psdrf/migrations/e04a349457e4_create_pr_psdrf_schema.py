"""create_pr_psdrf_schema

Revision ID: e04a349457e4
Revises: 
Create Date: 2021-07-21 18:38:24.512562

"""
from alembic import op
from sqlalchemy.sql import text
import pkg_resources

from geonature.utils.config import config


# revision identifiers, used by Alembic.
revision = 'e04a349457e4'
down_revision = None
branch_labels = ('psdrf',)
depends_on = None


schema = 'pr_psdrf'


def upgrade():
    sql_files = ['schema.sql', 'data.sql']
    for sql_file in sql_files:
        operations = pkg_resources.resource_string("gn_module_psdrf.migrations", f"data/{sql_file}").decode('utf-8')
        op.get_bind().execute(text(operations), MYLOCALSRID=config['LOCAL_SRID'])


def downgrade():
    op.execute(f'DROP SCHEMA {schema} CASCADE')
    op.execute("DELETE FROM ref_nomenclatures.t_nomenclatures WHERE source = 'PSDRF'")
    op.execute("DELETE FROM ref_nomenclatures.bib_nomenclatures_types WHERE source = 'PSDRF'")
    op.execute("DELETE FROM ref_geo.bib_areas_types WHERE type_code = 'PRBIOL'")
    op.execute("DELETE FROM ref_geo.bib_areas_types WHERE type_code = 'FDOM'")
    op.execute("DELETE FROM ref_geo.bib_areas_types WHERE type_code = 'RBIOLD'")
    op.execute("DELETE FROM ref_geo.bib_areas_types WHERE type_code = 'X'")
