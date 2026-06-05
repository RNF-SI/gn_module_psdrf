"""
Transformations pures (sans GeoNature ni BDD) du pont PSDRF.

Isolées ici pour être testables en unitaire avec pandas seul : normalisation de
parité (booléens ``t``/``f``, ``Type`` vide → None, colonnes de regroupement),
conversion des stades et mapping du paramètre web ``Answer_Radar``.
"""

from __future__ import annotations

from typing import Callable, Optional

import pandas as pd

# Colonnes booléennes (PostgreSQL boolean) → 't'/'f' attendus par le pipeline.
BOOL_COLS = {
    "Placettes": ["CorrectionPente"],
    "Arbres": ["Taillis", "Limite", "RatioHaut"],
    "Reges": ["Taillis", "Abroutis"],
    "Transect": ["Contact", "Chablis"],
    "BMSsup30": ["RatioHaut", "Chablis"],
}

# Colonnes texte de Placettes : forcées en dtype object (None si vide). Sinon une
# colonne partiellement vide revient en float64 depuis la BDD alors que le chemin
# Excel produit de l'object.
PLAC_TEXT_COLS = [
    "Strate", "Exposition", "Habitat", "PrecisionGPS", "Station", "Typologie",
    "Groupe", "Groupe1", "Groupe2", "Ref_Habitat", "Precision_Habitat",
    "Ref_Station", "Ref_Typologie", "Descriptif_Groupe", "Descriptif_Groupe1",
    "Descriptif_Groupe2", "Cheminement", "Nature_Intervention", "Gestion",
]

# Colonnes de regroupement pilotant l'agrégation par groupe : une colonne
# ENTIÈREMENT vide est retirée (comme une colonne absente du classeur Excel),
# sinon le pipeline tente de grouper/merger dessus et plante (float64 vs object).
GROUP_CANDIDATE_COLS = ["Strate", "Habitat", "Groupe", "Groupe1", "Groupe2", "Gestion"]

# Valeurs sentinelles d'Answer_Radar désactivant le chapitre Conservation.
_RADAR_OFF = {"none", "false", "non", "no", "0"}


def bool_to_tf(value) -> str:
    """True → 't', tout le reste (False/None/NaN) → 'f' (parité booleanToChar R)."""
    return "t" if value is True else "f"


def empty_to_none(value):
    return None if value == "" else value


def apply_bool_cols(df: pd.DataFrame, table: str) -> pd.DataFrame:
    for col in BOOL_COLS.get(table, []):
        if col in df.columns:
            df[col] = df[col].map(bool_to_tf)
    return df


def convert_stade_value(value, lookup: Callable[[int], Optional[str]]):
    """id_nomenclature (int, éventuellement NaN/float pandas) → code via ``lookup``."""
    if value is None or pd.isna(value):
        return None
    return lookup(int(value))


def convert_stades(
    df: pd.DataFrame,
    lookup_durete: Callable[[int], Optional[str]],
    lookup_ecorce: Callable[[int], Optional[str]],
) -> pd.DataFrame:
    """Convertit StadeD/StadeE d'id_nomenclature vers le code mnémonique (par nom)."""
    if "StadeD" in df.columns:
        df["StadeD"] = df["StadeD"].map(lambda v: convert_stade_value(v, lookup_durete))
    if "StadeE" in df.columns:
        df["StadeE"] = df["StadeE"].map(lambda v: convert_stade_value(v, lookup_ecorce))
    return df


def normalize_placettes(df: pd.DataFrame) -> pd.DataFrame:
    """Booléens t/f + retrait des colonnes de groupe vides + colonnes texte en object."""
    df = apply_bool_cols(df, "Placettes")
    empty_group_cols = [
        c for c in GROUP_CANDIDATE_COLS
        if c in df.columns and df[c].isna().all()
    ]
    if empty_group_cols:
        df = df.drop(columns=empty_group_cols)
    for col in PLAC_TEXT_COLS:
        if col in df.columns:
            df[col] = df[col].astype(object).where(df[col].notna(), None)
    return df


def map_radar(answer_radar) -> tuple[bool, Optional[list[str]]]:
    """
    Traduit le paramètre web ``Answer_Radar`` vers (include_conservation, groups).

    - vide / None        → radar dispositif global (conservation activée, pas de groupe)
    - 'none'/'false'/... → conservation désactivée
    - '<colonne>'        → radars par regroupement sur cette colonne
    """
    if answer_radar is None:
        return True, None
    value = str(answer_radar).strip()
    if value == "":
        return True, None
    if value.lower() in _RADAR_OFF:
        return False, None
    return True, [value]
