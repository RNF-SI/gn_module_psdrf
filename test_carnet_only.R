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
