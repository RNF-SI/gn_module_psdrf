# Documentation du développement - Génération de carnets PSDRF

## Introduction

Ce document décrit les aspects techniques de la génération des carnets d'analyse dans le module PSDRF de GeoNature. La génération du carnet est un composant essentiel du module, permettant de transformer les données forestières collectées en un document PDF d'analyse complet.

## Architecture générale

La génération du carnet implique plusieurs couches technologiques :

1. **Base de données** : Stockage des données forestières dans PostgreSQL (schéma `pr_psdrf`)
2. **Backend Python** : Extraction et préparation des données via l'API Flask
3. **Scripts R** : Analyse statistique et génération des visualisations
4. **LaTeX** : Mise en page du document final

## Flux de données

```
DB PostgreSQL → Python → R → LaTeX → PDF
```

Les données suivent un parcours précis lors de la génération :

1. Les données sont extraites de la base via des requêtes SQL
2. Le backend Python convertit ces données en formats adaptés pour R
3. Les scripts R effectuent les analyses et préparent les visualisations
4. Le template Rnw (LaTeX + R) est compilé pour générer le PDF final

## Méthodes de génération du carnet

### 1. Génération via l'interface web

La génération principale se fait via l'interface web de GeoNature. Le process est géré par :

- **Backend** : `data_analysis.py` - Point d'entrée principal qui appelle `generate_carnet_web.py`
- **Génération** : `generate_carnet_web.py` - Script optimisé pour l'interface web

```python
# Extrait de data_analysis.py
def data_analysis(dispId, isCarnetToDownload, isPlanDesArbresToDownload, carnetToDownloadParameters):
    try:
        # Utiliser le nouveau module pour générer le carnet directement
        success = generate_carnet_web(dispId, isCarnetToDownload, isPlanDesArbresToDownload, carnetToDownloadParameters)
        if success:
            print(f"Génération du carnet pour le dispositif {dispId} réussie avec le nouveau module!")
            return
    except Exception as e:
        print(f"Erreur avec le nouveau module de génération: {e}")
        print("Tentative avec l'ancienne méthode...")

    # Si le nouveau module échoue, on utilise l'ancienne méthode...
```

### 2. Scripts de tests optimisés

Pour accélérer le développement et le debugging, plusieurs scripts ont été créés :

#### a. `test_carnet.sh` - Shell script pour tester rapidement un dispositif

Ce script bash permet de tester la génération d'un carnet sans avoir à passer par l'interface web :

```bash
#!/bin/bash

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
```

#### b. `test_carnet_only.R` - Script R qui réutilise les données déjà générées

Ce script R permet de tester rapidement les modifications du template Rnw sans avoir à régénérer toutes les données depuis la base :

