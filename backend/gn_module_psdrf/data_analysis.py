"""
Génération carnet / plan des arbres — point d'entrée appelé par la tâche Celery.

Depuis la bascule R→Python, ce module ne fait plus que déléguer au pipeline Python
pur (sous-module PermPSDRF4py via :mod:`psdrf_py.run_pipeline`). Toute l'ancienne
machinerie rpy2 (conversion pandas→R, BDD2RData.R, knit2pdf) a été retirée.
"""

from __future__ import annotations

from celery.utils.log import get_task_logger

from .psdrf_py.run_pipeline import run_psdrf_pipeline

logger = get_task_logger(__name__)


def _as_bool(value) -> bool:
    """Les paramètres de la route arrivent en chaîne ('true'/None)."""
    return str(value).strip().lower() == "true"


def data_analysis(
    dispId,
    isCarnetToDownload,
    isPlanDesArbresToDownload,
    carnetToDownloadParameters,
    work_token=None,
):
    """
    Lance la génération pour un dispositif et retourne le descriptif des sorties.

    Returns
    -------
    dict
        ``{"pdfs": [...], "campagne_dir": Path, "work_dir": Path}`` (cf. run_pipeline).
    """
    answer_radar = None
    if carnetToDownloadParameters:
        answer_radar = carnetToDownloadParameters.get("Answer_Radar")

    logger.info(
        "[DATA_ANALYSIS] disp=%s carnet=%s plan=%s radar=%s",
        dispId, isCarnetToDownload, isPlanDesArbresToDownload, answer_radar,
    )
    return run_psdrf_pipeline(
        int(dispId),
        is_carnet=_as_bool(isCarnetToDownload),
        is_plan=_as_bool(isPlanDesArbresToDownload),
        answer_radar=answer_radar,
        work_token=work_token,
    )
