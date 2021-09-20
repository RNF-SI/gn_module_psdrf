##### fonction d'agrégation #####
Agreg01 <- function(df, vars, group_var) {
  if (dim(df)[1] > 0) {
    df <-
      df %>%
      group_by_at(group_var) %>%
      summarise_at(vars, sum, na.rm = T) %>%
      ungroup()
  } else {
    df <-
      df %>%
      select(group_var, vars) %>%
      mutate(
        NumDisp = as.numeric(NumDisp), 
        NumPlac = as.character(NumPlac), 
        Cycle = as.numeric(Cycle)
      )
  }
  df <- df %>%  data.frame()
  
  # retour de la fonction Agreg01
  return(df)
}

#' Aggrégation des valeurs à l'échelle de la placette.
#' @description La fonction permet d'aggréger les résultats d'analyse obtenus pour chaque arbre à l'échelle de la placette.
#'
#' @author Bruciamacchie Max, Demets Valentin
#' 
#' @param repPSDRF = répertoire de travail
#' @param repSav = répertoire de sauvegarde des archives (utilisé dans l'édition du carnet)
#' @param results_by_plot_to_get = data.frame contenant les différentes caractéristiques et combinaisons de caractéristiques à prendre en compte pour agréger les résultats
#' @param disp = lorsque la fonction est utilisée dans le cadre de l'édition d'un carnet d'inventaire, ce paramètre est le numéro du dispositif en cours d'édition.
#' 
#' @import stringr
#' @import reshape2
#' 
#' @export

