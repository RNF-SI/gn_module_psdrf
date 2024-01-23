from ..models_staging import TRegenerationsStaging
from geonature.utils.env import DB
from sqlalchemy import func

def insert_or_update_regeneration(category, cor_cycle_placette_category, cor_cycle_placette_id, regeneration_data):
    try:
        results = []

        # Handle created regenerations
        if category == 'created':
            
            max_id_regeneration= DB.session.query(func.max(TRegenerationsStaging.id_regeneration)).scalar()
            new_id_regeneration = (max_id_regeneration or 0) + 1

            new_regeneration = TRegenerationsStaging(
                id_regeneration=new_id_regeneration,
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
                # ... add any other fields as necessary ...
            )
            DB.session.add(new_regeneration)
            DB.session.commit()
            results.append({"message": "Regeneration created successfully.", "status": "created", "new_id": new_regeneration.id_regeneration})

        # Handle updated regenerations
        if category == 'updated': 
            existing_regeneration = DB.session.query(TRegenerationsStaging).filter_by(
                id_regeneration=regeneration_data['id_regeneration']
            ).first()

            if existing_regeneration:
                # Update existing fields from regeneration_data
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
    
                DB.session.commit()
                results.append({"message": "Regeneration updated successfully.", "status": "updated", "id": existing_regeneration.id_regeneration})

        # Handle deleted regenerations
        if category == 'deleted':
            regeneration_to_delete = DB.session.query(TRegenerationsStaging).filter_by(
                id_regeneration=regeneration_data['id_regeneration']
            ).first()
            if regeneration_to_delete:
                DB.session.delete(regeneration_to_delete)
                DB.session.commit()
                results.append({"message": "Regeneration deleted successfully.", "status": "deleted", "id": regeneration_to_delete.id_regeneration})

        return results

    except Exception as e:
        DB.session.rollback()
        print("Error in insert_or_update_regeneration: ", str(e))
        raise e
