from ..models_staging import TReperesStaging

def insert_update_or_delete_repere(placette_data, session):
    counts_repere = {
        'created': 0,
        'updated': 0,
        'deleted': 0
    }

    try:
        if 'reperes' in placette_data:
            reperes_data = placette_data['reperes']

            for category in ['created', 'updated', 'deleted']:
                if category in reperes_data:
                    for repere_data in reperes_data[category]:
                        id_repere = repere_data.get('id_repere')
                        existing_repere = session.query(TReperesStaging).filter_by(
                            id_repere=id_repere
                        ).first()

                        if category == 'created':
                            if existing_repere is None:
                                new_repere = TReperesStaging(
                                    id_repere=id_repere,
                                    id_placette=repere_data.get('id_placette'),
                                    azimut=repere_data.get('azimut'),
                                    distance=repere_data.get('distance'),
                                    diametre=repere_data.get('diametre'),
                                    repere=repere_data.get('repere'),
                                    observation=repere_data.get('observation'),
                                    created_by=repere_data.get('created_by'),
                                    created_on=repere_data.get('created_on'),
                                    created_at=repere_data.get('created_at'),
                                    updated_by=repere_data.get('updated_by'),
                                    updated_on=repere_data.get('updated_on'),
                                    updated_at=repere_data.get('updated_at'),
                                )
                                session.add(new_repere)
                                counts_repere['created'] += 1

                        elif category == 'updated':
                            if existing_repere:
                                existing_repere.azimut = repere_data.get('azimut', existing_repere.azimut)
                                existing_repere.distance = repere_data.get('distance', existing_repere.distance)
                                existing_repere.diametre = repere_data.get('diametre', existing_repere.diametre)
                                existing_repere.repere = repere_data.get('repere', existing_repere.repere)
                                existing_repere.observation = repere_data.get('observation', existing_repere.observation)
                                existing_repere.updated_by = repere_data.get('updated_by', existing_repere.updated_by)
                                existing_repere.updated_on = repere_data.get('updated_on', existing_repere.updated_on)
                                existing_repere.updated_at = repere_data.get('updated_at', existing_repere.updated_at)
                                counts_repere['updated'] += 1

                        elif category == 'deleted':
                            if existing_repere:
                                session.delete(existing_repere)
                                counts_repere['deleted'] += 1

        return counts_repere

    except Exception as e:
        print("Error in insert_update_or_delete_repere: ", str(e))
        raise e
