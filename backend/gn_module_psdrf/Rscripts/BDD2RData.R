# Fonction pour convertir les colonnes Cycle et NumDisp en numérique
convert_columns_to_numeric <- function(df) {
  if (is.data.frame(df)) {
    if ("Cycle" %in% colnames(df)) {
      df$Cycle <- as.numeric(as.character(df$Cycle))
    }
    if ("NumDisp" %in% colnames(df)) {
      df$NumDisp <- as.numeric(as.character(df$NumDisp))
    }
    if ("NumPlac" %in% colnames(df)) {
      # On garde NumPlac comme chaîne car il peut contenir des lettres
      df$NumPlac <- as.character(df$NumPlac)
    }
  }
  return(df)
}

editDocuments <- function(dispId, lastCycle, dispName, placettes, arbres, bms, reges, transects, reperes, cycles, isCarnetToDownload, isPlanDesArbresToDownload, Answer_Radar){
    # Tracer l'entrée dans cette fonction principale
    trace_exit <- trace_function("editDocuments")
    
    log_info("Chargement des bibliothèques R nécessaires")
    library(data.table)
    library("stringr")
    library("openxlsx") 
    library("rmarkdown") 
    library("tools")
    library("tidyr")
    library("dplyr") 
    library("gWidgets2")
    library("knitr")
    library("maptools")
    library("xtable")
    library("ggplot2")
    library("ggrepel") 
    library("ggthemes")
    library("scales")
    library("gridExtra")
    library("rgeos")
    library("rgdal")
    library("gdata") 
    library("grid")
    library("fmsb")
    library("rlang")
    library("tcltk")
    library("reshape2")
    library("sf")
    
    # Fonction pour vérifier qu'un dataframe existe dans l'environnement global
    check_df <- function(df_name, df) {
      log_debug(paste("Vérification du dataframe", df_name))
      if (!exists(df_name, envir = .GlobalEnv)) {
        assign(df_name, df, envir = .GlobalEnv)
        log_info(paste("Création de la variable globale:", df_name))
        
        # Log des dimensions et structure
        if (is.data.frame(df)) {
          log_info(paste0("DataFrame ", df_name, ": [", nrow(df), "x", ncol(df), "] colonnes: ", 
                         paste(names(df), collapse=", ")))
          
          if (nrow(df) > 0) {
            # Vérifier les types des colonnes importantes
            col_types <- sapply(df, class)
            log_debug(paste0("Types de données dans ", df_name, ": ", 
                           paste(names(col_types), "=", col_types, collapse=", ")))
          } else {
            log_warning(paste0("Le DataFrame ", df_name, " est vide!"))
          }
        } else {
          log_warning(paste0("Variable ", df_name, " n'est pas un DataFrame: ", class(df)[1]))
        }
      } else {
        # Si le dataframe existe déjà, comparer et utiliser celui qui a des données
        existing_df <- get(df_name, envir = .GlobalEnv)
        if (is.data.frame(existing_df) && is.data.frame(df)) {
          if (nrow(existing_df) == 0 && nrow(df) > 0) {
            assign(df_name, df, envir = .GlobalEnv)
            log_info(paste0("Remplacement du DataFrame vide ", df_name, " par un nouveau avec ", nrow(df), " lignes"))
          } else {
            log_debug(paste0("DataFrame ", df_name, " existe déjà avec ", nrow(existing_df), " lignes"))
          }
        }
      }
    }
    
    log_info("Vérification et chargement des dataframes dans l'environnement global")
    # Vérifier que les dataframes sont bien dans l'environnement global
    check_df("Arbres", arbres)
    check_df("BMSsup30", bms)
    check_df("Rege", reges)
    check_df("Placettes", placettes)
    check_df("Cycles", cycles)
    check_df("Reperes", reperes)
    check_df("Transects", transects)
    
    # Inspecter les dataframes pour le débogage
    for (df_name in c("Arbres", "BMSsup30", "Rege", "Placettes", "Cycles", "Reperes", "Transects")) {
      if (exists(df_name)) {
        df <- get(df_name)
        if (is.data.frame(df)) {
          log_debug(paste0("Inspecting ", df_name, ": [", nrow(df), "x", ncol(df), "] rows/cols"))
          if ("type" %in% names(df)) {
            log_debug(paste0("Column 'type' in ", df_name, ": class=", class(df$type)[1], 
                           ", first values=", paste(head(df$type), collapse=", ")))
          }
        }
      }
    }

    # Gestion sécurisée de lastCycle qui peut être un vecteur ou une matrice/dataframe
    if (is.matrix(lastCycle) || is.data.frame(lastCycle)) {
      if (nrow(lastCycle) > 0 && ncol(lastCycle) > 0) {
        lastCycle = lastCycle[1,1]
      }
    }
    print(paste("lastCycle:", lastCycle))
    
    # Conversion des dataframes en entrée pour éviter les problèmes de type
    placettes <- convert_columns_to_numeric(placettes)
    arbres <- convert_columns_to_numeric(arbres)
    bms <- convert_columns_to_numeric(bms)
    reges <- convert_columns_to_numeric(reges)
    transects <- convert_columns_to_numeric(transects)
    reperes <- convert_columns_to_numeric(reperes)
    cycles <- convert_columns_to_numeric(cycles)
    setwd('/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts')

    repPSDRF <- '/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts'

    # Conversion des données des réserves de la Bdd en Rdata (au format excel) 
    source(
        file.path("./psdrf_Xls2Rdata.R"), 
        encoding = 'UTF-8', echo = TRUE
    )
    source(
        file.path("./annexes.R"), 
        encoding = 'UTF-8', echo = TRUE
    )

    # Remplie la table psdrfDonneesBrutes.Rdata dans le dossier table
    psdrf_Xls2Rdata(repPSDRF, placettes, arbres, bms, reges, transects, reperes, cycles)

    # TODO: prendre les documents administrateurs depuis la bdd
    # Conversion des données administrateur en df Rdata
    # source(
#     file.path("./psdrf_Codes.R"), 
#     encoding = 'UTF-8', echo = TRUE
    # )
    # psdrf_Codes(repPSDRF, file)


    source(
        file.path("./psdrf_Calculs.R"), 
        encoding = 'UTF-8', echo = TRUE
    )    

    # Remplie la table psdrfTablesBrutes.Rdata dans le dossier table
    psdrf_Calculs(repPSDRF, dispId, lastCycle)

    source(
        file.path("./psdrf_AgregArbres.R"), 
        encoding = 'UTF-8', echo = TRUE
    )    

    tables_list <- c(
    "psdrfDispBM_", "psdrfDispBM_Classe", "psdrfDispBM_Essence", 
    "psdrfDispBM_EssenceClasse", "psdrfDispBM_EssReg", 
    "psdrfDispBM_EssRegClasse", "psdrfDispBM_StadeD", 
    "psdrfDispBM_StadeDStadeE", "psdrfDispBM_StadeE", 
    "psdrfDispBMP_", "psdrfDispBMP_Classe", 
    "psdrfDispBMP_ClasseStadeD", "psdrfDispBMP_ClasseStadeE", 
    "psdrfDispBMP_ClasseType", "psdrfDispBMP_Coupe", 
    "psdrfDispBMS_", "psdrfDispBMS_Classe", 
    "psdrfDispBMS_ClasseStadeD", "psdrfDispBMS_ClasseStadeE", 
    "psdrfDispBMS_Coupe", "psdrfDispCodes_", "psdrfDispCodes_Cat", 
    "psdrfDispCodes_CatCodeEcolo", "psdrfDispCodes_CodeEcolo", 
    "psdrfDispCodes_EssenceCodeEcolo", "psdrfDispDen_", 
    "psdrfDispDen_cat", "psdrfDispDen_Cat", "psdrfDispDen_CatCodeEcolo", 
    "psdrfDispDen_CatCoupe", "psdrfDispDen_Classe", 
    "psdrfDispDen_ClasseCodeEcolo", "psdrfDispDen_CodeEcolo", 
    "psdrfDispDen_CodeSanit", "psdrfDispDen_Coupe", 
    "psdrfDispDen_Essence", "psdrfDispDen_EssenceCat", 
    "psdrfDispDen_EssenceCatCoupe", "psdrfDispDen_EssenceClasse", 
    "psdrfDispDen_EssenceCodeEcolo", "psdrfDispDen_EssenceCodeSanit", 
    "psdrfDispDen_EssenceCoupe", "psdrfDispDen_EssReg", 
    "psdrfDispDen_EssRegCat", "psdrfDispDen_EssRegClasse", 
    "psdrfDispDen_EssRegCoupe", "psdrfDispExploit_", 
    "psdrfDispExploit_Cat", "psdrfDispExploit_Classe", 
    "psdrfDispExploit_Essence", "psdrfDispFpied_", 
    "psdrfDispFpied_Cat", "psdrfDispFpied_CatCodeEcolo", 
    "psdrfDispFpied_CatCoupe", "psdrfDispFpied_Classe", 
    "psdrfDispFpied_ClasseCodeEcolo", "psdrfDispFpied_CodeEcolo", 
    "psdrfDispFpied_Coupe", "psdrfDispFpied_Essence", 
    "psdrfDispFpied_EssenceCat", "psdrfDispFpied_EssenceClasse", 
    "psdrfDispFpied_EssenceCodeEcolo", "psdrfDispFpied_EssRegParCat", 
    "psdrfDispHabitatBM_", "psdrfDispHabitatBM_StadeD", 
    "psdrfDispHabitatBMP_", "psdrfDispHabitatBMS_", 
    "psdrfDispHabitatFpied_", "psdrfDispHabitatFpied_Classe", 
    "psdrfDispHabitatTaillis_", "psdrfDispHabitatTaillis_Classe", 
    "psdrfDispPer_", "psdrfDispPer_Classe", "psdrfDispPer_Cat", 
    "psdrfDispPer_Essence", 
    "psdrfDispPer_EssenceClasse", "psdrfDispPer_EssReg", 
    "psdrfDispPer_EssRegClasse", "psdrfDispPFutaie_", 
    "psdrfDispPFutaie_Cat", "psdrfDispPFutaie_Classe", 
    "psdrfDispPFutaie_Essence", "psdrfDispRege_Essence",
    "psdrfDispRege_EssenceRejet", "psdrfDispRege_EssReg", 
    "psdrfDispRege_EssRegPar", "psdrfDispRege_Rejet", 
    "psdrfDispTaillis_", "psdrfDispTaillis_Classe", 
    "psdrfDispTaillis_Essence", "psdrfDispTaillis_EssenceClasse", 
    "psdrfDispTaillis_EssRegClasse", "psdrfDispTot_", 
    "psdrfDispTot_Cat", "psdrfDispTot_CatCodeEcolo", 
    "psdrfDispTot_CatCoupe", "psdrfDispTot_Classe", 
    "psdrfDispTot_ClasseCoupe", "psdrfDispTot_Coupe", 
    "psdrfDispTot_Essence", "psdrfDispTot_EssenceClasse", 
    "psdrfDispTot_EssRegCat", "psdrfDispTot_EssRegClasse", "psdrfDispTot_EssRegParCat", 
    "psdrfPlaBM_", "psdrfPlaFpied_", "psdrfPlaFpied_Cat", 
    "psdrfPlaFpied_EssReg", "psdrfPlaRege_", "psdrfPlaTaillis_", 
    "psdrfPlaTaillis_Cat", "psdrfPlaTot_", "psdrfPlaTot_Cat", 
    "psdrfPlaTot_EssReg"
    )
    tables_list <- sort(unique(tables_list))
    save(tables_list, file = "tables/psdrf_tables_livret.Rdata")
    load("tables/psdrf_tables_livret.Rdata")
    # ----- Lancement manuel -----

    TabCombi <- build_combination_table(tables_list)

    # chargement du script
    source(
        file.path("./psdrf_AgregArbres.R"), 
        encoding = 'UTF-8', echo = TRUE
    )

    # lancement # TODO : supprimer le message de jonction lors de l'exécution de afi_AgregArbres
    TabPla = psdrf_AgregArbres(repPSDRF, dispId, lastCycle, TabCombi)

    # construction de la table de combinaison des résultats
    results_by_plot_to_get <- build_combination_table(tables_list)


    ##### Job 6 : agrégation des résultats par dispositif #####
    results_by_stand_to_get <- data.frame(
    V1 = "Disp",
    V2 = NA,
    V3 = NA,
    V4 = NA,
    V5 = NA,
    V6 = NA,
    V7 = NA,
    V8 = NA,
    V9 = NA,
    stringsAsFactors = F
    )


    source(
    file.path("./psdrf_AgregPlacettes.R"), 
    encoding = 'UTF-8', echo = TRUE
    )
    # lancement # TODO : supprimer le message de jonction lors de l'exécution de afi_AgregArbres
    psdrf_AgregPlacettes(
    repPSDRF, results_by_stand_to_get, dispId, lastCycle
    )


    source(
    file.path("./psdrf_EditCarnet.R"), 
    encoding = 'UTF-8', echo = TRUE
    )

    source(
    file.path("./psdrf_EditPlansArbres.R"), 
    encoding = 'UTF-8', echo = TRUE
    )

    source(
    file.path("./annexes.R"), 
    encoding = 'UTF-8', echo = TRUE
    )

    source(
    file.path("./psdrf_Calculs.R"), 
    encoding = 'UTF-8', echo = TRUE
    )

    source(
    file.path("./psdrf_AgregArbres.R"), 
    encoding = 'UTF-8', echo = TRUE
    )

    source(
    file.path("./psdrf_AgregPlacettes.R"), 
    encoding = 'UTF-8', echo = TRUE
    )
    if (isCarnetToDownload){
        print("About to launch psdrf_EditCarnet")
        tryCatch({
            psdrf_EditCarnet(repPSDRF, dispId, lastCycle, dispName, results_by_plot_to_get, Answer_Radar)
        }, error = function(e) {
            print(paste("Error in psdrf_EditCarnet call:", e$message))
        })
        print("psdrf_EditCarnet is finished")


    } 
    if (isPlanDesArbresToDownload){
        log_info("Lancement de psdrf_EditPlansArbres")
        tryCatch({
            psdrf_EditPlansArbres(repPSDRF, dispId, lastCycle, dispName, results_by_plot_to_get)
            log_info("psdrf_EditPlansArbres terminé avec succès")
        }, error = function(e) {
            log_error(paste("Erreur dans psdrf_EditPlansArbres:", e$message))
            stop(e)  # Relancer l'erreur pour que Python puisse la gérer
        })
    }
    
    log_info("Fonction editDocuments terminée avec succès")
    # Tracer la sortie de la fonction principale
    trace_exit()
}
