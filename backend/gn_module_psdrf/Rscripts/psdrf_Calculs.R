
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

##### fonction pour joindre CodeEssence et EssReg #####
set_up_calcul_tables <- function(df = NULL,
                                 species = CodeEssence,
                                 grouped_species = EssReg,
                                 cycles_inv = NULL,
                                 cycles_admin = NULL,
                                 tariffs = NULL) {
  if (dim(df)[1] > 0) {
    # Nous nous assurons que les types de colonnes sont corrects dans notre dataframe
    df <- convert_columns_to_numeric(df)
    
    # Assurer que les tables de référence ont aussi les bons types
    species_copy <- convert_columns_to_numeric(species)
    grouped_species_copy <- convert_columns_to_numeric(grouped_species)
    
    df <-
      df %>%
      left_join(species_copy[, c("Essence", "EssReg")],
                by = "Essence") %>%
      left_join(grouped_species_copy,
                by = c("NumDisp", "Essence"))
    
    if (!is.null(tariffs)) {
      tariffs_copy <- convert_columns_to_numeric(tariffs)
      df <-
        df %>%
        left_join(tariffs_copy, by = c("NumDisp", "Essence"))
    }
    if (!is.null(cycles_inv)) {
      # Convertir les colonnes dans cycles_inv aux types corrects
      cycles_inv_copy <- convert_columns_to_numeric(cycles_inv)
      
      # get the year and the settings
      df <-
        df %>%
        left_join(cycles_inv_copy[, c("NumDisp",
                                 "NumPlac",
                                 "Cycle",
                                 "Coeff",
                                 "DiamLim",
                                 "Annee")],
                  by = c("NumDisp", "NumPlac", "Cycle"))
    }
    if (!is.null(cycles_admin)) {
      # Convertir les colonnes dans cycles_admin aux types corrects
      cycles_admin_copy <- convert_columns_to_numeric(cycles_admin)
      
      # get the protocole
      df <-
        df %>%
        left_join(cycles_admin_copy[, c("NumDisp", "Cycle", "Monitor")],
                  by = c("NumDisp", "Cycle"))
    }
  }
  
  
  # -- retour de la fonction set_up_calcul_tables
  return(df)
}

##### fonction de préparation de la table Arbres #####
prep_df <- function(df = NULL, echant_change = F) {
  # df <- Arbres # debug
  # df <- head(BMP, 20) # debug
  df <-
    df %>%
    # left_join(
    # table_essence[, c("Essence", "EssReg")],
    # by = "Essence"
    # ) %>%
    mutate(
      NumArbre = as.numeric(NumArbre),
      Cycle = as.numeric(Cycle),
      Limite = 1,
      Dist = as.numeric(Dist),
      Azimut = as.numeric(Azimut),
      Diam1 = as.numeric(Diam1),
      Diam2 = as.numeric(Diam2),
      Haut = as.numeric(Haut),
      StadeD = as.numeric(StadeD),
      StadeE = as.numeric(StadeE),
      Diam1 = ifelse(is.na(Diam1), Diam2, Diam1),
      Diam2 = ifelse(is.na(Diam2), Diam1, Diam2),
      Diam1 = ifelse(Diam1 == 0, Diam2, Diam1),
      Diam2 = ifelse(Diam2 == 0, Diam1, Diam2),
      Diam = (Diam1 + Diam2) / 2,
      Classe = floor(Diam / 5 + 0.5) * 5,
      Cat = cut(
        Diam1,
        breaks = c(0, 17.5, 27.5, 47.5, 67.5, 200),
        labels = c("PER", "PB", "BM", "GB", "TGB"),
        include.lowest = T,
        right = F
      ),
      Cat = as.character(Cat),
      Coupe = as.character(Coupe)
    ) %>%
    # left_join(EssReg, by = c("NumDisp", "Essence")) %>%
    mutate(EssReg = ifelse(!is.na(EssRegPar), EssRegPar, EssReg)) %>%
    # get the tarifs
    # left_join(Tarifs, by = c("NumDisp", "Essence")) %>%
    filter(!is.na(Essence) &
             !is.na(Azimut) &
             !is.na(Dist)) %>% # Suppression des arbres sans leurs coordonnées (voir calculs d'accroissement)
    arrange(NumDisp, NumPlac, NumArbre, Cycle) %>%
    filter(
      !is.na(Diam1) |
        !is.na(Diam2) |
        Diam1 == 0 |
        Diam2 == 0 # supprime les arbres où les 2 diamètres sont vides
      )
      
      if (echant_change == F) {
        # cycles_inv <- get("Cycles",envir = parent.frame(-2))
        # cycles_admin <- get("CyclesCodes",envir = parent.frame(-2))
        df <-
          df %>%
          mutate(
            Rayon = ifelse(is.na(Type), 10, ifelse(Diam1 < 30, 10, 20)),
            # prise en compte des BMP dans les calculs
            Rayon = ifelse(Monitor == "PFA", 13.8, Rayon)
          )
      }
      
      # -- retour fonction prep_df
      return(df)
}

##### fonction de calcul du poids (pour les précomptables) #####
calculs_Nha <- function(df = NULL) {
  # -- initialisation
  df <- df %>% mutate(Nha = NA)
  
  # Conversion des colonnes en numériques pour éviter les erreurs d'opérations
  df$Dist <- as.numeric(as.character(df$Dist))
  df$Coeff <- as.numeric(as.character(df$Coeff))
  df$Diam1 <- as.numeric(as.character(df$Diam1))
  df$DiamLim <- as.numeric(as.character(df$DiamLim))
  df$Rayon <- as.numeric(as.character(df$Rayon))
  
  # -- cercle
  # (perches sur 10m pour le PSDRF + PSDRF MA - toutes les tiges sur 13,8m pour le PFA)
  pos <-
    with(df, which(is.na(Nha) &
                     !is.na(Diam1) & !is.na(Dist) & !is.na(Rayon) &
                     Diam1 >= 7.5 &
                     Dist <= Rayon)) # prend aussi en compte les précomptables qui sont dans le cercle
  if (length(pos) > 0) {
    df[pos, "Nha"] <- 10000 / pi / df$Rayon[pos] ^ 2
    df$Limite[pos] <- NA
  }
  
  # -- angle fixe
  pos <-
    with(df, which(!is.na(Diam1) & !is.na(DiamLim) & 
                     (Diam1 < DiamLim |
                     !is.na(Type)))) # ici, PFA écarté d'office car DiamLim et Coeff sont NA + bois mort écarté aussi
  if (length(pos) > 0) {
    df[pos, "Coeff"] <- NA
  }
  pos <- with(df, which(!is.na(Diam1) & !is.na(DiamLim) & 
                           Diam1 >= DiamLim & is.na(Type))) #
  # Changement Verif_Calculs Diam devient Diam1 -> indispensable sinon arbre de 29 par 32 sera inventorié ni par surface ni par angle fixe
  if (length(pos) > 0) {
    df[pos, "Nha"] <-
      NA # Remise à zéro au cas où il y aurait déjà des valeurs renseignées (cercle(s))
    df[pos, "Limite"] <- 1
  }
  
  # Éviter les calculs avec des NA
  pos <- with(df, which(!is.na(Coeff) & !is.na(Diam1) & !is.na(Dist) & 
                           Diam1 >= Dist * Coeff))
  if (length(pos) > 0) {
    df[pos, "Nha"] <-
      10 ^ 4 * df$Coeff[pos] ^ 2 / pi / df$Diam1[pos] ^ 2
    df$Limite[pos] <- NA
  }
  # cas des Arbres à inventorier par angle relascopique qui auraient été considérés comme non limite parce
  # que > DiamLim1, mais qui en fait sont hors inventaire
  pos <- with(
    df,
    which(
      !is.na(Coeff) & !is.na(Diam1) & !is.na(Dist) &
        Diam1 < Dist * Coeff # * 100 #& is.na(Type)
      ))
      if (length(pos) > 0) {
        df[pos, "Nha"] <- NA
        df$Limite[pos] <- 1
      }
      
      # Nha mis à 0 pour les arbres limites
      pos <- which(df$Limite == 1)
      if (length(pos) > 0)
        df[pos, "Nha"] <- 0
      
      rm(pos)
      # -- retour fonction calculs_Nha
      return(df)
}

##### fonction de calcul des volumes (pour les précomptables) #####
calculs_Vol <- function(df = NULL,
                        IFN = F,
                        Sup = F) {
  add_var <- ""
  add_Tarif <- ""
  add_Diam <- ""
  if (IFN == T) {
    add_var <- "IFN"
    add_Tarif <- "IFN"
    add_Diam <- ""
  }
  if (Sup == T) {
    add_var <- "Sup"
    add_Tarif <- ""
    add_Diam <- "Sup"
  }
  
  # Pour mémo (1) fonctionnement sans argument "add_var" :
  # var <- enquo(var)
  # var_name <- quo_name(var) # puis appel !!var_name:=f(!!var) dans mutate
  
  # Pour mémo (2) fonctionnement avec argument d'entrée définissant la variable (Vha)
  # var <- enquo(var)
  # var_name <- paste0(quo_name(var),add_var)
  
  # construction des variables
  var_name <- paste0("Vha", add_var)
  var <- quo(!!parse_expr(var_name))
  # variable = Type de tarif
  TypeTarif <- paste0("TypeTarif", add_Tarif)
  TypeTarif <- quo(!!parse_expr(TypeTarif))
  # variable = Numéro de tarif
  NumTarif <- paste0("NumTarif", add_Tarif)
  NumTarif <- quo(!!parse_expr(NumTarif))
  # variable = Diamètre
  Diam <- paste0("Diam", add_Diam)
  Diam <- quo(!!parse_expr(Diam))
  
  # calculs des volumes selon les tarifs de cubage
  df <-
    df %>%
    mutate(
      !!var_name := NA,!!var_name :=
        ifelse(
          !!TypeTarif == "SchR",
          5 / 70000 * (8+!!NumTarif) * (!!Diam - 5) * (!!Diam - 10) * Nha,!!var
        ),!!var_name :=
        ifelse(
          !!TypeTarif == "SchI",
          5 / 80000 * (8+!!NumTarif) * (!!Diam - 2.5) * (!!Diam - 7.5) * Nha,!!var
        ),!!var_name :=
        ifelse(
          !!TypeTarif == "SchL",
          5 / 90000 * (8+!!NumTarif) * (!!Diam - 5) * !!Diam * Nha,!!var
        ),!!var_name :=
        ifelse(
          !!TypeTarif == "SchTL",
          5 / 101250 * (8+!!NumTarif) * !!Diam * !!Diam * Nha,!!var
        ),!!var_name :=
        ifelse(!!var < 0, 0,!!var) # sécurité pour les tiges de moins de 10 # A revoir ?
    )
  
  # -- retour fonction calculs_Vol
  return(df)
}

