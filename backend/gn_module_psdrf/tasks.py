from flask import Response
from geonature.utils.celery import celery_app
import logging
import json
from .data_analysis import data_analysis
from io import BytesIO
import zipfile
import os
import tempfile
from datetime import datetime
from sqlalchemy.orm import joinedload, aliased

from geonature.utils.env import DB
from .models import TDispositifs
from .schemas.dispositifs import DispositifSchema
from .staging_schemas.dispositifs import DispositifStagingSchema
from .pr_psdrf_staging_functions.models_staging import TDispositifsStaging

from .pr_psdrf_staging_functions.insert_or_update_functions.insert_or_update_dispositif import insert_or_update_dispositif
from .pr_psdrf_staging_functions.insert_or_update_functions.insert_or_update_placette import insert_or_update_placette
from .pr_psdrf_staging_functions.insert_or_update_functions.insert_or_update_arbre import insert_update_or_delete_arbre
from .pr_psdrf_staging_functions.insert_or_update_functions.insert_or_update_bms import insert_update_or_delete_bms
from .pr_psdrf_staging_functions.insert_or_update_functions.insert_or_update_cycle import insert_or_update_cycle
from .pr_psdrf_staging_functions.insert_or_update_functions.insert_or_update_cor_cycle_placette import insert_or_update_cor_cycle_placette
from .pr_psdrf_staging_functions.insert_or_update_functions.insert_or_update_repere import insert_update_or_delete_repere


from celery.utils.log import get_task_logger
from celery.exceptions import SoftTimeLimitExceeded

logger = get_task_logger(__name__)

@celery_app.task(bind=True, soft_time_limit=700, time_limit=900)
def test_celery(self, id_dispositif, isCarnetToDownload, isPlanDesArbresToDownload, carnetToDownloadParameters, outFilePath):
    logger.info(f"Starting carnet d'analyse of dispositif {id_dispositif}.")
    temp_file = None  # Initialize temp_file and zipName before try-except block
    zipName = f'documents_dispositif-{str(id_dispositif)}.zip'
    try:
        data_analysis(str(id_dispositif), isCarnetToDownload, isPlanDesArbresToDownload, carnetToDownloadParameters)
        
        base_dir = os.path.dirname(os.path.abspath(__file__))  # Gets the directory of the current script
        output_dir = os.path.join(base_dir, 'Rscripts/zip')
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        temp_file = tempfile.NamedTemporaryFile(dir=output_dir, delete=False, suffix=".zip")
        outFilePath = os.path.join(base_dir, 'Rscripts/out')
        
        with zipfile.ZipFile(temp_file.name, 'w', zipfile.ZIP_DEFLATED) as zf:
            for dirname, subdirs, files in os.walk(outFilePath):
                for filename in files:
                    absname = os.path.abspath(os.path.join(dirname, filename))
                    arcname = absname[len(outFilePath) + 1:]
                    if (arcname != '.gitignore') and (not arcname.endswith(('.log', '.tex'))):
                        zf.write(absname, arcname)

        os.chmod(temp_file.name, 0o777)
        
        self.update_state(state='SUCCESS', meta={'file_path': temp_file.name, "file_name": zipName})

    except SoftTimeLimitExceeded as e:
        logger.exception("Soft time limit exceed for task id %s", self.request.id)
        self.update_state(state='FAILURE', meta={'exc_type': str(type(e).__name__), 'exc_message': str(e)})
        raise e
    except Exception as e:
        logger.exception("Error during processing task id %s", self.request.id)
        logger.exception("Error message %s", str(e))
        self.update_state(state='FAILURE', meta={'exc_type': str(type(e).__name__), 'exc_message': str(e)})
        raise e

    return {"file_path": temp_file.name if temp_file else "N/A", "file_name": zipName}




