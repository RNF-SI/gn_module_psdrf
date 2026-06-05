"""
Pont entre le module web GeoNature et le pipeline Python autonome PermPSDRF4py
(sous-module ``backend/gn_module_psdrf/PermPSDRF4py``).

Ce package remplace l'ancienne chaîne R (rpy2 → BDD2RData.R → knit2pdf) par des
appels directs aux fonctions Python du sous-module. L'import de ce package a deux
effets de bord nécessaires, exécutés une seule fois :

1. Forcer le backend matplotlib en ``Agg`` (génération de figures sans display,
   indispensable dans le worker Celery), AVANT tout import de ``matplotlib.pyplot``.
2. Ajouter la racine du sous-module au ``sys.path`` pour que les imports absolus
   du pipeline (``from python.script... import``) se résolvent. Cette racine est
   exactement le ``PROJECT_ROOT`` attendu par ``io_paths.py`` du sous-module.

NB : le sous-module expose un package top-level littéralement nommé ``python``.
On l'accepte via un ``sys.path`` ciblé (le sous-module n'a pas de ``setup.py``).
On ne doit jamais laisser le pipeline écrire dans ``SUBMODULE_ROOT/out/`` :
toujours passer un ``rep_sav`` / ``rep_data`` explicite (dossier campagne).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# 1/ Backend matplotlib headless — doit précéder tout import de pyplot.
os.environ.setdefault("MPLBACKEND", "Agg")
try:
    import matplotlib

    matplotlib.use("Agg", force=True)
except Exception:  # pragma: no cover - matplotlib absent au moment du bootstrap
    pass

# 2/ Racine du sous-module = PROJECT_ROOT attendu par le pipeline Python.
SUBMODULE_ROOT = Path(__file__).resolve().parent.parent / "PermPSDRF4py"
if str(SUBMODULE_ROOT) not in sys.path:
    sys.path.insert(0, str(SUBMODULE_ROOT))

__all__ = ["SUBMODULE_ROOT"]
