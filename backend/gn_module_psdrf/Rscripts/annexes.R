##### styles de cellules #####
# -- styles
# titre = ID
style_title_id <- createStyle(
  # police texte
  fontName = "Arial", fontSize = 12, 
  fontColour = "dodgerblue4", textDecoration = "bold", 
  # fond cellule
  fgFill = "tan1", 
  # bordure
  border =  "Bottom", 
  # alignement
  valign = "top", halign = "center", 
  # rotation et wrap
  textRotation = 90, wrapText = F
)
# titre = attributs
style_title_attr <- createStyle(
  # police texte
  fontName = "Arial", fontSize = 12, textDecoration = "bold", 
  # bordure
  border =  "Bottom",
  # fond cellule
  fgFill = "mediumaquamarine", 
  # alignement
  valign = "top", halign = "center", 
  # rotation et wrap
  textRotation = 90, wrapText = F
)
# corps général du texte
style_general <- createStyle(
  # police texte
  fontName = "Arial", fontSize = 12, 
  # alignement
  valign = "center", halign = "center",
  # rotation et wrap
  wrapText = F
)
# anciennes valeurs (déjà présentes au précédent inventaire)
style_former_value <- createStyle(
  # police texte
  fontName = "Arial", fontSize = 12, 
  # fond cellule
  fgFill = "gray90", 
  # alignement
  valign = "center", halign = "center",
  # rotation et wrap
  wrapText = F
)
# nouvelles valeurs (à compléter au nouvel inventaire)
style_new_value <- createStyle(
  # police texte
  fontName = "Arial", fontSize = 12, border =  "Bottom", 
  # alignement
  valign = "center", halign = "center",
  # rotation et wrap
  wrapText = F
)
# ligne de séparation
style_separate_row <- createStyle(
  # bordure
  border = "Bottom"
)

# -- liste des styles
styles_list <- c(
  style_title_id, 
  style_title_attr,
  style_general,
  style_former_value,
  style_new_value
)
names(styles_list) <- c(
  "style_title_id", 
  "style_title_attr",
  "style_general",
  "style_former_value",
  "style_new_value"
)

# -- sauvegarde des styles
# save(styles_list, file = "tables/wb_styles.Rdata")
##### /\ #####

# --------------------------------------------------------------------------------- #




##### SCRIPTS ANNEXES #####


##### fonction pour construire la table des combinaisons de données à obtenir #####
build_combination_table <- function(vecteur = NULL) {
  df <- data.frame(
    var = vecteur,
    stringsAsFactors = F
  ) %>% 
    mutate(
      # populations
      data = ifelse(str_detect(var, "BM"), "BM", NA),
      data = ifelse(str_detect(var, "BMP"), "BMP", data),
      data = ifelse(str_detect(var, "BMS"), "BMS", data),
      data = ifelse(str_detect(var, "Tot"), "Tot", data),
      data = ifelse(str_detect(var, "Fpied"), "Fpied", data),
      data = ifelse(str_detect(var, "Per"), "Per", data),
      data = ifelse(str_detect(var, "Taillis"), "Taillis", data),
      data = ifelse(str_detect(var, "Den"), "Den", data),
      data = ifelse(str_detect(var, "PFutaie"), "PFutaie", data),
      data = ifelse(str_detect(var, "Exploit"), "Exploit", data),
      data = ifelse(str_detect(var, "Codes"), "Codes", data),
      data = ifelse(str_detect(var, "Rege"), "Rege", data),
      
      # essences
      Var1 = ifelse(str_detect(var, "Essence"), "Essence", NA),
      Var1 = ifelse(str_detect(var, "EssReg"), "EssReg", Var1),
      Var1 = ifelse(str_detect(var, "EssRegPar"), "EssRegPar", Var1),
      # diamètre
      Var2 = ifelse(str_detect(var, "Classe"), "Classe", NA),
      Var2 = ifelse(str_detect(var, "Cat"), "Cat", Var2),
      # DMH
      Var3 = ifelse(str_detect(var, "CodeEcolo"), "CodeEcolo", NA),
      # codes sanitaire
      Var4 = ifelse(str_detect(var, "CodeSanit"), "CodeSanit", NA),
      # coupe
      Var5 = ifelse(str_detect(var, "Coupe"), "Coupe", NA),
      # stades bois mort
      Var6 = ifelse(str_detect(var, "StadeD"), "StadeD", NA),
      Var7 = ifelse(str_detect(var, "StadeE"), "StadeE", NA),
      # type de bmp
      Var8 = ifelse(str_detect(var, "Type"), "Type", NA),
      
      var = NULL
    ) %>% 
    filter(!is.na(data)) %>% # sécurité
    distinct()
  
  # retour de la fonction build_combination_table
  return(df)
}
##### /\ #####

