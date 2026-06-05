#!/bin/bash
# Installation des dépendances système du module PSDRF.
#
# Depuis la bascule R→Python, le module n'a plus besoin de R ni des ~30 paquets R.
# Seule subsiste une distribution LaTeX (pdflatex) pour compiler le carnet PDF
# produit par le pipeline Python (PermPSDRF4py). Les dépendances Python sont
# installées par `geonature install_gn_module` (via setup.py / requirements.in) ;
# on les (re)pose ici par sécurité dans le venv GeoNature.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Override via la variable d'environnement GEONATURE_VENV si l'install GeoNature
# n'est pas dans $HOME/geonature/backend
GEONATURE_VENV="${GEONATURE_VENV:-$HOME/geonature/backend}"

# LaTeX requis pour la compilation du carnet PDF (pdflatex).
# texlive-lang-french : indispensable (babel french / french.ldf) — le carnet est en français,
# sans lui pdflatex échoue avec « Package babel Error: Unknown option 'french' ».
sudo apt-get update
sudo apt-get install -y texlive-latex-extra texlive-latex-recommended texlive-fonts-recommended texlive-lang-french

# Récupérer le sous-module PermPSDRF4py (pipeline Python).
cd "$SCRIPT_DIR"
git submodule update --init --recursive

cd "$GEONATURE_VENV"
source venv/bin/activate

# Dépendances Python du pipeline (pandas, numpy, scipy, matplotlib, jinja2, openpyxl).
pip install -r "$SCRIPT_DIR/requirements.in"

geonature update_configuration

deactivate
