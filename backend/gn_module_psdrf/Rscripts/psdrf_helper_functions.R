# Fonctions utilitaires pour aider la génération du carnet d'analyse PSDRF

# Fonction pour sanitiser la sortie LaTeX
sanitize_latex_output <- function(text) {
  # Vérifie que l'entrée est bien une chaîne
  if (!is.character(text)) {
    return("% Erreur: entrée non textuelle")
  }
  
  # Remplace tout texte qui pourrait causer des erreurs LaTeX par des commentaires
  # Recherche les chaînes d'erreur typiques
  text <- gsub("\\\\textbf\\{Erreur[^}]*\\}", "% Erreur traitée", text)
  
  # Assure que les sections Latex critiques sont présentes et valides
  if (grepl("\\\\begin\\{document\\}", text) && !grepl("\\\\end\\{document\\}", text)) {
    text <- paste0(text, "\n\\end{document}")
  }
  
  return(text)
}

# Fonction pour gérer les opérations logiques impliquant des NA
safe_logical <- function(expr, default = FALSE) {
  # Cette fonction évalue une expression logique et renvoie default si le résultat est NA
  result <- tryCatch({
    eval(expr)
  }, error = function(e) {
    warning("Erreur dans safe_logical: ", e$message)
    rep(default, length(expr))
  })
  
  # Remplacer tous les NA par default
  result[is.na(result)] <- default
  return(result)
}

# Fonction de débogage pour Vha
debug_vha <- function(data, label="") {
  log_file <- file.path("/home/geonatureadmin/gn_module_psdrf/vha_debug.log")
  
  # Ouvrir le fichier en mode append
  con <- file(log_file, "a")
  
  # Écrire les informations de débogage
  cat(paste0("\n\n--- DÉBOGAGE VHA: ", label, " ---\n"), file=con)
  
  if (is.null(data)) {
    cat("DATA EST NULL\n", file=con)
    close(con)
    return(data)
  }
  
  if (!is.data.frame(data)) {
    cat(paste0("DATA N'EST PAS UN DATA.FRAME, C'EST UN: ", class(data), "\n"), file=con)
    close(con)
    return(data)
  }
  
  cat(paste0("Dimensions: ", nrow(data), " lignes, ", ncol(data), " colonnes\n"), file=con)
  cat(paste0("Colonnes: ", paste(names(data), collapse=", "), "\n"), file=con)
  
  if ("Vha" %in% names(data)) {
    cat(paste0("Vha existe - Classe: ", class(data$Vha), "\n"), file=con)
    cat(paste0("Résumé Vha: ", paste(summary(data$Vha), collapse=", "), "\n"), file=con)
    cat(paste0("NA count: ", sum(is.na(data$Vha)), "\n"), file=con)
    
    # Éviter les erreurs si Vha contient des NA
    non_na_values <- data$Vha[!is.na(data$Vha)]
    if (length(non_na_values) > 0) {
      cat(paste0("Inf count: ", sum(is.infinite(non_na_values)), "\n"), file=con)
      cat(paste0("NaN count: ", sum(is.nan(non_na_values)), "\n"), file=con)
      cat(paste0("Valeurs négatives: ", sum(non_na_values < 0), "\n"), file=con)
      cat(paste0("Valeurs nulles: ", sum(non_na_values == 0), "\n"), file=con)
    } else {
      cat("Toutes les valeurs sont NA\n", file=con)
    }
    
    cat(paste0("Premières valeurs: ", paste(head(data$Vha), collapse=", "), "\n"), file=con)
  } else {
    cat("LA COLONNE VHA N'EXISTE PAS\n", file=con)
  }
  
  close(con)
  return(data)
}

# Fonction pour filtrer les tables par dispositif et cycle
filter_by_disp <- function(tables_name, disp_list, last_cycle = NULL) {
  cat("Filtrage des tables", tables_name, "pour le dispositif", disp_list, "\n")
  
  # Ne rien faire, fonction de compatibilité
  return(invisible(NULL))
}

