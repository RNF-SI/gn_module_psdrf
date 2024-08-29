from ..models_staging import TRegenerationsStaging

def insert_or_update_regeneration(category, cor_cycle_placette_category, cor_cycle_placette_id, regeneration_data, session):
    try:
        counts_regeneration = {
            'created': 0,
            'updated': 0,
            'deleted': 0
        }

        if category == 'created':
            existing_regeneration = session.query(TRegenerationsStaging).filter_by(
                id_regeneration=regeneration_data.get('id_regeneration')
            ).first()

            if existing_regeneration is None:
                new_regeneration = TRegenerationsStaging(
                    id_regeneration=regeneration_data.get('id_regeneration'),
                    id_cycle_placette=cor_cycle_placette_id,
                    sous_placette=regeneration_data.get('sous_placette'),
                    code_essence=regeneration_data.get('code_essence'),
                    recouvrement=regeneration_data.get('recouvrement'),
                    classe1=regeneration_data.get('classe1'),
                    classe2=regeneration_data.get('classe2'),
                    classe3=regeneration_data.get('classe3'),
                    taillis=regeneration_data.get('taillis'),
                    abroutissement=regeneration_data.get('abroutissement'),
                    id_nomenclature_abroutissement=regeneration_data.get('id_nomenclature_abroutissement'),
                    observation=regeneration_data.get('observation'),
                    created_by=regeneration_data.get('created_by'),
                    created_on=regeneration_data.get('created_on'),
                    created_at=regeneration_data.get('created_at'),
                    updated_by=regeneration_data.get('updated_by'),
                    updated_on=regeneration_data.get('updated_on'),
                    updated_at=regeneration_data.get('updated_at'),
                )
                session.add(new_regeneration)
                session.commit()
                counts_regeneration['created'] += 1

        elif category == 'updated':
            existing_regeneration = session.query(TRegenerationsStaging).filter_by(
                id_regeneration=regeneration_data['id_regeneration']
            ).first()

            if existing_regeneration:
                existing_regeneration.id_cycle_placette = regeneration_data.get('id_cycle_placette', existing_regeneration.id_cycle_placette)
                existing_regeneration.sous_placette = regeneration_data.get('sous_placette', existing_regeneration.sous_placette)
                existing_regeneration.code_essence = regeneration_data.get('code_essence', existing_regeneration.code_essence)
                existing_regeneration.recouvrement = regeneration_data.get('recouvrement', existing_regeneration.recouvrement)
                existing_regeneration.classe1 = regeneration_data.get('classe1', existing_regeneration.classe1)
                existing_regeneration.classe2 = regeneration_data.get('classe2', existing_regeneration.classe2)
                existing_regeneration.classe3 = regeneration_data.get('classe3', existing_regeneration.classe3)
                existing_regeneration.taillis = regeneration_data.get('taillis', existing_regeneration.taillis)
                existing_regeneration.abroutissement = regeneration_data.get('abroutissement', existing_regeneration.abroutissement)
                existing_regeneration.id_nomenclature_abroutissement = regeneration_data.get('id_nomenclature_abroutissement', existing_regeneration.id_nomenclature_abroutissement)
                existing_regeneration.observation = regeneration_data.get('observation', existing_regeneration.observation)
                existing_regeneration.updated_by = regeneration_data.get('updated_by', existing_regeneration.updated_by)
                existing_regeneration.updated_on = regeneration_data.get('updated_on', existing_regeneration.updated_on)
                existing_regeneration.updated_at = regeneration_data.get('updated_at', existing_regeneration.updated_at)
                session.commit()
                counts_regeneration['updated'] += 1

        elif category == 'deleted':
            regeneration_to_delete = session.query(TRegenerationsStaging).filter_by(
                id_regeneration=regeneration_data['id_regeneration']
            ).first()
            if regeneration_to_delete:
                session.delete(regeneration_to_delete)
                session.commit()
                counts_regeneration['deleted'] += 1

        return counts_regeneration

    except Exception as e:
        session.rollback()
        print("Error in insert_or_update_regeneration: ", str(e))
        raise e
