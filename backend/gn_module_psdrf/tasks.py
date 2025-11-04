from flask import Response, current_app
from geonature.utils.celery import celery_app
import logging
import json
from .data_analysis import data_analysis
from io import BytesIO
import zipfile
import os
import tempfile
from datetime import datetime
from sqlalchemy.orm import sessionmaker, joinedload, aliased, scoped_session
from sqlalchemy.exc import SQLAlchemyError

from geonature.utils.env import DB
from .models import TDispositifs
from .schemas.dispositifs import DispositifSchema
from .staging_schemas.dispositifs import DispositifStagingSchema
from .pr_psdrf_staging_functions.models_staging import TDispositifsStaging
from .helpers.count_updates_and_creation import count_updates_and_creations

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

import os
import tempfile
import zipfile
from flask import current_app, jsonify, request, Response
from celery import Celery
from celery.exceptions import SoftTimeLimitExceeded
from celery.utils.log import get_task_logger
import logging

logger = get_task_logger(__name__)

@celery_app.task(bind=True, soft_time_limit=700, time_limit=900)
def test_celery(self, id_dispositif, isCarnetToDownload, isPlanDesArbresToDownload, carnetToDownloadParameters, outFilePath):
    logger.info(f"[TASK] Starting carnet d'analyse of dispositif {id_dispositif}.")
    logger.info(f"[TASK] Task ID: {self.request.id}")
    logger.info(f"[TASK] Parameters: isCarnet={isCarnetToDownload}, isPlan={isPlanDesArbresToDownload}")
    temp_file = None  # Initialize temp_file and zipName before try-except block
    zipName = f'documents_dispositif-{str(id_dispositif)}.zip'
    try:
        logger.info(f"[TASK] Getting app context...")
        with current_app.app_context():
            logger.info(f"[TASK] Calling data_analysis function...")
            data_analysis(str(id_dispositif), isCarnetToDownload, isPlanDesArbresToDownload, carnetToDownloadParameters)
            logger.info(f"[TASK] data_analysis completed successfully")
        
            logger.info(f"[TASK] Preparing output directories...")
            base_dir = os.path.dirname(os.path.abspath(__file__))  # Gets the directory of the current script
            output_dir = os.path.join(base_dir, 'Rscripts/zip')
            logger.info(f"[TASK] Output dir: {output_dir}")
        
            if not os.path.exists(output_dir):
                logger.info(f"[TASK] Creating output directory...")
                os.makedirs(output_dir)

            temp_file = tempfile.NamedTemporaryFile(dir=output_dir, delete=False, suffix=".zip")
            logger.info(f"[TASK] Created temp file: {temp_file.name}")
            outFilePath = os.path.join(base_dir, 'Rscripts/out')
            logger.info(f"[TASK] Looking for files in: {outFilePath}")
        
            files_added = 0
            with zipfile.ZipFile(temp_file.name, 'w', zipfile.ZIP_DEFLATED) as zf:
                for dirname, subdirs, files in os.walk(outFilePath):
                    for filename in files:
                        absname = os.path.abspath(os.path.join(dirname, filename))
                        arcname = absname[len(outFilePath) + 1:]
                        if (arcname != '.gitignore') and (not arcname.endswith(('.log', '.tex'))):
                            logger.info(f"[TASK] Adding file to zip: {arcname}")
                            zf.write(absname, arcname)
                            files_added += 1

            logger.info(f"[TASK] Zip created with {files_added} files")
            os.chmod(temp_file.name, 0o777)
        
        self.update_state(state='SUCCESS', meta={'file_path': temp_file.name, "file_name": zipName})

    except SoftTimeLimitExceeded as e:
        logger.exception("Soft time limit exceeded for task id %s", self.request.id)
        self.update_state(state='FAILURE', meta={'exc_type': str(type(e).__name__), 'exc_message': str(e)})
        raise e
    except OSError as e:
        logger.exception("OS error during processing task id %s", self.request.id)
        self.update_state(state='FAILURE', meta={'exc_type': str(type(e).__name__), 'exc_message': str(e)})
        raise e
    except zipfile.BadZipFile as e:
        logger.exception("Zip file error during processing task id %s", self.request.id)
        self.update_state(state='FAILURE', meta={'exc_type': str(type(e).__name__), 'exc_message': str(e)})
        raise e
    except Exception as e:
        logger.exception("General error during processing task id %s", self.request.id)
        self.update_state(state='FAILURE', meta={'exc_type': str(type(e).__name__), 'exc_message': str(e)})
        raise e

    return {"file_path": temp_file.name if temp_file else "N/A", "file_name": zipName}