@celery_app.task(bind=True, soft_time_limit=2400, time_limit=2600)
def insert_or_update_data(self, data):

    print('celery task started')
    logger.info(f"Inserting data on staging DB.")
    created_arbres = []
    created_arbres_temp = []
    counts_arbre = {
            'created': 0,
            'updated': 0,
            'deleted': 0
        }
    counts_arbre_temp = {}
    counts_arbre_mesure = {
            'created': 0,
            'updated': 0,
            'deleted': 0
        }
    counts_arbre_mesure_temp = {}
    created_bms = []
    created_bms_temp = []
    counts_bm = {
            'created': 0,
            'updated': 0,
            'deleted': 0
        }
    counts_bm_temp = {}
    counts_bm_mesure = {
            'created': 0,
            'updated': 0,
            'deleted': 0
        }
    counts_bm_mesure_temp = {}
    counts_repere = {
        'created': 0,
        'updated': 0,
        'deleted': 0
    }
    counts_repere_temp = {}
    counts_cor_cycle_placette = {
        'created': 0,
        'updated': 0,
        'deleted': 0
    }
    counts_cor_cycle_placette_temp = {}
    counts_regeneration = {
        'created': 0,
        'updated': 0,
        'deleted': 0
    }
    counts_regeneration_temp = {}
    counts_transect = {
        'created': 0,
        'updated': 0,
        'deleted': 0
    }
    counts_transect_temp = {}

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
                    
                    created_arbres_temp, counts_arbre_temp, counts_arbre_mesure_temp = insert_update_or_delete_arbre(placette_data)
                    created_arbres.extend(created_arbres_temp)
                    counts_arbre["created"] += counts_arbre_temp["created"]
                    counts_arbre["updated"] += counts_arbre_temp["updated"]
                    counts_arbre["deleted"] += counts_arbre_temp["deleted"]
                    counts_arbre_mesure["created"] += counts_arbre_mesure_temp["created"]
                    counts_arbre_mesure["updated"] += counts_arbre_mesure_temp["updated"]
                    counts_arbre_mesure["deleted"] += counts_arbre_mesure_temp["deleted"]

                    created_bms_temp, counts_bm_temp, counts_bm_mesure_temp = insert_update_or_delete_bms(placette_data)
                    created_bms.extend(created_bms_temp)
                    counts_bm["created"] += counts_bm_temp["created"]
                    counts_bm["updated"] += counts_bm_temp["updated"]
                    counts_bm["deleted"] += counts_bm_temp["deleted"]
                    counts_bm_mesure["created"] += counts_bm_mesure_temp["created"]
                    counts_bm_mesure["updated"] += counts_bm_mesure_temp["updated"]
                    counts_bm_mesure["deleted"] += counts_bm_mesure_temp["deleted"]

                    counts_repere_temp = insert_update_or_delete_repere(placette_data)
                    counts_repere["created"] += counts_repere_temp["created"]
                    counts_repere["updated"] += counts_repere_temp["updated"]
                    counts_repere["deleted"] += counts_repere_temp["deleted"]
                    logger.info(f"Starting carnet d'analyse of dispositif {counts_repere['created']}.")


                    counts_cor_cycle_placette_temp, counts_regeneration_temp, counts_transect_temp = insert_or_update_cor_cycle_placette(placette_data)
                    counts_cor_cycle_placette["created"] += counts_cor_cycle_placette_temp["created"]
                    counts_cor_cycle_placette["updated"] += counts_cor_cycle_placette_temp["updated"]
                    counts_cor_cycle_placette["deleted"] += counts_cor_cycle_placette_temp["deleted"]
                    counts_regeneration["created"] += counts_regeneration_temp["created"]
                    counts_regeneration["updated"] += counts_regeneration_temp["updated"]
                    counts_regeneration["deleted"] += counts_regeneration_temp["deleted"]
                    counts_transect["created"] += counts_transect_temp["created"]
                    counts_transect["updated"] += counts_transect_temp["updated"]
                    counts_transect["deleted"] += counts_transect_temp["deleted"]

        self.update_state(
            state='SUCCESS', 
            meta={
                'created_arbres': created_arbres, 
                'counts_arbre': counts_arbre, 
                'counts_arbre_mesure':counts_arbre_mesure, 
                'created_bms':created_bms, 
                'counts_bm': counts_bm, 
                'counts_bm_mesure': counts_bm_mesure, 
                'counts_repere': counts_repere, 
                'counts_cor_cycle_placette': counts_cor_cycle_placette, 
                'counts_regeneration': counts_regeneration, 
                'counts_transect': counts_transect,
                })

    except SoftTimeLimitExceeded as e:
        logger.exception("Soft time limit exceed for task id %s", self.request.id)
        self.update_state(state='FAILURE', meta={'exc_type': str(type(e).__name__), 'exc_message': str(e)})
        raise e
    except Exception as e:
        print("Error in insert_or_update_data: ", str(e))
        raise e
    
    return {
        'created_arbres': created_arbres, 
        'counts_arbre': counts_arbre, 
        'counts_arbre_mesure':counts_arbre_mesure, 
        'created_bms':created_bms, 
        'counts_bm': counts_bm, 
        'counts_bm_mesure': counts_bm_mesure,
        'counts_repere': counts_repere, 
        'counts_cor_cycle_placette': counts_cor_cycle_placette, 
        'counts_regeneration': counts_regeneration, 
        'counts_transect': counts_transect
        }


