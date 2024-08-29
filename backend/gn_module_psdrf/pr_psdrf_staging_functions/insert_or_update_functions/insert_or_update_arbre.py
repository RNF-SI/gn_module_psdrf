from ..models_staging import TArbresStaging
from sqlalchemy import func
from .insert_or_update_arbre_mesure import insert_update_or_delete_arbre_mesure
from sqlalchemy.exc import IntegrityError

def insert_update_or_delete_arbre(placette_data, session):
    try:
        counts_arbre = {
            'created': 0,
            'updated': 0,
            'deleted': 0
        }
        counts_arbre_mesure = {
            'created': 0,
            'updated': 0,
            'deleted': 0
        }
        created_arbres = []

        if 'arbres' in placette_data:
            arbres_data = placette_data['arbres']

            for category in ['created', 'updated', 'deleted']:
                if category in arbres_data:
                    for arbre_data in arbres_data[category]:
                        id_arbre = arbre_data.get('id_arbre')
                        existing_arbre = session.query(TArbresStaging).filter_by(
                            id_arbre=id_arbre
                        ).first()

                        if category == 'created':
                            if existing_arbre is None:
                                max_id_arbre_orig = session.query(func.max(TArbresStaging.id_arbre_orig)).filter_by(
                                    id_placette=arbre_data.get('id_placette')
                                ).scalar()
                                new_id_arbre_orig = (max_id_arbre_orig or 0) + 1
                                new_arbre = TArbresStaging(
                                    id_arbre=id_arbre,
                                    id_arbre_orig=new_id_arbre_orig,
                                    id_placette=arbre_data.get('id_placette'),
                                    code_essence=arbre_data.get('code_essence'),
                                    azimut=arbre_data.get('azimut'),
                                    distance=arbre_data.get('distance'),
                                    taillis=arbre_data.get('taillis', False),
                                    observation=arbre_data.get('observation'),
                                    created_by=arbre_data.get('created_by'),
                                    updated_by=arbre_data.get('updated_by'),
                                    created_on=arbre_data.get('created_on'),
                                    updated_on=arbre_data.get('updated_on'),
                                    created_at=arbre_data.get('created_at'),
                                    updated_at=arbre_data.get('updated_at'),
                                )
                                try:
                                    session.add(new_arbre)
                                    session.flush()  # Flush to get the auto-generated id_arbre
                                    created_arbres.append(
                                        {
                                            "status": "created",
                                            "id": new_arbre.id_arbre,
                                            "new_id_arbre_orig": new_id_arbre_orig
                                        }
                                    )
                                    counts_arbre['created'] += 1
                                    id_arbre = new_arbre.id_arbre
                                except IntegrityError:
                                    session.rollback()
                                    print("Duplicate entry found for id_arbre: ", id_arbre)
                                    continue  # Skip this entry to avoid duplicate

                        elif category == 'updated':
                            if existing_arbre:
                                existing_arbre.code_essence = arbre_data.get('code_essence', existing_arbre.code_essence)
                                existing_arbre.azimut = arbre_data.get('azimut', existing_arbre.azimut)
                                existing_arbre.distance = arbre_data.get('distance', existing_arbre.distance)
                                existing_arbre.taillis = arbre_data.get('taillis', existing_arbre.taillis)
                                existing_arbre.observation = arbre_data.get('observation', existing_arbre.observation)
                                existing_arbre.updated_by = arbre_data.get('updated_by', existing_arbre.updated_by)
                                existing_arbre.updated_on = arbre_data.get('updated_on', existing_arbre.updated_on)
                                existing_arbre.updated_at = arbre_data.get('updated_at', existing_arbre.updated_at)
                                counts_arbre['updated'] += 1
                                id_arbre = existing_arbre.id_arbre

                        elif category == 'deleted':
                            if existing_arbre:
                                session.delete(existing_arbre)
                                counts_arbre['deleted'] += 1

                        if 'arbres_mesures' in arbre_data:
                            for arbre_mesure_category in ['created', 'updated', 'deleted']:
                                if arbre_mesure_category in arbre_data['arbres_mesures']:
                                    for arbre_mesure_data in arbre_data['arbres_mesures'][arbre_mesure_category]:
                                        arbre_mesure_results = insert_update_or_delete_arbre_mesure(
                                            category=arbre_mesure_category,
                                            arbre_category=category,
                                            id_arbre=id_arbre,
                                            arbre_data=arbre_data,
                                            arbre_mesure_data=arbre_mesure_data,
                                            session=session
                                        )
                                        if arbre_mesure_results:
                                            counts_arbre_mesure[arbre_mesure_category] += arbre_mesure_results[arbre_mesure_category]

        session.commit()
        return created_arbres, counts_arbre, counts_arbre_mesure

    except Exception as e:
        session.rollback()
        print("Error in insert_update_or_delete_arbre: ", str(e))
        raise e
