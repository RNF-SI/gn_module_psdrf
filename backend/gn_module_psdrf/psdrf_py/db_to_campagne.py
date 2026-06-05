"""
Adaptateur BDD GeoNature → dossier « campagne » du pipeline PermPSDRF4py.

Remplace l'étape d'import Excel (``psdrf_xls2data`` / ``psdrf_codes``) du pipeline
autonome : on lit le schéma ``pr_psdrf`` de PostgreSQL et on écrit les deux pickles
d'entrée attendus par les calculs (``psdrfDonneesBrutes.pkl`` + ``psdrfCodes.pkl``)
dans un dossier campagne conforme ``out/{disp}-{slug}/Campagne{annee}/``.

Les requêtes et le mapping de colonnes reprennent ceux de l'ancienne chaîne rpy2
(``data_analysis.formatBdd2RData``), seule la sortie change (DataFrames pandas au
lieu de data.frames R). Le pré-traitement de parité (booléens ``t``/``f``,
``NumPlac`` en chaîne, ``Type`` vide → ``None``, nomenclatures durete/écorce
id→cd) est indispensable pour que les calculs Python reproduisent le R.

Décision projet : les référentiels (``codes``) proviennent de PsdrfListes
(``PSDRF_DATA_DIR``), comme l'ancien ``psdrf_Codes.R`` — pas de la BDD (les tables
Cat/Tarifs/EssReg y sont vides).
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd
from geonature.utils.env import DB
from sqlalchemy.sql.expression import func

# Déclenche le bootstrap (sys.path vers le sous-module + backend matplotlib).
from . import SUBMODULE_ROOT  # noqa: F401

from python.script.campagne_paths import (  # noqa: E402
    campagne_dir_name,
    campagne_year_rule_c,
    disp_dir_slug,
    ensure_campagne_layout,
)
from python.script.io_paths import psdrf_listes_path  # noqa: E402
from python.script.io_storage import (  # noqa: E402
    codes_pickle_path,
    load_pickle,
    save_psdrf_codes,
    save_psdrf_donnees_brutes,
)
from python.script.psdrf_codes import psdrf_codes  # noqa: E402
from python.script.psdrf_xls2data import build_id_arbres  # noqa: E402

from ..geonature_PSDRF_function import (  # noqa: E402
    get_cd_nomenclature_from_id_type_and_id_nomenclature,
    get_id_type_from_mnemonique,
)
from ..models import (  # noqa: E402
    CorCyclesPlacettes,
    TArbres,
    TArbresMesures,
    TBmSup30,
    TBmSup30Mesures,
    TCycles,
    TPlacettes,
    TRegenerations,
    TReperes,
    TTransects,
)

# Colonnes texte de Placettes : forcées en dtype object (None si vide). Sinon une
# colonne partiellement vide revient en float64 depuis la BDD alors que le chemin
# Excel produit de l'object.
_PLAC_TEXT_COLS = [
    "Strate", "Exposition", "Habitat", "PrecisionGPS", "Station", "Typologie",
    "Groupe", "Groupe1", "Groupe2", "Ref_Habitat", "Precision_Habitat",
    "Ref_Station", "Ref_Typologie", "Descriptif_Groupe", "Descriptif_Groupe1",
    "Descriptif_Groupe2", "Cheminement", "Nature_Intervention", "Gestion",
]

# Colonnes de regroupement pilotant l'agrégation par groupe : une colonne
# ENTIÈREMENT vide est retirée (comme une colonne absente du classeur Excel),
# sinon le pipeline tente de grouper/merger dessus et plante (float64 vs object).
_GROUP_CANDIDATE_COLS = ["Strate", "Habitat", "Groupe", "Groupe1", "Groupe2", "Gestion"]

# Colonnes booléennes (PostgreSQL boolean) → 't'/'f' attendus par le pipeline.
_BOOL_COLS = {
    "Placettes": ["CorrectionPente"],
    "Arbres": ["Taillis", "Limite", "RatioHaut"],
    "Reges": ["Taillis", "Abroutis"],
    "Transect": ["Contact", "Chablis"],
    "BMSsup30": ["RatioHaut", "Chablis"],
}


@dataclass
class CampagneRefs:
    """Pointeurs vers la campagne générée et ses métadonnées."""

    campagne_dir: Path
    num_disp: int
    last_cycle: int
    disp_slug: str


def _bool_to_tf(value) -> str:
    """True → 't', tout le reste (False/None) → 'f' (parité booleanToChar R)."""
    return "t" if value is True else "f"


def _empty_to_none(value):
    return None if value == "" else value


def _apply_bool_cols(df: pd.DataFrame, table: str) -> pd.DataFrame:
    for col in _BOOL_COLS.get(table, []):
        if col in df.columns:
            df[col] = df[col].map(_bool_to_tf)
    return df


def _convert_stade_value(value, id_type):
    """id_nomenclature (int, éventuellement NaN/float pandas) → code mnémonique."""
    if value is None or pd.isna(value):
        return None
    return get_cd_nomenclature_from_id_type_and_id_nomenclature(id_type, int(value))


def _convert_stades(df: pd.DataFrame, id_type_durete: int, id_type_ecorce: int) -> pd.DataFrame:
    """Convertit StadeD/StadeE d'id_nomenclature vers le code mnémonique (par nom)."""
    if "StadeD" in df.columns:
        df["StadeD"] = df["StadeD"].map(lambda v: _convert_stade_value(v, id_type_durete))
    if "StadeE" in df.columns:
        df["StadeE"] = df["StadeE"].map(lambda v: _convert_stade_value(v, id_type_ecorce))
    return df


