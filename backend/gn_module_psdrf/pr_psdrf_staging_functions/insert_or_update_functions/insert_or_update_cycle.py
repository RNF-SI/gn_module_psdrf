from ..models_staging import TCyclesStaging

def insert_or_update_cycle(data, session):
    """
    Insert or update a cycle in the database based on the provided data.
    :param data: The data of the cycle to be inserted or updated.
    :param session: The SQLAlchemy session to use for database operations.
    :return: The result of the operation.
    """
    try:
        existing_cycle = session.query(TCyclesStaging).filter_by(id_cycle=data['id_cycle']).first()

        if existing_cycle:
            existing_cycle.id_dispositif = data.get('id_dispositif', existing_cycle.id_dispositif)
            existing_cycle.num_cycle = data.get('num_cycle', existing_cycle.num_cycle)
            existing_cycle.date_debut = data.get('date_debut', existing_cycle.date_debut)
            existing_cycle.date_fin = data.get('date_fin', existing_cycle.date_fin)
            existing_cycle.monitor = data.get('monitor', existing_cycle.monitor)
            return "Cycle updated successfully."
        else:
            new_cycle = TCyclesStaging(
                id_cycle=data['id_cycle'],
                id_dispositif=data['id_dispositif'],
                num_cycle=data['num_cycle'],
                date_debut=data.get('date_debut', None),
                date_fin=data.get('date_fin', None),
                monitor=data.get('monitor', None)
            )
            session.add(new_cycle)
            return "Cycle inserted successfully."
    except Exception as e:
        print("Error in insert_or_update_cycle: ", str(e))
        raise e
