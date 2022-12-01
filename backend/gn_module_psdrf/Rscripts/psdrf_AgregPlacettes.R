##### fonction calcul de moyenne et d'ecart-type pour une table et un regroupement donnés  #####
psdrf_AgregMoySdEr <- function(
  data_table = NULL, 
  Regroup = "Disp", 
  Donnees = "Dendro",
  table_ponderation = NULL,
  plot_table = NULL
) {

  df <-
    plot_table[, c("NumDisp", Regroup, "NumPlac", "Cycle", "PoidsPlacette")] %>%
    right_join(data_table, by = c("NumDisp", "NumPlac", "Cycle"))
  
  # --- Cas où table est vide
  if (dim(df)[1] == 0) { 
    df <- df %>% mutate(NumPlac = NULL, PoidsPlacette = NULL)
    return(df)
  }
  
  # --- Récupération des variables de résultats
  # table listant les nombres de colonnes à prendre en compte pour les populations
  
  # NbCol <-
  #   data.frame(
  #     Tab = c("Dendro","Taillis","Rege","BM","BMS","BMP","Codes"), # Rege Taillis et All inutile (Taillis pour l'instant)
  #     NbCol_uniCycle = c(8,8,4,5,2,4,4), #EC: nb de colonne unicyle >multicycle (comme dans Afi), c'est normal?
  #     NbCol_multiCycle = c(4,4,4,5,1,2,4)
  #   )
  # 
  # # nombre de colonnes
  # ncol <-
  #   if (DernierCycle > 1) {
  #     NbCol$NbCol_uniCycle[which(NbCol$Tab == Donnees)]
  #   } else {
  #     NbCol$NbCol_multiCycle[which(NbCol$Tab == Donnees)]
  #   }
  # 
  # # variables à analyser
  # debut <- dim(df)[2]-ncol
  # 
  # vars  <- names(df)[(debut+1):(debut+ncol)]
  # TODO : installer sécurité pour vérifier le nombre de variables ?
  
  # --- Récupération des variables de résultats
  # table listant les nombres de colonnes à prendre en compte pour les populations
  results_vars <- c(
    # BV
    "Nha", "Gha", "Vha", "VhaIFN", "VcHa", "VpHa", "AcctD", "AcctV", "AcctVper", 
    "AcctG", "AcctGper", "TauxV", "TauxPU", "Taux",
    # BM
    "BMSinf", "BMSsup", "BMPinf", "BMPsup", "VhaBMT", 
    # régénération
    "Recouv", "Classe1Ha", "Classe2Ha", "Classe3Ha"
  )
  
  # variables à analyser
  vars <- names(df)[ which(names(df) %in% results_vars) ]
  ncol <- length(vars)
  # définition des variables de regroupement
  group_var <- setdiff(names(df), vars)
  group_var <- 
    group_var[-match(c("NumPlac", "PoidsPlacette"), group_var)]
  
  
  # --- Table de résultats
  df <-
    df %>%
    gather(var, value, vars) %>%
    # filter(EssReg == "Hêtre" & Cat == "GB" & var == "AcctGper") %>%
    mutate(
      var = factor(var, levels = vars),
      value1 = PoidsPlacette * value,
      value2 = PoidsPlacette * value ^ 2
    ) %>% #
    group_by_at(c(group_var, "Cycle", "var")) %>%
    summarise(
      value1 = sum(value1),
      value2 = sum(value2)
    ) %>%
    ungroup() %>%
    left_join(
      table_ponderation, 
      by = c("NumDisp", Regroup, "Cycle")
    ) %>% # joindre table_ponderation pour pondération juste
    mutate(
      poids = ifelse(
        str_detect(var, "Acct") | str_detect(var, "Gain"),
        PoidsAcct, Poids
      ),
      nbre = ifelse(
        str_detect(var, "Acct") | str_detect(var, "Gain"),
        NbreAcct, Nbre
      ),
      
      Moy = value1 / poids, # moyenne
      Sd = ((poids * value2 - value1 ^ 2) / poids / (poids - 1)) ^ 0.5, # écart-type
      CV = Sd / Moy * 100, # coefficient de variation
      Er = qt(0.975, nbre) * CV / nbre ^ 0.5 # erreur relative
    ) %>%
    select(
      group_var, "Cycle", "var", "Poids", "Nbre", "PoidsAcct", "NbreAcct",
      "Moy", "CV", "Er"
    ) %>%
    gather(var_result, value, Moy:Er) %>%
    unite(var, var_result, var) %>%
    mutate(
      var = gsub("Moy_", "", var),
      var = factor(
        var,
        levels = paste0(
          c(rep("", ncol), rep("CV_", ncol), rep("Er_", ncol)), rep(vars, 3)
        )
      )
    ) %>%
    select(-Poids, -Nbre, -PoidsAcct, -NbreAcct) %>%
    spread(var, value, drop = T, fill = 0) %>%
    left_join(
      table_ponderation, 
      by = c("NumDisp", Regroup, "Cycle")
    ) %>%
    rename(
      "PoidsPlacettes" = "Poids",
      "NbrePlacettes" = "Nbre",
      "PoidsPlacettes_Acct" = "PoidsAcct",
      "NbrePlacettes_Acct" = "NbreAcct"
    ) %>%
    data.frame()
  
  # -- retour de la fonction psdrf_AgregMoySdEr
  return(df)
}

