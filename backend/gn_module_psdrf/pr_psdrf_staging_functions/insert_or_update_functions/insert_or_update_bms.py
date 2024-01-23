from ..models_staging import TBmSup30Staging
from geonature.utils.env import DB
from sqlalchemy import func
from .insert_or_update_bms_mesure import insert_update_or_delete_bms_mesure

def insert_update_or_delete_bms(placette_data):
    try:
        results = []

        if 'bms' in placette_data:
            bms_data = placette_data['bms']

            # Process each category: 'created', 'updated', 'deleted'
            for category in ['created', 'updated', 'deleted']:
                if category in bms_data:
                    for bms_data_item in bms_data[category]:
                        if category == 'created':

                            max_id_bm_sup_30= DB.session.query(func.max(TBmSup30Staging.id_bm_sup_30)).scalar()
                            new_id_bm_sup_30 = (max_id_bm_sup_30 or 0) + 1 

                            max_id_bm_orig = DB.session.query(func.max(TBmSup30Staging.id_bm_sup_30_orig)).filter_by(
                                id_placette=bms_data_item.get('id_placette')
                            ).scalar()
                            new_id_bm_orig = (max_id_bm_orig or 0) + 1 
                            new_bm = TBmSup30Staging(
                                id_bm_sup_30=new_id_bm_sup_30,
                                id_bm_sup_30_orig=new_id_bm_orig,
                                id_placette=bms_data_item.get('id_placette', None),
                                code_essence=bms_data_item.get('code_essence', None),
                                azimut=bms_data_item.get('azimut', None),
                                distance=bms_data_item.get('distance', None),
                                # ... add other fields ...
                            )
                            DB.session.add(new_bm)
                            DB.session.flush()
                            DB.session.commit()
                            results.append({"message": "BMS inserted successfully.", "status": "created", "new_id": new_bm.id_bm_sup_30, "new_id_bm_orig": new_id_bm_orig})
                            id_bm = new_bm.id_bm_sup_30


                        # Handle updated arbres
                        if category == 'updated':
                            existing_bms = DB.session.query(TBmSup30Staging).filter_by(
                                id_bm_sup_30=bms_data_item['id_bm_sup_30'],
                            ).first()

                            if existing_bms:
                                existing_bms.id_arbre = bms_data_item.get('id_arbre', existing_bms.id_arbre)
                                existing_bms.code_essence = bms_data_item.get('code_essence', existing_bms.code_essence)
                                existing_bms.azimut = bms_data_item.get('azimut', existing_bms.azimut)
                                existing_bms.distance = bms_data_item.get('distance', existing_bms.distance)
                                DB.session.commit()
                                results.append({
                                    "message": "BMS updated successfully.", 
                                    "status": "updated", 
                                    "old_id": existing_bms.id_bm_sup_30,
                                    "new_id": existing_bms.id_bm_sup_30 
                                })
                                id_bm = existing_bms.id_bm_sup_30
                                
                        elif category == 'deleted':
                            bm_to_delete = DB.session.query(TBmSup30Staging).filter_by(
                                id_bm_sup_30=bms_data_item['id_bm_sup_30'],
                            ).first()
                            if bm_to_delete:
                                DB.session.delete(bm_to_delete)
                                DB.session.commit()
                                results.append({
                                    "message": "BMS deleted successfully.", 
                                    "status": "deleted", 
                                    "id": bm_to_delete.id_bm_sup_30
                                })

                        if 'bm_sup_30_mesures' in bms_data_item:
                            for bm_mesure_category in ['created', 'updated', 'deleted']:
                                for bm_mesure_data in bms_data_item['bm_sup_30_mesures'][bm_mesure_category]:
                                    bm_mesure_result = insert_update_or_delete_bms_mesure(
                                        category= bm_mesure_category,
                                        bm_category=category, 
                                        id_bm=id_bm,
                                        bm_data=bms_data_item, 
                                        bms_mesure_data=bm_mesure_data,
                                        )
                                    if bm_mesure_result:
                                        results.extend(bm_mesure_result)
                                        


        return results

    except Exception as e:
        DB.session.rollback()
        print("Error in insert_update_or_delete_bms: ", str(e))
        raise e