@celery_app.task(bind=True, soft_time_limit=2400, time_limit=2600)
def insert_or_update_data(self, data):
    Session = sessionmaker(bind=DB.engine)
    session = Session()

    print('celery task started')
    logger.info(f"Inserting data on staging DB.")

    created_arbres = []
    created_bms = []
    counts_arbre = {'created': 0, 'updated': 0, 'deleted': 0}
    counts_arbre_mesure = {'created': 0, 'updated': 0, 'deleted': 0}
    counts_bm = {'created': 0, 'updated': 0, 'deleted': 0}
    counts_bm_mesure = {'created': 0, 'updated': 0, 'deleted': 0}
    counts_repere = {'created': 0, 'updated': 0, 'deleted': 0}
    counts_cor_cycle_placette = {'created': 0, 'updated': 0, 'deleted': 0}
    counts_regeneration = {'created': 0, 'updated': 0, 'deleted': 0}
    counts_transect = {'created': 0, 'updated': 0, 'deleted': 0}

    try:
        with current_app.app_context():
            if 'id_dispositif' in data:
                result = insert_or_update_dispositif(data, session)

                if 'cycles' in data:
                    for cycle_data in data['cycles']:
                        cycle_result = insert_or_update_cycle(cycle_data, session)

                if 'placettes' in data:
                    for placette_data in data['placettes']:
                        placette_result = insert_or_update_placette(placette_data, session)
                    
                        created_arbres_temp, counts_arbre_temp, counts_arbre_mesure_temp = insert_update_or_delete_arbre(placette_data, session)
                        created_arbres.extend(created_arbres_temp)
                        for key in counts_arbre_temp:
                            counts_arbre[key] += counts_arbre_temp[key]
                        for key in counts_arbre_mesure_temp:
                            counts_arbre_mesure[key] += counts_arbre_mesure_temp[key]

                        created_bms_temp, counts_bm_temp, counts_bm_mesure_temp = insert_update_or_delete_bms(placette_data, session)
                        created_bms.extend(created_bms_temp)
                        for key in counts_bm_temp:
                            counts_bm[key] += counts_bm_temp[key]
                        for key in counts_bm_mesure_temp:
                            counts_bm_mesure[key] += counts_bm_mesure_temp[key]

                        counts_repere_temp = insert_update_or_delete_repere(placette_data, session)
                        for key in counts_repere_temp:
                            counts_repere[key] += counts_repere_temp[key]

                        counts_cor_cycle_placette_temp, counts_regeneration_temp, counts_transect_temp = insert_or_update_cor_cycle_placette(placette_data, session)
                        for key in counts_cor_cycle_placette_temp:
                            counts_cor_cycle_placette[key] += counts_cor_cycle_placette_temp[key]
                        for key in counts_regeneration_temp:
                            counts_regeneration[key] += counts_regeneration_temp[key]
                        for key in counts_transect_temp:
                            counts_transect[key] += counts_transect_temp[key]

            session.commit()

        self.update_state(
            state='SUCCESS', 
            meta={
                'created_arbres': created_arbres, 
                'counts_arbre': counts_arbre, 
                'counts_arbre_mesure': counts_arbre_mesure, 
                'created_bms': created_bms, 
                'counts_bm': counts_bm, 
                'counts_bm_mesure': counts_bm_mesure, 
                'counts_repere': counts_repere, 
                'counts_cor_cycle_placette': counts_cor_cycle_placette, 
                'counts_regeneration': counts_regeneration, 
                'counts_transect': counts_transect,
            }
        )

    except SoftTimeLimitExceeded as e:
        logger.exception("Soft time limit exceeded for task id %s", self.request.id)
        session.rollback()
        self.update_state(state='FAILURE', meta={'exc_type': str(type(e).__name__), 'exc_message': str(e)})
        raise e
    except Exception as e:
        logger.exception("Error in insert_or_update_data: %s", str(e))
        session.rollback()
        self.update_state(state='FAILURE', meta={'exc_type': str(type(e).__name__), 'exc_message': str(e)})
        raise e
    finally:
        session.close()

    return {
        'created_arbres': created_arbres, 
        'counts_arbre': counts_arbre, 
        'counts_arbre_mesure': counts_arbre_mesure, 
        'created_bms': created_bms, 
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
        with current_app.app_context():
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
        with current_app.app_context():
            logger.info("Starting database query...")
            logger.error("Fetching data from staging DB")
            # Fetch the entire dispositif including all related entities
            dispositif = (
                DB.session.query(TDispositifsStaging)
                .filter(TDispositifsStaging.id_dispositif == id_dispositif)
                .first()
            )

            if not dispositif:
                # Handle the no data case as a normal situation
                logger.info(f"No data found for dispositif ID {id_dispositif}. No updates needed.")
                return {'status': 'SUCCESS', 'data': None, 'message': 'No data available to update'}

            # Using the schema to serialize the data
            dispositif_schema = DispositifStagingSchema(many=False)
            full_data = dispositif_schema.dump(dispositif)

            counts = count_updates_and_creations(full_data, last_sync_date)

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

            return {'status': 'SUCCESS', 'data': filtered_data, 'counts': counts}
    except Exception as e:
        logger.exception("Failed to fetch or serialize updated data", exc_info=e)
        return {'status': 'FAILURE', 'data': str(e)}