# Task to get all the data of a dispositif from the prod database
@celery_app.task(bind=True, soft_time_limit=2400, time_limit=2600)
def fetch_dispositif_data(self, id_dispositif):
    logger.info(f"Task started for dispositif ID: {id_dispositif}")
    try:
        logger.info("Starting database query...")
        query = DB.session.query(TDispositifs).filter(TDispositifs.id_dispositif == id_dispositif).one()
        logger.info("Database query completed.")
        schema = DispositifSchema(many=False)
        logger.info("Starting serialization of data...")
        result = schema.dump(query)
        logger.info("Serialization completed.")
        logger.info(f"Successfully fetched and serialized data for dispositif ID: {id_dispositif}")
        return {'status': 'SUCCESS', 'data': result}
    except Exception as e:
        logger.exception("Error during fetching dispositif data")
        return {'status': 'FAILURE', 'data': str(e)}
    

@celery_app.task(bind=True, soft_time_limit=2400, time_limit=2600)
def fetch_updated_data(self, id_dispositif, last_sync):
    logger.info(last_sync)
    last_sync_date = datetime.fromisoformat(last_sync.rstrip('Z'))
    logger.info(f"Fetching updated data for dispositif ID: {id_dispositif} since last sync: {last_sync}")

    try:

        logger.info("Starting database query...")
        logger.error("Fetching data from staging DB")
        # Fetch the entire dispositif including all related entities
        dispositif = (
            DB.session.query(TDispositifsStaging)
            .filter(TDispositifsStaging.id_dispositif == id_dispositif)
            .one()
        )

        # Using the schema to serialize the data
        dispositif_schema = DispositifStagingSchema(many=False)
        full_data = dispositif_schema.dump(dispositif)

        # Asserting that datetime fields are parsed correctly
        # remove in prod
        logger.info(full_data['cycles'][0]['corCyclesPlacettes'][0]['updated_at'])
        assert isinstance(full_data['cycles'][0]['corCyclesPlacettes'][0]['updated_at'], datetime), "updated_at must be a datetime object"

        # Filtering the serialized data
        filtered_data = {
            'cycles': [
                {
                    **cycle,
                    'corCyclesPlacettes': [
                        {
                            **cor_cycle,
                            'regenerations': [
                                reg for reg in cor_cycle['regenerations'] if reg['updated_at'] > last_sync_date
                            ],
                            'transects': [
                                tran for tran in cor_cycle['transects'] if tran['updated_at'] > last_sync_date
                            ]
                        } 
                        for cor_cycle in cycle['corCyclesPlacettes'] if cor_cycle['updated_at'] > last_sync_date
                    ]
                }
                for cycle in full_data['cycles']
            ],
            'placettes': [
                {
                    **placette,
                    'arbres': [
                        {
                            **arbre,
                            'arbres_mesures': [
                                mesure for mesure in arbre['arbres_mesures'] if mesure['updated_at'] > last_sync_date
                            ]
                        }
                        for arbre in placette['arbres'] if arbre['updated_at'] > last_sync_date
                    ],
                    'bmsSup30': [
                        {
                            **bms,
                            'bm_sup_30_mesures': [
                                mesure for mesure in bms['bm_sup_30_mesures'] if mesure['updated_at'] > last_sync_date
                            ]
                        }
                        for bms in placette['bmsSup30'] if bms['updated_at'] > last_sync_date
                    ],
                    'reperes': [
                        rep for rep in placette['reperes'] if rep['updated_at'] > last_sync_date
                    ]
                }
                for placette in full_data['placettes']
            ]
        }

        return {'status': 'SUCCESS', 'data': filtered_data}
    except Exception as e:
        logger.exception("Failed to fetch or serialize updated data", exc_info=e)
        return {'status': 'FAILURE', 'data': str(e)}
