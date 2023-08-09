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

logger = get_task_logger(__name__)

@celery_app.task(bind=True)
def test_celery(self, id_dispositif, isCarnetToDownload, isPlanDesArbresToDownload, carnetToDownloadParameters, outFilePath):
    logger.info(f"Starting carnet d'analyse of dispositif {id_dispositif}.")
    try:
        data_analysis(str(id_dispositif), isCarnetToDownload, isPlanDesArbresToDownload, carnetToDownloadParameters)
    except Exception as e:
        logging.critical(e)
        msg = json.dumps({"type": "bug", "msg": "Unkown error during analysis"})
        logging.info(msg)
        return Response(msg, status=500)

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    with zipfile.ZipFile(temp_file.name, 'w', zipfile.ZIP_DEFLATED) as zf:
        for dirname, subdirs, files in os.walk(outFilePath):
            for filename in files:
                absname = os.path.abspath(os.path.join(dirname, filename))
                arcname = absname[len(outFilePath) :]
                if (arcname != '.gitignore') and (not arcname.endswith(('.log', '.tex'))):
                    zf.write(absname, arcname)

    zipName = 'documents_dispositif-'+str(id_dispositif)+'.zip'

    return {"file_path": temp_file.name, "file_name": zipName}