##### fonction de calcul de Nha, Gha, Vha #####
calculs_Arbres <- function(df = NULL, echant_change = F) {
  # df <- Arbres_Acct # debug
  # df <- head(BMP, 20) # debug
  
  df <-
    df %>%
    # ----- Jonctions et préparation
    prep_df(echant_change) %>%
    # ----- Poids
    calculs_Nha() %>%
    # ----- Surface terrière
    mutate(Gha = pi * Diam1 ^ 2 / 40000 * Nha) %>% # Utiliser Diam1 pour retrouver le coeff relascopique (1 à 2%)
    # ----- Volume gestionnaire
    calculs_Vol() %>%
    # ----- Volume IFN
    calculs_Vol(IFN = T) %>%
    mutate(# ----- Taux d'accroissement en volume
      # -- Volume de la classe supérieure
      DiamSup = Diam + 5,
      ClasseSup = Classe + 5) %>%
    calculs_Vol(Sup = T) %>%
    mutate(TauxV = ifelse(Vha > 0, log(VhaSup / Vha) / 5, 0),
           Vha = ifelse(
       # choix 1 : si bois vivant ou bois mort type 'Arbre', on garde Vha déjà calculé
       Type == 1 | is.na(Type),
       Vha,
       # choix 2 : si bois mort type souche ou chandelle, on calcule le volume ...
       ifelse(
         # ... en multipliant le Gha par 8 pour avoir Vha
         is.na(Haut), 8 * Gha,
         # ... à partir de la hauteur (diamètre médian et décroissance métrique = 1cm/m par défaut)
         ( pi / 40000 * (Diam - (Haut / 2 - 1.30)) ^ 2 * Haut ) * Nha
       )
     )
    )
  
  if (echant_change == F) {
    # selection de variables
    df <-
      df %>%
      select(
        NumDisp,
        NumPlac,
        NumArbre,
        IdArbre,
        Cycle,
        Essence,
        EssReg,
        EssRegPar,
        Azimut,
        Dist,
        Diam1,
        Diam2,
        Diam,
        Classe,
        Cat,
        DiamSup,
        ClasseSup,
        VhaSup,
        TauxV,
        Nha,
        Gha,
        Vha,
        VhaIFN,
        CodeSanit,
        Taillis,
        Coupe,
        Limite,
        CodeEcolo,
        Ref_CodeEcolo,
        Haut,
        HautV,
        Type,
        StadeD,
        StadeE,
        Observation
      )
  } else {
    df <-
      df %>%
      mutate(echant_ID = NA) %>%
      # selection de variables
      select(
        NumDisp,
        NumPlac,
        NumArbre,
        IdArbre,
        Cycle,
        Essence,
        EssReg,
        EssRegPar,
        Azimut,
        Dist,
        Diam1,
        Diam2,
        Diam,
        Classe,
        Cat,
        DiamSup,
        ClasseSup,
        VhaSup,
        TauxV,
        Nha,
        Gha,
        Vha,
        VhaIFN,
        CodeSanit,
        Taillis,
        Coupe,
        Limite,
        echant_ID,
        CodeEcolo,
        Ref_CodeEcolo,
        Haut,
        HautV,
        Type,
        StadeD,
        StadeE,
        Observation
      )
  }
  
  # -- retour fonction calculs_Arbres
  return(df)
}

##### fonction de calcul des accroissements (bois vivants précomptables) #####
calculs_acct_bv <- function(df = NULL,
                            cycle_num = last_cycle,
                            cycles_inv = NULL,
                            echant_change = F) {
  # df <- Arbres # debug
  # df <- Arbres_Acct # debug
  # Paramètres initiaux
  # cycle_num <- max(df$Cycle, na.rm = T)
  
  if (cycle_num > 1) {
    # table contenant les pas de temps
    tLaps <-
      df %>%
      distinct(NumDisp, NumPlac, NumArbre, IdArbre) %>%
      full_join(cycles_inv[, c("NumDisp", "NumPlac", "Cycle", "Annee")],
                by = c("NumDisp", "NumPlac")) %>%
      group_by(NumDisp, NumPlac, NumArbre, IdArbre) %>%
      mutate(Inter = Annee - lag(Annee)) %>%
      ungroup() %>%
      # filter(Cycle > 1) %>%
      left_join(distinct(df[, c("IdArbre", "Essence", "EssReg", "Azimut", "Dist")]),
                by = "IdArbre") %>%
      select(NumDisp,
             NumPlac,
             NumArbre,
             Cycle,
             IdArbre,
             Essence,
             EssReg,
             Azimut,
             Dist,
             Inter)
    
    # Sécurité : contrôle des valeurs dupliquées (ID="NumDisp+NumPlac+NumArbre+Cycle")
    df_Dupl <-
      df %>%
      select(NumDisp, NumPlac, Cycle, Azimut, Dist) %>% #,Taillis
      arrange(NumDisp, NumPlac, Cycle, Azimut, Dist)
    # rangement de df dans le même ordre que df_Dupl
    df <-
      df %>%
      arrange(NumDisp, NumPlac, Cycle, Azimut, Dist)
    
    # valeurs dupliquées
    Dupl <- which(duplicated(df_Dupl) & df_Dupl$Taillis != "t")
    # édition d'un classeur listant les valeurs dupliquées
    if (length(Dupl) > 0) {
      Dupl_INV <-
        which(duplicated(df_Dupl, fromLast = TRUE) &
                df_Dupl$Taillis != "t")
      Dupl <- c(Dupl, Dupl_INV)
      Error_DF <- df[Dupl, c("NumDisp",
                             "NumPlac",
                             "Cycle",
                             "NumArbre",
                             "Essence",
                             "Azimut",
                             "Dist",
                             "Diam1")] %>%
        arrange(NumDisp, NumPlac, Cycle, Azimut, Dist)
      write.xlsx(Error_DF,
                 file = file.path(repPSDRF, "Doublons.xlsx"))
      stop(
        "Attention : doublon(s) d\u00E9tect\u00E9(s) lors des calculs d'accroissement.\n\nDoublons list\u00E9s dans le classeur excel 'Doublons.xlsx'"
      )
    }
    
    # Calculs des accroissements (superassignement)
    acct_bv <<-
      df %>%
      left_join(
        tLaps,
        by = c(
          "NumDisp",
          "NumPlac",
          "NumArbre",
          "Cycle",
          "IdArbre",
          "Essence",
          "EssReg",
          "Azimut",
          "Dist"
        )
      ) %>%
      # left_join(tLaps, by = c("NumDisp", "NumPlac", "NumArbre", "Cycle")) %>%
      arrange(NumDisp, NumPlac, NumArbre, Cycle) %>%
      group_by(NumDisp, NumPlac, NumArbre) %>%
      mutate(
        # Arbres devenus morts sur pied :
        Coupe =
          ifelse(
            is.na(Type) & !is.na(lead(Type)) & Cycle < cycle_num & is.na(Coupe),
            "C",
            Coupe
          ),
        Coupe =
          ifelse(
            is.na(Type) & !is.na(lead(Type)) & Cycle < cycle_num &
              !is.na(Coupe) & str_detect(Coupe, "PF"),
            "PF/C",
            Coupe
          ),
        Coupe =
          ifelse(
            is.na(Type) & !is.na(lead(Type)) & Cycle < cycle_num &
              !is.na(Coupe) & !str_detect(Coupe, "PF"),
            "C",
            Coupe
          ),
        
        # Arbres passant à la futaie :
        # la colonne coupe peut déjà contenir des infos
        # les notations "C" ou "PF/C" sont à conserver.
        # les notations "E", "PF" ou "PF/E", sont de toutes façons reconstituées
        Coupe =
          ifelse(
            is.na(lag(Nha)) & !is.na(Nha) & Cycle > 1 & !is.na(Coupe) &
              Coupe == "C",
            paste("PF", Coupe, sep = "/"),
            Coupe
          ),
        Coupe =
          ifelse(
            is.na(lag(Nha)) & !is.na(Nha) & Cycle > 1 & is.na(Coupe),
            "PF",
            Coupe
          ),
        # Arbres coupés :
        Coupe =
          ifelse(is.na(lead(Nha)) &
                   Cycle < cycle_num & is.na(Coupe),
                 "E",
                 Coupe),
        Coupe =
          ifelse(
            is.na(lead(Nha)) & Cycle < cycle_num & !is.na(Coupe) &
              Coupe == "PF",
            #!str_detect(Coupe, "C")
            "PF/E",
            Coupe
          ),
        
        Coupe = ifelse(is.na(Limite), Coupe, NA),
        
        # --- Calcul des accroissements
        # Inter = Annee - lag(Annee),
        Acct_Diam = round((Diam - lag(Diam, default = NA)) / Inter, digits = 10),
        # mettre plus bas et ensuite rajouter condition : si Coupe detect C ou E ?
        AcctGper = round((Gha - lag(Gha, default = 0)) / Inter, digits = 10),
        AcctVper = round((Vha - lag(Vha, default = 0)) / Inter, digits = 10)
        
      ) %>%
      ungroup() %>%
      as.data.frame() #%>%
    # right_join(
    # tLaps,
    # by = c(
    # "NumDisp", "NumPlac", "NumArbre", "Cycle", "IdArbre",
    # "Strate", "Essence", "EssReg", "Azimut", "Dist", "Inter"
    # )
    # ) # A rajouter pour calculs accroissements avec coupés + 1/2 Acct
    
    ### ----- Table des accroissements en diamètre ----- ###
    # Attribution d'une valeur d'accroissement en diamètre (si Acct_Diam vide)
    acctD_bv <-
      acct_bv %>% # s'assurer qu'on a bien des arbres limites dans la table
      select(IdArbre,
             NumDisp,
             NumPlac,
             NumArbre,
             Cycle,
             Essence,
             Classe,
             Acct_Diam,
             Coupe) %>%
      
      # valeurs moyennes d'AcctD attribuées par forêt, essence et classe
      group_by(NumDisp, Essence, Classe) %>%
      mutate(AcctD_ForetEssClasse = mean(Acct_Diam, na.rm = T)) %>%
      # sinon valeurs moyennes d'AcctD attribuées par forêt et par essence
      group_by(NumDisp, Essence) %>%
      mutate(AcctD_ForetEss = mean(Acct_Diam, na.rm = T)) %>%
      # sinon valeurs moyennes d'AcctD attribuées par forêt
      group_by(NumDisp) %>%
      mutate(AcctD_Foret = mean(Acct_Diam, na.rm = T)) %>%
      ungroup() %>%
      
      # distribution des valeurs d'AcctD moyennes calculées
      mutate(
        AcctD =
          ifelse(is.na(Acct_Diam), AcctD_ForetEssClasse, Acct_Diam),
        AcctD =
          ifelse(is.na(AcctD), AcctD_ForetEss, AcctD),
        AcctD =
          ifelse(is.na(AcctD), AcctD_Foret, AcctD)
      ) %>%
      
      # on remplace les valeurs d'AcctD du cycle 1 par les valeurs du cycle 2
      group_by(NumDisp, NumPlac, NumArbre) %>%
      mutate(AcctD =
               ifelse(Cycle == 1 &
                        !(Coupe %in% c("E", "C")), lead(AcctD), AcctD)) %>%
      ungroup() %>%
      
      select(IdArbre, NumDisp, NumPlac, NumArbre, Cycle, AcctD)
    
    # Récupération des AcctD dans la table principale
    df <-
      acct_bv %>%
      left_join(acctD_bv,
                c("IdArbre", "NumDisp", "NumPlac", "NumArbre", "Cycle")) #%>%
    if (echant_change == F) {
      df <-
        df %>%
        mutate(echant_ID = NA) %>%
        # selection de variables
        select(
          NumDisp,
          NumPlac,
          NumArbre,
          IdArbre,
          Cycle,
          Essence,
          EssReg,
          EssRegPar,
          Azimut,
          Dist,
          Diam1,
          Diam2,
          Diam,
          Classe,
          Cat,
          DiamSup,
          ClasseSup,
          VhaSup,
          TauxV,
          Nha,
          Gha,
          Vha,
          VhaIFN,
          CodeSanit,
          Taillis,
          Coupe,
          Limite,
          CodeEcolo,
          Ref_CodeEcolo,
          Haut,
          HautV,
          Type,
          StadeD,
          StadeE,
          Observation,
          
          AcctD,
          AcctGper,
          AcctVper#,
          #Inter
        )
    } else {
      # selection de variables
      df <-
        df %>%
        select(
          NumDisp,
          NumPlac,
          NumArbre,
          IdArbre,
          Cycle,
          Essence,
          EssReg,
          EssRegPar,
          Azimut,
          Dist,
          Diam1,
          Diam2,
          Diam,
          Classe,
          Cat,
          DiamSup,
          ClasseSup,
          VhaSup,
          TauxV,
          Nha,
          Gha,
          Vha,
          VhaIFN,
          CodeSanit,
          Taillis,
          Coupe,
          Limite,
          echant_ID,
          CodeEcolo,
          Ref_CodeEcolo,
          Haut,
          HautV,
          Type,
          StadeD,
          StadeE,
          Observation,
          
          AcctD,
          AcctGper,
          AcctVper#,
          #Inter
        )
    }
  } else {
    df <-
      df %>%
      mutate(
        AcctD = NA,
        AcctGper = NA,
        AcctVper = NA#,
        # AcctG = NA, AcctV = NA,
        )
  }
  
  # -- retour fonction calculs_acct_bv
  return(df)
}
# TODO N.B : certains dispositifs identifient bien tous les brins de taillis (NumArbre ET association Azimut+Dist), et d'autres veillent à distinguer les NumArbre MAIS laissent le même azimut => quid des arbres qui passent à la futaie (comment est-ce possible d'ailleurs -> il ne reste qu'un brin ?) entre 2 inventaires ? (Forêt d'Erstein) Tester tous les cas !! Demander aux gestionnaires / référents ?
# En tous cas, si chaque brin est identifié par une combinaison NumDisp-NumPlac-NumArbre à travers les différents cycles, alors on peut faire les calculs d'accroissement à l'échelle de chaque individu, sans regrouper les résultats par cépée

