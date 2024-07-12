from ..models_staging import CorCyclesPlacettesStaging
from geonature.utils.env import DB
from sqlalchemy import func
from .insert_or_update_regeneration import insert_or_update_regeneration
from .insert_or_update_transect import insert_or_update_transect

def insert_or_update_cor_cycle_placette(placette_data):
    try:
        counts_cor_cycle_placette = {
            'created': 0,
            'updated': 0,
            'deleted': 0
        }
        counts_regenerations = {
            'created': 0,
            'updated': 0,
            'deleted': 0
        }
        counts_transects = {
            'created': 0,
            'updated': 0,
            'deleted': 0
        }
        # define id_cycle_placette
        id_cycle_placette = None
        if 'corCyclesPlacettes' in placette_data:
            cors_cycles_placettes_data = placette_data['corCyclesPlacettes']

            # Process each category: 'created', 'updated', 'deleted'
            for category in ['created', 'updated', 'deleted']:
                if category in cors_cycles_placettes_data:
                    for cor_cycle_placette_item_data in cors_cycles_placettes_data[category]:
                        id_cycle_placette = cor_cycle_placette_item_data.get('id_cycle_placette')
                        existing_cor_cycle_placette = DB.session.query(CorCyclesPlacettesStaging).filter_by(
                            id_cycle_placette=id_cycle_placette
                        ).first()

                        if category == 'created':
                            if existing_cor_cycle_placette is None:
                                new_cor_cycle_placette = CorCyclesPlacettesStaging(
                                    id_cycle_placette=id_cycle_placette,
                                    id_cycle=cor_cycle_placette_item_data.get('id_cycle'),
                                    id_placette=cor_cycle_placette_item_data.get('id_placette'),
                                    date_releve=cor_cycle_placette_item_data.get('date_releve'),
                                    date_intervention=cor_cycle_placette_item_data.get('date_intervention'),
                                    annee=cor_cycle_placette_item_data.get('annee'),
                                    nature_intervention=cor_cycle_placette_item_data.get('nature_intervention'),
                                    gestion_placette=cor_cycle_placette_item_data.get('gestion_placette'),
                                    id_nomenclature_castor=cor_cycle_placette_item_data.get('id_nomenclature_castor'),
                                    id_nomenclature_frottis=cor_cycle_placette_item_data.get('id_nomenclature_frottis'),
                                    id_nomenclature_boutis=cor_cycle_placette_item_data.get('id_nomenclature_boutis'),
                                    recouv_herbes_basses=cor_cycle_placette_item_data.get('recouv_herbes_basses'),
                                    recouv_herbes_hautes=cor_cycle_placette_item_data.get('recouv_herbes_hautes'),
                                    recouv_buissons=cor_cycle_placette_item_data.get('recouv_buissons'),
                                    recouv_arbres=cor_cycle_placette_item_data.get('recouv_arbres'),
                                    coeff=cor_cycle_placette_item_data.get('coeff'),
                                    diam_lim=cor_cycle_placette_item_data.get('diam_lim'),
                                    created_by=cor_cycle_placette_item_data.get('created_by'),
                                    updated_by=cor_cycle_placette_item_data.get('updated_by'),
                                    created_on=cor_cycle_placette_item_data.get('created_on'),
                                    updated_on=cor_cycle_placette_item_data.get('updated_on'),
                                    created_at=cor_cycle_placette_item_data.get('created_at'),
                                    updated_at=cor_cycle_placette_item_data.get('updated_at'),
                                )
                                DB.session.add(new_cor_cycle_placette)
                                DB.session.commit()
                                counts_cor_cycle_placette['created'] += 1
                                id_cycle_placette = new_cor_cycle_placette.id_cycle_placette

                        elif category == 'updated':
                            if existing_cor_cycle_placette:
                                # ... update existing fields from cor_cycle_placette_data ...
                                existing_cor_cycle_placette.id_cycle = cor_cycle_placette_item_data.get('id_cycle', existing_cor_cycle_placette.id_cycle)
                                existing_cor_cycle_placette.id_placette = cor_cycle_placette_item_data.get('id_placette', existing_cor_cycle_placette.id_placette)
                                existing_cor_cycle_placette.date_releve = cor_cycle_placette_item_data.get('date_releve', existing_cor_cycle_placette.date_releve)
                                existing_cor_cycle_placette.date_intervention = cor_cycle_placette_item_data.get('date_intervention', existing_cor_cycle_placette.date_intervention)
                                existing_cor_cycle_placette.annee = cor_cycle_placette_item_data.get('annee', existing_cor_cycle_placette.annee)
                                existing_cor_cycle_placette.nature_intervention = cor_cycle_placette_item_data.get('nature_intervention', existing_cor_cycle_placette.nature_intervention)
                                existing_cor_cycle_placette.gestion_placette = cor_cycle_placette_item_data.get('gestion_placette', existing_cor_cycle_placette.gestion_placette)
                                existing_cor_cycle_placette.id_nomenclature_castor = cor_cycle_placette_item_data.get('id_nomenclature_castor', existing_cor_cycle_placette.id_nomenclature_castor)
                                existing_cor_cycle_placette.id_nomenclature_frottis = cor_cycle_placette_item_data.get('id_nomenclature_frottis', existing_cor_cycle_placette.id_nomenclature_frottis)
                                existing_cor_cycle_placette.id_nomenclature_boutis = cor_cycle_placette_item_data.get('id_nomenclature_boutis', existing_cor_cycle_placette.id_nomenclature_boutis)
                                existing_cor_cycle_placette.recouv_herbes_basses = cor_cycle_placette_item_data.get('recouv_herbes_basses', existing_cor_cycle_placette.recouv_herbes_basses)
                                existing_cor_cycle_placette.recouv_herbes_hautes = cor_cycle_placette_item_data.get('recouv_herbes_hautes', existing_cor_cycle_placette.recouv_herbes_hautes)
                                existing_cor_cycle_placette.recouv_buissons = cor_cycle_placette_item_data.get('recouv_buissons', existing_cor_cycle_placette.recouv_buissons)
                                existing_cor_cycle_placette.recouv_arbres = cor_cycle_placette_item_data.get('recouv_arbres', existing_cor_cycle_placette.recouv_arbres)
                                existing_cor_cycle_placette.coeff = cor_cycle_placette_item_data.get('coeff', existing_cor_cycle_placette.coeff)
                                existing_cor_cycle_placette.diam_lim = cor_cycle_placette_item_data.get('diam_lim', existing_cor_cycle_placette.diam_lim)
                                existing_cor_cycle_placette.updated_by = cor_cycle_placette_item_data.get('updated_by', existing_cor_cycle_placette.updated_by)
                                existing_cor_cycle_placette.updated_on = cor_cycle_placette_item_data.get('updated_on', existing_cor_cycle_placette.updated_on)
                                existing_cor_cycle_placette.updated_at = cor_cycle_placette_item_data.get('updated_at', existing_cor_cycle_placette.updated_at)
                                DB.session.commit()
                                counts_cor_cycle_placette['updated'] += 1
                                id_cycle_placette = existing_cor_cycle_placette.id_cycle_placette

                        elif category == 'deleted':
                            if existing_cor_cycle_placette:
                                DB.session.delete(existing_cor_cycle_placette)
                                DB.session.commit()
                                counts_cor_cycle_placette['deleted'] += 1

                        # Now process regenerations within each cor_cycle_placette
                        if 'regenerations' in cor_cycle_placette_item_data:
                            for regeneration_category in ['created', 'updated', 'deleted']:
                                if regeneration_category in cor_cycle_placette_item_data['regenerations']:
                                    for regeneration_data in cor_cycle_placette_item_data['regenerations'][regeneration_category]:
                                        regeneration_results = insert_or_update_regeneration(
                                            category=regeneration_category,
                                            cor_cycle_placette_category=category,
                                            cor_cycle_placette_id=id_cycle_placette,  # Pass the current cor_cycle_placette data
                                            regeneration_data=regeneration_data
                                        )
                                        if regeneration_results:
                                            counts_regenerations[regeneration_category] += regeneration_results[regeneration_category]

                        # Now process transects within each cor_cycle_placette
                        if 'transects' in cor_cycle_placette_item_data:
                            for transect_category in ['created', 'updated', 'deleted']:
                                if transect_category in cor_cycle_placette_item_data['transects']:
                                    for transect_data in cor_cycle_placette_item_data['transects'][transect_category]:
                                        transect_results = insert_or_update_transect(
                                            category=transect_category,
                                            cor_cycle_placette_category=category,
                                            cor_cycle_placette_id=id_cycle_placette,  # Pass the current cor_cycle_placette data
                                            transect_data=transect_data
                                        )
                                        if transect_results:
                                            counts_transects[transect_category] += transect_results[transect_category]

        return counts_cor_cycle_placette, counts_regenerations, counts_transects

    except Exception as e:
        DB.session.rollback()
        print("Error in insert_or_update_cor_cycle_placette: ", str(e))
        raise e