def _build_donnees_brutes(disp_id: int) -> dict:
    """Construit le dict des tables d'inventaire (équivalent psdrfDonneesBrutes)."""
    session = DB.session
    id_type_durete = get_id_type_from_mnemonique("PSDRF_DURETE")
    id_type_ecorce = get_id_type_from_mnemonique("PSDRF_ECORCE")

    # --- Arbres ---
    arbres_rows = (
        session.query(
            TPlacettes.id_dispositif, TPlacettes.id_placette_orig,
            TArbres.id_arbre_orig, TArbres.code_essence, TArbres.azimut,
            TArbres.distance, TArbres.taillis,
            TArbresMesures.diametre1, TArbresMesures.diametre2,
            TArbresMesures.type, TArbresMesures.hauteur_totale,
            TArbresMesures.stade_durete, TArbresMesures.stade_ecorce,
            TArbresMesures.coupe, TArbresMesures.limite,
            TArbresMesures.code_ecolo, TArbresMesures.ref_code_ecolo,
            TArbresMesures.id_nomenclature_code_sanitaire, TArbresMesures.hauteur_branche,
            TArbresMesures.ratio_hauteur,
            TArbresMesures.observation, TCycles.num_cycle,
        )
        .filter(TPlacettes.id_dispositif == disp_id)
        .join(TArbres, TArbres.id_placette == TPlacettes.id_placette)
        .join(TArbresMesures)
        .join(TCycles, TCycles.id_cycle == TArbresMesures.id_cycle)
        .all()
    )
    arbres = pd.DataFrame(arbres_rows, columns=[
        "NumDisp", "NumPlac", "NumArbre", "Essence", "Azimut", "Dist", "Taillis",
        "Diam1", "Diam2", "Type", "Haut", "StadeD", "StadeE", "Coupe", "Limite",
        "CodeEcolo", "Ref_CodeEcolo", "CodeSanit", "HautV", "RatioHaut",
        "Observation", "Cycle",
    ])
    arbres = _convert_stades(arbres, id_type_durete, id_type_ecorce)
    arbres = _apply_bool_cols(arbres, "Arbres")
    if "Type" in arbres.columns:
        arbres["Type"] = arbres["Type"].map(_empty_to_none)

    # --- BMSsup30 ---
    bms_rows = (
        session.query(
            TPlacettes.id_dispositif, TPlacettes.id_placette_orig,
            TBmSup30.id_bm_sup_30_orig, TBmSup30.id_arbre, TCycles.num_cycle,
            TBmSup30.code_essence, TBmSup30.azimut, TBmSup30.distance,
            TBmSup30Mesures.diametre_ini, TBmSup30Mesures.diametre_med,
            TBmSup30Mesures.diametre_fin, TBmSup30Mesures.longueur,
            TBmSup30Mesures.contact, TBmSup30Mesures.chablis,
            TBmSup30Mesures.stade_durete, TBmSup30Mesures.stade_ecorce,
            TBmSup30Mesures.observation, TBmSup30Mesures.diametre_130,
            TBmSup30.azimut_souche, TBmSup30.distance_souche,
            TBmSup30Mesures.ratio_hauteur, TBmSup30.orientation,
        )
        .filter(TPlacettes.id_dispositif == disp_id)
        .join(TBmSup30, TBmSup30.id_placette == TPlacettes.id_placette)
        .join(TBmSup30Mesures)
        .join(TCycles, TCycles.id_cycle == TBmSup30Mesures.id_cycle)
        .all()
    )
    bms = pd.DataFrame(bms_rows, columns=[
        "NumDisp", "NumPlac", "Id", "NumArbre", "Cycle", "Essence", "Azimut",
        "Dist", "DiamIni", "DiamMed", "DiamFin", "Longueur", "Contact", "Chablis",
        "StadeD", "StadeE", "Observation", "Diam130", "AzimutS", "DistS",
        "RatioHaut", "Orientation",
    ])
    bms = _convert_stades(bms, id_type_durete, id_type_ecorce)
    bms = _apply_bool_cols(bms, "BMSsup30")

    # --- Placettes ---
    placettes_rows = (
        session.query(
            TPlacettes.id_dispositif, TPlacettes.id_placette_orig, TPlacettes.strate,
            TPlacettes.poids_placette, TPlacettes.pente, TPlacettes.correction_pente,
            TPlacettes.exposition, TPlacettes.habitat, TPlacettes.precision_gps,
            TPlacettes.station, TPlacettes.typologie, TPlacettes.groupe,
            TPlacettes.groupe1, TPlacettes.groupe2, TPlacettes.ref_habitat,
            TPlacettes.precision_habitat, TPlacettes.ref_station, TPlacettes.ref_typologie,
            TPlacettes.descriptif_groupe, TPlacettes.descriptif_groupe1,
            TPlacettes.descriptif_groupe2, TPlacettes.cheminement,
            CorCyclesPlacettes.date_intervention, CorCyclesPlacettes.nature_intervention,
            CorCyclesPlacettes.gestion_placette, TCycles.num_cycle,
        )
        .filter(TPlacettes.id_dispositif == disp_id)
        .join(CorCyclesPlacettes, CorCyclesPlacettes.id_placette == TPlacettes.id_placette)
        .join(TCycles, TCycles.id_cycle == CorCyclesPlacettes.id_cycle)
        .all()
    )
    placettes = pd.DataFrame(placettes_rows, columns=[
        "NumDisp", "NumPlac", "Strate", "PoidsPlacette", "Pente", "CorrectionPente",
        "Exposition", "Habitat", "PrecisionGPS", "Station", "Typologie", "Groupe",
        "Groupe1", "Groupe2", "Ref_Habitat", "Precision_Habitat", "Ref_Station",
        "Ref_Typologie", "Descriptif_Groupe", "Descriptif_Groupe1",
        "Descriptif_Groupe2", "Cheminement", "Date_Intervention",
        "Nature_Intervention", "Gestion", "Cycle",
    ])
    placettes = _apply_bool_cols(placettes, "Placettes")
    # Retirer les colonnes de regroupement entièrement vides (mirror du classeur Excel).
    empty_group_cols = [
        c for c in _GROUP_CANDIDATE_COLS
        if c in placettes.columns and placettes[c].isna().all()
    ]
    if empty_group_cols:
        placettes = placettes.drop(columns=empty_group_cols)
    # Forcer les colonnes texte restantes en object (None si vide).
    for col in _PLAC_TEXT_COLS:
        if col in placettes.columns:
            placettes[col] = placettes[col].astype(object).where(placettes[col].notna(), None)

    # --- Régénérations ---
    reges_rows = (
        session.query(
            TPlacettes.id_dispositif, TPlacettes.id_placette_orig,
            TRegenerations.sous_placette, TCycles.num_cycle, TRegenerations.code_essence,
            TRegenerations.recouvrement, TRegenerations.classe1, TRegenerations.classe2,
            TRegenerations.classe3, TRegenerations.taillis, TRegenerations.abroutissement,
            TRegenerations.observation,
        )
        .filter(TPlacettes.id_dispositif == disp_id)
        .join(CorCyclesPlacettes, CorCyclesPlacettes.id_placette == TPlacettes.id_placette)
        .join(TCycles, TCycles.id_cycle == CorCyclesPlacettes.id_cycle)
        .join(TRegenerations, TRegenerations.id_cycle_placette == CorCyclesPlacettes.id_cycle_placette)
        .all()
    )
    reges = pd.DataFrame(reges_rows, columns=[
        "NumDisp", "NumPlac", "SsPlac", "Cycle", "Essence", "Recouv",
        "Class1", "Class2", "Class3", "Taillis", "Abroutis", "Observation",
    ])
    reges = _apply_bool_cols(reges, "Reges")

    # --- Transects ---
    transects_rows = (
        session.query(
            TPlacettes.id_dispositif, TPlacettes.id_placette_orig,
            TTransects.id_transect_orig, TCycles.num_cycle, TTransects.ref_transect,
            TTransects.code_essence, TTransects.distance, TTransects.diametre,
            TTransects.angle, TTransects.contact, TTransects.chablis,
            TTransects.stade_durete, TTransects.stade_ecorce, TTransects.observation,
        )
        .filter(TPlacettes.id_dispositif == disp_id)
        .join(CorCyclesPlacettes, CorCyclesPlacettes.id_placette == TPlacettes.id_placette)
        .join(TCycles, TCycles.id_cycle == CorCyclesPlacettes.id_cycle)
        .join(TTransects, TTransects.id_cycle_placette == CorCyclesPlacettes.id_cycle_placette)
        .all()
    )
    transect = pd.DataFrame(transects_rows, columns=[
        "NumDisp", "NumPlac", "Id", "Cycle", "Transect", "Essence", "Dist",
        "Diam", "Angle", "Contact", "Chablis", "StadeD", "StadeE", "Observation",
    ])
    transect = _convert_stades(transect, id_type_durete, id_type_ecorce)
    transect = _apply_bool_cols(transect, "Transect")

    # --- Repères ---
    reperes_rows = (
        session.query(
            TPlacettes.id_dispositif, TPlacettes.id_placette_orig, TReperes.azimut,
            TReperes.distance, TReperes.diametre, TReperes.repere, TReperes.observation,
        )
        .filter(TPlacettes.id_dispositif == disp_id)
        .join(TReperes, TReperes.id_placette == TPlacettes.id_placette)
        .all()
    )
    reperes = pd.DataFrame(reperes_rows, columns=[
        "NumDisp", "NumPlac", "Azimut", "Dist", "Diam", "Repere", "Observation",
    ])

    # --- Cycles (par placette : Annee/Coeff/DiamLim) ---
    cycles_rows = (
        session.query(
            TPlacettes.id_dispositif, TPlacettes.id_placette_orig,
            CorCyclesPlacettes.annee, TCycles.num_cycle, CorCyclesPlacettes.coeff,
            CorCyclesPlacettes.diam_lim,
        )
        .filter(TPlacettes.id_dispositif == disp_id)
        .join(CorCyclesPlacettes, CorCyclesPlacettes.id_placette == TPlacettes.id_placette)
        .join(TCycles, TCycles.id_cycle == CorCyclesPlacettes.id_cycle)
        .all()
    )
    cycles = pd.DataFrame(cycles_rows, columns=[
        "NumDisp", "NumPlac", "Annee", "Cycle", "Coeff", "DiamLim",
    ])

    # --- Normalisations communes (parité _coerce_stacked) ---
    for df in (arbres, bms, placettes, reges, transect, reperes, cycles):
        if "NumPlac" in df.columns and not df.empty:
            df["NumPlac"] = df["NumPlac"].astype(str)

    pcqm = pd.DataFrame(columns=["NumDisp", "NumPlac", "Cycle", "Quart"])

    # --- IdArbres / ValArbres (identité inter-cycles) ---
    if not arbres.empty:
        id_arbres, val_arbres = build_id_arbres(arbres)
    else:
        id_arbres, val_arbres = (
            pd.DataFrame(columns=["NumDisp", "NumPlac", "NumArbre", "Essence", "Azimut", "Dist", "IdArbre", "IdArbreLocal"]),
            pd.DataFrame(),
        )

    return {
        "Placettes": placettes,
        "IdArbres": id_arbres,
        "ValArbres": val_arbres,
        "PCQM": pcqm,
        "Reges": reges,
        "Transect": transect,
        "BMSsup30": bms,
        "Reperes": reperes,
        "Cycles": cycles,
    }