##### fonction de traitement des données PCQM #####
calculs_PCQM <- function(pcqm = NULL, placettes = NULL) {
  # -- df et vecteurs annexes
  Coeffts <- data.frame(Vides = c(0:4),
                        Coeffts = c(1, 0.58159, 0.33930, 0.15351, 0))
  populations <-
    c("VivantInf20",
      "VivantSup20",
      "VivantSup40",
      "MortSup20D",
      "MortInf20D")
  # -- jonction
  pcqm <- convert_columns_to_numeric(pcqm)
  placettes_copy <- convert_columns_to_numeric(placettes)
  
  pcqm <-
    pcqm %>%
    left_join(placettes_copy[, c("NumDisp", "NumPlac", "Cycle", "Strate")],
              by = c("NumDisp", "NumPlac", "Cycle"))
  
  # -- table de résultats
  df <- data.frame(
    NumDisp = numeric(),
    NumPlac = character(),
    Cycle = numeric(),
    Quart = character(),
    Essence = character(),
    EssReg = character(),
    Diam = numeric(),
    Classe = numeric(),
    Nha = numeric(),
    Gha = numeric(),
    Vha = numeric(),
    stringsAsFactors = F
  )
  
  if (nrow(pcqm) > 0) {
    # cond 'nrow(pcqm) > 0'
    for (pop in populations) {
      # loop 'pop in populations'
      # pop <- populations[1] # debug
      df0 <- pcqm %>% filter(Population == pop & !is.na(Diam))
      
      if (dim(df0)[1] > 0) {
        # -- df de correction pour les quarts demeurés vides
        Corr <- data.frame(Coeff = table(df0$NumDisp, df0$NumPlac),
                           stringsAsFactors = F) %>%
          rename(NumDisp = Coeff.Var1,
                 NumPlac = Coeff.Var2,
                 Nbre = Coeff.Freq) %>%
          mutate(
            NumDisp = as.numeric(as.character(NumDisp)),
            NumPlac = as.character(NumPlac),
            Nbre = as.numeric(Nbre),
            Vides = 4 - Nbre
          ) %>%
          left_join(Coeffts, by = "Vides")
        
        # -- calcul
        df1 <-
          df0 %>%
          filter(Dist <= 20) %>%
          group_by(NumDisp, NumPlac, Cycle) %>%
          mutate(Nha = sum(Dist ^ 2, na.rm = T),
                 Nha = 10000 * 3 / pi / Nha) %>%
          ungroup() %>%
          left_join(Corr[, c("NumDisp", "NumPlac", "Coeffts")],
                    by = c("NumDisp", "NumPlac")) %>%
          mutate(
            Nha = Nha * Coeffts,
            Gha = pi / 40000 * Diam ^ 2 * Nha,
            Classe = floor(Diam / 5 + 0.5) * 5,
            Cat = cut(
              Diam,
              breaks = c(0, 17.5, 27.5, 47.5, 67.5, 200),
              labels = c("PER", "PB", "BM", "GB", "TGB"),
              include.lowest = T,
              right = F
            ),
            Cat = as.character(Cat),
            Vha = Gha * 7
          ) %>%
          # left_join(table_essence[, c("Essence", "EssReg")], by = "Essence") %>%
          # left_join(EssReg, by = c("NumDisp", "Essence")) %>%
          mutate(EssReg = ifelse(!is.na(EssRegPar), EssRegPar, EssReg)) %>%
          select(
            NumDisp,
            NumPlac,
            Cycle,
            Quart,
            Essence,
            EssReg,
            EssRegPar,
            Diam,
            Classe,
            Nha,
            Gha,
            Vha
          )
        
        
      } else {
        df1 <-
          df0 %>%
          mutate(
            Essence = NA,
            EssReg = NA,
            EssRegPar = NA,
            Diam = NA,
            Classe = NA,
            Nha = NA,
            Gha = NA,
            Vha = NA
          ) %>%
          select(
            NumDisp,
            NumPlac,
            Cycle,
            Quart,
            Essence,
            EssReg,
            EssRegPar,
            Diam,
            Classe,
            Nha,
            Gha,
            Vha
          )
      }
      
      df <- rbind(df, df1)
    } # end of loop 'pop in populations'
  } # end of cond 'nrow(pcqm) > 0'
  
  # -- retour fonction calculs_PCQM
  return(df)
}

##### fonction de calcul des accroissements de bois mort sur pied #####
calculs_acct_bmp <-
  function(# TODO : essayer de rassembler les fonctions d'acct (optimal mais facultatif)
    df = NULL,
    cycle_num = last_cycle,
    cycles_inv = NULL,
    echant_change = F) {
    # df <- bms_sup30 # debug
    # df <- head(BMP, 30) # debug
    # df <- BMP
    # Paramètres initiaux
    # cycle_num <- max(df$Cycle, na.rm = T)
    
    if (cycle_num > 1) {
      # table contenant les pas de temps
      tLaps <-
        df %>%
        distinct(NumDisp, NumPlac, NumArbre, IdArbre) %>%
        full_join(cycles_inv[, c("NumDisp", "NumPlac", "Cycle", "Annee")],
                  by = c("NumDisp", "NumPlac")) %>%
        group_by(NumDisp, NumPlac, NumArbre, IdArbre) %>%
        mutate(Inter = Annee - lag(Annee)) %>%
        ungroup() %>%
        # filter(Cycle > 1) %>%
        left_join(distinct(df[, c("IdArbre", "Essence", "EssReg", "Azimut", "Dist")]),
                  by = "IdArbre") %>%
        select(NumDisp,
               NumPlac,
               NumArbre,
               Cycle,
               IdArbre,
               Essence,
               EssReg,
               Azimut,
               Dist,
               Inter)
      
      # Sécurité : contrôle des valeurs dupliquées (ID="NumDisp+NumPlac+NumArbre+Cycle")
      df_Dupl <-
        df %>%
        select(NumDisp, NumPlac, Cycle, Azimut, Dist) %>% #,Taillis
        arrange(NumDisp, NumPlac, Cycle, Azimut, Dist)
      # rangement de df dans le même ordre que df_Dupl
      df <-
        df %>%
        arrange(NumDisp, NumPlac, Cycle, Azimut, Dist)
      
      # valeurs dupliquées
      Dupl <- which(duplicated(df_Dupl) & df_Dupl$Taillis != "t")
      # édition d'un classeur listant les valeurs dupliquées
      if (length(Dupl) > 0) {
        Dupl_INV <-
          which(duplicated(df_Dupl, fromLast = TRUE) &
                  df_Dupl$Taillis != "t")
        Dupl <- c(Dupl, Dupl_INV)
        Error_DF <- df[Dupl, c("NumDisp",
                               "NumPlac",
                               "Cycle",
                               "NumArbre",
                               "Essence",
                               "Azimut",
                               "Dist",
                               "Diam1")] %>%
          arrange(NumDisp, NumPlac, Cycle, Azimut, Dist)
        write.xlsx(Error_DF,
                   file = file.path(repPSDRF, "Doublons.xlsx"))
        stop(
          "Attention : doublon(s) d\u00E9tect\u00E9(s) lors des calculs d'accroissement.\n\nDoublons list\u00E9s dans le classeur excel 'Doublons.xlsx'"
        )
      }
      
      # Calculs des accroissements (superassignement)
      acct_bmp <<-
        df %>%
        left_join(
          tLaps,
          by = c(
            "NumDisp",
            "NumPlac",
            "NumArbre",
            "Cycle",
            "IdArbre",
            "Essence",
            "EssReg",
            "Azimut",
            "Dist"
          )
        ) %>%
        # left_join(tLaps, by = c("NumDisp", "NumPlac", "NumArbre", "Cycle")) %>%
        arrange(NumDisp, NumPlac, NumArbre, Cycle) %>%
        group_by(NumDisp, NumPlac, NumArbre) %>%
        mutate(
          # BM apparaissant :
          # les notations "E", "PF" ou "PF/E", sont reconstituées
          Coupe =
            ifelse(
              is.na(lag(Vha)) &
                !is.na(Vha) &
                Cycle > 1 & is.na(Coupe),
              # Coupe est forcément vide à ce moment
              "PF",
              Coupe
            ),
          # BM disparus :
          Coupe =
            ifelse(is.na(lead(Vha)) &
                     Cycle < cycle_num & is.na(Coupe),
                   "E",
                   Coupe),
          Coupe =
            ifelse(
              is.na(lead(Vha)) & Cycle < cycle_num & !is.na(Coupe) &
                Coupe == "PF",
              #!str_detect(Coupe, "C")
              "PF/E",
              Coupe
            ),
          
          # --- Calcul des accroissements
          # Inter = Annee - lag(Annee),
          # Acct_DiamIni = round( (DiamIni - lag(DiamIni, default = NA)) / Inter, digits = 10), # mettre plus bas et ensuite rajouter condition : si Coupe detect C ou E ?
          Acct_Diam = round((Diam - lag(Diam, default = NA)) / Inter, digits = 10),
          # Acct_DiamFin = round( (DiamFin - lag(DiamFin, default = NA)) / Inter, digits = 10),
          AcctGper = round((Gha - lag(Gha, default = 0)) / Inter, digits = 10),
          AcctVper = round((Vha - lag(Vha, default = 0)) / Inter, digits = 10)
          
        ) %>%
        ungroup() %>%
        as.data.frame()
      
      ### ----- Table des accroissements en diamètre ----- ###
      # Attribution d'une valeur d'accroissement en diamètre (si Acct_Diam vide)
      acctD_bmp <-
        acct_bmp %>% # s'assurer qu'on a bien des arbres limites dans la table
        select(IdArbre,
               NumDisp,
               NumPlac,
               NumArbre,
               Cycle,
               Essence,
               Classe,
               Acct_Diam,
               Coupe) %>%
        
        # valeurs moyennes d'AcctD attribuées par forêt, essence et classe
        group_by(NumDisp, Essence, Classe) %>%
        mutate(AcctD_ForetEssClasse = mean(Acct_Diam, na.rm = T)) %>%
        # sinon valeurs moyennes d'AcctD attribuées par forêt et par essence
        group_by(NumDisp, Essence) %>%
        mutate(AcctD_ForetEss = mean(Acct_Diam, na.rm = T)) %>%
        # sinon valeurs moyennes d'AcctD attribuées par forêt
        group_by(NumDisp) %>%
        mutate(AcctD_Foret = mean(Acct_Diam, na.rm = T)) %>%
        ungroup() %>%
        
        # distribution des valeurs d'AcctD moyennes calculées
        mutate(
          AcctD =
            ifelse(is.na(Acct_Diam), AcctD_ForetEssClasse, Acct_Diam),
          AcctD =
            ifelse(is.na(AcctD), AcctD_ForetEss, AcctD),
          AcctD =
            ifelse(is.na(AcctD), AcctD_Foret, AcctD)
        ) %>%
        
        # on remplace les valeurs d'AcctD du cycle 1 par les valeurs du cycle 2
        group_by(NumDisp, NumPlac, NumArbre) %>%
        mutate(AcctD =
                 ifelse(Cycle == 1 &
                          !(Coupe %in% c("E", "C")), lead(AcctD), AcctD)) %>%
        ungroup() %>%
        
        select(IdArbre, NumDisp, NumPlac, NumArbre, Cycle, AcctD)
      
      # Récupération des AcctD dans la table principale
      df <-
        acct_bmp %>%
        left_join(acctD_bmp,
                  c("IdArbre", "NumDisp", "NumPlac", "NumArbre", "Cycle")) #%>%
      if (echant_change == F) {
        df <-
          df %>%
          mutate(echant_ID = NA) %>%
          # selection de variables
          select(
            NumDisp,
            NumPlac,
            NumArbre,
            IdArbre,
            Cycle,
            Essence,
            EssReg,
            EssRegPar,
            Azimut,
            Dist,
            Diam1,
            Diam2,
            Diam,
            Classe,
            Cat,
            DiamSup,
            ClasseSup,
            VhaSup,
            TauxV,
            Nha,
            Gha,
            Vha,
            VhaIFN,
            Limite,
            CodeEcolo,
            Ref_CodeEcolo,
            Haut,
            HautV,
            Type,
            StadeD,
            StadeE,
            Observation,
            
            AcctGper,
            AcctVper,
            AcctD,
            Coupe#, Inter
          )
      } else {
        # selection de variables
        df <-
          df %>%
          select(
            NumDisp,
            NumPlac,
            NumArbre,
            IdArbre,
            Cycle,
            Essence,
            EssReg,
            EssRegPar,
            Azimut,
            Dist,
            Diam1,
            Diam2,
            Diam,
            Classe,
            Cat,
            DiamSup,
            ClasseSup,
            VhaSup,
            TauxV,
            Nha,
            Gha,
            Vha,
            VhaIFN,
            Limite,
            echant_ID,
            # CodeEcolo, Ref_CodeEcolo,
            Haut,
            HautV,
            Type,
            StadeD,
            StadeE,
            Observation,
            
            AcctGper,
            AcctVper,
            AcctD,
            Coupe#, Inter
          )
      }
    } else {
      df <- df %>%
        mutate(
          AcctD = NA,
          AcctVper = NA,
          AcctGper = NA,
          AcctV = NA,
          AcctG = NA
        )
    }
    
    # -- retour fonction calculs_acct_bmp
    return(df)
  }

