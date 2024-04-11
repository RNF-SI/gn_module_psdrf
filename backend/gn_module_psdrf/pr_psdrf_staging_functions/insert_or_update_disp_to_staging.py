from .insert_or_update_functions.insert_or_update_dispositif import insert_or_update_dispositif
from .insert_or_update_functions.insert_or_update_placette import insert_or_update_placette
from .insert_or_update_functions.insert_or_update_arbre import insert_update_or_delete_arbre
from .insert_or_update_functions.insert_or_update_bms import insert_update_or_delete_bms
from .insert_or_update_functions.insert_or_update_cycle import insert_or_update_cycle
from .insert_or_update_functions.insert_or_update_cor_cycle_placette import insert_or_update_cor_cycle_placette
from .insert_or_update_functions.insert_or_update_repere import insert_update_or_delete_repere

def insert_or_update_data(data):
    id_mappings = []
    print("start insert_or_update_data")
    try:
        if 'id_dispositif' in data:
            result = insert_or_update_dispositif(data)
            if 'cycles' in data:
                for cycle_data in data['cycles']:
                    cycle_result = insert_or_update_cycle(cycle_data)

            if 'placettes' in data:
                for placette_data in data['placettes']:
                    placette_result = insert_or_update_placette(placette_data)
                    
                    
                    arbre_results = insert_update_or_delete_arbre(placette_data)
                    for arbre_result in arbre_results:
                        if arbre_result:
                            id_mappings.append({
                                "type": "arbre",
                                "id": arbre_result.get("id"),
                                "new_id_arbre_orig": arbre_result.get("new_id_arbre_orig", None)  # Added None as default
                            })

                    bms_results = insert_update_or_delete_bms(placette_data)
                    for bms_result in bms_results:
                        if bms_result:
                            id_mappings.append({
                                "type": "bms",
                                "id": bms_result.get("id"),
                                "new_id_arbre_orig": bms_result.get("new_id_arbre_orig")
                            })


                    repere_result = insert_update_or_delete_repere(placette_data)
                    if repere_result:
                            for result in repere_result:
                                id_mappings.append({
                                    "type": "repere",
                                    "id": repere_result.get("id_repere"),  # Assuming id_repere is present in repere_data
                                    "status": result.get("status")
                                })

                    cor_cycle_placette_result = insert_or_update_cor_cycle_placette(placette_data)


        # ...
        print("id_mappings: ", id_mappings)
        return id_mappings
    except Exception as e:
        print("Error in insert_or_update_data: ", str(e))
        raise e
