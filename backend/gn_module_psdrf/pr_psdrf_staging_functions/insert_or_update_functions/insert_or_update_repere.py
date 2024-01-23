from ..models_staging import TReperesStaging
from geonature.utils.env import DB
from sqlalchemy import func

def insert_update_or_delete_repere(placette_data):
    try:
        results = []

        if 'reperes' in placette_data:
            reperes_data = placette_data['reperes']
            # Process each category: 'created', 'updated', 'deleted'
            for category in ['created', 'updated', 'deleted']:
                if category in reperes_data:
                    for repere_data in reperes_data[category]:
                        if category == 'created':
                            max_id_repere= DB.session.query(func.max(TReperesStaging.id_repere)).scalar()
                            new_id_repere = (max_id_repere or 0) + 1


                            new_repere = TReperesStaging(
                                id_repere=new_id_repere,
                                id_placette=repere_data.get('id_placette'),
                                azimut=repere_data.get('azimut'),
                                distance=repere_data.get('distance'),
                                diametre=repere_data.get('diametre'),
                                repere=repere_data.get('repere'),
                                observation=repere_data.get('observation')
                                # ... add any other fields as necessary ...
                            )
                            DB.session.add(new_repere)
                            DB.session.commit()
                            results.append({"message": "Repere created successfully.", "status": "created", "new_id": new_repere.id_repere})

                        if category == 'updated':
                            existing_repere = DB.session.query(TReperesStaging).filter_by(
                                id_repere=repere_data['id_repere']
                            ).first()
                            if existing_repere:
                                existing_repere.azimut = repere_data.get('azimut', existing_repere.azimut)
                                existing_repere.distance = repere_data.get('distance', existing_repere.distance)
                                existing_repere.diametre = repere_data.get('diametre', existing_repere.diametre)
                                existing_repere.repere = repere_data.get('repere', existing_repere.repere)
                                existing_repere.observation = repere_data.get('observation', existing_repere.observation)
                                # ... update any additional fields as necessary ...
                                DB.session.commit()
                                results.append({
                                    "status": "updated",
                                    "old_id": repere_data.get("id_arbre"),
                                    "new_id": existing_repere.id_arbre  # Assuming this is the updated arbre ID
                                })
                        elif category == 'deleted':
                            repere_to_delete = DB.session.query(TReperesStaging).filter_by(
                                id_repere=repere_data['id_repere']
                            ).first()
                            if repere_to_delete:
                                DB.session.delete(repere_to_delete)
                                DB.session.commit()
                                results.append({
                                    "message": "Repere deleted successfully.", 
                                    "status": "deleted", 
                                    "id": repere_to_delete.id_repere
                                    })

        return results

    except Exception as e:
        DB.session.rollback()
        print("Error in insert_update_or_delete_repere: ", str(e))
        raise e