##### fonction de traitement du bois mort au sol < 30 cm #####
calculs_bms_lineaire <- function(df = NULL) {
  df <-
    df %>%
    mutate(
      Angle = ifelse(is.na(Angle), 0, Angle),
      Classe = floor(Diam / 5 + 0.5) * 5,
      Cat = cut(
        Diam,
        breaks = c(0, 17.5, 27.5, 47.5, 67.5, 200),
        labels = c("PER", "PB", "BM", "GB", "TGB"),
        include.lowest = T,
        right = F
      ),
      Cat = as.character(Cat),
      Vha = pi ^ 2 / 8 / 60 * Diam ^ 2 / cos(Angle / 180 * pi)
    ) %>%
    # left_join(table_essence[, c("Essence", "EssReg")], by = "Essence") %>%
    # left_join(EssReg, by = c("NumDisp", "Essence")) %>%
    mutate(EssReg = ifelse(!is.na(EssRegPar), EssRegPar, EssReg)) %>%
    select(
      NumDisp,
      Cycle,
      NumPlac,
      Transect,
      Essence,
      EssReg,
      EssRegPar,
      Diam,
      Classe,
      Cat,
      StadeD,
      StadeE,
      Vha
    )
  
  # -- retour de la fonction calculs_bms_lineaire
  return(df)
}

##### fonction de calcul des volumes de bois mort au sol > 30 cm #####
# ----- calcul des Vha
calculs_bms_sup30 <- function(df = NULL, echant_change = F) {
  # df <- BMSsup30 # debug
  # df <- bms_sup30 # debug
  df <-
    df %>%
    mutate(
      DiamIni = ifelse(is.na(DiamIni), 0, DiamIni),
      DiamMed = ifelse(is.na(DiamMed), 0, DiamMed),
      DiamFin = ifelse(is.na(DiamFin), 0, DiamFin),
      Vha = 0,
      Classe = 0,
      # ---- formule de Huber
      Vha = ifelse(
        (DiamIni + DiamFin) == 0,
        pi / 40000 * DiamMed ^ 2 * Longueur * 10000 / pi / Rayon ^ 2,
        Vha
      ),
      Classe = ifelse((DiamIni + DiamFin) == 0,
                      floor(DiamMed / 5 + 0.5) * 5,
                      Classe),
      # ---- formule de Smalian
      Vha = ifelse(
        (DiamIni + DiamFin) != 0 & DiamMed == 0,
        pi / 80000 * (DiamIni ^ 2 + DiamFin ^ 2) *
          Longueur * 10000 / pi / Rayon ^ 2,
        Vha
      ),
      Classe = ifelse(
        (DiamIni + DiamFin) != 0 & DiamMed == 0,
        floor((DiamIni + DiamFin) / 2 / 5 + 0.5) * 5,
        Classe
      ),
      # ---- formule de Newton
      Vha = ifelse(
        (DiamIni + DiamFin) != 0 & DiamMed != 0,
        pi / 240000 * (DiamIni ^ 2 + DiamFin ^ 2 + 4 * DiamMed ^ 2) *
          Longueur * 10000 / (pi * Rayon ^ 2),
        Vha
      ),
      Classe = ifelse(
        (DiamIni + DiamFin) != 0 & DiamMed != 0,
        floor((DiamIni + DiamFin + DiamMed) / 3 / 5 + 0.5) * 5,
        Classe
      )
    ) %>%
    mutate(
      Cat = cut(
        Classe,
        breaks = c(0, 17.5, 27.5, 47.5, 67.5, 500),
        labels = c("PER", "PB", "BM", "GB", "TGB"),
        include.lowest = T,
        right = F
      ),
      Cat = as.character(Cat)
    ) %>%
    # left_join(table_essence[, c("Essence", "EssReg")], by = "Essence") %>%
    # left_join(EssReg, by = c("NumDisp", "Essence")) %>%
    mutate(EssReg = ifelse(!is.na(EssRegPar), EssRegPar, EssReg),
           Coupe = NA)
  
  if (echant_change == F) {
    # selection de variables
    df <-
      df %>%
      select(
        NumDisp,
        NumPlac,
        Id,
        Cycle,
        Essence,
        EssReg,
        EssRegPar,
        # Contact, Chablis,
        Classe,
        Cat,
        DiamIni,
        DiamMed,
        DiamFin,
        StadeD,
        StadeE,
        Vha,
        Coupe
      )
  } else {
    df <-
      df %>%
      mutate(echant_ID = NA) %>%
      # selection de variables
      select(
        NumDisp,
        NumPlac,
        Id,
        Cycle,
        Essence,
        EssReg,
        EssRegPar,
        # Contact, Chablis,
        Classe,
        Cat,
        DiamIni,
        DiamMed,
        DiamFin,
        StadeD,
        StadeE,
        Vha,
        echant_ID,
        Coupe
      )
  }
  
  # -- retour de la fonction calculs_BMSsup30
  return(df)
}

##### fonction de calcul de l'évolution des diamètres et des volumes de bois mort au sol < 30 cm #####
calculs_acct_bms <- function(df = NULL,
                             cycle_num = last_cycle,
                             cycles_inv = NULL,
                             echant_change = F) {
  # df <- bms_sup30 # debug
  # Paramètres initiaux
  
  if (cycle_num > 1) {
    # table contenant les pas de temps
    tLaps <-
      df %>%
      distinct(NumDisp, NumPlac, Id) %>%
      full_join(cycles_inv[, c("NumDisp", "NumPlac", "Cycle", "Annee")],
                by = c("NumDisp", "NumPlac")) %>%
      group_by(NumDisp, NumPlac, Id) %>%
      mutate(Inter = Annee - lag(Annee)) %>%
      ungroup() %>%
      left_join(distinct(df[, c("NumDisp", "NumPlac", "Id", "Cycle",
                                "Essence", "EssReg")]),
                by = c("NumDisp", "NumPlac", "Id", "Cycle")) %>%
      select(NumDisp, NumPlac, Id, Cycle,
             Essence, EssReg, Inter)
    
    # Sécurité : contrôle des valeurs dupliquées (ID="NumDisp+NumPlac+NumArbre+Cycle")
    df_Dupl <-
      df %>%
      select(NumDisp, NumPlac, Id, Cycle) %>% #,Taillis
      arrange(NumDisp, NumPlac, Id, Cycle)
    # rangement de df dans le même ordre que df_Dupl
    df <-
      df %>% arrange(NumDisp, NumPlac, Id, Cycle)
    
    # valeurs dupliquées
    Dupl <- which(duplicated(df_Dupl))
    # édition d'un classeur listant les valeurs dupliquées
    if (length(Dupl) > 0) {
      Dupl_INV <- which(duplicated(df_Dupl, fromLast = TRUE))
      Dupl <- c(Dupl, Dupl_INV)
      Error_DF <- df[Dupl, c("NumDisp",
                             "NumPlac",
                             "Id",
                             "Cycle",
                             "Essence",
                             "DiamIni",
                             "DiamMed",
                             "DiamFin")] %>%
        arrange(NumDisp, NumPlac, Id, Cycle)
      write.xlsx(Error_DF,
                 file = file.path(repPSDRF, "Doublons_BMSsup30.xlsx"))
      stop(
        "Attention : doublon(s) d\u00E9tect\u00E9(s) lors des calculs d'accroissement.\n\nDoublons list\u00E9s dans le classeur excel 'Doublons.xlsx'"
      )
    }
    
    # Calculs des accroissements (superassignement)
    acct_bms <<-
      df %>%
      mutate(Type = "BMSsup30", Coupe = NA) %>%
      left_join(tLaps,
                by = c("NumDisp", "NumPlac", "Id", "Cycle",
                       "Essence", "EssReg")) %>%
      arrange(NumDisp, NumPlac, Id, Cycle) %>%
      group_by(NumDisp, NumPlac, Id) %>%
      mutate(
        # BM apparaissant :
        # les notations "E", "PF" ou "PF/E", sont reconstituées
        Coupe =
          ifelse(
            is.na(lag(Vha)) &
              !is.na(Vha) &
              Cycle > 1 & is.na(Coupe),
            # Coupe est forcément vide à ce moment
            "PF",
            Coupe
          ),
        # BM disparus :
        Coupe =
          ifelse(is.na(lead(Vha)) &
                   Cycle < cycle_num & is.na(Coupe),
                 "E",
                 Coupe),
        Coupe =
          ifelse(
            is.na(lead(Vha)) & Cycle < cycle_num & !is.na(Coupe) &
              Coupe == "PF",
            #!str_detect(Coupe, "C")
            "PF/E",
            Coupe
          ),
        
        # --- Calcul des accroissements
        # Inter = Annee - lag(Annee),
        # Acct_DiamIni = round( (DiamIni - lag(DiamIni, default = NA)) / Inter, digits = 10), # mettre plus bas et ensuite rajouter condition : si Coupe detect C ou E ?
        Acct_Diam = round((DiamMed - lag(
          DiamMed, default = NA
        )) / Inter, digits = 10),
        # Acct_DiamFin = round( (DiamFin - lag(DiamFin, default = NA)) / Inter, digits = 10),
        # AcctGper = round( (Gha - lag(Gha, default = 0)) / Inter, digits = 10),
        AcctVper = round((Vha - lag(Vha, default = 0)) / Inter, digits = 10)
        
      ) %>%
      ungroup() %>%
      as.data.frame()
    
    ### ----- Table des accroissements en diamètre ----- ###
    # Attribution d'une valeur d'accroissement en diamètre (si Acct_Diam vide)
    acctD_bms <-
      acct_bms %>% # s'assurer qu'on a bien des arbres limites dans la table
      select(NumDisp,
             NumPlac,
             Id,
             Cycle,
             Essence,
             Classe,
             Acct_Diam,
             Coupe) %>%
      
      # valeurs moyennes d'AcctD attribuées par forêt, essence et classe
      group_by(NumDisp, Essence, Classe) %>%
      mutate(AcctD_ForetEssClasse = mean(Acct_Diam, na.rm = T)) %>%
      # sinon valeurs moyennes d'AcctD attribuées par forêt et par essence
      group_by(NumDisp, Essence) %>%
      mutate(AcctD_ForetEss = mean(Acct_Diam, na.rm = T)) %>%
      # sinon valeurs moyennes d'AcctD attribuées par forêt
      group_by(NumDisp) %>%
      mutate(AcctD_Foret = mean(Acct_Diam, na.rm = T)) %>%
      ungroup() %>%
      
      # distribution des valeurs d'AcctD moyennes calculées
      mutate(
        AcctD =
          ifelse(is.na(Acct_Diam), AcctD_ForetEssClasse, Acct_Diam),
        AcctD =
          ifelse(is.na(AcctD), AcctD_ForetEss, AcctD),
        AcctD =
          ifelse(is.na(AcctD), AcctD_Foret, AcctD)
      ) %>%
      
      # on remplace les valeurs d'AcctD du cycle 1 par les valeurs du cycle 2
      group_by(NumDisp, NumPlac, Id) %>%
      mutate(AcctD =
               ifelse(Cycle == 1 &
                        !(Coupe %in% c("E", "C")), lead(AcctD), AcctD)) %>%
      ungroup() %>%
      
      select(NumDisp, NumPlac, Id, Cycle, AcctD)
    
    # Récupération des AcctD dans la table principale
    df <-
      acct_bms %>%
      left_join(acctD_bms,
                by = c("NumDisp", "NumPlac", "Id", "Cycle"))
    
    if (echant_change == F) {
      df <-
        df %>%
        mutate(echant_ID = NA) %>%
        # selection de variables
        select(
          NumDisp,
          NumPlac,
          Id,
          Cycle,
          Essence,
          EssReg,
          EssRegPar,
          DiamIni,
          DiamMed,
          DiamFin,
          Classe,
          Cat,
          Vha,
          StadeD,
          StadeE,
          
          AcctVper,
          AcctD,
          Coupe#, Inter
        )
    } else {
      # selection de variables
      df <-
        df %>%
        select(
          NumDisp,
          NumPlac,
          Id,
          Cycle,
          Essence,
          EssReg,
          EssRegPar,
          DiamIni,
          DiamMed,
          DiamFin,
          Classe,
          Cat,
          Vha,
          StadeD,
          StadeE,
          
          AcctVper,
          AcctD,
          Coupe,
          #Inter,
          echant_ID
        )
    }
  } else {
    df <- df %>% mutate(AcctD = NA, AcctVper = NA)
  }
  
  # -- retour fonction calculs_acct_bms
  return(df)
}

