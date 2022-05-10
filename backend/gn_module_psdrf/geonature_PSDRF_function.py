from geonature.utils.env import DB

def get_id_type_from_mnemonique(mnemonique_name):
    # set 'IMPORT' as variable initialized in configuration parameter ?
    try:
        id_type = DB.session.execute("""
            SELECT id_type
            FROM ref_nomenclatures.bib_nomenclatures_types
            WHERE mnemonique = '{mnemonique_name}';
            """.format(
                mnemonique_name=mnemonique_name
            )
        ).fetchone()[0]
        return id_type
    except Exception:
        raise

def get_mnemonique_from_id(id_type):
    # set 'IMPORT' as variable initialized in configuration parameter ?
    try:
        mnemonique = DB.session.execute("""
            SELECT mnemonique
            FROM ref_nomenclatures.bib_nomenclatures_types
            WHERE id_type = '{id_type}';
            """.format(
                id_type=id_type
            )).fetchone()[0]
        return mnemonique
    except Exception:
        raise

def get_id_nomenclature_from_id_type_and_cd_nomenclature(id_type, cd_nomenclature):
    # set 'IMPORT' as variable initialized in configuration parameter ?
    try:
        id_nomenclature = DB.session.execute("""
            SELECT id_nomenclature
            FROM ref_nomenclatures.t_nomenclatures
            WHERE id_type = '{id_type}'
            AND cd_nomenclature = '{cd_nomenclature}';
            """.format(
                id_type=id_type,
                cd_nomenclature=cd_nomenclature
            )).fetchone()[0]
        return id_nomenclature
    except Exception:
        raise

def get_cd_nomenclature_from_id_type_and_id_nomenclature(id_type, id_nomenclature):
    # set 'IMPORT' as variable initialized in configuration parameter ?
    try:
        cd_nomenclature = DB.session.execute("""
            SELECT cd_nomenclature
            FROM ref_nomenclatures.t_nomenclatures
            WHERE id_type = '{id_type}'
            AND id_nomenclature = '{id_nomenclature}';
            """.format(
                id_type=id_type,
                id_nomenclature=id_nomenclature
            )).fetchone()[0]
        return cd_nomenclature
    except Exception:
        raise