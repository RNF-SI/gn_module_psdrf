#!/bin/bash

# Script pour tester uniquement la génération du carnet sans régénérer les données
# Usage: bash test_carnet.sh [DISPOSITIF_ID]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Définir l'ID du dispositif (par défaut: 152)
DISPOSITIF_ID=${1:-152}

# Chemin vers R
R_PATH=$(which Rscript)
if [ -z "$R_PATH" ]; then
  echo "ERREUR: Rscript n'est pas disponible. Assurez-vous que R est installé."
  exit 1
fi

echo "Génération du carnet pour le dispositif $DISPOSITIF_ID..."
echo "Cette opération peut prendre quelques minutes."

# Executer le script R pour générer uniquement le carnet
$R_PATH "$SCRIPT_DIR/test_carnet_only.R" $DISPOSITIF_ID

# Vérifier si la génération a réussi
if [ $? -eq 0 ]; then
  echo "Opération terminée!"
  echo "Vous pouvez trouver le PDF généré dans: $SCRIPT_DIR/backend/gn_module_psdrf/Rscripts/out/"

  # Créer un lien symbolique pour faciliter l'accès
  mkdir -p "$HOME/output_files"
  ln -sf "$SCRIPT_DIR/backend/gn_module_psdrf/Rscripts/out/"* "$HOME/output_files/"
  echo "Un lien symbolique a été créé dans: $HOME/output_files/"
else
  echo "La génération du carnet a échoué. Consultez le fichier de log pour plus de détails:"
  echo "$SCRIPT_DIR/carnet_generation.log"
fi