##### fonction de traitement de la régénération #####
calculs_Reges <- function(df = NULL) {
  df <-
    df %>%
    # left_join(table_essence[, c("Essence", "EssReg")], by = "Essence") %>%
    # left_join(EssReg, by = c("NumDisp", "Essence")) %>%
    filter(!is.na(Essence)) %>% # Il peut y avoir des essences vides si on a fait une Ss-placette et juste noté 1 observation
    # select(-one_of("Rejet","Observations")) %>%
    arrange(NumDisp, Cycle, NumPlac, SsPlac) %>%
    # replace(is.na(.),0) %>%
    mutate(
      EssReg = ifelse(!is.na(EssRegPar), EssRegPar, EssReg),
      
      Recouv = ifelse(is.na(Recouv), 0, Recouv),
      Class1 = ifelse(is.na(Class1), 0, Class1),
      Class2 = ifelse(is.na(Class2), 0, Class2),
      Class3 = ifelse(is.na(Class3), 0, Class3),
      
      Recouv = as.numeric(Recouv),
      Class1 = as.numeric(Class1),
      Class2 = as.numeric(Class2),
      Class3 = as.numeric(Class3),
      
      # Surf = ifelse(Class1 + Class2 + Class3 >= 5, 1, 0),
      plac_nb = ifelse(Monitor == "PFA", 2, 3),
      
      Recouv = Recouv / plac_nb,
      Classe1Ha = Class1 * 10000 / (pi * 1.5 ^ 2) / plac_nb,
      Classe2Ha = Class2 * 10000 / (pi * 1.5 ^ 2) / plac_nb,
      Classe3Ha = Class3 * 10000 / (pi * 1.5 ^ 2) / plac_nb
    )
  
  # -- retour de la fonction calculs_Reges
  return(df)
}

##### fonction de détection des changements de protocoles (s'ils existent) #####
change_protocole <- function(echant_DF = NULL) {
  # echant_DF <- Echantillonnages # debug
  # on détecte si le protocole change à travers les cycles d'inventaire
  # echant_NAMES <- syms(setdiff(names(echant_DF), "Cycle"))
  echant_NAMES <-
    c("NumDisp", "Monitor", "Coeff", "DiamLim", "Rayon")
  echant_DF <-
    echant_DF %>%
    distinct_at(echant_NAMES, .keep_all = T)
  
  # on recrée une table "echant_DF" avec les paramètres du plus
  # grand dénominateur commun entre les 2 (ou plus) protocoles d'inventaire
  # différents
  echant_DF <-
    echant_DF %>%
    group_by(NumDisp) %>%
    mutate(
      DiamLim = min(DiamLim),
      Rayon = min(Rayon),
      Coeff = max(Coeff),
      
      # Identifiant pour retrouver les arbres concernés par le
      # changement de protocole
      echant_ID = paste0(NumDisp, "-", Cycle),
      Observations = NULL
    ) %>%
    ungroup()
  # -- retour fonction change_protocole
  return(echant_DF)
}

##### function to check protocols #####
check_protocol <- function(table = NULL) {
  # -- repérage des placettes pour lesquelles le protocole change
  # table0 <- echant_DF %>% arrange(NumDisp, NumPlac, Cycle) # debug
  # table0[2, "DiamLim"] <- 30 # debug
  table <-
    table %>%
    
    # sort
    arrange(NumDisp, Monitor, Coeff, DiamLim, Rayon, NumPlac) %>%
    
    # group by protocol
    group_by(Monitor, Coeff, DiamLim, Rayon) %>%
    
    # create protocol id
    mutate(id_protocol = cur_group_id()) %>%
    ungroup() %>%
    
    # sort
    arrange(NumDisp, NumPlac, Cycle) %>%
    
    # group par dispositif et placette
    group_by(NumDisp, NumPlac) %>%
    
    # décompte des différents protocoles par placette à travers les cycles
    mutate(nb_protocol = length(unique(id_protocol))) %>%
    ungroup()
  
  
  # filtre des placettes pour lesquelles plusieurs protocoles sont utilisés
  unstable_protocol <- table %>% filter(nb_protocol > 1)
  steady_protocol <- table %>% filter(nb_protocol == 1)
  
  # -- retour fonction 'check_protocol'
  return(list(unstable_protocol = unstable_protocol,
              steady_protocol = steady_protocol))
}

##### fonction dmh_split #####
dmh_split <- function (df0 = NULL,
                       list = list) {
  df <- data.frame(
    NumDisp = rep.int(df0$NumDisp, sapply(list, length)),
    NumPlac = rep.int(df0$NumPlac, sapply(list, length)),
    NumArbre = rep.int(df0$NumArbre, sapply(list, length)),
    CodeEcolo = unlist(list),
    stringsAsFactors = F
  )
  # suppression de la colonne CodeEcolo
  df0 <- df0 %>% select(-CodeEcolo)
  # fusion de df et df0
  df <-
    df %>% left_join(df0, by = c("NumDisp", "NumPlac", "NumArbre"))
  
  # -- retour de dmh_split
  return(df)
}

##### fonction de calculs des dmh (duplique les lignes de la table Arbres pour chaque dmh reconnu) #####
calculs_dmh <- function(df = NULL, dmh_df = NULL) {
  if (dim(df)[1] > 0) {
    df_ProSilva <- df %>% filter(Ref_CodeEcolo == "prosilva")
    df_AFI <-
      df %>% filter(Ref_CodeEcolo == "engref" |
                      Ref_CodeEcolo == "afi")
    df_EFI <- df %>% filter(Ref_CodeEcolo == "efi")
    df_IRSTEA <- df %>% filter(Ref_CodeEcolo == "irstea")
    
    # ----- Codification ProSilva
    if (dim(df_ProSilva)[1] > 0) {
      # ---- décomposition
      # liste
      list <- with(df_ProSilva,
                   str_split(CodeEcolo, boundary("word")))
      # df
      codes1 <- dmh_split(df_ProSilva, list)
    } else {
      codes1 <- data.frame()
    }
    
    # ----- Codification AFI
    if (dim(df_AFI)[1] > 0) {
      # ----- df # TODO : à mettre dans le job2
      df_AFI <-
        df_AFI %>% mutate(CodeEcolo = str_replace(CodeEcolo, "0", ""))
      # ----- niveaux
      niveaux <-
        dmh_df %>%
        filter(Codification == "engref") %>%
        select(Code) %>%
        unlist()
      # ---- décomposition
      # liste
      list <- c()
      for (i in 1:dim(df_AFI)[1]) {
        list0 <- with(df_AFI, str_extract(CodeEcolo[i], niveaux))
        list0 <- list0[!is.na(list0)]
        list <- c(list, list(list0))
      }
      # df
      codes2 <- dmh_split(df_AFI, list)
    } else {
      codes2 <- data.frame()
    }
    
    # ----- Codification EFI
    if (dim(df_EFI)[1] > 0) {
      # ---- décomposition
      # liste
      list <- with(df_EFI,
                   str_split(CodeEcolo, boundary("word")))
      # df
      codes3 <- dmh_split(df_EFI, list)
    } else {
      codes3 <- data.frame()
    }
    
    # ----- Codification IRSTEA
    if (dim(df_IRSTEA)[1] > 0) {
      # ----- df # TODO : à mettre dans le job2
      df_IRSTEA <-
        df_IRSTEA %>% mutate(CodeEcolo = str_replace(CodeEcolo, "0", ""))
      # ----- niveaux
      niveaux <-
        dmh_df %>%
        filter(Codification == "IRSTEA") %>%
        select(Code) %>%
        unlist()
      # ---- décomposition
      # liste
      list <- c()
      for (i in 1:dim(df_IRSTEA)[1]) {
        list0 <- with(df_IRSTEA, str_extract(CodeEcolo[i], niveaux))
        list0 <- list0[!is.na(list0)]
        list <- c(list, list(list0))
      }
      # df
      codes4 <- dmh_split(df_IRSTEA, list)
    } else {
      codes4 <- data.frame()
    }
    
    codes <- rbind(codes1, codes2, codes3, codes4)
  } else {
    codes <- data.frame()
  }
  
  # -- retour de la fonction calculs_dmh
  return(codes)
}




#' Calcul des variables dendrométriques et écologiques des données d'inventaire PSDRF.
#'
#' @description Cette fonction permet de calculer les valeurs de volume, densité, surface terrière à l'hectare pour chaque
#' élément inventorié dans le PSDRF (bois vivant, bois mort).
#'
#' @author Bruciamacchie Max, Demets Valentin
#'
#' @param repPSDRF = répertoire de travail
#'
#' @importFrom dplyr %>%
#' @importFrom dplyr mutate
#' @importFrom dplyr select
#' @importFrom dplyr left_join
#' @importFrom reshape2 melt
#' @importFrom dplyr arrange
#' @importFrom reshape2 dcast
#' @importFrom dplyr rename_
#' @importFrom dplyr group_by
#' @importFrom dplyr ungroup
#' @importFrom dplyr rename
#' @importFrom stringr str_sub
#' @importFrom stringr str_locate
#' @import tcltk
#' @import reshape2
#'
#' @export