##### fonction pour filtrer les tables selon une liste de dispositifs #####
filter_by_disp <- function(
  tables = NULL, 
  disp_list = NULL, 
  cycle = NULL
) {
  # -- liste des numéros de dispositifs
  num_list <- as.numeric( str_sub(disp_list, 1, str_locate(disp_list, "-")[, 1] - 1) )
  
  for (tmp in tables) {
    # print(df) # debug
    # print(class(tmp)) # debug
    # tmp <- tables[[1]] # debug
    
    # cas où tmp est un nom de table
    # -- nom de la table
    tmp_NAME <- tmp
    # print(tmp_NAME) # debug
    # -- data.frame
    tmp <- get(tmp_NAME, envir = parent.frame())
    
    if (class(tmp) == "data.frame") {
      if (dim(tmp)[1] > 0) {
        # -- filtre selon la liste de dispositifs sélectionnés
        tmp <- tmp %>% filter(NumDisp %in% num_list)
        assign(tmp_NAME, tmp, envir = parent.frame())
        
        # -- filtre selon le cycle
        if ("Cycle" %in% names(tmp)) {
          tmp <- tmp %>% filter(Cycle <= cycle) 
          assign(tmp_NAME, tmp, envir = parent.frame())
        }
        
        if (cycle == 1) {
          tmp <- tmp %>% mutate(AcctGper = NULL, AcctVper = NULL, AcctD = NULL)
          assign(tmp_NAME, tmp, envir = parent.frame())
        }
      }
    }
    
    # cas où tmp est une liste
    if (class(tmp) == "list") {
      for (i in 1:length(tmp)) {
        if (dim(tmp[[i]])[1] > 0) {
          # -- filtre selon la liste de dispositifs sélectionnés
          tmp[[i]] <- tmp[[i]] %>% filter(NumDisp %in% num_list)
          
          # -- filtre selon le cycle
          if ("Cycle" %in% names(tmp[[i]])) {
            tmp[[i]] <- tmp[[i]] %>% filter(Cycle <= cycle)
          }
          
          if (cycle == 1) {
            tmp[[i]] <- 
              tmp[[i]] %>% mutate(AcctGper = NULL, AcctVper = NULL, AcctD = NULL)
          }
        }
      } # end of loop length(tmp)
      assign(tmp_NAME, tmp, envir = parent.frame())
    }
  }
  
  # retour de la fonction filter_by_disp
  
}

