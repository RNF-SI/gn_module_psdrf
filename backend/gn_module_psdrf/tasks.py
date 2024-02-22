from flask import Response
from geonature.utils.celery import celery_app
import logging
import json
from .data_analysis import data_analysis
from io import BytesIO
import zipfile
import os
import tempfile

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
