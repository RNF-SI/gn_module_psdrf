#\!/bin/bash

# Script pour tester uniquement la génération du carnet sans régénérer les données
# Usage: bash test_carnet.sh [DISPOSITIF_ID]

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
$R_PATH /home/geonatureadmin/gn_module_psdrf/test_carnet_only.R $DISPOSITIF_ID

# Vérifier si la génération a réussi
if [ $? -eq 0 ]; then
  echo "Opération terminée!"
  echo "Vous pouvez trouver le PDF généré dans: /home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/out/"
  
  # Créer un lien symbolique pour faciliter l'accès
  mkdir -p /home/geonatureadmin/output_files
  ln -sf /home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/out/* /home/geonatureadmin/output_files/
  echo "Un lien symbolique a été créé dans: /home/geonatureadmin/output_files/"
else
  echo "La génération du carnet a échoué. Consultez le fichier de log pour plus de détails:"
  echo "/home/geonatureadmin/gn_module_psdrf/carnet_generation.log"
fi
