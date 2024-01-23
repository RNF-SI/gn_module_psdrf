from ..models_staging import TBmSup30MesuresStaging
from geonature.utils.env import DB
from sqlalchemy import func

def insert_update_or_delete_bms_mesure(category, bm_category, id_bm, bm_data, bms_mesure_data):
    try:
        results = []

        if category == 'deleted':
            # Delete logic
            bms_mesure_to_delete = DB.session.query(TBmSup30MesuresStaging).filter_by(
                id_bm_sup_30_mesure=bm_data['id_bm_sup_30_mesure']
            ).first()
            if bms_mesure_to_delete:
                DB.session.delete(bms_mesure_to_delete)
                DB.session.commit()
                results.append({"message": "BMS mesure deleted successfully.", "status": "deleted", "id": bms_mesure_to_delete.id_bm_sup_30_mesure})
        elif category == 'updated':
            existing_bms_mesure = DB.session.query(TBmSup30MesuresStaging).filter_by(
                id_bm_sup_30_mesure=bm_data['id_bm_sup_30_mesure']
            ).first()

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

            DB.session.commit()
            results.append({
                "message": "BMS mesure updated successfully.", 
                "status": "updated", 
                "old_id": existing_bms_mesure.id_bm_sup_30_mesure,
                "new_id": existing_bms_mesure.id_bm_sup_30_mesure 
                })
        elif category == 'created':

            max_id_bm_sup_30_mesure= DB.session.query(func.max(TBmSup30MesuresStaging.id_bm_sup_30_mesure)).scalar()
            new_id_bm_sup_30_mesure = (max_id_bm_sup_30_mesure or 0) + 1

            # Insert logic as before
            new_bms_mesure = TBmSup30MesuresStaging(
                id_bm_sup_30_mesure=new_id_bm_sup_30_mesure,
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
            )
            DB.session.add(new_bms_mesure)
            DB.session.commit()
            results.append({
                "message": "BMS mesure created successfully.", 
                "status": "created", 
                "new_id": new_bms_mesure.id_bm_sup_30_mesure
                })

        return results

    except Exception as e:
        DB.session.rollback()
        print("Error in insert_update_or_delete_bms_mesure: ", str(e))
        raise e