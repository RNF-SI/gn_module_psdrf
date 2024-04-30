from geonature.utils.env import DB
# import model relatively from parent of parent folder
from ..models_staging import TDispositifsStaging

def insert_or_update_dispositif(data):
    """
    Insert or update a dispositif in the database based on the provided data.
    :param data: The data of the dispositif to be inserted or updated.
    :return: The result of the operation.
    """
    try:
        existing_dispositif = DB.session.query(TDispositifsStaging).filter_by(id_dispositif=data['id_dispositif']).first()

        if existing_dispositif:
            existing_dispositif.name = data.get('name', existing_dispositif.name)
            existing_dispositif.id_organisme = data.get('id_organisme', existing_dispositif.id_organisme)
            existing_dispositif.alluvial = data.get('alluvial', existing_dispositif.alluvial)
            DB.session.commit()
            return "Dispositif updated successfully."
        else:
            new_dispositif = TDispositifsStaging(
                id_dispositif=data['id_dispositif'],
                name=data['name'],
                id_organisme=data.get('id_organisme', None),
                alluvial=data.get('alluvial', False)
            )
            DB.session.add(new_dispositif)
            DB.session.commit()
            return "Dispositif inserted successfully."
    except Exception as e:
        DB.session.rollback()
        print("Error in insert_or_update_dispositif: ", str(e))
        raise e