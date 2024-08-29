from ..models_staging import TTransectsStaging

def insert_or_update_transect(category, cor_cycle_placette_category, cor_cycle_placette_id, transect_data, session):
    try:
        counts_transect = {
            'created': 0,
            'updated': 0,
            'deleted': 0
        }

        if category == 'created':
            existing_transect = session.query(TTransectsStaging).filter_by(
                id_transect=transect_data.get('id_transect')
            ).first()

            if existing_transect is None:
                new_transect = TTransectsStaging(
                    id_transect=transect_data.get('id_transect'),
                    id_cycle_placette=cor_cycle_placette_id,
                    id_transect_orig=transect_data.get('id_transect_orig'),
                    code_essence=transect_data.get('code_essence'),
                    ref_transect=transect_data.get('ref_transect'),
                    distance=transect_data.get('distance'),
                    orientation=transect_data.get('orientation'),
                    azimut_souche=transect_data.get('azimut_souche'),
                    distance_souche=transect_data.get('distance_souche'),
                    diametre=transect_data.get('diametre'),
                    diametre_130=transect_data.get('diametre_130'),
                    ratio_hauteur=transect_data.get('ratio_hauteur'),
                    contact=transect_data.get('contact'),
                    angle=transect_data.get('angle'),
                    chablis=transect_data.get('chablis'),
                    stade_durete=transect_data.get('stade_durete'),
                    stade_ecorce=transect_data.get('stade_ecorce'),
                    observation=transect_data.get('observation'),
                    created_by=transect_data.get('created_by'),
                    created_on=transect_data.get('created_on'),
                    created_at=transect_data.get('created_at'),
                    updated_by=transect_data.get('updated_by'),
                    updated_on=transect_data.get('updated_on'),
                    updated_at=transect_data.get('updated_at'), 
                )
                session.add(new_transect)
                session.commit()
                counts_transect['created'] += 1

        elif category == 'updated':
            existing_transect = session.query(TTransectsStaging).filter_by(
                id_transect=transect_data['id_transect']
            ).first()
            if existing_transect:
                existing_transect.id_cycle_placette = transect_data.get('id_cycle_placette', existing_transect.id_cycle_placette)
                existing_transect.id_transect_orig = transect_data.get('id_transect_orig', existing_transect.id_transect_orig)
                existing_transect.code_essence = transect_data.get('code_essence', existing_transect.code_essence)
                existing_transect.ref_transect = transect_data.get('ref_transect', existing_transect.ref_transect)
                existing_transect.distance = transect_data.get('distance', existing_transect.distance)
                existing_transect.orientation = transect_data.get('orientation', existing_transect.orientation)
                existing_transect.azimut_souche = transect_data.get('azimut_souche', existing_transect.azimut_souche)
                existing_transect.distance_souche = transect_data.get('distance_souche', existing_transect.distance_souche)
                existing_transect.diametre = transect_data.get('diametre', existing_transect.diametre)
                existing_transect.diametre_130 = transect_data.get('diametre_130', existing_transect.diametre_130)
                existing_transect.ratio_hauteur = transect_data.get('ratio_hauteur', existing_transect.ratio_hauteur)
                existing_transect.contact = transect_data.get('contact', existing_transect.contact)
                existing_transect.angle = transect_data.get('angle', existing_transect.angle)
                existing_transect.chablis = transect_data.get('chablis', existing_transect.chablis)
                existing_transect.stade_durete = transect_data.get('stade_durete', existing_transect.stade_durete)
                existing_transect.stade_ecorce = transect_data.get('stade_ecorce', existing_transect.stade_ecorce)
                existing_transect.observation = transect_data.get('observation', existing_transect.observation)
                existing_transect.updated_by = transect_data.get('updated_by', existing_transect.updated_by)
                existing_transect.updated_on = transect_data.get('updated_on', existing_transect.updated_on)
                existing_transect.updated_at = transect_data.get('updated_at', existing_transect.updated_at)
  
                session.commit()
                counts_transect['updated'] += 1

        elif category == 'deleted':
            transect_to_delete = session.query(TTransectsStaging).filter_by(
                id_transect=transect_data['id_transect']
            ).first()
            if transect_to_delete:
                session.delete(transect_to_delete)
                session.commit()
                counts_transect['deleted'] += 1

        return counts_transect

    except Exception as e:
        session.rollback()
        print("Error in insert_or_update_transect: ", str(e))
        raise e
