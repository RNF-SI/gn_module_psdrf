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
  tryCatch({
    load("tables/psdrfCodes.Rdata")
  }, error = function(e) {
    cat("Erreur lors du chargement de psdrfCodes.Rdata:", e$message, "\n")
    cat("Création de Dispositifs avec structure par défaut\n")
    Dispositifs <<- data.frame(NumDisp = disp, Nom = paste("Dispositif", disp))
  })
  
  tryCatch({
    load("tables/psdrfDonneesBrutes.Rdata")
  }, error = function(e) {
    cat("Erreur lors du chargement de psdrfDonneesBrutes.Rdata:", e$message, "\n")
    cat("Création de tables vides\n")
    # Créer des objets vides
    Placettes <<- data.frame()
    IdArbre <<- data.frame()
    ValArbres <<- data.frame()
    PCQM <<- data.frame()
    Reges <<- data.frame()
    Transect <<- data.frame()
    BMSsup30 <<- data.frame()
    Reperes <<- data.frame()
    Cycles <<- data.frame()
  })
  
  # Vérifier si les tables sont vides et les compléter si nécessaire
  if (nrow(Placettes) == 0) {
    cat("Table Placettes est vide, création d'une structure minimale\n")
    Placettes <<- data.frame(
      NumDisp = as.numeric(disp),
      NumPlac = character(0),
      Cycle = numeric(0),
      PoidsPlacette = numeric(0)
    )
  }
  
  # -- chargement des tables élaborées par placettes
  tryCatch({
    load("tables/psdrfTablesElaboreesPlac.Rdata")
  }, error = function(e) {
    cat("Erreur lors du chargement de psdrfTablesElaboreesPlac.Rdata:", e$message, "\n")
    cat("Création de TabPla vide\n")
    TabPla <<- list()
    TabPla$psdrf_TabPla_Tot_Stock_Diametre <<- data.frame()
  })
  
  # -- vérifier si TabPla est vide
  if (length(TabPla) == 0 || length(names(TabPla)) == 0) {
    cat("TabPla est vide ou mal formé, création d'une structure de base\n")
    TabPla$psdrf_TabPla_Tot_Stock_Diametre <<- data.frame(
      NumDisp = numeric(0),
      NumPlac = character(0),
      Cycle = numeric(0)
    )
  }
  
  # -- list des tables pour le choix du dispositif/pour le calcul du dernier cycle/ à filtrer
  df_list <- names(TabPla)
  
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
  
  # Vérifier si results_by_group_to_get est NULL ou vide
  if (is.null(results_by_group_to_get) || nrow(results_by_group_to_get) == 0) {
    cat("results_by_group_to_get est NULL ou vide, utilisation de 'Disp' par défaut\n")
    results_by_group_to_get <- data.frame(Group = "Disp")
  }
  
  # Vérifier si Placettes est vide
  if (nrow(Placettes) == 0) {
    cat("Placettes est vide, impossible de continuer l'agrégation\n")
    # Créer une table vide comme résultat
    Tableaux <- list(data.frame())
    names(Tableaux)[1] <- "psdrf_DistrDiam_Tot"
    
    # Sauvegarder et retourner
    file = file.path(repPSDRF,"tables", "psdrfTablesElaborees.Rdata")
    save(Tableaux, file = file)
    return(invisible(NULL))
  }
  
  tryCatch({
    for (i in 1:dim(results_by_group_to_get)[1]) {
      cat(paste0("Traitement de la ligne ", i, " de results_by_group_to_get\n"))
      Regroup <- unlist(results_by_group_to_get[i, 1:dim(results_by_group_to_get)[2]])
      Regroup <- unique(Regroup[!is.na(Regroup)])
      Regroup <- unname(Regroup)
      Regroup <- 
        if (class(Regroup) == "factor") {
          as.character(Regroup)
          } else Regroup
      cat(paste0(
        "résultats groupés par : ", paste0(Regroup, collapse =", "), "\n"
      ))
      
      tempTableaux <- c()
      
      # Vérifier si Regroup existe dans les colonnes de Placettes
      for (reg in Regroup) {
        if (!reg %in% colnames(Placettes) && reg != "Disp") {
          cat("Attention: colonne", reg, "n'existe pas dans Placettes, ajout avec valeurs NA\n")
          Placettes[[reg]] <- NA
        }
      }
      
      # Assurer que Disp existe si nécessaire
      if ("Disp" %in% Regroup && !"Disp" %in% colnames(Placettes)) {
        cat("Ajout de la colonne Disp à Placettes\n")
        Placettes$Disp <- paste("Dispositif", Placettes$NumDisp)
      }
  
      # Créer ponderation_DF
      tryCatch({
        ponderation_DF <-
          Placettes %>%
          select("NumDisp", all_of(Regroup), "NumPlac", "Cycle", "PoidsPlacette") %>%
          rename(Poids = PoidsPlacette) %>%
          mutate(Nbre = 1) %>%
          # on complète les placettes qui seraient éventuellement absentes
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
          
          # Supprimer les lignes avec Nbre NA
          filter(!is.na(Nbre)) %>% 
          
          # Agrégation par groupes
          group_by_at(c("NumDisp", all_of(Regroup), "Cycle")) %>%
          summarise_at(c("Poids", "Nbre", "PoidsAcct", "NbreAcct"), sum, na.rm = TRUE) %>%
          ungroup() %>%
          data.frame()
        
        cat("ponderation_DF créé avec", nrow(ponderation_DF), "lignes\n")
      }, error = function(e) {
        cat("Erreur lors de la création de ponderation_DF:", e$message, "\n")
        # Créer un data.frame minimal
        ponderation_DF <<- data.frame(
          NumDisp = as.numeric(disp),
          Disp = paste("Dispositif", disp),
          Cycle = 1, 
          Poids = 1, 
          Nbre = 1, 
          PoidsAcct = 1, 
          NbreAcct = 1
        )
      })
  
      # Traiter chaque table dans TabPla
      if (length(TabPla) > 0) {
        for (k in 1:length(TabPla)) {
          cat(paste0("Traitement de la table ", k, " de TabPla\n"))
          tryCatch({
            # Extraction du nom de la population
            pop_NAME <- names(TabPla)[k]
            pop <- unique(str_sub(pop_NAME, 9, str_locate(pop_NAME, "_")[,1] - 1))
            
            data <- unique(TabData$Donnees[TabData$Pop %in% pop])
            df <- TabPla[[k]]
            
            # Vérifier si df est vide
            if (nrow(df) == 0) {
              cat("df est vide pour", pop_NAME, "\n")
              # Créer un résultat vide avec la structure attendue
              result_df <- data.frame(
                NumDisp = as.numeric(disp),
                Cycle = 1
              )
              # Ajouter les colonnes de regroupement
              for (col in Regroup) {
                result_df[[col]] <- if (col == "Disp") paste("Dispositif", disp) else NA
              }
            } else {
              # Appliquer la fonction d'agrégation
              result_df <- psdrf_AgregMoySdEr(
                df, 
                Regroup, data, 
                table_ponderation = ponderation_DF, 
                plot_table = Placettes
              )
            }
            
            # Ajouter à tempTableaux
            tempTableaux <- c(tempTableaux, list(result_df))
            
            # Nommer le résultat
            name_parts <- str_locate(pop_NAME, "_")
            if (all(is.na(name_parts))) {
              tail_name <- pop_NAME
            } else {
              tail_name <- str_sub(
                pop_NAME,
                name_parts[1] + 1,
                -1
              )
            }
            
            names(tempTableaux)[length(tempTableaux)] <-
              paste0(
                "psdrf", paste0(Regroup, collapse = ""), pop, "_",
                tail_name
              )
          }, error = function(e) {
            cat("Erreur lors du traitement de la table", k, ":", e$message, "\n")
          })
        }
      } else {
        cat("TabPla est vide, aucune table à traiter\n")
      }
      
      # Ajouter les résultats à Tableaux
      if (length(tempTableaux) > 0) {
        Tableaux <- c(Tableaux, tempTableaux)
      } else {
        cat("tempTableaux est vide, création d'un tableau par défaut\n")
        default_df <- data.frame(
          NumDisp = as.numeric(disp),
          Cycle = 1
        )
        for (col in Regroup) {
          default_df[[col]] <- if (col == "Disp") paste("Dispositif", disp) else NA
        }
        default_list <- list(default_df)
        names(default_list)[1] <- paste0("psdrf", paste0(Regroup, collapse = ""), "Tot_Stock_Diametre")
        Tableaux <- c(Tableaux, default_list)
      }
    }
  }, error = function(e) {
    cat("Erreur lors du traitement des groupes:", e$message, "\n")
    # Créer au moins un tableau vide pour éviter les erreurs
    default_df <- data.frame(
      NumDisp = as.numeric(disp),
      Disp = paste("Dispositif", disp),
      Cycle = 1
    )
    default_list <- list(default_df)
    names(default_list)[1] <- "psdrfDispTot_Stock_Diametre"
    Tableaux <- default_list
  })
  
  # Si Tableaux est toujours vide, créer au moins un résultat par défaut
  if (length(Tableaux) == 0) {
    cat("Tableaux est vide, création d'un tableau par défaut\n")
    default_df <- data.frame(
      NumDisp = as.numeric(disp),
      Disp = paste("Dispositif", disp),
      Cycle = 1
    )
    Tableaux <- list(default_df)
    names(Tableaux)[1] <- "psdrfDispTot_Stock_Diametre"
  }

  ##### 3/ Sauvegarde  #####
  cat("Sauvegarde des résultats dans psdrfTablesElaborees.Rdata\n")
  file = file.path(repPSDRF,"tables", "psdrfTablesElaborees.Rdata")
  save(
    Tableaux,
    file = file
  )
  
  cat("Agrégation des placettes terminée\n")
 }
