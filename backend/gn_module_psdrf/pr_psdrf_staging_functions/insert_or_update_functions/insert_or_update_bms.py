from ..models_staging import TBmSup30Staging
from geonature.utils.env import DB
from sqlalchemy import func
from .insert_or_update_bms_mesure import insert_update_or_delete_bms_mesure

def insert_update_or_delete_bms(placette_data):
    try:
        counts_bm = {
            'created': 0,
            'updated': 0,
            'deleted': 0
        }
        counts_bm_mesure = {
            'created': 0,
            'updated': 0,
            'deleted': 0
        }
        created_bms = []

        if 'bms' in placette_data:
            bms_data = placette_data['bms']

            # Process each category: 'created', 'updated', 'deleted'
            for category in ['created', 'updated', 'deleted']:
                if category in bms_data:
                    for bms_data_item in bms_data[category]:
                        if category == 'created':

                            max_id_bm_orig = DB.session.query(func.max(TBmSup30Staging.id_bm_sup_30_orig)).filter_by(
                                id_placette=bms_data_item.get('id_placette')
                            ).scalar()
                            new_id_bm_orig = (max_id_bm_orig or 0) + 1 
                            new_bm = TBmSup30Staging(
                                id_bm_sup_30=bms_data_item.get('id_bm_sup_30'),
                                id_bm_sup_30_orig=new_id_bm_orig,
                                id_placette=bms_data_item.get('id_placette', None),
                                code_essence=bms_data_item.get('code_essence', None),
                                azimut=bms_data_item.get('azimut', None),
                                distance=bms_data_item.get('distance', None),
                                orientation=bms_data_item.get('orientation', None),
                                azimut_souche = bms_data_item.get('azimut_souche', None),
                                distance_souche = bms_data_item.get('distance_souche', None),
                                observation=bms_data_item.get('observation', None),
                                created_by= bms_data_item.get('created_by', None),
                                updated_by= bms_data_item.get('updated_by', None),
                                created_on= bms_data_item.get('created_on', None),
                                updated_on= bms_data_item.get('updated_on', None),
                                created_at= bms_data_item.get('created_at', None),
                                updated_at= bms_data_item.get('updated_at', None),
                                
                            )
                            DB.session.add(new_bm)
                            DB.session.flush()
                            DB.session.commit()
                            created_bms.append(
                                {
                                    "status": "created",
                                    "id": new_bm.id_bm_sup_30,
                                    "new_id_bm_orig": new_id_bm_orig
                                }
                            )
                            counts_bm['created'] += 1
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
                                existing_bms.orientation = bms_data_item.get('orientation', existing_bms.orientation)
                                existing_bms.azimut_souche = bms_data_item.get('azimut_souche', existing_bms.azimut_souche)
                                existing_bms.distance_souche = bms_data_item.get('distance_souche', existing_bms.distance_souche)
                                existing_bms.observation = bms_data_item.get('observation', existing_bms.observation)
                                existing_bms.updated_by = bms_data_item.get('updated_by', existing_bms.updated_by)
                                existing_bms.updated_on = bms_data_item.get('updated_on', existing_bms.updated_on)
                                existing_bms.updated_at = bms_data_item.get('updated_at', existing_bms.updated_at)
                                DB.session.commit()
                                counts_bm['updated'] += 1

                                id_bm = existing_bms.id_bm_sup_30
                                
                        elif category == 'deleted':
                            bm_to_delete = DB.session.query(TBmSup30Staging).filter_by(
                                id_bm_sup_30=bms_data_item['id_bm_sup_30'],
                            ).first()
                            if bm_to_delete:
                                DB.session.delete(bm_to_delete)
                                DB.session.commit()
                                counts_bm['deleted'] += 1

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
                                        counts_bm_mesure[bm_mesure_category] += bm_mesure_result[bm_mesure_category]
                                        


        return created_bms, counts_bm, counts_bm_mesure

    except Exception as e:
        DB.session.rollback()
        print("Error in insert_update_or_delete_bms: ", str(e))
        raise e