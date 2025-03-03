#' Importation des données d'inventaire dans une archive RData
#' @description Import des classeurs Excel de chaque réserve et sauvegarde dans l'archive
#' psdrfDonneesBrutes.RData.
#' TODO : détailler le détail de la fonction
#'
#' @return La fonction exporte dans le dossier Tables l'archive suivante :
#' psdrfDonneesBrutes.RData
#'
#' @author Bruciamacchie Max, Demets Valentin
#' 
#' @param repPSDRF = répertoire de travail
#' @param files = liste des classeurs d'inventaire 
#' 
#' @importFrom dplyr %>%
#' @importFrom dplyr distinct
#' @importFrom dplyr left_join
#' @importFrom gWidgets2 gmessage
#' @importFrom openxlsx convertToDate
#' @importFrom openxlsx read.xlsx
#' @importFrom stringr str_sub
#' @importFrom stringr str_locate
#' @import tcltk
#' 
#' @export

psdrf_Xls2Rdata <- function(repPSDRF, RPlacettes, RArbres, Rbms, Rreges, Rtransects, Rreperes, Rcycles) {
  # Tracer l'entrée dans cette fonction
  trace_exit <- trace_function("psdrf_Xls2Rdata")
  
  log_info("Début de la fonction psdrf_Xls2Rdata")
  
  # -- définition nulle des variables utilisées (cf règles de mise en forme des packages R)
  objects <- c(
    "Abroutis", "Angle", "Azimut", "Chablis", "Cheminement", "Class1", 
    "Class2", "Class3", "CodeEcolo", "Contact", "CorrectionPente", "Coupe", 
    "Cycle", "Date_Intervention", "Descriptif_Groupe", "Descriptif_Groupe1", 
    "Descriptif_Groupe2", "Diam", "Diam1", "Diam2", "DiamFin", "DiamIni", "DiamMed", 
    "Dist", "Essence", "Exposition", "Gestion", "Groupe", "Groupe1", 
    "Groupe2", "Habitat", "Haut", "Id", "Limite", "Longueur", "Nature_Intervention", 
    "NumArbre", "NumDisp", "NumPlac", "Observation", 
    "Pente", "PoidsPlacette", "Precision_Habitat", "PrecisionGPS", "Recouv", 
    "Ref_CodeEcolo", "Ref_Habitat", "Ref_Station", "Ref_Typologie", "Repere", 
    "SsPlac", "StadeD", "StadeE", "Station", "Strate", "Taillis", "Type", "Typologie"
  )
  
  log_debug(paste("Initialisation des objets nuls:", paste(objects, collapse=", ")))
  create_null(objects)
    
  ##### 1/ Initialisation #####
  # -- choix du répertoire de travail
  log_debug(paste("Répertoire de travail:", repPSDRF))
  setwd(repPSDRF)
  
  # Vérifier les données d'entrée
  log_debug("Vérification des données d'entrée")
  for (df_name in c("RPlacettes", "RArbres", "Rbms", "Rreges", "Rtransects", "Rreperes", "Rcycles")) {
    df <- get(df_name)
    if (is.data.frame(df)) {
      log_debug(paste0("Input ", df_name, ": [", nrow(df), "x", ncol(df), "] rows/cols"))
      if (nrow(df) > 0) {
        # Vérifier les colonnes problématiques
        if ("type" %in% tolower(names(df))) {
          type_col <- names(df)[tolower(names(df)) == "type"]
          type_values <- df[[type_col]]
          log_debug(paste0("Column '", type_col, "' in ", df_name, ": class=", class(type_values)[1], 
                         ", first values=", paste(head(type_values), collapse=", ")))
        }
      } else {
        log_warning(paste0("DataFrame ", df_name, " est vide!"))
      }
    } else {
      log_warning(paste0("Variable ", df_name, " n'est pas un DataFrame: ", class(df)[1]))
    }
  }
  
  
  # -- initialisation des tables d'import
  Placettes <- data.frame()
  Arbres    <- data.frame()
  PCQM      <- data.frame()
  Reges     <- data.frame()
  Transect  <- data.frame()
  BMSsup30  <- data.frame()
  Reperes   <- data_frame(
    NumDisp = numeric(), 
    NumPlac = character(), 
    Azimut = numeric(), 
    Dist = numeric(), 
    Diam = numeric(), 
    Repere = character(), 
    Observation = character()
  )
  Cycles    <- data.frame()
  
  
  # -- création des vecteurs d'erreur
  ErrPlacettes <- c()
  ErrArbres <- c()
  ErrPCQM <- c()
  ErrRege <- c()
  ErrTransect <- c()
  ErrBMSsup30 <- c()
  ErrReperes <- c()
  ErrCycles <- c()
  
  ##### / \ #####
  
  ##### 2/ Import des classeurs d'inventaire #####

    # TODO :Penser à parler du module Méditérannéen 
    # if (!is.element("BMSsup20", ListSheetNames)) {
      # -- hors module méditerrannée
      # arbres
  PCQM_tmp <- data.frame(
    NumDisp = numeric(), 
    NumPlac = character(), 
    Cycle = numeric(), 
    Quart = character(),
    Population = numeric(),
    Diam = numeric()
  )
  Arbres_tmp <- RArbres
  # if (!"CodeSanit" %in% names(Arbres_tmp)) {
  #   Arbres_tmp <- 
  #     Arbres_tmp %>% mutate(HautV = NA, CodeSanit = NA)
  # }


  # TODO: HautV correspond bien à hauteur branche ? 
  setnames(
    Arbres_tmp,
    old = c('id_dispositif', 'id_placette_orig', 'id_arbre_orig',
  'code_essence', 'azimut', 'distance', 'taillis', 'num_cycle',
  'diametre1', 'diametre2', 'type', 'hauteur_totale', 'stade_durete',
  'stade_ecorce', 'coupe', 'limite', 'code_ecolo', 'ref_code_ecolo',
  'id_nomenclature_code_sanitaire', 'hauteur_branche', "observation"), 
    new = c("NumDisp","NumPlac","NumArbre","Essence","Azimut",
  "Dist","Taillis","Cycle","Diam1","Diam2","Type","Haut","StadeD","StadeE", 
  "Coupe","Limite","CodeEcolo","Ref_CodeEcolo","CodeSanit","HautV", "Observation")
  )
  Arbres_tmp <- 
    Arbres_tmp %>% 
    select(one_of(
      "NumDisp", "NumPlac", "NumArbre", "Cycle", # Quart, Population
      "Essence", "Azimut", "Dist", 
      "Diam1", "Diam2", "Type", "Haut", #Diam
      
      "HautV", 
      
      "StadeD", "StadeE", "Taillis", 
      "Coupe", "Limite", "CodeEcolo", 
      "Ref_CodeEcolo", 
      
      "CodeSanit", 
      
      "Observation"
    ))
  if (
    is.element(TRUE, is.na(Arbres_tmp$NumDisp)) & 
    dim(Arbres_tmp)[1] > 0
  ) {
    ErrArbres <- c(
      ErrArbres, 
      str_sub(file, 1, str_locate(file, " ")-1)[1]
    )
  }
  
  ### BMSsup30

  # bois mort au sol par surface fixe
  BMSsup30_tmp <- Rbms
  BMSsup30_tmp %>% mutate(Observation = NA)

  setnames(
    BMSsup30_tmp,
    old = c('id_dispositif', 'id_placette_orig', 'id_bm_sup_30_orig',
'code_essence', 'azimut', 'distance', 'azimut_souche', 'distance_souche',
'diametre_ini', 'diametre_med', 'diametre_fin', 'diametre_130', 'longueur',
'contact', 'chablis', 'stade_durete', 'stade_ecorce', 'num_cycle',
'ratio_hauteur', 'orientation'), 
    new = c("NumDisp","NumPlac","Id","Essence","Azimut",
  "Dist","AzimutS","DistS","DiamIni","DiamMed","DiamFin","Diam130","Longueur","Contact", 
  "Chablis","StadeD","StadeE","Cycle","RatioHaut","Orientation")
  )

  BMSsup30_tmp <- 
    BMSsup30_tmp %>% 
    select(one_of(
      "NumDisp", "NumPlac", "Id", "NumArbre", "Cycle", 
      "Essence", "Azimut", "Dist", 
      
      "Orientation", "AzimutS", "DistS", 
      
      "DiamIni", "DiamMed", "DiamFin", 
      
      "Diam130", 
      
      "Longueur", "Contact", "Chablis", 
      "StadeD", "StadeE", "Observation"
    ))
  if (length(BMSsup30_tmp$NumDisp) > 0) {
    if (
      is.element(TRUE, is.na(BMSsup30_tmp$NumDisp)) & 
      dim(BMSsup30_tmp)[1] > 0
    ) {
      ErrBMSsup30 <- c(
        ErrBMSsup30, 
        str_sub(file, 1, str_locate(file, " ") - 1)[1]
      )
    }
  } 
    
    
    
    ### placettes
    Placettes_tmp <- RPlacettes

    setnames(
      Placettes_tmp,
      old = c('id_dispositif', 'id_placette_orig', 'num_cycle',
      'strate', 'poids_placette', 'pente', 'correction_pente', 'exposition',
      'precision_gps', 'habitat', 'station', 'typologie', 'groupe',
      'groupe1', 'groupe2', 'ref_habitat', 'precision_habitat', 'ref_station',
      'ref_typologie', 'descriptif_groupe', "descriptif_groupe1", "descriptif_groupe2",
      'date_intervention', 'nature_intervention', 'gestion_placette', 'cheminement'), 
      new = c("NumDisp","NumPlac","Cycle","Strate","PoidsPlacette",
      "Pente","correction_pente","Exposition","PrecisionGPS","Habitat","Station",
      "Typologie","Groupe","Groupe1", "Groupe2","Ref_Habitat","Precision_Habitat",
      "Ref_Station","Ref_Typologie","Descriptif_Groupe", "Descriptif_Groupe1", "Descriptif_Groupe2",
      "Date_Intervention", "Nature_Intervention", "Gestion", "Cheminement"
      )
    )

    Placettes_tmp %>%
    select(
      NumDisp, NumPlac, Cycle, Strate, PoidsPlacette, 
      Pente, CorrectionPente, Exposition, PrecisionGPS, 
      Habitat, Station, Typologie, Groupe, Groupe1, Groupe2, 
      Ref_Habitat, Precision_Habitat, Ref_Station, Ref_Typologie, 
      Descriptif_Groupe, Descriptif_Groupe1, Descriptif_Groupe2, 
      Date_Intervention, Nature_Intervention, Gestion, Cheminement
    )
    if (
      is.element(TRUE, is.na(Placettes_tmp$NumDisp)) & 
      dim(Placettes_tmp)[1] > 0
    ) {
      ErrPlacettes <- c(ErrPlacettes, file)
    }

    # régénération
    Rege_tmp <- Rreges
    Rege_tmp %>% mutate(Observation = NA)
    setnames(
      Rege_tmp,
      old = c("id_dispositif", "id_placette_orig", "num_cycle", "sous_placette", "code_essence", 
        "recouvrement", "classe1", "classe2", "classe3",
        "taillis", "abroutissement"
      ), 
      new = c("NumDisp", "NumPlac", "Cycle", "SsPlac", "Essence", 
        "Recouv", "Class1", "Class2", "Class3",
        "Taillis", "Abroutis"
      )
    )
    Rege_tmp %>%
      select(
        NumDisp, NumPlac, Cycle, SsPlac, Essence, 
        Recouv, Class1, Class2, Class3,
        Taillis, Abroutis, Observation
      )
    if (length(Rege_tmp$NumDisp) > 0) {
      if (
        is.element(TRUE, is.na(Rege_tmp$NumDisp)) & 
        dim(Rege_tmp)[1] > 0
      ) {
        ErrRege <- c(
          ErrRege, 
          str_sub(file, 1, str_locate(file, " ")-1)[1]
        )
      }
    } else {
      print(paste0("Attention colonne NumDisp vide dans la feuille Rege pour le dispositif ", file))
    }
    
    # transects de bois mort
    Transect_tmp <- Rtransects
    Transect_tmp %>% mutate(Observation = NA)
    setnames(
      Transect_tmp,
      old = c("id_dispositif", "id_placette_orig", "id_transect_orig", "num_cycle", 
        "code_essence", "ref_transect", "distance", 
        "diametre", "contact", "angle", "chablis",
        "stade_durete", "stade_ecorce"
      ), 
      new = c("NumDisp", "NumPlac", "Id", "Cycle", 
        "Essence", "Transect", "Dist", 
        "Diam", "Contact", "Angle", "Chablis", 
        "StadeD", "StadeE"
      )
    )
    Transect_tmp %>%
      select(
        NumDisp, NumPlac, Id, Cycle, 
        Essence, Transect, Dist, 
        Diam, Contact, Angle, Chablis, 
        StadeD, StadeE, Observation
      )
    if (
      is.element(TRUE, is.na(Transect_tmp$NumDisp)) & 
      dim(Transect_tmp)[1] > 0
    ) {
      ErrTransect <- c(
        ErrTransect, 
        str_sub(file, 1, str_locate(file, " ")-1)[1]
      )
    }
    
    # repères
    Reperes_tmp <- Rreperes
    Reperes_tmp %>% mutate(Observation = NA)
    setnames(
      Reperes_tmp,
      old = c("id_dispositif", "id_placette_orig", "azimut", "distance", 
        "diametre", "repere"
      ), 
      new = c("NumDisp", "NumPlac", "Azimut", "Dist", 
        "Diam", "Repere"
      )
    )
    Reperes_tmp %>%
      select(
        NumDisp, NumPlac, Azimut, Dist, 
        Diam, Repere, Observation
      )
    if (suppressWarnings(
      is.element(TRUE, is.na(Reperes_tmp$NumDisp)) & 
      dim(Reperes_tmp)[1] > 0
    )) {
      ErrReperes <- c(
        ErrReperes, 
        str_sub(file, 1, str_locate(file, " ")-1)[1]
      )
    }
    
    # cycles
    Cycles_tmp <- Rcycles
    print(names(Cycles_tmp))
    setnames(
      Cycles_tmp,
      old = c("id_dispositif", "id_placette_orig", "num_cycle", "annee", "coeff", "diam_lim"), 
      new = c("NumDisp", "NumPlac", "Cycle", "Ann\u00E9e", "Coeff", "DiamLim")
    )
    if (
      is.element(TRUE, is.na(Cycles_tmp$NumDisp)) & 
      dim(Cycles_tmp)[1] > 0
    ) {
      ErrCycles <- c(
        ErrCycles, 
        str_sub(file, 1, str_locate(file, " ")-1)[1]
      )
    }
    Cycles_tmp$Annee <- as.numeric(as.character(Cycles_tmp[, "Ann\u00E9e"]))
    Cycles_tmp[, "Ann\u00E9e"] <- NULL
    pos1 <- which(Cycles_tmp$Annee > 3000)
    if (length(pos1) > 0) {
      Cycles_tmp$Annee <- convertToDate(Cycles_tmp$Annee)
      Cycles_tmp$Annee <- format(Cycles_tmp$Annee, "%Y")
      pos <- which(Cycles_tmp$Annee < 2000)
      if (length(pos) > 0) {
        print(paste0("Attention valeurs d'ann\u00E9e fausses dans la feuille Cycles pour le dispositif ", 
                     file, 
                     ". Correction auto :Ann\u00E9e r\u00E9cup\u00E9r\u00E9e depuis date"))
        Cycles_tmp$Annee <- format(Cycles_tmp$Date, "%Y")
        Cycles_tmp$Annee <- as.numeric(Cycles_tmp$Annee)
      }
    }
    
    # -- stacking df
    Placettes <- 
      Placettes %>% 
      rbind(Placettes_tmp) %>%
      mutate(NumPlac = as.character(NumPlac))
    
    Arbres <- 
      Arbres %>% 
      rbind(Arbres_tmp) %>%
      mutate(
        NumDisp = as.numeric(NumDisp), 
        NumPlac = as.character(NumPlac), 
        Cycle = as.numeric(Cycle), 
        Azimut = as.numeric(Azimut),
        Dist = as.numeric(Dist),
        Diam1 = as.numeric(Diam1), 
        Diam2 = as.numeric(Diam2)
      )
    

    PCQM <- 
      PCQM %>% 
      rbind(PCQM_tmp ) %>%
      mutate(
        NumDisp = as.numeric(NumDisp), 
        NumPlac = as.character(NumPlac), 
        Cycle = as.numeric(Cycle),
      )
    
    Reges <- 
      Reges %>% 
      rbind(Rege_tmp) %>%
      mutate(
        NumDisp = as.numeric(NumDisp), 
        NumPlac = as.character(NumPlac), 
        Cycle = as.numeric(Cycle)
      )
    
    Transect <- 
      Transect %>% 
      rbind(Transect_tmp) %>%
      mutate(
        NumDisp = as.numeric(NumDisp), 
        NumPlac = as.character(NumPlac), 
        Cycle = as.numeric(Cycle), 
        Diam = as.numeric(Diam), 
        Angle = as.numeric(Angle)
      )
    
    BMSsup30 <- 
      BMSsup30 %>% 
      rbind(BMSsup30_tmp) %>%
      mutate(
        NumDisp = as.numeric(NumDisp), 
        NumPlac = as.character(NumPlac), 
        Cycle = as.numeric(Cycle), 
        Essence = as.character(Essence), 
        DiamIni = as.numeric(DiamIni), 
        DiamMed = as.numeric(DiamMed), 
        DiamFin = as.numeric(DiamFin), 
        Longueur = as.numeric(Longueur), 
        Dist = as.numeric(Dist)
      )
    
    if (dim(Reperes_tmp)[1] > 0) {
      Reperes   <- 
        Reperes %>% 
        rbind(Reperes_tmp) %>%
        mutate(NumPlac = as.character(NumPlac))
    }
    
    Cycles <- 
      Cycles %>% 
      rbind(Cycles_tmp) %>%
      mutate(
        NumDisp = as.numeric(NumDisp), 
        NumPlac = as.character(NumPlac)
      )
    
  
  # -- réorganisation des tables
  if (dim(Arbres)[1] > 0) {
    Arbres <- 
      Arbres %>% 
      mutate(Taillis = ifelse(is.na(Taillis), "f", Taillis))
    IdArbres <- 
      Arbres %>% 
      select(NumDisp, NumPlac, NumArbre, Essence, Azimut, Dist) %>%
      distinct()
    IdArbres$IdArbre <- 1:dim(IdArbres)[1]
    
    Arbres <- Arbres %>% left_join(IdArbres)
    ValArbres <- 
      Arbres %>% 
      select("IdArbre", names(Arbres)[!names(Arbres) %in% names(IdArbres)])
  }
  if (dim(PCQM)[1] > 0) {
    PCQM <- PCQM %>% mutate(Haut = as.numeric(Haut))
  }
  
  # -- corrections
  if (dim(Transect)[1] > 0) Transect$Angle[which(is.na(Transect$Angle))] <- 0
  
  Placettes$Pente[which(is.na(Placettes$Pente))] <- 0
  
  if (dim(Reges)[1] > 0) {
    Reges <- 
      Reges %>% 
      mutate(
        Recouv = ifelse(is.na(Recouv), 0, Recouv),
        Class1 = ifelse(is.na(Class1), 0, Class1),
        Class2 = ifelse(is.na(Class2), 0, Class2),
        Class3 = ifelse(is.na(Class3), 0, Class3),
        Taillis = ifelse(is.na(Taillis), 0, Taillis),
        Abroutis = ifelse(is.na(Abroutis), 0, Abroutis)
      )
  }
  # ##### / \ #####
  
  # ##### 3/ Sauvegarde #####
  log_info("Sauvegarde des données traitées")
  setwd(repPSDRF)
  file = file.path(repPSDRF,"tables", "psdrfDonneesBrutes.Rdata")

  # Log des informations sur les dataframes avant sauvegarde
  log_debug("Résumé des dataframes à sauvegarder:")
  for (df_name in c("Placettes", "IdArbres", "ValArbres", "PCQM", "Reges", "Transect", "BMSsup30", "Reperes", "Cycles")) {
    if (exists(df_name)) {
      df <- get(df_name)
      if (is.data.frame(df)) {
        log_debug(paste0("DataFrame ", df_name, ": [", nrow(df), "x", ncol(df), "] rows/cols"))
      } else {
        log_warning(paste0("Variable ", df_name, " n'est pas un DataFrame: ", class(df)[1]))
      }
    } else {
      log_error(paste0("DataFrame ", df_name, " n'existe pas!"))
    }
  }

  # Utiliser tryCatch pour capturer les erreurs lors de la sauvegarde
  tryCatch({
    save(
      Placettes, IdArbres, ValArbres, PCQM, Reges, 
      Transect, BMSsup30, Reperes, Cycles, 
      file = file
    )
    log_info(paste0("Données sauvegardées avec succès dans: ", file))
  }, error = function(e) {
    log_error(paste0("Erreur lors de la sauvegarde dans ", file, ": ", e$message))
    stop(e)  # Relancer l'erreur pour que Python puisse la gérer
  })
  
  log_info("Fonction psdrf_Xls2Rdata terminée avec succès")
  # Tracer la sortie de la fonction
  trace_exit()
}

