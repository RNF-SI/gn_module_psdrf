"""Régression : la liste des tables du carnet doit rester complète et cohérente."""

from gn_module_psdrf.psdrf_py.carnet_tables import TABPLA_NAMES_CARNET


def test_97_tables():
    assert len(TABPLA_NAMES_CARNET) == 97


def test_noms_uniques():
    assert len(set(TABPLA_NAMES_CARNET)) == len(TABPLA_NAMES_CARNET)


def test_prefixe_psdrfpla():
    assert all(name.startswith("psdrfPla") for name in TABPLA_NAMES_CARNET)