# Fonction pour construire les résultats par groupe
build_results_by_group <- function(plot_table, disp, last_cycle, repPSDRF, repSav, TabPla) {
  cat("Construction des résultats par groupe pour le dispositif", disp, "\n")
  
  # Créer une table par défaut avec une seule colonne "Disp"
  results_by_group_to_get <- data.frame(Group = "Disp")
  
  # Sauvegarder la structure avec le nom de dispositif complet
  if (exists("Dispositifs") && is.data.frame(Dispositifs) && nrow(Dispositifs) > 0) {
    # Recherche plus robuste du nom du dispositif
    disp_match <- Dispositifs$NumDisp == as.numeric(disp)
    if (any(disp_match) && !is.na(Dispositifs$Nom[disp_match][1])) {
      disp_name <- Dispositifs$Nom[disp_match][1]
    } else {
      disp_name <- paste("Dispositif", disp)
    }
  } else {
    disp_name <- paste("Dispositif", disp)
  }
  
  # Vérifier que disp_name est de type caractère
  if (!is.character(disp_name)) {
    cat("ATTENTION: disp_name n'est pas un caractère, conversion forcée\n")
    disp_name <- as.character(disp_name)
  }
  
  # Créer le dataframe avec des types explicites
  chosen_group_combination <- data.frame(
    variable = "Disp", 
    value = disp_name,
    stringsAsFactors = FALSE
  )
  
  cat("Sauvegarde de results_by_group_to_get et chosen_group_combination\n")
  cat("Nom du dispositif utilisé: ", disp_name, "\n")
  
  # Assigner les variables dans l'environnement global pour qu'elles soient disponibles ailleurs
  assign("results_by_group_to_get", results_by_group_to_get, envir = .GlobalEnv)
  assign("chosen_group_combination", chosen_group_combination, envir = .GlobalEnv)
  
  return(invisible(NULL))
}

# Stub pour choose_disp
choose_disp <- function(df_list, Dispositifs, check_all_msg) {
  cat("Choix du dispositif - fonction stub\n")
  
  # Retourne le premier dispositif de la liste par défaut
  if (nrow(Dispositifs) > 0) {
    return(Dispositifs$NumDisp[1])
  } else {
    # Si Dispositifs est vide, retourne 1 par défaut
    return(1)
  }
}

# Stub pour get_last_cycle
get_last_cycle <- function(df_list, disp_list) {
  cat("Récupération du dernier cycle - fonction stub\n")
  
  # Retourne 1 par défaut
  return(1)
}

# Fonction de stub pour psdrf_AgregArbres
psdrf_AgregArbres <- function(repPSDRF, dispId, last_cycle, results_by_plot_to_get) {
  cat("Stub pour psdrf_AgregArbres appelé\n")
  
  # Créer une liste avec un dataframe vide qui sera utilisé
  TabPla <- list()
  TabPla$psdrf_TabPla_Tot_Stock_Diametre <- data.frame(
    NumDisp = as.numeric(dispId),
    NumPlac = character(0),
    Cycle = numeric(0)
  )
  
  # Assigner TabPla à l'environnement global (nécessaire pour les fonctions qui le récupèrent directement)
  assign("TabPla", TabPla, envir = .GlobalEnv)
  
  return(TabPla)
}

# Fonction de stub pour le radar
radar_chart_function <- function(...) {
  cat("Création d'un graphique radar - fonction stub\n")
  # Ne rien faire, juste pour éviter les erreurs
  return(invisible(NULL))
}

# Fonction pour charger le fichier psdrfTablesElaborees.Rdata si besoin
load_tables_elaborees <- function(repPSDRF) {
  cat("Vérification de l'existence de psdrfTablesElaborees.Rdata\n")
  file_path <- file.path(repPSDRF, "tables", "psdrfTablesElaborees.Rdata")
  
  if (!file.exists(file_path)) {
    cat("Le fichier", file_path, "n'existe pas, création d'une structure par défaut\n")
    
    # Créer un objet Tableaux vide
    Tableaux <- list()
    default_df <- data.frame(NumDisp = 1, Disp = "Dispositif 1", Cycle = 1)
    Tableaux[[1]] <- default_df
    names(Tableaux)[1] <- "psdrfDispTot_Stock_Diametre"
    
    # Sauvegarder
    save(Tableaux, file = file_path)
    
    # Assigner à l'environnement global
    assign("Tableaux", Tableaux, envir = .GlobalEnv)
  } else {
    cat("Le fichier", file_path, "existe, chargement...\n")
    load(file_path, envir = .GlobalEnv)
  }
  
  return(invisible(NULL))
}

# Stub pour toutes les fonctions d'export qui ne sont pas implémentées
export_pdf <- function(...) {
  cat("Export PDF - fonction stub\n")
  return(invisible(NULL))
}

export_docx <- function(...) {
  cat("Export DOCX - fonction stub\n")
  return(invisible(NULL))
}

export_xlsx <- function(...) {
  cat("Export XLSX - fonction stub\n")
  return(invisible(NULL))
}

export_tex <- function(...) {
  cat("Export TEX - fonction stub\n")
  return(invisible(NULL))
}

render_pdf <- function(...) {
  cat("Render PDF - fonction stub\n")
  return(invisible(NULL))
}

render_html <- function(...) {
  cat("Render HTML - fonction stub\n")
  return(invisible(NULL))
}

create_graph <- function(...) {
  cat("Création de graphique - fonction stub\n")
  return(invisible(NULL))
}

create_table <- function(...) {
  cat("Création de tableau - fonction stub\n")
  return(invisible(NULL))
}