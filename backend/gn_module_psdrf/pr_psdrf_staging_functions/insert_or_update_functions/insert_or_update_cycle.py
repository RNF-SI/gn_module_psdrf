from ..models_staging import TCyclesStaging
from geonature.utils.env import DB

def insert_or_update_cycle(data):
    try:
        existing_cycle = DB.session.query(TCyclesStaging).filter_by(id_cycle=data['id_cycle']).first()

        if existing_cycle:
            existing_cycle.id_dispositif = data.get('id_dispositif', existing_cycle.id_dispositif)
            existing_cycle.num_cycle = data.get('num_cycle', existing_cycle.num_cycle)
            existing_cycle.coeff = data.get('coeff', existing_cycle.coeff)
            existing_cycle.date_debut = data.get('date_debut', existing_cycle.date_debut)
            existing_cycle.date_fin = data.get('date_fin', existing_cycle.date_fin)
            existing_cycle.diam_lim = data.get('diam_lim', existing_cycle.diam_lim)
            existing_cycle.monitor = data.get('monitor', existing_cycle.monitor)
            DB.session.commit()
            return "Cycle updated successfully."
        else:
            new_cycle = TCyclesStaging(
                id_cycle=data['id_cycle'],
                id_dispositif=data['id_dispositif'],
                num_cycle=data['num_cycle'],
                coeff=data.get('coeff', None),
                date_debut=data.get('date_debut', None),
                date_fin=data.get('date_fin', None),
                diam_lim=data.get('diam_lim', None),
                monitor=data.get('monitor', None)
            )
            DB.session.add(new_cycle)
            DB.session.commit()
            return "Cycle inserted successfully."
    except Exception as e:
        DB.session.rollback()
        print("Error in insert_or_update_cycle: ", str(e))
        raise e