##### fonction pour choisir le dispositif à traiter #####
choose_disp <- function(
  object_list = df_list, 
  admin = Dispositifs, 
  check_all_msg = NULL,
  df_2_test = NULL
) {
  # -- initialisation
  tmp <- c()
  all_num_list <- c()
  
  # -- boucle
  for (i in 1:length(object_list)) {
    # i = 1 # debug
    tmp <- 
      if (class(object_list) == "list") object_list[[i]] else {
        get(object_list[i], envir = parent.frame())
      }
    
    # cas où tmp est un data.frame
    if (class(tmp) == "data.frame") {
      if ("NumDisp" %in% names(tmp)) {
        tmp <- 
          tmp %>% select(NumDisp) %>% distinct() %>% unlist() %>% unname()
        tmp <- tmp[!tmp %in% all_num_list]
        all_num_list <- c(all_num_list, tmp)
      }
    }
    
    # cas où tmp est une liste (ex : TabPla)
    if (class(tmp) == "list") {
      for (tab in tmp) {
        if ("NumDisp" %in% names(tab)) {
          tab <- 
            tab %>% select(NumDisp) %>% distinct() %>% unlist() %>% unname()
          tab <- tab[!tab %in% all_num_list]
          all_num_list <- c(all_num_list, tab)
        }
      }
    }
  } # end of loop object_list
  all_num_list <- sort( as.numeric( unique(all_num_list) ) )
  
  if (is.element(NA, all_num_list)) warning("NumDisp vide d\u00E9tect\u00E9")
  all_disp_list <- paste0(
    all_num_list, "-", admin$Nom[match(all_num_list, admin$NumDisp)]
  )
  
  # -- choix du dispositif
  disp_list <- tk_select.list(
    choices = c(check_all_msg, as.character(all_disp_list)), 
    multiple = T, 
    title = "Choisir un ou plusieurs dispositifs"
  )
  # -- sortie si aucun choix fait
  if (length(disp_list) == 0) stop("traitement interrompu - aucun dispositif choisi", call. = FALSE)
  if (is.element(check_all_msg, disp_list)) {disp_list = all_disp_list}
  
  if (!is.null(df_2_test)) {
    # test si les numéros de disp_list sont présents dans la table df_2_test
    num_list <-
      as.numeric( str_sub(disp_list, 1, str_locate(disp_list, "-")[, 1] - 1) )
    pos <- which(!num_list %in% df_2_test$NumDisp)
    if (length(pos) > 0) {
      stop(
        "Can't find the chosen stand number(s) '", 
        paste0(num_list[pos], collapse = ", "), 
        "' within the '", substitute(df_2_test), "' table"
      )
    }
  }
  
  # -- retour de la fonction choose_disp
  return(disp_list)
}

##### fonction de nettoyage des noms #####
clean_names <- function(string) {
  # string <- gsub(".", "_", string, fixed = T)
  string <- gsub(" ", "_", string, fixed = T)
  string <- gsub("'", "", string, fixed = T)
  string <- gsub(",", "_", string, fixed = T)
  string <- gsub("\u00EA", "e", string, fixed = T)
  string <- gsub("\u00E2", "a", string, fixed = T)
  string <- gsub("\u00E9", "e", string, fixed = T)
  string <- gsub("\u00E8", "e", string, fixed = T)
  string <- gsub("\u00FB", "u", string, fixed = T)
  string <- gsub("\u00EE", "i", string, fixed = T)
  string <- gsub("\u00F4", "o", string, fixed = T)
  
  # retour de la fonction clean_names
  return(string)
}

##### fonction de nettoyage compilation pdf #####
clean_after_knit <- function(output) {
  file.remove(output)
  if (exists(gsub(".tex", ".aux", output))) file.remove(gsub(".tex", ".aux", output))
  if (exists(gsub(".tex", ".log", output))) file.remove(gsub(".tex", ".log", output))
  if (exists(gsub(".tex", ".out", output))) file.remove(gsub(".tex", ".out", output))
}

##### fonction pour créer des objets nuls (package) #####
create_null <- function(objects_list) {
  for (obj in objects_list) assign(obj, NULL, envir = parent.frame())
}

