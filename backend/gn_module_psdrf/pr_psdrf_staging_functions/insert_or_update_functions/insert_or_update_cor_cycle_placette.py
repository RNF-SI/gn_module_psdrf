from ..models_staging import CorCyclesPlacettesStaging
from geonature.utils.env import DB
from sqlalchemy import func
from .insert_or_update_regeneration import insert_or_update_regeneration
from .insert_or_update_transect import insert_or_update_transect

def insert_or_update_cor_cycle_placette(placette_data):
    try:
        results = []
        # define id_cycle_placette
        id_cycle_placette = None
        if 'corCyclesPlacettes' in placette_data:
            cors_cycles_placettes_data = placette_data['corCyclesPlacettes']

            # Process each category: 'created', 'updated', 'deleted'
            for category in ['created', 'updated', 'deleted']:
                if category in cors_cycles_placettes_data:
                    for cor_cycle_placette_item_data in cors_cycles_placettes_data[category]:
                        id_cycle_placette = None
                        if category == 'created':
                            max_id_cycle_placette= DB.session.query(func.max(CorCyclesPlacettesStaging.id_cycle_placette)).scalar()
                            new_id_cycle_placette = (max_id_cycle_placette or 0) + 1

                            new_cor_cycle_placette = CorCyclesPlacettesStaging(
                                id_cycle_placette=new_id_cycle_placette,
                                id_cycle=cor_cycle_placette_item_data.get('id_cycle'),
                                id_placette=cor_cycle_placette_item_data.get('id_placette'),
                                date_releve=cor_cycle_placette_item_data.get('date_releve'),
                                date_intervention=cor_cycle_placette_item_data.get('date_intervention'),
                                annee=cor_cycle_placette_item_data.get('annee'),
                                nature_intervention=cor_cycle_placette_item_data.get('nature_intervention'),
                                gestion_placette=cor_cycle_placette_item_data.get('gestion_placette'),
                                # ... add any other fields as necessary ...
                            )
                            DB.session.add(new_cor_cycle_placette)
                            DB.session.commit()
                            results.append({
                                "message": "CorCyclePlacette created successfully.", 
                                "status": "created", 
                                "old_id": cor_cycle_placette_item_data.get("id_cycle_placette"),  # Assuming this is the old arbre ID
                                "new_id": new_cor_cycle_placette.id_cycle_placette
                                })
                            id_cycle_placette = new_cor_cycle_placette.id_cycle_placette

                        if category == 'updated':
                            existing_cor_cycle_placette = DB.session.query(CorCyclesPlacettesStaging).filter_by(
                                id_cycle_placette=cor_cycle_placette_item_data['id_cycle_placette'],
                            ).first()

                            if existing_cor_cycle_placette:
                                # ... update existing fields from cor_cycle_placette_data ...
                                existing_cor_cycle_placette.id_cycle = cor_cycle_placette_item_data.get('id_cycle', existing_cor_cycle_placette.id_cycle)
                                existing_cor_cycle_placette.id_placette = cor_cycle_placette_item_data.get('id_placette', existing_cor_cycle_placette.id_placette)
                                existing_cor_cycle_placette.date_releve = cor_cycle_placette_item_data.get('date_releve', existing_cor_cycle_placette.date_releve)
                                existing_cor_cycle_placette.date_intervention = cor_cycle_placette_item_data.get('date_intervention', existing_cor_cycle_placette.date_intervention)
                                existing_cor_cycle_placette.annee = cor_cycle_placette_item_data.get('annee', existing_cor_cycle_placette.annee)
                                existing_cor_cycle_placette.nature_intervention = cor_cycle_placette_item_data.get('nature_intervention', existing_cor_cycle_placette.nature_intervention)
                                existing_cor_cycle_placette.gestion_placette = cor_cycle_placette_item_data.get('gestion_placette', existing_cor_cycle_placette.gestion_placette)
                    
                                DB.session.commit()
                                results.append({
                                    "message": "CorCyclePlacette updated successfully.", 
                                    "status": "updated", 
                                    "old_id": cor_cycle_placette_item_data.get("id_arbre"),
                                    "new_id": existing_cor_cycle_placette.id_arbre 
                                    })
                                id_cycle_placette = existing_cor_cycle_placette.id_cycle_placette

                        elif category == 'deleted':
                            cor_cycle_placette_to_delete = DB.session.query(CorCyclesPlacettesStaging).filter_by(
                                id_cycle_placette=cor_cycle_placette_item_data['id_cycle_placette'],
                            ).first()
                            if cor_cycle_placette_to_delete:
                                DB.session.delete(cor_cycle_placette_to_delete)
                                DB.session.commit()
                                results.append({
                                    "message": "CorCyclePlacette deleted successfully.", 
                                    "status": "deleted", 
                                    "old_id": cor_cycle_placette_item_data.get("id_arbre"),
                                    "new_id": existing_cor_cycle_placette.id_arbre 
                                    
                                    })
                                
                        # Now process arbres_mesures within each arbre
                        if 'regenerations' in cor_cycle_placette_item_data:
                            for regeneration_category in ['created', 'updated', 'deleted']:
                                for regeneration_data in cor_cycle_placette_item_data['regenerations'][regeneration_category]:
                                    regeneration_results = insert_or_update_regeneration(
                                        category= regeneration_category,
                                        cor_cycle_placette_category=category,
                                        cor_cycle_placette_id=id_cycle_placette,  # Pass the current arbre data
                                        regeneration_data=regeneration_data
                                    )
                                    if regeneration_results:
                                        results.extend(regeneration_results)

                        # Now process arbres_mesures within each arbre
                        if 'transects' in cor_cycle_placette_item_data:
                            for transect_category in ['created', 'updated', 'deleted']:
                                for transect_data in cor_cycle_placette_item_data['transects'][transect_category]:
                                    transect_results = insert_or_update_transect(
                                        category= transect_category,
                                        cor_cycle_placette_category=category,
                                        cor_cycle_placette_id=id_cycle_placette,  # Pass the current arbre data
                                        transect_data=transect_data
                                    )
                                    if transect_results:
                                        results.extend(transect_results)



        return results

    except Exception as e:
        DB.session.rollback()
        print("Error in insert_or_update_cor_cycle_placette: ", str(e))
        raise e