```r
# Script pour tester uniquement la génération du carnet sans régénérer les données
# Usage: Rscript test_carnet_only.R [dispositif_id]

# Récupérer l'ID du dispositif en argument
args <- commandArgs(trailingOnly = TRUE)
disp_num <- if (length(args) > 0) as.numeric(args[1]) else 152  # Utiliser 152 par défaut

# Définir le chemin du répertoire de base
repPSDRF <- "/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts"

# Définir les chemins des fichiers
output_dir <- file.path(repPSDRF, "out")
template_file <- file.path(repPSDRF, "template/psdrf_Carnet_V3.Rnw")
carnet_name <- paste0("carnet_Altier_", format(Sys.Date(), "%Y"), ".tex")

# Définir le fichier de log
log_file <- "/home/geonatureadmin/gn_module_psdrf/carnet_generation.log"
cat(paste("=== Démarrage génération carnet pour dispositif", disp_num, "à", format(Sys.time()), "===\n"),
    file=log_file, append=TRUE)

# Vérifier si les fichiers R Data nécessaires existent déjà
if (!file.exists(file.path(repPSDRF, "tables/psdrfTablesElaborees.Rdata")) ||
    !file.exists(file.path(repPSDRF, "tables/psdrfTablesElaboreesPlac.Rdata"))) {
  cat("ERREUR: Les fichiers de données n'existent pas encore. Vous devez d'abord générer les données.\n",
      file=log_file, append=TRUE)
  cat("ERREUR: Les fichiers de données n'existent pas encore. Vous devez d'abord générer les données.\n")
  quit(status=1)
}

# Librairies nécessaires pour la génération du carnet
required_packages <- c("knitr", "xtable", "reshape2", "dplyr", "stringr", "stringi", "ggplot2")
for (pkg in required_packages) {
  if (!require(pkg, character.only = TRUE, quietly = TRUE)) {
    install.packages(pkg, repos="https://cloud.r-project.org")
    library(pkg, character.only = TRUE)
  }
}

# Tester seulement la génération du PDF
try({
  # Assurer que le répertoire de sortie existe
  dir.create(output_dir, showWarnings = FALSE, recursive = TRUE)

  # Assigner l'ID du dispositif dans l'environnement global
  assign("disp_num", disp_num, envir = .GlobalEnv)
  assign("Answer_Radar", NULL, envir = .GlobalEnv)

  # Générer le PDF à partir du template
  cat("Génération du carnet pour dispositif", disp_num, "...\n", file=log_file, append=TRUE)
  knit2pdf(template_file, output = file.path(output_dir, carnet_name))
  cat("Génération du carnet terminée!\n", file=log_file, append=TRUE)

  # Afficher le chemin du fichier généré
  pdf_file <- gsub(".tex$", ".pdf", file.path(output_dir, carnet_name))
  cat("PDF généré:", pdf_file, "\n", file=log_file, append=TRUE)
  cat("PDF généré:", pdf_file, "\n")
})

cat("=== Fin génération carnet à", format(Sys.time()), "===\n", file=log_file, append=TRUE)
```

### 3. Génération autonome pour les tests avancés

Pour les tests plus approfondis nécessitant une régénération complète des données depuis la base, le script `generate_carnet_adapted.py` permet une exécution autonome sans dépendre de GeoNature :

```python
# Extrait de generate_carnet_adapted.py
def generate_carnet(disp_id, is_carnet=True, is_plan=False):
    """
    Génère le carnet PSDRF en utilisant les scripts R originaux

    Args:
        disp_id (int): ID du dispositif
        is_carnet (bool): Si True, génère le carnet
        is_plan (bool): Si True, génère le plan des arbres
    """
    try:
        print(f"Génération du carnet pour le dispositif {disp_id}")

        # Nettoyer les fichiers de sortie au préalable
        out_dir = '/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/out'
        ...

        # Établir une connexion directe à la base de données
        # Extraire les données
        # Transformer en format R
        # Générer le carnet
        ...
```

## Bonnes pratiques pour la modification des templates

1. **Utiliser les scripts de test** : Privilégier `test_carnet.sh` pour itérer rapidement
2. **Journalisation** : Vérifier les fichiers de log pour le débogage
3. **Protection contre les NA** : Toujours utiliser les fonctions sécurisées comme `safe_filter_vha()`
4. **Sanitisation LaTeX** : Utiliser `sanitize_latex_output()` pour les chaînes qui pourraient contenir des caractères spéciaux

## Workflow recommandé pour les modifications

1. **Génération initiale** via l'interface web ou `generate_carnet_adapted.py` pour créer tous les fichiers nécessaires
2. **Modifications du template** en utilisant `test_carnet_only.R` pour des itérations rapides
3. **Test complet** en utilisant `test_carnet.sh` ou l'interface web
4. **Debug** en consultant les fichiers de log en cas d'erreur

## Conclusion

La génération du carnet est un processus complexe qui intègre plusieurs technologies. Les outils de test développés permettent d'itérer rapidement sur les modifications sans avoir à régénérer toutes les données à chaque fois, ce qui accélère considérablement le développement et la correction des problèmes.