##### fonction pour choisir obtenir le numéro du dernier passage en inventaire #####
get_last_cycle <- function(object_list, disp_list) {
  # -- initialisation
  tmp <- c()
  all_cycle_list <- c()
  
  # -- liste des numéros de dispositifs
  num_list <- as.numeric( str_sub(disp_list, 1, str_locate(disp_list, "-")[, 1] - 1) )
  
  # -- boucle
  for (i in 1:length(object_list)) {
    # i = 1 # debug
    tmp <- 
      if (class(object_list) == "list") object_list[[i]] else {
        get(object_list[i], envir = parent.frame())
      }
    
    # cas où tmp est un data.frame
    if (class(tmp) == "data.frame") {
      if ("NumDisp" %in% names(tmp) && "Cycle" %in% names(tmp)) {
        tmp <- 
          tmp %>% 
          filter(NumDisp %in% num_list) %>% 
          select(Cycle) %>% 
          distinct() %>% unlist() %>% unname()
        tmp <- tmp[!tmp %in% all_cycle_list]
        all_cycle_list <- c(all_cycle_list, tmp)
      }
    }
    
    # cas où tmp est une liste (ex : TabPla)
    if (class(tmp) == "list") {
      for (i in 1:length(tmp)) {
        tab <- tmp[[i]]
        if ("NumDisp" %in% names(tab) && "Cycle" %in% names(tab)) {
          tab <- 
            tab %>% 
            filter(NumDisp %in% num_list) %>% 
            select(Cycle) %>% 
            distinct() %>% unlist() %>% unname()
          tab <- tab[!tab %in% all_cycle_list]
          all_cycle_list <- c(all_cycle_list, tab)
        }
      }
    }
  }
  all_cycle_list <- sort( as.numeric( unique(all_cycle_list) ) )
  
  # -- numéro du dernier cycle
  last_cycle <- max(all_cycle_list, na.rm = T)
  
  # -- retour de la fonction get_last_cycle
  return(last_cycle)
}


##### /\ #####

# ----------------------- SIG ---------------------------
##### fonction pour tester si résultats par placettes vides #####
test_empty_plot_results <- function(df, var_results, admin) {
  # Sécurité : détection des résultats "vides" dans la table attributaire
  # initialisation
  num <- unique(df$NumDisp)
  empty_values_df <- df %>% select("NumPlac", var_results)
  
  # détection des lignes contenant des valeurs vides
  empty_values_pos <- c()
  for (col in colnames(empty_values_df)) {
    empty_values_pos <- 
      c(empty_values_pos, which(is.na(empty_values_df[, col])) )
  }
  empty_values_pos <- unique(empty_values_pos)
  
  # mise en forme de la liste des placettes contenant des valeurs vides
  empty_values_plot <- with(empty_values_df, unique(NumPlac[empty_values_pos]))
  
  # warnings
  if (length(empty_values_plot) > 0) {
    if (length(empty_values_pos) == 1) {
      warning(
        paste0(
          "Il y a des r\u00E9sultats d'analyse vides pour la placette ", 
          empty_values_plot, 
          " du dispositif ", 
          with(admin, unique(Nom)), 
          " (placette pr\u00E9sente dans le shape initial mais sans r\u00E9sultats placettes au dernier passage)"
        ), 
        call. = FALSE, 
        immediate. = TRUE
      )
    } else {
      if (length(empty_values_plot) > 20) {
        warning(
          paste0(
            "Il y a des r\u00E9sultats d'analyse vides pour les placettes\n", 
            paste0(empty_values_plot[1:20], collapse = ", "), "...", 
            "\ndu dispositif ", 
            with(admin, unique(Nom[NumDisp == num])), 
            " (placettes pr\u00E9sentes dans le shape initial mais sans r\u00E9sultats placettes au dernier passage)"
          ), 
          call. = FALSE, 
          immediate. = TRUE
        )
      } else {
        warning(
          paste0(
            "Il y a des r\u00E9sultats d'analyse vides pour les placettes\n", 
            paste0(empty_values_plot, collapse = ", "), 
            "\ndu dispositif ", 
            with(admin, unique(Nom[NumDisp == num])), 
            " (placettes pr\u00E9sentes dans le shape initial mais sans r\u00E9sultats placettes au dernier passage)"
          ), 
          call. = FALSE, 
          immediate. = TRUE
        )
      }
    }
  }
  
  # retour de la fonction test_empty_plot_results
  return(df)
}

