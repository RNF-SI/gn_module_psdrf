from ..models_staging import TPlacettesStaging

def insert_or_update_placette(data, session):
    try:
        existing_placette = session.query(TPlacettesStaging).filter_by(id_placette=data['id_placette']).first()

        if existing_placette:
            existing_placette.id_dispositif = data.get('id_dispositif', existing_placette.id_dispositif)
            existing_placette.id_placette_orig = data.get('id_placette_orig', existing_placette.id_placette_orig)
            existing_placette.strate = data.get('strate', existing_placette.strate)
            existing_placette.pente = data.get('pente', existing_placette.pente)
            existing_placette.poids_placette = data.get('poids_placette', existing_placette.poids_placette)
            existing_placette.correction_pente = data.get('correction_pente', existing_placette.correction_pente)
            existing_placette.exposition = data.get('exposition', existing_placette.exposition)

            return "Placette updated successfully."
        else:
            new_placette = TPlacettesStaging(
                id_placette=data['id_placette'],
                id_dispositif=data['id_dispositif'],
                id_placette_orig=data.get('id_placette_orig', None),
                strate=data.get('strate', None),
                pente=data.get('pente', None),
                poids_placette=data.get('poids_placette', None),
                correction_pente=data.get('correction_pente', None),
                exposition=data.get('exposition', None),
            )
            session.add(new_placette)
            return "Placette inserted successfully."
    except Exception as e:
        print("Error in insert_or_update_placette: ", str(e))
        raise e
