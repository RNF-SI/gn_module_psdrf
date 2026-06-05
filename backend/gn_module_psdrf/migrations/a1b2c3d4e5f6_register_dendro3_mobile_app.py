"""register dendro3 mobile app in gn_commons.t_mobile_apps

dendro3 (application Flutter terrain PSDRF) est enregistrée dans la table
standard GeoNature gn_commons.t_mobile_apps, qui devient la source unique de
vérité pour la version et le chemin de l'APK. La route standard
GET /gn_commons/t_mobile_apps et la route pont GET /psdrf/mobile-app lisent
toutes deux cette ligne, sans duplication de la donnée.

Revision ID: a1b2c3d4e5f6
Revises: 2115ba146beb
Create Date: 2026-06-03

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "2115ba146beb"
branch_labels = None
depends_on = None


def upgrade():
    # version_code = Android versionCode courant (entier sous forme de chaîne).
    #   C'est LE champ comparé par le client pour décider d'une mise à jour.
    #   Pour publier une nouvelle version : bumper cette valeur ET déposer le
    #   nouvel APK (voir relative_path_apk).
    # relative_path_apk = chemin RELATIF au dossier {MEDIA_FOLDER}/mobile/
    #   (le préfixe "mobile/" est ajouté par GeoNature à la construction d'URL).
    #   Le binaire doit donc être déposé dans :
    #   {MEDIA_FOLDER}/mobile/dendro3/dendro3-1.0.2.apk
    op.execute(
        """
        INSERT INTO gn_commons.t_mobile_apps
            (app_code, package, version_code, relative_path_apk)
        VALUES
            ('dendro3', 'org.reserves_naturelles.dendro3', '1', 'dendro3/dendro3-1.0.2.apk')
        ON CONFLICT (app_code) DO UPDATE SET
            package = EXCLUDED.package,
            version_code = EXCLUDED.version_code,
            relative_path_apk = EXCLUDED.relative_path_apk
        """
    )


def downgrade():
    op.execute(
        """
        DELETE FROM gn_commons.t_mobile_apps WHERE app_code = 'dendro3'
        """
    )