##### fonction pour tester si coordonnées placettes vides #####
test_empty_plot_coords <- function(df, admin) {
  # Sécurité : détection des placettes sans localisation
  # initialisation
  num <- unique(df$NumDisp)
  empty_coords_df <- df
  
  # détection des lignes contenant des valeurs vides
  empty_coords_pos <- which(st_is_empty(df))
  
  # mise en forme de la liste des placettes contenant des valeurs vides
  empty_coords_plot <- with(empty_coords_df, unique(NumPlac[empty_coords_pos]))
  
  # warnings
  if (length(empty_coords_plot) > 0) {
    if (length(empty_coords_plot) == 1) {
      warning(
        paste0(
          "La placette ", 
          empty_coords_plot, 
          " du dispositif ", 
          with(admin, unique(Nom[NumDisp == num])), 
          " n'a pas de coordonnées renseignées dans le shape initial.
          \nLes r\u00E9sultats d'analyse pour cette placette non localis\u00E9e ne figureront pas dans les shapes de r\u00E9sultats."
        ), 
        call. = FALSE, 
        immediate. = TRUE
        )
    } else {
      if (length(empty_coords_plot) > 20) {
        warning(
          paste0(
            "Les placettes :\n", 
            paste0(empty_coords_plot[1:20], collapse = ", "), "...", 
            "\ndu dispositif ", 
            with(admin, unique(Nom[NumDisp == num])), 
            " n'ont pas de coordonnées renseignées dans le shape initial.
            \nLes r\u00E9sultats d'analyse pour les placettes non localis\u00E9es ne figureront pas dans les shapes de r\u00E9sultats."
          ), 
          call. = FALSE, 
          immediate. = TRUE
          )
      } else {
        warning(
          paste0(
            "Les placettes :\n", 
            paste0(empty_coords_plot, collapse = ", "), 
            "\ndu dispositif ", 
            with(admin, unique(Nom[NumDisp == num])), 
            " n'ont pas de coordonnées renseignées dans le shape initial.
            \nLes r\u00E9sultats d'analyse pour les placettes non localis\u00E9es ne figureront pas dans les shapes de r\u00E9sultats."
          ), 
          call. = FALSE, 
          immediate. = TRUE
          )
      }
    }
    # enlève les placettes non localisées
    df <- df %>% filter(NumPlac != empty_coords_plot)
  }
  
  # retour de la fonction test_empty_plot_coords
  return(df)
  }

