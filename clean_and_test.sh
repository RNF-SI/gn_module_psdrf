#!/bin/bash

# Script pour nettoyer les fichiers et tester uniquement la génération du carnet
# Usage: bash clean_and_test.sh [DISPOSITIF_ID]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Définir l'ID du dispositif (par défaut: 152)
DISPOSITIF_ID=${1:-152}

# Répertoire de sortie
OUTPUT_DIR="$SCRIPT_DIR/backend/gn_module_psdrf/Rscripts/out"
LOG_FILE="$SCRIPT_DIR/vha_debug.log"
CARNET_LOG="$SCRIPT_DIR/carnet_generation.log"

echo "Nettoyage des fichiers temporaires..."

# Nettoyer le fichier TEX problématique
rm -f $OUTPUT_DIR/carnet_*.tex
rm -f $OUTPUT_DIR/carnet_*.pdf
rm -f $OUTPUT_DIR/carnet_*.log
rm -f $OUTPUT_DIR/carnet_*.aux
rm -f $OUTPUT_DIR/carnet_*.toc
rm -f $OUTPUT_DIR/carnet_*.out

# Vider les fichiers de log
echo "=== Nouveau test à $(date) ===" > $LOG_FILE
echo "=== Nouveau test à $(date) ===" > $CARNET_LOG

echo "Fichiers temporaires nettoyés!"
echo "Lancement de la génération du carnet..."

# Lancer le test du carnet
bash "$SCRIPT_DIR/test_carnet.sh" $DISPOSITIF_ID