##### fonction d'aggrégation des placettes par ensembles #####
#' Aggrégation des placettes par ensembles.
#' @description La fonction permet de calculer les moyennes, coefficient de variations et erreurs relatives des variables d'analyse, à l'échelle d'un ou de plusieurs ensembles choisis par l'opérateur.
#' 
#' @author Bruciamacchie Max, Demets Valentin
#' 
#' @param repPSDRF = répertoire de travail
#' @param repSav = répertoire de sauvegarde des archives (utilisé dans l'édition du carnet)
#' @param results_by_group_to_get = data.frame contenant les différents groupes et combinaisons de groupes à prendre en compte pour l'agrégation des résultats.
#' @param Choix = numéro du dispositif sur lequel faire l'agrégation. Utilisé uniquement lors des agrégations faites pour le carnet
#' 
#' @importFrom dplyr right_join
#' @importFrom doBy summaryBy
#' @importFrom dplyr distinct
#' @importFrom dplyr full_join
#' @importFrom stats as.formula
#' @importFrom stats 'as.formula'
#' @importFrom stats 'qt'
#' @importFrom stats qt
#' @import tcltk
#' 
#' @export

psdrf_AgregPlacettes <- function(
  repPSDRF = NULL,
  results_by_group_to_get = NULL, 
  disp = NULL, last_cycle = NULL # lorsque appel pour édition du livret
  ) {
  # -- définition nulle des variables utilisées
  objects <- c(
    "Arbres", "CV", "Cycle", "Disp", "Dispositifs", "Er", "Moy", 
    "NbPlacettes", "nbre", "Nbre", "NbreAcct", "Nom", "NumDisp", 
    "NumPlac", "poids", "Poids", "PoidsAcct", "PoidsPlacette", 
    "Sd", "TabData", "value", "value1", "value2", "var", 
    "var_result", "variable"
  )
  disp_list <- list(disp)
  create_null(objects)
  ##### 1/ Initialisation #####
  # -- répertoire de travail

  setwd(repPSDRF)
  
  # -- chargement des données d'inventaire et administratives
  load("tables/psdrfCodes.Rdata")
  load("tables/psdrfDonneesBrutes.Rdata")
  
  # -- chargement des tables élaborées par placettes
  load("tables/psdrfTablesElaboreesPlac.Rdata")
  
  # -- list des tables pour le choix du dispositif/pour le calcul du dernier cycle/ à filtrer
  df_list <- load("tables/psdrfTablesElaboreesPlac.Rdata")
  
  # -- chargement des résultats de psdrf_AgregPlac()
  # if (repSav == repPSDRF) {
  #   # -- choix du dispositif
  #   # initialisation
  #   check_all_msg <- "Editer les r\u00E9sultats pour tous les dispositifs"
  #   df_list <- load("tables/psdrfTablesElaboreesPlac.Rdata")
  #   disp_list <- choose_disp(df_list, Dispositifs, check_all_msg) # TODO : laisser le choix du dispositif ?(même si déjà fait au job4)
  # }# else {
  # #   disp_list <- disp
  # # } # end condition "repSav == repPSDRF"
  # last_cycle <- get_last_cycle(df_list, disp_list)
  
  # -- filtre des tables d'inventaire en fonction des numéros de dispositif sélectionnés
  # Placettes,IdArbres,ValArbres,PCQM,Reges,Transect,BMSsup30,Reperes,Cycles
  tables <- "TabPla"
  filter_by_disp(tables, disp_list, last_cycle)
  filter_by_disp("Placettes", disp_list, last_cycle)
  

  #  Définition de TabData
  TabData <-
    data.frame(
      Pop = c(
        "Tot","Fpied", "Den", "PFutaie", "Exploit", "Per", "Taillis", "Codes",
        "Rege", "BM", "BMS", "BMP"
      ),
      Donnees = c(
        rep("Dendro", 5), "Per", "Taillis", "Codes", "Rege", "BM", "BMS", "BMP"
      )
    )
  ##### / \ #####
  
  
  ##### 2/ Boucle - agrégation par ensembles #####
  Tableaux <- c()
  for (i in 1:dim(results_by_group_to_get)[1]) {
    #print(paste0("i = ",i)) #debug
    Regroup <- unlist( results_by_group_to_get[
      i, 1:dim(results_by_group_to_get)[2]
      ] )
    Regroup <- unique(Regroup[!is.na(Regroup)])
    Regroup <- unname(Regroup)
    Regroup <- 
      if (class(Regroup) == "factor") {
        as.character(Regroup)
        } else Regroup
    print(paste0(
      "résultats groupés par : ", paste0(Regroup, collapse =", ")
    )) # debug
    
    tempTableaux <- c()
    
    # ----- tables pondération - distinction stock et accroissement
    # DernierCycle <- max(as.numeric(Placettes$Cycle),na.rm=T) # TODO : corriger
    
    
    # ponderation_DF <-
    #   Cycles %>%
    #   # filter(is.element(NumDisp, num_list)) %>%
    #   select(NumDisp, Cycle, NbPlacettes) %>%
    #   mutate(
    #     Nbre = NbPlacettes,
    #     NbreAcct = NbPlacettes,
    #     Poids = NbPlacettes,
    #     PoidsAcct = NbPlacettes
    #   ) %>%
    #   select(NumDisp, Cycle, Nbre, NbreAcct, Poids, PoidsAcct)

    # table contenant les nombres et les poids des placettes des différents cycles
    # (importance de PoidsAcct et NbreAcct pour cycle > 1)
    if (i == 1) {
      Placettes <-
        Placettes %>%
        left_join(Dispositifs[, c("NumDisp", "Nom")], by = "NumDisp") %>%
        rename(Disp = Nom)
    }
    ponderation_DF <-
      Placettes %>%
      select("NumDisp", Regroup, "NumPlac", "Cycle", "PoidsPlacette") %>%
      rename(Poids = PoidsPlacette) %>%
      mutate(Nbre = 1) %>%
      # on complète les placettes qui seraient éventuellement absentes
      # (indispensables pour faire les bons calculs d'accroissement)
      group_by(NumDisp) %>%
      complete(NumPlac, Cycle) %>%
      
      arrange(NumDisp, NumPlac, Cycle) %>%
      group_by(NumDisp, NumPlac) %>%
      mutate(
        NbreAcct = ifelse(
          Cycle > 1, 
          (Nbre + lag(Nbre)) / 2, 
          (Nbre + lead(Nbre)) / 2
        ),
        PoidsAcct = ifelse(
          Cycle > 1, 
          (Poids + lag(Poids)) / 2, 
          (Poids + lead(Poids)) / 2
        ),
        
        NbreAcct = ifelse(last_cycle > 1, NbreAcct, Nbre),
        PoidsAcct = ifelse(last_cycle > 1, PoidsAcct, Poids)
      ) %>%
      ungroup() %>%
      # mutate(NumPlac = as.numeric(NumPlac)) %>% # not allowed since NumPlac are character type for disp 131
      
      # suppress missing plots
      filter(!is.na(Nbre)) %>% 
      
      # agrégation :
      group_by_at(c("NumDisp", Regroup, "Cycle")) %>%
      # autre option : quo_Regroup <- quo(!!parse_expr(Regroup)) ; group_by(NumDisp, !!quo_Regroup, Cycle) %>%
      summarise_at(c("Poids", "Nbre", "PoidsAcct", "NbreAcct"), sum, na.rm = T) %>%
      ungroup() %>%
      data.frame()


    for (k in 1:length(TabPla)) {
      # print(k) # debug
      # k=1 # debug
      # print(k) # debug
      # extraction nom population
      pop_NAME <- names(TabPla[k])
      pop <- #lVar
        unique(str_sub(pop_NAME, 9, str_locate(pop_NAME, "_")[,1] - 1))
      
      data <- unique(TabData$Donnees[TabData$Pop %in% pop])
      df <- TabPla[[k]]
      
      tempTableaux <- c(tempTableaux, list(
        psdrf_AgregMoySdEr(
          df, 
          Regroup, data, 
          table_ponderation = ponderation_DF, 
          plot_table = Placettes
        )
      ))
      
      names(tempTableaux)[k] <-
        paste0(
          "psdrf", paste0(Regroup, collapse = ""), pop, "_",
          str_sub(
            pop_NAME,
            str_locate(pop_NAME, "_")[, 1] + 1,
            -1
          )
        )
    }
    
    Tableaux <- c(Tableaux, tempTableaux)
  }

  ##### 3/ Sauvegarde  #####
  file = file.path(repPSDRF,"tables", "psdrfTablesElaborees.Rdata")
  save(
    Tableaux,
    file = file
  )
    
 }
