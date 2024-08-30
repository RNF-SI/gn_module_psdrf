from ..models_staging import TArbresMesuresStaging

def insert_update_or_delete_arbre_mesure(category, arbre_category, id_arbre, arbre_data, arbre_mesure_data, session):
    counts_arbre_mesure = {
        'created': 0,
        'updated': 0,
        'deleted': 0
    }

    try:
        if category == 'deleted':
            # Delete logic
            arbre_mesure_to_delete = session.query(TArbresMesuresStaging).filter_by(
                id_arbre_mesure=arbre_mesure_data['id_arbre_mesure']
            ).first()
            if arbre_mesure_to_delete:
                session.delete(arbre_mesure_to_delete)
                counts_arbre_mesure['deleted'] += 1

        elif category == 'updated':
            existing_arbre_mesure = session.query(TArbresMesuresStaging).filter_by(
                id_arbre_mesure=arbre_mesure_data['id_arbre_mesure']
            ).first()

            if existing_arbre_mesure:
                existing_arbre_mesure.diametre1 = arbre_mesure_data.get('diametre1', existing_arbre_mesure.diametre1)
                existing_arbre_mesure.diametre2 = arbre_mesure_data.get('diametre2', existing_arbre_mesure.diametre2)
                existing_arbre_mesure.type = arbre_mesure_data.get('type', existing_arbre_mesure.type)
                existing_arbre_mesure.hauteur_totale = arbre_mesure_data.get('hauteur_totale', existing_arbre_mesure.hauteur_totale)
                existing_arbre_mesure.hauteur_branche = arbre_mesure_data.get('hauteur_branche', existing_arbre_mesure.hauteur_branche)
                existing_arbre_mesure.stade_durete = arbre_mesure_data.get('stade_durete', existing_arbre_mesure.stade_durete)
                existing_arbre_mesure.stade_ecorce = arbre_mesure_data.get('stade_ecorce', existing_arbre_mesure.stade_ecorce)
                existing_arbre_mesure.liane = arbre_mesure_data.get('liane', existing_arbre_mesure.liane)
                existing_arbre_mesure.diametre_liane = arbre_mesure_data.get('diametre_liane', existing_arbre_mesure.diametre_liane)
                existing_arbre_mesure.coupe = arbre_mesure_data.get('coupe', existing_arbre_mesure.coupe)
                existing_arbre_mesure.limite = arbre_mesure_data.get('limite', existing_arbre_mesure.limite)
                existing_arbre_mesure.id_nomenclature_code_sanitaire = arbre_mesure_data.get('id_nomenclature_code_sanitaire', existing_arbre_mesure.id_nomenclature_code_sanitaire)
                existing_arbre_mesure.code_ecolo = arbre_mesure_data.get('code_ecolo', existing_arbre_mesure.code_ecolo)
                existing_arbre_mesure.ref_code_ecolo = arbre_mesure_data.get('ref_code_ecolo', existing_arbre_mesure.ref_code_ecolo)
                existing_arbre_mesure.ratio_hauteur = arbre_mesure_data.get('ratio_hauteur', existing_arbre_mesure.ratio_hauteur)
                existing_arbre_mesure.observation = arbre_mesure_data.get('observation', existing_arbre_mesure.observation)
                existing_arbre_mesure.updated_by = arbre_mesure_data.get('updated_by', existing_arbre_mesure.updated_by)
                existing_arbre_mesure.updated_on = arbre_mesure_data.get('updated_on', existing_arbre_mesure.updated_on)
                existing_arbre_mesure.updated_at = arbre_mesure_data.get('updated_at', existing_arbre_mesure.updated_at)
                counts_arbre_mesure['updated'] += 1

        elif category == 'created':
            existing_arbre_mesure = session.query(TArbresMesuresStaging).filter_by(
                id_arbre_mesure=arbre_mesure_data['id_arbre_mesure']
            ).first()

            if existing_arbre_mesure is None:
                new_arbre_mesure = TArbresMesuresStaging(
                    id_arbre_mesure=arbre_mesure_data.get('id_arbre_mesure'),
                    id_arbre=id_arbre,
                    id_cycle=arbre_mesure_data.get('id_cycle', None),
                    diametre1=arbre_mesure_data.get('diametre1', None),
                    diametre2=arbre_mesure_data.get('diametre2', None),
                    type=arbre_mesure_data.get('type', None),
                    hauteur_totale=arbre_mesure_data.get('hauteur_totale', None),
                    hauteur_branche=arbre_mesure_data.get('hauteur_branche', None),
                    stade_durete=arbre_mesure_data.get('stade_durete', None),
                    stade_ecorce=arbre_mesure_data.get('stade_ecorce', None),
                    liane=arbre_mesure_data.get('liane', None),
                    diametre_liane=arbre_mesure_data.get('diametre_liane', None),
                    coupe=arbre_mesure_data.get('coupe', None),
                    limite=arbre_mesure_data.get('limite', None),
                    id_nomenclature_code_sanitaire=arbre_mesure_data.get('id_nomenclature_code_sanitaire', None),
                    code_ecolo=arbre_mesure_data.get('code_ecolo', None),
                    ref_code_ecolo=arbre_mesure_data.get('ref_code_ecolo', None),
                    ratio_hauteur=arbre_mesure_data.get('ratio_hauteur', None),
                    observation=arbre_mesure_data.get('observation', None),
                    created_by=arbre_mesure_data.get('created_by', None),
                    updated_by=arbre_mesure_data.get('updated_by', None),
                    created_on=arbre_mesure_data.get('created_on', None),
                    updated_on=arbre_mesure_data.get('updated_on', None),
                    created_at=arbre_mesure_data.get('created_at', None),
                    updated_at=arbre_mesure_data.get('updated_at', None)
                )
                session.add(new_arbre_mesure)
                counts_arbre_mesure['created'] += 1

        return counts_arbre_mesure

    except Exception as e:
        print("Error in insert_update_or_delete_arbre_mesure: ", str(e))
        raise e
