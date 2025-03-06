from ..models_staging import TBmSup30MesuresStaging

def insert_update_or_delete_bms_mesure(category, bm_category, id_bm, bm_data, bms_mesure_data, session):
    counts_bm_mesure = {
        'created': 0,
        'updated': 0,
        'deleted': 0
    }

    try:
        if category == 'deleted':
            # Delete logic
            bms_mesure_to_delete = session.query(TBmSup30MesuresStaging).filter_by(
                id_bm_sup_30_mesure=bms_mesure_data['id_bm_sup_30_mesure']
            ).first()
            if bms_mesure_to_delete:
                session.delete(bms_mesure_to_delete)
                counts_bm_mesure['deleted'] += 1

        elif category == 'updated':
            existing_bms_mesure = session.query(TBmSup30MesuresStaging).filter_by(
                id_bm_sup_30_mesure=bms_mesure_data['id_bm_sup_30_mesure']
            ).first()

            if existing_bms_mesure:
                existing_bms_mesure.diametre_ini = bms_mesure_data.get('diametre_ini', existing_bms_mesure.diametre_ini)
                existing_bms_mesure.diametre_med = bms_mesure_data.get('diametre_med', existing_bms_mesure.diametre_med)
                existing_bms_mesure.diametre_fin = bms_mesure_data.get('diametre_fin', existing_bms_mesure.diametre_fin)
                existing_bms_mesure.diametre_130 = bms_mesure_data.get('diametre_130', existing_bms_mesure.diametre_130)
                existing_bms_mesure.longueur = bms_mesure_data.get('longueur', existing_bms_mesure.longueur)
                existing_bms_mesure.ratio_hauteur = bms_mesure_data.get('ratio_hauteur', existing_bms_mesure.ratio_hauteur)
                existing_bms_mesure.contact = bms_mesure_data.get('contact', existing_bms_mesure.contact)
                existing_bms_mesure.chablis = bms_mesure_data.get('chablis', existing_bms_mesure.chablis)
                existing_bms_mesure.stade_durete = bms_mesure_data.get('stade_durete', existing_bms_mesure.stade_durete)
                existing_bms_mesure.stade_ecorce = bms_mesure_data.get('stade_ecorce', existing_bms_mesure.stade_ecorce)
                existing_bms_mesure.observation = bms_mesure_data.get('observation', existing_bms_mesure.observation)
                existing_bms_mesure.updated_by = bms_mesure_data.get('updated_by', existing_bms_mesure.updated_by)
                existing_bms_mesure.updated_on = bms_mesure_data.get('updated_on', existing_bms_mesure.updated_on)
                existing_bms_mesure.updated_at = bms_mesure_data.get('updated_at', existing_bms_mesure.updated_at)
                counts_bm_mesure['updated'] += 1

        elif category == 'created':
            existing_bms_mesure = session.query(TBmSup30MesuresStaging).filter_by(
                id_bm_sup_30_mesure=bms_mesure_data['id_bm_sup_30_mesure']
            ).first()

            if existing_bms_mesure is None:
                new_bms_mesure = TBmSup30MesuresStaging(
                    id_bm_sup_30_mesure=bms_mesure_data.get('id_bm_sup_30_mesure'),
                    id_bm_sup_30=id_bm,
                    id_cycle=bms_mesure_data.get('id_cycle', None),
                    diametre_ini=bms_mesure_data.get('diametre_ini', None),
                    diametre_med=bms_mesure_data.get('diametre_med', None),
                    diametre_fin=bms_mesure_data.get('diametre_fin', None),
                    diametre_130=bms_mesure_data.get('diametre_130', None),
                    longueur=bms_mesure_data.get('longueur', None),
                    ratio_hauteur=bms_mesure_data.get('ratio_hauteur', None),
                    contact=bms_mesure_data.get('contact', None),
                    chablis=bms_mesure_data.get('chablis', None),
                    stade_durete=bms_mesure_data.get('stade_durete', None),
                    stade_ecorce=bms_mesure_data.get('stade_ecorce', None),
                    observation=bms_mesure_data.get('observation', None),
                    created_by=bms_mesure_data.get('created_by', None),
                    updated_by=bms_mesure_data.get('updated_by', None),
                    created_on=bms_mesure_data.get('created_on', None),
                    updated_on=bms_mesure_data.get('updated_on', None),
                    created_at=bms_mesure_data.get('created_at', None),
                    updated_at=bms_mesure_data.get('updated_at', None),
                )
                session.add(new_bms_mesure)
                counts_bm_mesure['created'] += 1

        return counts_bm_mesure

    except Exception as e:
        print("Error in insert_update_or_delete_bms_mesure: ", str(e))
        raise e