def _load_codes(data_dir: Path) -> dict:
    """
    Charge le référentiel ``codes`` depuis PsdrfListes (décision projet).

    Priorité au pickle global ``{data_dir}/tables/psdrfCodes.pkl`` (produit à
    l'upload ``/psdrfListe``) ; sinon (re)génère depuis ``PsdrfListes.xlsx``.
    """
    global_pkl = codes_pickle_path(data_dir)
    if global_pkl.is_file():
        return load_pickle(global_pkl)
    xlsx = psdrf_listes_path(data_dir)
    if not xlsx.is_file():
        raise FileNotFoundError(
            f"Référentiel introuvable : ni {global_pkl} ni PsdrfListes.xlsx sous {data_dir}. "
            "Charger d'abord PsdrfListes via /psdrfListe."
        )
    return psdrf_codes(data_dir, xlsx)


def _last_cycle(disp_id: int) -> int:
    val = (
        DB.session.query(func.max(TCycles.num_cycle))
        .filter(TCycles.id_dispositif == disp_id)
        .scalar()
    )
    return int(val) if val is not None else 1


def build_campagne_from_db(disp_id: int, *, base_dir: Path, data_dir: Path) -> CampagneRefs:
    """
    Construit un dossier campagne complet (pickles codes + données brutes) à partir
    de la BDD, prêt à être consommé par psdrf_calculs / psdrf_edit_carnet.

    Parameters
    ----------
    disp_id
        Identifiant de dispositif (== NumDisp côté pipeline).
    base_dir
        Racine de travail (ex. ``{PSDRF_EXPORT_DIR}/disp-{id}-{task_id}``) ;
        joue le rôle de ``PROJECT_ROOT`` pour la convention ``out/...``.
    data_dir
        Répertoire des référentiels web (``PSDRF_DATA_DIR``) contenant PsdrfListes.
    """
    base_dir = Path(base_dir)
    data_dir = Path(data_dir)

    donnees = _build_donnees_brutes(disp_id)
    codes = _load_codes(data_dir)
    last_cycle = _last_cycle(disp_id)

    year = campagne_year_rule_c(donnees, disp_id, last_cycle)
    slug = disp_dir_slug(disp_id, codes)
    if "-" not in slug:  # garantir le séparateur attendu par les détections internes
        slug = f"{disp_id}-disp"
    campagne = base_dir / "out" / slug / campagne_dir_name(year)
    ensure_campagne_layout(
        campagne, num_disp=disp_id, cycle=last_cycle, year=year, disp_slug=slug
    )

    save_psdrf_donnees_brutes(campagne, donnees)
    save_psdrf_codes(campagne, codes)

    return CampagneRefs(
        campagne_dir=campagne,
        num_disp=disp_id,
        last_cycle=last_cycle,
        disp_slug=slug,
    )
