"""
Orchestration de la génération carnet + plans des arbres en Python pur.

Remplace l'ancienne chaîne ``data_analysis`` → rpy2 → ``BDD2RData.R`` → knit2pdf.
Enchaîne les étapes du pipeline PermPSDRF4py sur un dossier campagne alimenté
depuis la BDD (cf. :mod:`db_to_campagne`) :

    psdrf_calculs → psdrf_agreg_arbres → psdrf_agreg_placettes → psdrf_edit_carnet
                                                              ↘ psdrf_edit_plans_arbres

Tous les pickles intermédiaires cohabitent dans ``{campagne}/tables/`` : on impose
donc ``rep_psdrf == rep_sav == campagne`` pour les étapes de calcul, et on passe
la racine du sous-module comme ``project`` aux étapes de mise en page (code,
templates LaTeX, images).
"""

from __future__ import annotations

import logging
import shutil
import uuid
from pathlib import Path
from typing import Optional

from flask import current_app

# Déclenche le bootstrap (sys.path sous-module + matplotlib Agg).
from . import SUBMODULE_ROOT
from .carnet_tables import TABPLA_NAMES_CARNET
from .db_to_campagne import CampagneRefs, build_campagne_from_db
from .transforms import map_radar

import pandas as pd  # noqa: E402

from python.script.annexes import results_by_plot_from_table_names  # noqa: E402
from python.script.psdrf_agreg_arbres import psdrf_agreg_arbres  # noqa: E402
from python.script.psdrf_agreg_placettes import psdrf_agreg_placettes  # noqa: E402
from python.script.psdrf_calculs import psdrf_calculs  # noqa: E402
from python.script.psdrf_edit_plans_arbres import psdrf_edit_plans_arbres  # noqa: E402
from python.template.carnet.psdrf_edit_carnet import psdrf_edit_carnet  # noqa: E402

logger = logging.getLogger(__name__)


def _config_dirs() -> tuple[Path, Path]:
    """(data_dir, export_dir) résolus depuis la config GeoNature."""
    root = Path(current_app.config["ROOT_PATH"])
    data_dir = root / current_app.config.get("PSDRF_DATA_DIR", "media/psdrf/data")
    export_dir = root / current_app.config.get("PSDRF_EXPORT_DIR", "media/psdrf/exports")
    return data_dir, export_dir


def run_psdrf_pipeline(
    disp_id: int,
    *,
    is_carnet: bool = True,
    is_plan: bool = False,
    answer_radar=None,
    work_token: Optional[str] = None,
) -> dict:
    """
    Génère le carnet et/ou le plan des arbres pour un dispositif.

    Returns
    -------
    dict
        ``{"pdfs": [Path, ...], "campagne_dir": Path, "work_dir": Path}``.
        ``work_dir`` est le dossier temporaire à purger après archivage.
    """
    data_dir, export_dir = _config_dirs()
    token = work_token or uuid.uuid4().hex[:12]
    work_dir = export_dir / f"disp-{disp_id}-{token}"
    work_dir.mkdir(parents=True, exist_ok=True)

    include_conservation, groups = map_radar(answer_radar)

    if is_carnet and shutil.which("pdflatex") is None:
        raise RuntimeError(
            "pdflatex introuvable : impossible de compiler le carnet PDF. "
            "Installer une distribution LaTeX (cf. install_env.sh)."
        )

    logger.info(
        "[PSDRF] Pipeline disp=%s carnet=%s plan=%s groups=%s conservation=%s",
        disp_id, is_carnet, is_plan, groups, include_conservation,
    )

    refs: CampagneRefs = build_campagne_from_db(
        disp_id, base_dir=work_dir, data_dir=data_dir
    )
    camp = refs.campagne_dir
    pdfs: list[Path] = []

    if is_carnet:
        psdrf_calculs(camp, rep_sav=camp, disp_list=[disp_id], last_cycle=refs.last_cycle)
        psdrf_agreg_arbres(
            camp,
            results_by_plot_to_get=results_by_plot_from_table_names(TABPLA_NAMES_CARNET),
            rep_sav=camp,
            disp_list=[disp_id],
            last_cycle=refs.last_cycle,
        )
        # DataFrame VIDE (et non None) quand aucun regroupement n'est demandé :
        # None déclencherait le calcul de TOUS les groupes par défaut (Strate,
        # Habitat, Groupe…), inutile ici et fragile sur données partielles. Vide
        # ⇒ seules les tables globales (Disp) sont produites.
        groups_df = pd.DataFrame({"V1": groups}) if groups else pd.DataFrame()
        psdrf_agreg_placettes(
            camp,
            results_by_group_to_get=groups_df,
            rep_sav=camp,
            disp_list=[disp_id],
            last_cycle=refs.last_cycle,
        )
        tex = psdrf_edit_carnet(
            SUBMODULE_ROOT,
            disp_id,
            rep_sav=camp,
            compile_pdf=True,
            groups=groups,
            include_conservation=include_conservation,
            include_ign=False,
        )
        pdf_carnet = Path(tex).with_suffix(".pdf")
        if pdf_carnet.is_file():
            pdfs.append(pdf_carnet)
        else:
            logger.error("[PSDRF] Carnet non produit (pdflatex) : %s", pdf_carnet)

    if is_plan:
        plan_pdfs = psdrf_edit_plans_arbres(
            SUBMODULE_ROOT,
            num_disp=disp_id,
            rep_data=camp,
        )
        pdfs.extend(Path(p) for p in plan_pdfs if Path(p).is_file())

    logger.info("[PSDRF] Pipeline terminé : %d PDF(s) — %s", len(pdfs), [p.name for p in pdfs])
    return {"pdfs": pdfs, "campagne_dir": camp, "work_dir": work_dir}