##### fonction de vérification du sf #####
# contrôle : 1/ présence des colonnes NumDisp et NumPlac
#            2/ valeurs vides dans les colonnes NumDisp et NumPlac
#            3/ coordonnées vides ?
check_sf <- function(sf) {
  # intitulé recherchés par défaut
  NumDisp_label <- "NumDisp"
  NumPlac_label <- "NumPlac"
  
  # ----- 1/ contrôle des colonnes NumDisp et NumPlac -----
  if (!NumDisp_label %in% names(sf)) {
    # intitulé
    title_msg <- paste0(
      str_wrap("L'intitulé de colonne pour les numéros de dispositif n'est pas reconnu dans le fichier", 70), 
      " ", basename(file_path_sans_ext(sf_path)), 
      " ('", NumDisp_label, "' recherché).\n\n               Choisissez l'attribut désignant NumDisp"
    )
    
    # choix
    choices_msg <- 
      names(sf)[!names(sf) %in% c(NumDisp_label, NumPlac_label, "geometry")]
    # sécurité sur les choix
    if (length(choices_msg) == 0) stop("Plus aucun attribut de colonne disponible !")
    
    # fenêtre de dialogue
    NumDisp_label <- tk_select.list( # NumDisp_label : NumDisp0 anciennement
      title = title_msg, 
      choices = choices_msg, 
      multiple = F
    )
  } else if (!NumPlac_label %in% names(sf)) {
    # intitulé
    title_msg <- paste0(
      str_wrap("L'intitulé de colonne pour les numéros de placettes n'est pas reconnu dans le fichier", 70), 
      " ", basename(file_path_sans_ext(sf_path)), 
      " ('", NumPlac_label, "' recherché).\n\n               Choisissez l'attribut désignant NumPlac"
    )
    
    # choix
    choices_msg <- 
      names(sf)[!names(sf) %in% c(NumDisp_label, NumPlac_label, "geometry")]
    # sécurité sur les choix
    if (length(choices_msg) == 0) stop("Plus aucun attribut de colonne disponible !")
    
    # fenêtre de dialogue
    NumPlac_label <- tk_select.list( # NumPlac_label : NumPlac0 anciennement
      title = title_msg, 
      choices = names(sf), 
      multiple = F
    )
  }
  
  sf <- 
    sf %>% 
    select(NumDisp_label, NumPlac_label) %>% 
    rename(
      "NumDisp"= NumDisp_label,
      "NumPlac"= NumPlac_label
    )
  
  # ----- 2/ contrôle de valeurs vides dans les colonnes NumDisp et NumPlac -----
  empty_pos <- with(sf, which(is.na(NumDisp) | is.na(NumPlac)))
  if (length(empty_pos) > 0) {
    stop(
      "Il y a des valeurs (", 
      length(empty_pos),
      ") vides dans les colonnes désignant le(s) numéro(s) de dispositif et les numéros de placettes"
    )
  }
  
  # ----- 3/ contrôle de geometry vides
  empty_pos <- which(st_is_empty(sf))
  if (length(empty_pos) > 0) {
    stop(
      "Il y a des placettes (", 
      length(empty_pos),
      ") non localisées"
    )
  }
  
  # ----- 4/ table finale -----
  sf <- 
    sf %>% 
    mutate(
      NumDisp = as.numeric(NumDisp), 
      NumPlac = as.character(NumPlac)
    )
  
  # retour de la fonction check_sf
  return(sf)
}

##### fonction choix du shape des placettes #####
read_shp <- function() {
  # -- choix des fichiers
  all_sf_path <- tk_choose.files( # sf_list = ListShp anciennement
    caption = "Choix du/des shape(s) des placettes", 
    multi = T, 
    filters = matrix(c("fichier shape", ".shp"), 1, 2, byrow = T)
  )
  # all_sf_path <- file.path(repPSDRF, "data/PSDRF_extract/SIG/Vecteurs/Placettes/Plac_Chalmessin_L93.shp") # debug
  
  # -- lecture des shapes
  all_sf <- c()
  # barre de progression
  pb <- tkProgressBar(
    title = "Progression", 
    label = "Lecture des shapes de placettes en cours... (%)", 
    min = 0, max = 100, width = 500
  )
  for (sf_path in all_sf_path) {
    # chemin d'accès du fichier
    # sf_path <- all_sf_path[1] # debug
    print(
      paste0(
        "Lecture du shape : ", basename(file_path_sans_ext(sf_path))
      )
    )
    sf <- st_read(
      sf_path,
      stringsAsFactors = FALSE, 
      quiet = T
    ) %>% 
      st_transform(crs = 2154) # reprojette en L93
    # TODO : ajouter sécurité sur le système de projection ? -> st_crs
    
    # vérification des colonnes
    sf <- check_sf(sf)
    
    # rassemble les données
    all_sf <- rbind(all_sf, sf)
    info <- round(match(sf_path, all_sf_path) / length(all_sf_path) * 100)
    setTkProgressBar(
      pb, value = info, 
      title = paste0("Lecture (", info, " %)"), 
      label = paste0("Lecture des shapes de placettes en cours : ", info, "% done")
    )
  } # end of all_sf_path loop
  close(pb)
  
  # retour de la fonction read_shp
  return(all_sf)
}