psdrf_Calculs <- function(
  repPSDRF = NULL, dispId, last_cycle
  ) {
  # -- définition nulle des variables utilisées
  objects <- c(
    "AccDMoyDispEss", "AccDMoyDispEssClasse", "AccDMoyEssClasse", 
    "AcctD", "AcctD_Chgt", "AcctG", "AcctGper", "AcctGper_Chgt", 
    "AcctVper", "AcctVper_Chgt", "Angle", "Annee", "Azimut", "Cat", 
    "CatPar", "Cercle", "Chablis", "Class1", "Class2", "Class3", 
    "Classe", "Classe1Ha", "Classe2Ha", "Classe3Ha", "CodeEcolo", 
    "CodeEcologie", "CodeEssence", "Coeff", "Coeff.Freq", "Coeff.Var1", 
    "Coeff.Var2", "Contact", "Coupe", "Coupe_Chgt", "Cycle", "Cycle_Max", 
    "Cycle_PFAMA", "CycleMax_PFA", "CycleMin_MA", "Cycles", "CyclesCodes", 
    "Date", "Diam", "Diam1", "Diam2", "DiamFin", "DiamIni", "DiamLim", 
    "DiamMed", "Dispositifs", "Dist", "Essence", "EssReg", "EssRegPar", 
    "g", "Gha", "Haut", "Id", "IdArbre", "IdArbres", "Lim", "Limite", 
    "Longueur", "Monitor", "Nbre", "Nha", "NumArbre", "NumDisp", "NumPlac", 
    "NumTarif", "NumTarifIFN", "Observation", "Placettes", "Population", 
    "Presence", "Quart", "Recouv", "Ref_CodeEcolo", "StadeD", "StadeE", 
    "Tarifs", "TauxV", "Transect", "Type", "TypeTarif", "TypeTarifIFN", 
    "ValArbres", "value", "variable", "Vha", "Vol", "Arbres"
  )
  create_null(objects)
  ##### 1/ Initialisation #####
  # -- répertoire de travail
  setwd(repPSDRF)
  
  # -- chargement des données d'inventaire et administratives
  load("tables/psdrfCodes.Rdata")
  load("tables/psdrfDonneesBrutes.Rdata")
  
  # -- Conversion des colonnes Cycle en numérique pour éviter les problèmes de jointure
  # Cette étape est cruciale pour éviter l'erreur "ℹ `x$Cycle` is a <double>. ℹ `y$Cycle` is a <character>."
  print("Conversion des colonnes Cycle et NumDisp en numérique...")
  
  # Conversion des colonnes numériques dans toutes les tables principales
  print("Conversion des colonnes numériques (Cycle, NumDisp)...")
  
  if (exists("Cycles")) Cycles <- convert_columns_to_numeric(Cycles)
  if (exists("CyclesCodes")) CyclesCodes <- convert_columns_to_numeric(CyclesCodes)
  if (exists("IdArbres")) IdArbres <- convert_columns_to_numeric(IdArbres)
  if (exists("ValArbres")) ValArbres <- convert_columns_to_numeric(ValArbres)
  if (exists("Placettes")) Placettes <- convert_columns_to_numeric(Placettes)
  if (exists("PCQM")) PCQM <- convert_columns_to_numeric(PCQM)
  if (exists("Reges")) Reges <- convert_columns_to_numeric(Reges)
  if (exists("Transect")) Transect <- convert_columns_to_numeric(Transect)
  if (exists("BMSsup30")) BMSsup30 <- convert_columns_to_numeric(BMSsup30)
  
  # Fonction pour gérer la colonne Type/type
  handle_type_column <- function(df) {
    type_col_names <- c("Type", "type")
    for (col_name in type_col_names) {
      if (col_name %in% colnames(df)) {
        print(paste("Attention: Colonne", col_name, "détectée. Tentative de conversion en numérique..."))
        # Sauvegarder les valeurs originales
        df[[paste0(col_name, "_orig")]] <- df[[col_name]]
        
        # Essayer de convertir en numérique
        df[[col_name]] <- suppressWarnings(as.numeric(as.character(df[[col_name]])))
        
        # Vérifier si la conversion a réussi
        na_count <- sum(is.na(df[[col_name]]) & !is.na(df[[paste0(col_name, "_orig")]]))
        if (na_count > 0) {
          print(paste("  - Attention:", na_count, "valeurs n'ont pas pu être converties en numérique et sont devenues NA."))
        }
        print(paste("  - Conversion terminée pour", col_name))
      }
    }
    return(df)
  }
  
  # Conversion des colonnes numériques dans les tables administratives
  if (exists("Cat")) Cat <- convert_columns_to_numeric(Cat)
  if (exists("CodeEssence")) CodeEssence <- convert_columns_to_numeric(CodeEssence)
  if (exists("EssReg")) EssReg <- convert_columns_to_numeric(EssReg)
  if (exists("Tarifs")) Tarifs <- convert_columns_to_numeric(Tarifs)
  if (exists("Dispositifs")) Dispositifs <- convert_columns_to_numeric(Dispositifs)
  if (exists("Communes")) Communes <- convert_columns_to_numeric(Communes)
  if (exists("Suivi")) Suivi <- convert_columns_to_numeric(Suivi)
  
  print("Conversion des colonnes Cycle terminée.")

  ##### 2/ Calculs sur les précomptables #####
                          # Vérification de l'existence des variables nécessaires
                          if (!exists("IdArbres") || !exists("ValArbres")) {
                            stop("Les variables IdArbres et/ou ValArbres n'existent pas dans psdrfDonneesBrutes.Rdata")
                          }
                          
                          # Construction explicite de la variable Arbres
                          print("Construction de la variable Arbres à partir de IdArbres et ValArbres")
                          Arbres <-
                            IdArbres %>%
                            left_join(ValArbres, by = "IdArbre") %>%
                            set_up_calcul_tables(CodeEssence, EssReg,
                                                 Cycles,
                                                 CyclesCodes,
                                                 Tarifs)
                          
                          # Gestion de la colonne Type/type
                          if (exists("Arbres")) {
                            print("Application de handle_type_column à Arbres")
                            Arbres <- handle_type_column(Arbres)
                          }
                          ##### --- 2.1/ Calculs de Nha, Gha, Vha, ... #####
                          Arbres <- Arbres %>% calculs_Arbres()
                          
                          ##### --- 2.2/ Distinction des populations (prec, per, bmp) #####
                          # Perches
                          Perches <-
                            Arbres %>%
                            filter(Diam1 < 17.5 & is.na(Type)) %>%
                            mutate(
                              AcctD = NA,
                              AcctGper = NA,
                              AcctVper = NA,
                              AcctG = NA,
                              AcctV = NA
                            )
                          # BMP
                          BMP <- Arbres %>% filter(!is.na(Type))
                          # Précomptables
                          Arbres <-
                            Arbres %>% filter(Diam1 >= 17.5 &
                                                is.na(Type))
                          
                          ##### --- 2.3/ Calculs d'accroissement (précomptables) #####
                          Arbres <-
                            Arbres %>%
                            calculs_acct_bv(last_cycle, Cycles) %>%
                            mutate(
                              AcctV = TauxV * Vha * AcctD,
                              AcctG = pi / 20000 * AcctD * Diam * Nha,
                              AcctG = ifelse(is.na(AcctG), 0, AcctG)
                            )
                          ##### / \ #####
                          
                          
                          ##### 3/ PCQM #####
                          PCQM <-
                            PCQM %>%
                            set_up_calcul_tables(CodeEssence, EssReg) %>%
                            calculs_PCQM(Placettes)
                          ##### / \ #####
                          
                          
                          ##### 4/ Bois mort sur pied #####
                          ##### --- 4.1/ calculs de l'évolution des diamètres et des volumes #####
                          bmp <-
                            BMP %>% calculs_acct_bmp(last_cycle, Cycles)
                          ##### / \ #####
                          
                          
                          ##### 5/ Calculs sur les bois morts au sol #####
                          ##### --- 5.1/ Echantillonnage linéaire #####
                          BMSLineaires <-
                            Transect %>%
                            set_up_calcul_tables(CodeEssence, EssReg) %>%
                            calculs_bms_lineaire()
                          # TODO : vérifier qu'il n'y a pas de valeur particulière de transect pour le module PFA ? (ou autre module)
                          
                          ##### --- 5.2/ Cercle 20 m #####
                          bms_sup30 <-
                            BMSsup30 %>%
                            # Assurer que Cycle est un nombre dans les deux dataframes
                            mutate(Cycle = as.numeric(as.character(Cycle))) %>%
                            {
                              # Créer une copie de CyclesCodes avec Cycle en numérique
                              CyclesCodes_copy <- CyclesCodes
                              CyclesCodes_copy$Cycle <- as.numeric(as.character(CyclesCodes_copy$Cycle))
                              
                              # Effectuer la jointure
                              left_join(., CyclesCodes_copy[, c("NumDisp", "Cycle", "Monitor")],
                                        by = c("NumDisp", "Cycle"))
                            } %>%
                            mutate(Rayon = ifelse(Monitor == "PFA", 13.8, 20)) %>% # TODO : vérifier qu'il y a du BMSsup30 sur cercle de 20m dans le module Med
                            set_up_calcul_tables(CodeEssence,
                                                 EssReg) %>%
                            calculs_bms_sup30() %>%
                            calculs_acct_bms(last_cycle, Cycles)
                          ##### / \ #####
                          
                          
                          ##### 6/ Régénération #####
                          Reges <-
                            Reges %>%
                            set_up_calcul_tables(CodeEssence, EssReg) %>%
                            {
                              # Créer une copie de CyclesCodes avec types corrects
                              CyclesCodes_copy <- convert_columns_to_numeric(CyclesCodes)
                              
                              # Convertir aussi Reges
                              . <- convert_columns_to_numeric(.)
                              
                              left_join(., CyclesCodes_copy, by = c("NumDisp", "Cycle"))
                            } %>%
                            calculs_Reges()
                          ##### / \ #####
                          
                          
                          ##### 7/ Changements de protocole #####
                          ##### --- 7.1/ Précomptables #####
                          # extrait des tables Cycles et CyclesCodes des cycles concernés par
                          # le changement de protocole (s'il existe)
                          echant_DF <-
                            Cycles %>%
                            # select(NumDisp, Cycle, Monitor) %>%
                            {
                              # Créer une copie de CyclesCodes avec types corrects
                              CyclesCodes_copy <- convert_columns_to_numeric(CyclesCodes)
                              
                              # Convertir aussi Cycles
                              . <- convert_columns_to_numeric(.)
                              
                              left_join(., CyclesCodes_copy, by = c("NumDisp", "Cycle"))
                            } %>%
                            mutate(Rayon = 10,
                                   Rayon = ifelse(Monitor == "PFA", 13.8, Rayon))
                          # echant_DF <- change_protocole(echant_DF)
                          check_protocol_results <-
                            check_protocol(echant_DF)
                          
                          if (nrow(check_protocol_results$unstable_protocol) > 0) {
                            # cond 'nrow(check_protocol_results$unstable_protocol) > 0'
                            # doublons
                            # dupl <- duplicated(echant_DF$NumDisp) | duplicated(echant_DF$NumDisp, fromLast = T)
                            # echant_DF <- echant_DF %>% filter(dupl)
                            echant_DF <-
                              check_protocol_results$unstable_protocol %>%
                              mutate(echant_ID = paste0(NumDisp, "-", Cycle))
                            
                            # Recalculs des valeurs à l'hectare selon les paramètres stables dans le temps.
                            Arbres_Acct <-
                              left_join(IdArbres, ValArbres, by = "IdArbre") %>%
                              set_up_calcul_tables(CodeEssence,
                                                   EssReg,
                                                   cycles_inv = NULL,
                                                   cycles_admin = NULL,
                                                   Tarifs) %>%
                              filter(!is.na(Essence) &
                                       !is.na(Azimut) &
                                       !is.na(Dist)) %>% # on ne prend que les arbres repérés
                              # left_join(
                              # Placettes[,c(
                              # "NumDisp", "NumPlac", "Cycle", "Strate", "PoidsPlacette",
                              # "Pente", "CoeffPente", "Parcelle", "Station"
                              # )],
                              # by = c("NumDisp", "NumPlac", "Cycle")
                              # ) %>%
                              mutate(Coupe = as.character(Coupe),
                                     echant_ID = paste0(NumDisp, "-", Cycle)) %>%
                              # on ne sélectionne que les arbres concernés par le changement de protocole
                              right_join(echant_DF[, c("NumDisp",
                                                       "Cycle",
                                                       "DiamLim",
                                                       "Rayon",
                                                       "Coeff",
                                                       "echant_ID")],
                                         by = c("NumDisp", "Cycle", "echant_ID" = "echant_ID")) %>%
                              # filtre sur la population de précomptables
                              filter(Diam1 >= 17.5 & is.na(Type))
                            
                            # Calculs d'accroissement avec le nouveau protocole
                            Arbres_Acct2 <-
                              calculs_Arbres(Arbres_Acct, echant_change = T)
                            
                            # repérage des cycles concernés par le changement de protocole
                            # cycle_INI <- min(echant_DF$Cycle)
                            # cycle_FIN <- max(echant_DF$Cycle)
                            
                            # recalcul des accroissements
                            Arbres_Acct3 <-
                              Arbres_Acct2 %>%
                              calculs_acct_bv(last_cycle, Cycles, echant_change = T)
                            Arbres_Acct3 <-
                              Arbres_Acct3 %>%
                              group_by(NumDisp) %>%
                              mutate(echant_ID = min(Cycle)) %>%
                              ungroup()
                            
                            # fusion de l'ancienne tables arbres avec la table Arbres_Acct
                            # df1 <- Arbres %>% filter(NumPlac == 1) # debug
                            # df2 <- Arbres_Acct3 %>% filter(NumPlac == 1) # debug
                            Arbres <-
                              Arbres %>%
                              # df1 %>% # debug
                              full_join(
                                Arbres_Acct3,
                                # df2, # debug
                                by = c("NumDisp", "NumPlac", "NumArbre", "IdArbre", "Cycle"),
                                suffix = c("", "_changed")
                              ) %>%
                              select(
                                NumDisp,
                                NumPlac,
                                NumArbre,
                                IdArbre,
                                Cycle,
                                Essence,
                                EssReg,
                                EssRegPar,
                                Azimut,
                                Dist,
                                Diam1,
                                Diam2,
                                Diam,
                                Classe,
                                Cat,
                                DiamSup,
                                ClasseSup,
                                VhaSup,
                                TauxV,
                                Nha,
                                Gha,
                                Vha,
                                VhaIFN,
                                CodeSanit,
                                Taillis,
                                Limite,
                                CodeEcolo,
                                Ref_CodeEcolo,
                                Haut,
                                HautV,
                                Type,
                                StadeD,
                                StadeE,
                                Observation,
                                
                                AcctGper,
                                AcctGper_changed,
                                AcctVper,
                                AcctVper_changed,
                                AcctD,
                                #AcctD_changed, # on garde quoi qu'il arrive AcctD initial car contient plus d'infos
                                AcctG,
                                AcctV,
                                # même raisonnement que AcctD
                                Coupe,
                                Coupe_changed,
                                
                                # Inter,
                                echant_ID
                              ) %>%
                              # si le cycle est concerné par le changement de protocole alors on prend
                              # les valeurs d'accroissement 'changed'
                              mutate(
                                AcctGper = ifelse(!is.na(echant_ID), AcctGper_changed, AcctGper),
                                AcctVper = ifelse(!is.na(echant_ID), AcctVper_changed, AcctVper)
                              ) %>%
                              group_by(NumDisp, NumPlac, NumArbre, IdArbre, Cycle) %>%
                              # cas de la colonne Coupe :
                              mutate(Coupe_temp = ifelse(Cycle == echant_ID, Coupe_changed, Coupe),
                                     # on récupère les notations "E" ou "C"
                                     Coupe = Coupe_temp) %>%
                              ungroup() %>%
                              mutate(
                                AcctGper_changed = NULL,
                                AcctVper_changed = NULL,
                                Gainper_changed = NULL,
                                Coupe_changed = NULL,
                                Coupe_temp = NULL
                              ) %>%
                              select(-echant_ID) %>%
                              as.data.frame()
                          } # end of cond 'nrow(check_protocol_results$unstable_protocol) > 0'
                          ##### --- 7.2/ BMP #####
                          # extrait des tables Cycles et CyclesCodes des cycles concernés par
                          # le changement de protocole (s'il existe)
                          echant_DF <-
                            Cycles %>%
                            # select(NumDisp, Cycle, Monitor) %>%
                            left_join(CyclesCodes, by = c("NumDisp", "Cycle")) %>%
                            mutate(Rayon = 20,
                                   # changement pour les BMSsup30
                                   Rayon = ifelse(Monitor == "PFA", 13.8, Rayon))
                          # echant_DF <- change_protocole(echant_DF)
                          check_protocol_results <-
                            check_protocol(echant_DF)
                          
                          if (nrow(check_protocol_results$unstable_protocol) > 0) {
                            # cond 'nrow(check_protocol_results$unstable_protocol) > 0'
                            # doublons
                            # dupl <- duplicated(echant_DF$NumDisp) | duplicated(echant_DF$NumDisp, fromLast = T)
                            # echant_DF <- echant_DF %>% filter(dupl)
                            echant_DF <-
                              check_protocol_results$unstable_protocol %>%
                              mutate(echant_ID = paste0(NumDisp, "-", Cycle))
                            
                            # Recalculs des valeurs à l'hectare selon les paramètres stables dans le temps.
                            bmp_Acct <-
                              left_join(IdArbres, ValArbres, by = "IdArbre") %>%
                              set_up_calcul_tables(CodeEssence,
                                                   EssReg,
                                                   cycles_inv = NULL,
                                                   cycles_admin = NULL,
                                                   Tarifs) %>%
                              filter(!is.na(Essence) &
                                       !is.na(Azimut) &
                                       !is.na(Dist)) %>% # on ne prend que les arbres repérés
                              mutate(Coupe = as.character(Coupe),
                                     echant_ID = paste0(NumDisp, "-", Cycle)) %>%
                              # on ne sélectionne que les arbres concernés par le changement de protocole
                              right_join(echant_DF[, c("NumDisp",
                                                       "Cycle",
                                                       "DiamLim",
                                                       "Rayon",
                                                       "Coeff",
                                                       "echant_ID")],
                                         by = c("NumDisp", "Cycle", "echant_ID" = "echant_ID")) %>%
                              # filtre sur la population de précomptables
                              filter(!is.na(Type))
                            
                            # Calculs d'accroissement avec le nouveau protocole
                            bmp_Acct2 <-
                              bmp_Acct %>% calculs_Arbres(echant_change = T)
                            
                            # repérage des cycles concernés par le changement de protocole
                            # cycle_INI <- min(echant_DF$Cycle)
                            # cycle_FIN <- max(echant_DF$Cycle)
                            
                            # recalcul des accroissements
                            bmp_Acct3 <-
                              bmp_Acct2 %>%
                              calculs_acct_bmp(last_cycle, Cycles, echant_change = T)
                            bmp_Acct3 <-
                              bmp_Acct3 %>%
                              group_by(NumDisp) %>%
                              mutate(echant_ID = min(Cycle)) %>%
                              ungroup()
                            
                            # fusion de l'ancienne tables arbres avec la table bmp_Acct
                            # df1 <- Arbres %>% filter(NumPlac == 1) # debug
                            # df2 <- bmp_Acct3 %>% filter(NumPlac == 1) # debug
                            bmp <-
                              bmp %>%
                              # df1 %>% # debug
                              full_join(
                                bmp_Acct3,
                                # df2, # debug
                                by = c("NumDisp", "NumPlac", "NumArbre", "IdArbre", "Cycle"),
                                suffix = c("", "_changed")
                              ) %>%
                              select(
                                NumDisp,
                                NumPlac,
                                NumArbre,
                                IdArbre,
                                Cycle,
                                Essence,
                                EssReg,
                                EssRegPar,
                                Azimut,
                                Dist,
                                Diam1,
                                Diam2,
                                Diam,
                                Classe,
                                Cat,
                                DiamSup,
                                ClasseSup,
                                VhaSup,
                                TauxV,
                                Nha,
                                Gha,
                                Vha,
                                VhaIFN,
                                Limite,
                                CodeEcolo,
                                Ref_CodeEcolo,
                                Haut,
                                HautV,
                                Type,
                                StadeD,
                                StadeE,
                                Observation,
                                
                                AcctGper,
                                AcctGper_changed,
                                AcctVper,
                                AcctVper_changed,
                                AcctD,
                                #AcctD_changed, # on garde quoi qu'il arrive AcctD initial car contient plus d'infos
                                Coupe,
                                Coupe_changed,
                                
                                # Inter,
                                echant_ID
                              ) %>%
                              # si le cycle est concerné par le changement de protocole alors on prend
                              # les valeurs d'accroissement 'changed'
                              mutate(
                                AcctGper = ifelse(!is.na(echant_ID), AcctGper_changed, AcctGper),
                                AcctVper = ifelse(!is.na(echant_ID), AcctVper_changed, AcctVper)
                              ) %>%
                              group_by(NumDisp, NumPlac, NumArbre, IdArbre, Cycle) %>%
                              # cas de la colonne Coupe :
                              mutate(Coupe_temp = ifelse(Cycle == echant_ID, Coupe_changed, Coupe),
                                     # on récupère les notations "E" ou "C"
                                     Coupe = Coupe_temp) %>%
                              ungroup() %>%
                              mutate(
                                AcctGper_changed = NULL,
                                AcctVper_changed = NULL,
                                Gainper_changed = NULL,
                                Coupe_changed = NULL,
                                Coupe_temp = NULL
                              ) %>%
                              select(-echant_ID) %>%
                              as.data.frame()
                          } # end of cond 'nrow(check_protocol_results$unstable_protocol) > 0'
                          ##### --- 7.3/ BMS > 30 #####
                          # extrait des tables Cycles et CyclesCodes des cycles concernés par
                          # le changement de protocole (s'il existe)
                          echant_DF <-
                            Cycles %>%
                            # select(NumDisp, Cycle, Monitor) %>%
                            left_join(CyclesCodes, by = c("NumDisp", "Cycle")) %>%
                            mutate(Rayon = 20,
                                   # changement pour les BMSsup30
                                   Rayon = ifelse(Monitor == "PFA", 13.8, Rayon))
                          # echant_DF <- change_protocole(echant_DF)
                          check_protocol_results <-
                            check_protocol(echant_DF)
                          
                          if (nrow(check_protocol_results$unstable_protocol) > 0) {
                            # cond 'dim(echant_DF)[1] > length(disp_list)'
                            # doublons
                            # dupl <- duplicated(echant_DF$NumDisp) | duplicated(echant_DF$NumDisp, fromLast = T)
                            # echant_DF <- echant_DF %>% filter(dupl)
                            echant_DF <-
                              check_protocol_results$unstable_protocol %>%
                              mutate(echant_ID = paste0(NumDisp, "-", Cycle))
                            
                            # Recalculs des valeurs à l'hectare selon les paramètres stables dans le temps.
                            bms_sup30_acct <-
                              BMSsup30 %>%
                              set_up_calcul_tables(CodeEssence,
                                                   EssReg) %>%
                              filter(!is.na(NumDisp) &
                                       !is.na(NumPlac) &
                                       !is.na(Id) &
                                       !is.na(Cycle)) %>% # on ne prend que les arbres repérés
                              mutate(Coupe = NA,
                                     echant_ID = paste0(NumDisp, "-", Cycle)) %>%
                              # on ne sélectionne que les arbres concernés par le changement de protocole
                              right_join(echant_DF[, c("NumDisp",
                                                       "Cycle",
                                                       "DiamLim",
                                                       "Rayon",
                                                       "Coeff",
                                                       "echant_ID")],
                                         by = c("NumDisp", "Cycle", "echant_ID" = "echant_ID"))
                            
                            # Calculs d'accroissement avec le nouveau protocole
                            bms_sup30_acct2 <-
                              calculs_bms_sup30(bms_sup30_acct, echant_change = T)
                            
                            # repérage des cycles concernés par le changement de protocole
                            # cycle_INI <- min(echant_DF$Cycle)
                            # cycle_FIN <- max(echant_DF$Cycle)
                            
                            # recalcul des accroissements
                            bms_sup30_acct3 <-
                              bms_sup30_acct2 %>%
                              calculs_acct_bms(last_cycle, Cycles, echant_change = T)
                            bms_sup30_acct3 <-
                              bms_sup30_acct3 %>%
                              group_by(NumDisp) %>%
                              mutate(echant_ID = min(Cycle)) %>%
                              ungroup()
                            
                            # fusion de l'ancienne tables arbres avec la table Arbres_Acct
                            # df1 <- Arbres %>% filter(NumPlac == 1) # debug
                            # df2 <- Arbres_Acct3 %>% filter(NumPlac == 1) # debug
                            bms_sup30 <-
                              bms_sup30 %>%
                              # df1 %>% # debug
                              full_join(
                                bms_sup30_acct3,
                                # df2, # debug
                                by = c("NumDisp", "NumPlac", "Id", "Cycle"),
                                suffix = c("", "_changed")
                              ) %>%
                              select(
                                NumDisp,
                                NumPlac,
                                Id,
                                Cycle,
                                Essence,
                                EssReg,
                                EssRegPar,
                                DiamIni,
                                DiamMed,
                                DiamFin,
                                Classe,
                                Cat,
                                Vha,
                                StadeD,
                                StadeE,
                                
                                AcctVper,
                                AcctVper_changed,
                                AcctD,
                                #AcctD_changed, # on garde quoi qu'il arrive AcctD initial car contient plus d'infos
                                Coupe,
                                Coupe_changed,
                                
                                # Inter,
                                echant_ID
                              ) %>%
                              # si le cycle est concerné par le changement de protocole alors on prend
                              # les valeurs d'accroissement 'changed'
                              mutate(AcctVper = ifelse(!is.na(echant_ID), AcctVper_changed, AcctVper)) %>%
                              group_by(NumDisp, NumPlac, Id, Cycle) %>%
                              # cas de la colonne Coupe :
                              mutate(Coupe_temp = ifelse(Cycle == echant_ID, Coupe_changed, Coupe),
                                     # on récupère les notations "E" ou "C"
                                     Coupe = Coupe_temp) %>%
                              ungroup() %>%
                              mutate(
                                AcctVper_changed = NULL,
                                Coupe_changed = NULL,
                                Coupe_temp = NULL
                              ) %>%
                              as.data.frame()
                          } # end of 'nrow(check_protocol_results$unstable_protocol) > 0'
                          #####
                          
                          ##### 8/ Mise en forme des tables d'accroissement #####
                          # if (DernierCycle > 1) {
                          # # ----- Arbres vivants
                          # AcctD_savfin <-
                          # AcctD_sav %>%
                          # melt(id = c("IdArbre", "NumDisp", "NumPlac", "NumArbre", "Essence")) %>%
                          # mutate(
                          # Cycle = str_sub(variable, str_locate(variable, "_")[, 2] + 1, -1),
                          # Cycle = as.numeric(Cycle),
                          # variable = str_sub(variable, 1, str_locate(variable, "_")[, 1] - 1)
                          # ) %>%
                          # dcast(IdArbre + NumDisp + NumPlac + NumArbre + Essence + Cycle ~ variable) %>%
                          # filter(!is.na(Diam)) %>%
                          # select(IdArbre, NumDisp, NumPlac, NumArbre, Essence, Classe, Cycle, AcctD) %>%
                          # mutate(
                          # Classe = as.numeric(Classe),
                          # Population = "BV"
                          # )
                          # # ----- BMP
                          # AcctD_BM_savfin <-
                          # AcctD_BM_sav %>%
                          # melt(id = c("IdArbre", "NumDisp", "NumPlac", "NumArbre", "Essence")) %>%
                          # mutate(
                          # Cycle = str_sub(variable, str_locate(variable, "_")[, 2] + 1, -1),
                          # Cycle = as.numeric(Cycle),
                          # variable = str_sub(variable, 1, str_locate(variable, "_")[, 1] - 1)
                          # ) %>%
                          # dcast(IdArbre + NumDisp + NumPlac + NumArbre + Essence + Cycle ~ variable) %>%
                          # filter(!is.na(Diam)) %>%
                          # select(IdArbre, NumDisp, NumPlac, NumArbre, Essence, Classe, Cycle, AcctD) %>%
                          # mutate(
                          # Classe = as.numeric(Classe),
                          # Population = "BMP"
                          # )
                          # # ----- BMSsup30
                          # AcctD_BMS_savfin <-
                          # AcctD_BMS_sav %>%
                          # melt(id = c("NumDisp", "NumPlac", "Id", "Essence")) %>%
                          # mutate(
                          # Cycle = str_sub(variable, str_locate(variable, "_")[, 2] + 1, -1),
                          # Cycle = as.numeric(Cycle),
                          # variable = str_sub(variable, 1, str_locate(variable, "_")[, 1] - 1)
                          # ) %>%
                          # dcast(NumDisp + NumPlac + Id + Essence + Cycle ~ variable) %>%
                          # filter(!is.na(DiamMed)) %>%
                          # select(NumDisp, NumPlac, Id, Essence, Classe, Cycle, AcctD) %>%
                          # mutate(
                          # Classe = as.numeric(Classe),
                          # Population = "BMSsup30"
                          # )
                          # }
                          ##### / \ #####
                          
                          
                          ##### 9/ dendromicohabitats #####
                          # Vérifier que Arbres existe et contient les colonnes nécessaires
                          if (exists("Arbres") && "CodeEcolo" %in% names(Arbres)) {
                            print("Création de la variable Codes à partir de Arbres")
                            # Remplacer les NA et "" par des valeurs par défaut pour CodeEcolo
                            Arbres_safe <- Arbres
                            Arbres_safe$CodeEcolo <- ifelse(is.na(Arbres_safe$CodeEcolo) | Arbres_safe$CodeEcolo == "", 
                                                           "DEFAUT", Arbres_safe$CodeEcolo)
                            # Correction pour Ref_CodeEcolo si elle n'existe pas
                            if (!"Ref_CodeEcolo" %in% names(Arbres_safe)) {
                              Arbres_safe$Ref_CodeEcolo <- "DEFAUT"
                            }
                            
                            Codes <-
                              Arbres_safe %>%
                              filter(
                                !is.na(NumDisp) & !is.na(NumPlac) &
                                !is.na(NumArbre)
                              ) %>%
                              mutate(
                                Ref_CodeEcolo = tolower(Ref_CodeEcolo)
                                )
                          } else {
                            print("ATTENTION: La variable Arbres n'existe pas ou ne contient pas CodeEcolo. Création d'un dataframe Codes vide.")
                            Codes <- data.frame(
                              NumDisp = numeric(0),
                              NumPlac = character(0),
                              NumArbre = numeric(0),
                              Cycle = numeric(0),
                              Essence = character(0),
                              EssReg = character(0),
                              EssRegPar = character(0),
                              Classe = numeric(0),
                              Cat = character(0),
                              CodeEcolo = character(0),
                              CodeSanit = character(0),
                              Nha = numeric(0),
                              Gha = numeric(0),
                              Vha = numeric(0),
                              VhaIFN = numeric(0)
                            )
                          }
                          
                          # Traitement des dendromicohabitats
                          print("Calculs des dendromicohabitats")
                          dmh_results <- NULL
                          if (exists("Codes") && nrow(Codes) > 0 && exists("CodeEcologie")) {
                            dmh_results <- try(calculs_dmh(df = Codes, dmh_df = CodeEcologie), silent = TRUE)
                            if (inherits(dmh_results, "try-error")) {
                              print("ATTENTION: Erreur lors du calcul des dendromicohabitats")
                              print(dmh_results)
                            }
                          } else {
                            print("ATTENTION: Pas de données pour calculer les dendromicohabitats")
                          }
                          
                          ##### / \ #####
                              
                              
                              ##### 10/ Sauvegarde #####
                              # -- Distinction Arbres, Perches et Taillis
                              Taillis <-
                                Perches %>%
                                rbind(Arbres) %>%
                                filter(Taillis == "t")
                              Arbres <-
                                Arbres %>% filter(Taillis != "t")
                              Perches <-
                                Perches %>% filter(Taillis != "t")
                              
                              # -- Enregistrement
                              BMP <- bmp
                              BMSsup30 <- bms_sup30
                              # tables_to_save <- c(
                              # "Arbres", "Perches", "Taillis",
                              # "BMP", "BMSLineaires", "BMSsup30",
                              # "Reges", "Codes"
                              # )
                              # if (last_cycle == 1) tables_to_save <- setdiff(tables_to_save, "AcctD")
                              
                              # -- tables d'accroissements
                              if (last_cycle < 2) {
                                acct_bv <- data.frame(
                                  IdArbre = integer(),
                                  NumDisp = numeric(),
                                  NumPlac = character(),
                                  NumArbre = numeric(),
                                  Cycle = numeric(),
                                  Essence = character(),
                                  EssReg = character(),
                                  Classe = numeric(),
                                  Cat = character(),
                                  Taillis = character(),
                                  Acct_Diam = numeric(),
                                  AcctGper = numeric(),
                                  AcctVper = numeric(),
                                  Population = character()
                                )
                                acct_bmp <- data.frame(
                                  IdArbre = integer(),
                                  NumDisp = numeric(),
                                  NumPlac = character(),
                                  NumArbre = numeric(),
                                  Cycle = numeric(),
                                  Essence = character(),
                                  EssReg = character(),
                                  Classe = numeric(),
                                  Cat = character(),
                                  Taillis = character(),
                                  Acct_Diam = numeric(),
                                  AcctGper = numeric(),
                                  AcctVper = numeric(),
                                  Population = character()
                                )
                                acct_bms <- data.frame(
                                  Id = character(),
                                  NumDisp = numeric(),
                                  NumPlac = character(),
                                  NumArbre = numeric(),
                                  Cycle = numeric(),
                                  Essence = character(),
                                  EssReg = character(),
                                  Classe = numeric(),
                                  Cat = character(),
                                  Taillis = character(),
                                  AcctD = numeric(),
                                  AcctVper = numeric(),
                                  Population = character()
                                )
                              } else {
                                acct_bv <-
                                  acct_bv %>%
                                  rename(AcctD = Acct_Diam) %>%
                                  mutate(Population = "BV") %>%
                                  select(
                                    IdArbre,
                                    NumDisp,
                                    NumPlac,
                                    NumArbre,
                                    Cycle,
                                    Essence,
                                    EssReg,
                                    Classe,
                                    Cat,
                                    Taillis,
                                    AcctD,
                                    AcctGper,
                                    AcctVper,
                                    Population
                                  )
                                acct_bmp <-
                                  acct_bmp %>%
                                  rename(AcctD = Acct_Diam) %>%
                                  mutate(Population = "BMP") %>%
                                  select(
                                    IdArbre,
                                    NumDisp,
                                    NumPlac,
                                    NumArbre,
                                    Cycle,
                                    Essence,
                                    EssReg,
                                    Classe,
                                    Cat,
                                    Taillis,
                                    AcctD,
                                    AcctGper,
                                    AcctVper,
                                    Population
                                  )
                                acct_bms <-
                                  acct_bms %>%
                                  rename(AcctD = Acct_Diam) %>%
                                  mutate(Population = "BMSsup30") %>%
                                  select(
                                    Id,
                                    NumDisp,
                                    NumPlac,
                                    NumArbre,
                                    Cycle,
                                    Essence,
                                    EssReg,
                                    Classe,
                                    Cat,
                                    AcctD,
                                    AcctVper,
                                    Population
                                  )
                              }
                              
                              # -- sauvegarde
                              # # -- sauvegarde
                              file = file.path(repPSDRF, "tables", "psdrfTablesBrutes.Rdata")
                              
                              # Vérification que Codes existe, sinon le créer comme data frame vide
                              if (!exists("Codes") || is.null(Codes)) {
                                Codes <- data.frame(
                                  NumDisp = numeric(0),
                                  NumPlac = character(0),
                                  NumArbre = numeric(0),
                                  Cycle = numeric(0),
                                  Essence = character(0),
                                  EssReg = character(0),
                                  EssRegPar = character(0),
                                  Classe = numeric(0),
                                  Cat = character(0),
                                  CodeEcolo = character(0),
                                  CodeSanit = character(0),
                                  Nha = numeric(0),
                                  Gha = numeric(0),
                                  Vha = numeric(0),
                                  VhaIFN = numeric(0)
                                )
                              }
                              
                              save(
                                Arbres,
                                Perches,
                                Taillis,
                                BMP,
                                BMSLineaires,
                                BMSsup30,
                                Reges,
                                Codes,
                                acct_bv,
                                acct_bmp,
                                acct_bms,
                                file = file
                              )
                              ##### / \ #####
                              
                              
                              }