psdrf_AgregArbres <- function(
  repPSDRF = NULL, 
  dispId, last_cycle,
  donneesBrutesObj, 
  psdrfTablesBrutes,
  results_by_plot_to_get = NULL
) {
  # -- Définition nulle des variables utilisées
  objects <- c(
    "Reges", "data", "Arbres", "Taillis", "Codes", "EssReg", 
    "BMSline", "BMSsup30", "BMP", "Diam", "EssRegPar", 
    "NumDisp", "NumPlac", "Cycle", "Essence", "StadeD", 
    "StadeE", "Classe", "Type", "Vha", "Coupe", "Cat"
  )
  create_null(objects)
  
  ##### 1/ Initialisation #####
  # -- choix du répertoire de travail --- ####
  setwd(repPSDRF)
  
  # -- chargement des données --- ####
  load("tables/psdrfCodes.Rdata")

  IdArbres = donneesBrutesObj$IdArbres
  BMSsup30 = donneesBrutesObj$BMSsup30
  Transect = donneesBrutesObj$Transect
  Cycles = donneesBrutesObj$Cycles
  Reges = donneesBrutesObj$Reges
  Reperes = donneesBrutesObj$Reperes
  PCQM = donneesBrutesObj$PCQM
  ValArbres = donneesBrutesObj$ValArbres
  Placettes = donneesBrutesObj$Placettes

  Arbres = psdrfTablesBrutes$Arbres 
  Perches = psdrfTablesBrutes$Perches 
  Taillis = psdrfTablesBrutes$Taillis 
  BMP = psdrfTablesBrutes$BMP 
  BMSLineaires = psdrfTablesBrutes$BMSLineaires 
  BMSsup30 = psdrfTablesBrutes$BMSsup30 
  Reges = psdrfTablesBrutes$Reges 
  Codes = psdrfTablesBrutes$Codes
  acct_bv = psdrfTablesBrutes$acct_bv 
  acct_bmp = psdrfTablesBrutes$acct_bmp 
  acct_bms = psdrfTablesBrutes$acct_bms


  ##### 2/ Définition des populations #####
  ######## ---------- 2.1/Bois vivant ---------- ########
  tBoisVivant <- Arbres %>% rbind(Perches) %>% rbind(Taillis)
  tTaillis <- Taillis[which(!names(Taillis) %in% c("HautV", "CodeSanit"))]
  
  # ----- Arbres
  # Construction de tTot, t et tCodes sans ou avec Acct en fonction du cycle 1 ou plus
    tTot <- 
      tBoisVivant %>% 
      select(one_of(c(
        "NumDisp", "NumPlac", "NumArbre", "Cycle", 
        "Essence", "EssReg", "EssRegPar", 
        "Classe", "Cat", "CodeEcolo", 
        "CodeSanit", #MA
        "Nha", "Gha", "Vha", "VhaIFN", 
        "AcctV", "AcctVper", "AcctG", "AcctGper", "Coupe"
      ))) %>%
      as.data.frame()
    
    t <- 
      Arbres %>% 
      select(one_of(c(
        "NumDisp", "NumPlac", "NumArbre", "Cycle", 
        "Essence", "EssReg", "EssRegPar", 
        "Classe", "Cat", "CodeEcolo", 
        "CodeSanit", #MA
        "Nha", "Gha", "Vha", "VhaIFN", 
        "AcctV", "AcctVper", "AcctG", "AcctGper", "Coupe"
      ))) %>%
      as.data.frame()
    
    if (dim(Codes)[1] > 0) {
      tCodes <- 
        Codes %>% 
        select(one_of(c(
          "NumDisp", "NumPlac", "NumArbre", "Cycle", 
          "Essence", "EssReg", "EssRegPar", 
          "Classe", "Cat", "CodeEcolo", 
          "CodeSanit", #MA
          "Nha", "Gha", "Vha", "VhaIFN"
        ))) %>%
        as.data.frame()
    }
    
    if (last_cycle > 1) {
      var <- c("Nha", "Gha", "Vha", "VhaIFN", "AcctG", "AcctGper", "AcctV", "AcctVper") #
    } else {
      var <- c("Nha", "Gha", "Vha", "VhaIFN")
    }
  # A venir : mettre en place AccD même au cycle 1  = > Attendre correction des données SIG
  t <- t[!is.na(t$NumDisp), ] # A déplacer ?
  
  # ----- Tous arbres vivants confondus
 # tTot <- t
  vTot <- var
  
  # ----- Ensembles exploités (tExploit) et arbres passés à la futaie (tPFutaie)
  tPFutaie <- 
    t %>% 
    filter(is.element(Coupe, c("PF/E", "PF"))) %>%
    mutate(Coupe = ifelse(Coupe == "PF/E", "PF", Coupe))
  
  tExploit <- 
    t %>% 
    filter(is.element(Coupe, c("PF/E", "E", "C"))) %>%
    mutate(Coupe = ifelse(Coupe == "PF/E", "E", Coupe))
  
  vPFutaie <- var
  vExploit <- var
  
  # ----- Taillis
  tTaillis <- as.data.frame(tTaillis)
  vTaillis <- var
  
  # ----- Arbres de franc-pied
  tFpied <- t
  vFpied <- var
  
  # ----- Arbres de franc-pied (uniquement les précomptables)
  tDen <- t[which(t$Cat != "PER"), ]
  vDen <- var
  
  # ----- Perches
  tPer <-  t[which(t$Cat == "PER"), ]
  vPer <- var
  
  # ----- Arbres porteurs de micro-habitats
  vCodes <- c("Nha", "Gha", "Vha", "VhaIFN")
  
  # ---2.2/ Bois Mort --- ####
  # ----- Bois mort au Sol
  # Construction de BMSsup, vBMS et BMSinf sans ou avec "AcctVper"et "Coupe" en fonction du cycle 1 ou plus
    BMSsup <- 
      BMSsup30 %>% 
      select(one_of(c(
        "NumDisp", "NumPlac", "Cycle", 
        "Essence", "EssReg", "EssRegPar", "StadeD", "StadeE", 
        "Classe", "Cat", "Vha", "AcctVper", "Coupe"
      )))
    vBMS <- c("Vha", "AcctVper")
    
    BMSinf <- 
      BMSLineaires %>% 
      select(one_of(c(
        "NumDisp", "NumPlac", "Cycle", 
        "Essence", "EssReg", "EssRegPar", "StadeD", "StadeE", 
        "Classe", "Cat", "Vha"
      )))
    if (last_cycle > 1) {
      BMSinf <- BMSinf %>% mutate(AcctVper = NA, Coupe = "BMSinf30")
    } else {
      BMSinf <- BMSinf %>% mutate(AcctVper = NA, Coupe = "BMSinf30")
      vBMS <- c("Vha")
    #   BMSinf <- BMSinf %>% mutate(Coupe = NA)
    #   BMSsup <- BMSsup %>% mutate(Coupe = NA)
    }
  tBMS <- rbind(BMSinf, BMSsup)
  
  # ----- Bois Mort sur Pied
  tBMP <- 
    BMP %>% 
    select(one_of(c(
      "NumDisp", "NumPlac", "Cycle", "Type", 
      "Essence", "EssReg", "EssRegPar", 
      "StadeD", "StadeE", "Classe", "Cat", "Vha", "Gha", 
      "AcctVper", "AcctGper", "Coupe", "Diam"
    ))) %>%
    as.data.frame()
  BMPinf <- tBMP %>% filter(Diam < 30) %>% mutate(Diam = NULL)
  BMPsup <- tBMP %>% filter(Diam > 30) %>% mutate(Diam = NULL)
  vBMP <- c("Gha", "Vha", "AcctVper", "AcctGper")
  
  if (last_cycle == 1) {
    tBMP <- tBMP %>% mutate(Coupe = NA)
    vBMP <- c("Gha", "Vha")
  }
  tBMP <- tBMP %>% mutate(Diam = NULL)
  
  # ----- Bois Mort Total
  tempBMSinf <- BMSinf %>% mutate(Type = "BMSinf", Coupe = NULL)
  tempBMSsup <- BMSsup %>% mutate(Type = "BMSsup", Coupe = NULL)
  tempBMPinf <- BMPinf %>% mutate(Type = "BMPinf", Gha = NULL, AcctGper = NULL, Coupe = NULL) # AcctVper = NULL, 
  tempBMPsup <- BMPsup %>% mutate(Type = "BMPsup", Gha = NULL, AcctGper = NULL, Coupe = NULL) # AcctVper = NULL, 
  
  tBM <- tempBMSinf %>% 
    rbind(
      tempBMSsup, 
      tempBMPinf, 
      tempBMPsup
    ) %>%
    select(
      NumDisp, NumPlac, Cycle, 
      Essence, EssReg, EssRegPar, 
      StadeD, StadeE, Classe, Cat, Type, Vha
    ) %>%
    group_by(
      NumDisp, NumPlac, Cycle, 
      Essence, EssReg, EssRegPar, 
      StadeD, StadeE, Classe, Cat, Type
    ) %>%
    summarise(Vha = sum(Vha, na.rm = T)) %>%
    ungroup()
  
  # Sécurité si tables vides (Alibi nous assure que la table est bien présente)
  Alibi_DF_1 <- 
    tBM %>% 
    select(NumDisp, NumPlac, Cycle, Essence, EssReg, EssRegPar, Classe) %>%
    distinct() %>%
    mutate(Type = "BMSinf")
  
  Alibi_DF_2 <- 
    tBM %>% 
    select(NumDisp, NumPlac, Cycle, Essence, EssReg, EssRegPar, Classe) %>%
    distinct() %>%
    mutate(Type = "BMSsup")
  
  Alibi_DF_3 <- 
    tBM %>% 
    select(NumDisp, NumPlac, Cycle, Essence, EssReg, EssRegPar, Classe) %>%
    distinct() %>%
    mutate(Type = "BMPinf")
  
  Alibi_DF_4 <- 
    tBM %>% 
    select(NumDisp, NumPlac, Cycle, Essence, EssReg, EssRegPar, Classe) %>%
    distinct() %>%
    mutate(Type = "BMPsup")
  
  Alibi_DF <- 
    Alibi_DF_1 %>% 
    rbind(
      Alibi_DF_2, 
      Alibi_DF_3, 
      Alibi_DF_4
    )
  
  tBM <- 
    tBM %>% 
    full_join(
      Alibi_DF,
      by = c(
        "NumDisp", "NumPlac", "Cycle", "Essence", 
        "EssReg", "EssRegPar", "Classe", "Type"
      )
    ) %>%
    spread(Type, Vha) %>% 
    mutate(
      BMSinf = ifelse(is.na(BMSinf), 0, BMSinf), 
      BMSsup = ifelse(is.na(BMSsup), 0, BMSsup), 
      BMPinf = ifelse(is.na(BMPinf), 0, BMPinf), 
      BMPsup = ifelse(is.na(BMPsup), 0, BMPsup), 
      VhaBMT = BMSinf + BMSsup + BMPinf + BMPsup
    )
  vBM <- c("BMSinf", "BMSsup", "BMPinf", "BMPsup", "VhaBMT")
  
  
  # ---2.3/ Rege --- ####
  tRege <- Reges
  vRege <- c("Recouv", "Classe1Ha", "Classe2Ha", "Classe3Ha")
  
  ##### 3/ Agrégations Placettes #####
  # initialisation
  TabPla <- c()
  
  for (pop in unique(results_by_plot_to_get$data)) {
    # print(pop) # debug
    # data <- unique(results_by_plot_to_get$data)[1] # debug
    # print(data) # debug
    temp <- results_by_plot_to_get %>% filter(data == pop)
    TabPla_temp <- c()
    
    for (i in 1:dim(temp)[1]) {
      # Paramètres
      Caract_LISTE2 <- unname(unlist(temp[i, 2:dim(temp)[2]]))
      # print(Caract_LISTE2) # debug
      group_var <- c("NumDisp", "NumPlac", "Cycle", Caract_LISTE2)
      group_var <- group_var[!is.na(group_var)]
      
      # Agrégation de la table
      TabPla_temp <- c(
        TabPla_temp, 
        list(Agreg01(
          get(paste0("t", temp$data[i])), 
          get(paste0("v", pop)), 
          group_var
        ))
      )
      # Nom de la table
      Name <- str_replace_all(
        paste0("psdrfPla", pop, "_", paste0(Caract_LISTE2, collapse = "")), 
        "NA", ""
      )
      Name_AgregPlac <- clean_names(Name)
      names(TabPla_temp)[i] <- Name_AgregPlac
      # print(names(TabPla_temp)[i]) # debug
    }
    
    TabPla <- c(TabPla, TabPla_temp)
  } # end of loop unique(results_by_plot_to_get$data)
  
  # ##### 4/ Sauvegarde #####
  save("TabPla", file = "tables/psdrfTablesElaboreesPlac.Rdata")
  list("TabPla"= TabPla)
  
}
