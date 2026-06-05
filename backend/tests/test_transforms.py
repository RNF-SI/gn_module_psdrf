"""
Tests des transformations de parité BDD → pipeline (sans GeoNature ni BDD).

Verrouille les corrections trouvées lors de la bascule R→Python :
- booléens PostgreSQL → 't'/'f' (sinon les filtres `== "t"` ne matchent jamais) ;
- StadeD/StadeE id_nomenclature avec NaN → None (et non la chaîne 'nan' en SQL) ;
- colonnes de regroupement entièrement vides retirées + colonnes texte en object
  (sinon merge float64 vs object dans l'agrégation) ;
- mapping du paramètre web Answer_Radar.
"""

import numpy as np
import pandas as pd

from gn_module_psdrf.psdrf_py.transforms import (
    apply_bool_cols,
    bool_to_tf,
    convert_stades,
    empty_to_none,
    map_radar,
    normalize_placettes,
)


def test_bool_to_tf():
    assert bool_to_tf(True) == "t"
    assert bool_to_tf(False) == "f"
    assert bool_to_tf(None) == "f"


def test_apply_bool_cols_arbres():
    df = pd.DataFrame({"Taillis": [True, False, None], "Autre": [1, 2, 3]})
    out = apply_bool_cols(df, "Arbres")
    assert out["Taillis"].tolist() == ["t", "f", "f"]
    assert out["Autre"].tolist() == [1, 2, 3]  # colonne non booléenne intacte


def test_empty_to_none():
    assert empty_to_none("") is None
    assert empty_to_none("Vivant") == "Vivant"


def test_convert_stades_gere_nan():
    calls = []

    def lookup(v):
        calls.append(v)
        return f"code{v}"

    df = pd.DataFrame({"StadeD": [2.0, np.nan, 3.0], "StadeE": [np.nan, 1.0, np.nan]})
    out = convert_stades(df, lookup, lookup)
    assert out["StadeD"].tolist() == ["code2", None, "code3"]
    assert out["StadeE"].tolist() == [None, "code1", None]
    # le lookup ne reçoit jamais de NaN, et reçoit des int (pas 2.0)
    assert all(isinstance(c, int) for c in calls)


def test_normalize_placettes():
    df = pd.DataFrame({
        "NumPlac": ["1", "2"],
        "CorrectionPente": [True, False],
        "Strate": [1, 1],
        "Groupe": [None, None],        # entièrement vide → retirée
        "Groupe1": ["A", None],        # partielle → object, NaN → None
    })
    out = normalize_placettes(df)
    assert "Groupe" not in out.columns          # colonne vide retirée
    assert out["CorrectionPente"].tolist() == ["t", "f"]
    assert out["Groupe1"].tolist() == ["A", None]
    assert out["Groupe1"].dtype == object


def test_map_radar():
    assert map_radar(None) == (True, None)
    assert map_radar("") == (True, None)
    assert map_radar("none") == (False, None)
    assert map_radar("false") == (False, None)
    assert map_radar("Strate") == (True, ["Strate"])
