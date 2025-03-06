from ..models_staging import TDispositifsStaging

def insert_or_update_dispositif(data, session):
    """
    Insert or update a dispositif in the database based on the provided data.
    :param data: The data of the dispositif to be inserted or updated.
    :param session: The SQLAlchemy session to use for database operations.
    :return: The result of the operation.
    """
    try:
        existing_dispositif = session.query(TDispositifsStaging).filter_by(id_dispositif=data['id_dispositif']).first()

        if existing_dispositif:
            existing_dispositif.name = data.get('name', existing_dispositif.name)
            existing_dispositif.id_organisme = data.get('id_organisme', existing_dispositif.id_organisme)
            existing_dispositif.alluvial = data.get('alluvial', existing_dispositif.alluvial)
            return "Dispositif updated successfully."
        else:
            new_dispositif = TDispositifsStaging(
                id_dispositif=data['id_dispositif'],
                name=data['name'],
                id_organisme=data.get('id_organisme', None),
                alluvial=data.get('alluvial', False)
            )
            session.add(new_dispositif)
            return "Dispositif inserted successfully."
    except Exception as e:
        print("Error in insert_or_update_dispositif: ", str(e))
        raise e
