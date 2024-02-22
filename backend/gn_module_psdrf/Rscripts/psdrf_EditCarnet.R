##### fonction de création d'une interface pour le choix des groupes #####
create_choosing_group_ui <- function(
  group_combination = NULL, 
  ui_title = NULL
) {
  # -- define group_list
  group_list <- unique(group_combination$variable)
  
  # -- ui fonts :
  font3 <- c("bold", "forestgreen")
  names(font3) <- c("weight", "color")
  
  # -- create window
  ui <- gwindow(
    title = ui_title, 
    visible = F, width = 300, height = 100
  )
  
  # -- create main group
  main_group <- ggroup(
    container = ui,  
    horizontal = F, 
    use.scrollwindow = T
  )
  main_group_label <- glabel( # TODO : statuer si dispositif par défaut ?
    text = "Ensembles \u00E0 consid\u00E9rer individuellement\n(Dispositif consid\u00E9r\u00E9 par d\u00E9faut) :", 
    container = main_group
  )
  font(main_group_label) <- font3
  
  layout <- glayout(
    homogeneous = FALSE, 
    container = main_group, 
    horizontal = FALSE
  )
  
  # -- création des sous-groupes de l'interface
  # set up
  num <- 1
  ui_elements_list <- c()
  
  # -- dispositif
  # if ("Dispositif" %in% group_list) {
  #   # define group name
  #   group_name <- "Dispositif"
  #   
  #   # create groups
  #   dispositif_groups <- create_group(
  #     layout, group_combination, group_name
  #   )
  #   dispositif_group <- dispositif_groups[[1]]
  #   dispositif_frame <- dispositif_groups[[2]]
  #   
  #   # add in window
  #   layout[num, 1] <- dispositif_group
  #   
  #   # save window elements in list
  #   # ----- create list
  #   dispositif_ui_elements <- list(
  #     dispositif_group,
  #     dispositif_frame
  #     )
  #   names(dispositif_ui_elements) <- c("group", "frame")
  #   # ----- add to main list
  #   ui_elements_list <- 
  #     c(ui_elements_list, list(dispositif_ui_elements))
  #   names(ui_elements_list)[num] <- 
  #     "dispositif_ui_elements"
  #   
  #   # update num
  #   num = num + 1
  # }
  
  # -- strate
  if ("Strate" %in% group_list) {
    # define group name
    group_name <- "Strate"
    
    # create groups
    strate_groups <- create_group(
      layout, group_combination, group_name
    )
    strate_group <- strate_groups[[1]]
    strate_frame <- strate_groups[[2]]
    
    # add in window
    layout[num, 1] <- strate_group
    
    # save window elements in list
    # ----- create list
    strate_ui_elements <- list(
      strate_group,
      strate_frame
    )
    names(strate_ui_elements) <- c("group", "frame")
    # ----- add to main list
    ui_elements_list <- 
      c(ui_elements_list, list(strate_ui_elements))
    names(ui_elements_list)[num] <- 
      "strate_ui_elements"
    
    # update num
    num = num + 1
  }
  
  # -- habitat
  if ("Habitat" %in% group_list) {
    # define group name
    group_name <- "Habitat"
    
    # create groups
    habitat_groups <- create_group(
      layout, group_combination, group_name
    )
    habitat_group <- habitat_groups[[1]]
    habitat_frame <- habitat_groups[[2]]
    
    # add in window
    layout[num, 1] <- habitat_group
    
    # save window elements in list
    # ----- create list
    habitat_ui_elements <- list(
      habitat_group,
      habitat_frame
    )
    names(habitat_ui_elements) <- c("group", "frame")
    # ----- add to main list
    ui_elements_list <- 
      c(ui_elements_list, list(habitat_ui_elements))
    names(ui_elements_list)[num] <- 
      "habitat_ui_elements"
    
    # update num
    num = num + 1
  }
  
  # -- station
  if ("Station" %in% group_list) {
    # define group name
    group_name <- "Station"
    
    # create groups
    station_groups <- create_group(
      layout, group_combination, group_name
    )
    station_group <- station_groups[[1]]
    station_frame <- station_groups[[2]]
    
    # add in window
    layout[num, 1] <- station_group
    
    # save window elements in list
    # ----- create list
    station_ui_elements <- list(
      station_group,
      station_frame
    )
    names(station_ui_elements) <- c("group", "frame")
    # ----- add to main list
    ui_elements_list <- 
      c(ui_elements_list, list(station_ui_elements))
    names(ui_elements_list)[num] <- 
      "station_ui_elements"
    
    # update num
    num = num + 1
  }
  
  # -- typologie
  if ("Typologie" %in% group_list) {
    # define group name
    group_name <- "Typologie"
    
    # create groups
    typologie_groups <- create_group(
      layout, group_combination, group_name
    )
    typologie_group <- typologie_groups[[1]]
    typologie_frame <- typologie_groups[[2]]
    
    # add in window
    layout[num, 1] <- typologie_group
    
    # save window elements in list
    # ----- create list
    typologie_ui_elements <- list(
      typologie_group,
      typologie_frame
    )
    names(typologie_ui_elements) <- c("group", "frame")
    # ----- add to main list
    ui_elements_list <- 
      c(ui_elements_list, list(typologie_ui_elements))
    names(ui_elements_list)[num] <- 
      "typologie_ui_elements"
    
    # update num
    num = num + 1
  }
  
  # -- groupe
  if ("Groupe" %in% group_list) {
    # define group name
    group_name <- "Groupe"
    
    # create groups
    groupe_groups <- create_group(
      layout, group_combination, group_name
    )
    groupe_group <- groupe_groups[[1]]
    groupe_frame <- groupe_groups[[2]]
    
    # add in window
    layout[num, 1] <- groupe_group
    
    # save window elements in list
    # ----- create list
    groupe_ui_elements <- list(
      groupe_group,
      groupe_frame
    )
    names(groupe_ui_elements) <- c("group", "frame")
    # ----- add to main list
    ui_elements_list <- 
      c(ui_elements_list, list(groupe_ui_elements))
    names(ui_elements_list)[num] <- 
      "groupe_ui_elements"
    
    # update num
    num = num + 1
  }
  
  # -- groupe1
  if ("Groupe1" %in% group_list) {
    # define group name
    group_name <- "Groupe1"
    
    # create groups
    groupe1_groups <- create_group(
      layout, group_combination, group_name
    )
    groupe1_group <- groupe1_groups[[1]]
    groupe1_frame <- groupe1_groups[[2]]
    
    # add in window
    layout[num, 1] <- groupe1_group
    
    # save window elements in list
    # ----- create list
    groupe1_ui_elements <- list(
      groupe1_group,
      groupe1_frame
    )
    names(groupe1_ui_elements) <- c("group", "frame")
    # ----- add to main list
    ui_elements_list <- 
      c(ui_elements_list, list(groupe1_ui_elements))
    names(ui_elements_list)[num] <- 
      "groupe1_ui_elements"
    
    # update num
    num = num + 1
  }
  
  # -- groupe2
  if ("Groupe2" %in% group_list) {
    # define group name
    group_name <- "Groupe2"
    
    # create groups
    groupe2_groups <- create_group(
      layout, group_combination, group_name
    )
    groupe2_group <- groupe2_groups[[1]]
    groupe2_frame <- groupe2_groups[[2]]
    
    # add in window
    layout[num, 1] <- groupe2_group
    
    # save window elements in list
    # ----- create list
    groupe2_ui_elements <- list(
      groupe2_group,
      groupe2_frame
    )
    names(groupe2_ui_elements) <- c("group", "frame")
    # ----- add to main list
    ui_elements_list <- 
      c(ui_elements_list, list(groupe2_ui_elements))
    names(ui_elements_list)[num] <- 
      "groupe2_ui_elements"
    
    # update num
    num = num + 1
  }
  
  # -- gestion
  if ("Gestion" %in% group_list) {
    # define group name
    group_name <- "Gestion"
    
    # create groups
    gestion_groups <- create_group(
      layout, group_combination, group_name
    )
    gestion_group <- gestion_groups[[1]]
    gestion_frame <- gestion_groups[[2]]
    
    # add in window
    layout[num, 1] <- gestion_group
    
    # save window elements in list
    # ----- create list
    gestion_ui_elements <- list(
      gestion_group,
      gestion_frame
    )
    names(gestion_ui_elements) <- c("group", "frame")
    # ----- add to main list
    ui_elements_list <- 
      c(ui_elements_list, list(gestion_ui_elements))
    names(ui_elements_list)[num] <- 
      "gestion_ui_elements"
    
    # update num
    num = num + 1
  }
  
  # -- set window visible
  visible(ui) <- TRUE
  
  # -- retour de la fonction create_choosing_group_ui
  # return(dispositif_group) # debug
  return(list(
    ui = ui,
    ui_elements_list = ui_elements_list
  ))
}

##### fonction pour créer les groupes de l'interface #####
create_group <- function(
  layout = NULL, table = NULL, 
  group_name = NULL
) {
  # create group object
  group_group <- ggroup(
    container = layout,  
    horizontal = T
  )
  
  # create and share checkbox
  group_checkbox <- gcheckbox(
    group_name, 
    checked = F, 
    use.togglebutton = F, 
    container = group_group,
    
    handler = function(h, ...) {
      if (class(group_frame) == "GFrame") {
        if (svalue(group_checkbox)) {
          add(group_group, group_frame)
        } 
        if (!svalue(group_checkbox)) {
          delete(group_group, group_frame)
        }
      }
    }
  )
  
  # detect multiple choices
  tmp <- table %>% 
  filter(variable %in% group_name)
  if (group_name != "Dispositif" & dim(tmp)[1] > 0) {
    # -- construction du checkboxgroup
    # frame
    group_frame <- gframe(
      "Choix des caract\u00E9ristiques", 
      container = group_group, 
      horizontal = T
    )
    
    # checkboxgroup
    group_checkboxgroup <- gcheckboxgroup(
      tmp$value, 
      container = group_frame, 
      pos = 1, horizontal = FALSE, visible = T
    )

    # default value - hide frame
    delete(group_group, group_frame)
  } else {
    group_frame <- ""
  }
  
  # retour de la fonction create_group
  return(list(group = group_group, frame = group_frame))
}



#' Edition du carnet PSDRF
#' @description Cette fonction permet d'éditer un rapport d'analyse automatique des données d'inventaire pour les différents dispositifs PSDRF sélectionnés.
#'
#' @return Renvoi un rapport (carnet PSDRF) par dispositif au format pdf (au contenu et à la forme prédéfinis).
#'
#' @param repPSDRF adresse du répertoire de travail.
#' @param continue paramètre permettant de sauter l'étape de calcul (non visible alors) dans l'interface opérateur
#'
#' @details La fonction est incluse dans l'interface de traitement des données.
#' Il est nécessaire de réaliser le calcul des variables par arbres (psdrf_Calculs()) avant de lancer la fonction.
#' Au cours de l'édition du rapport, un certain nombre de fenêtre seront à renseigner.
#' @author Valentin Demets, Bruciamacchie Max
#' @encoding UTF-8
#' @import tcltk
#' @import openxlsx
#' @export

##### fonction pour éditer le livret d'analyse #####
psdrf_EditCarnet <- function(
  repPSDRF = NULL, dispId, last_cycle, dispName, 
  results_by_plot_to_get, Answer_Radar,
  continue = T, template = "psdrf_Carnet_V3.Rnw"
) {
  # -- définition nulle des variables utilisées
  objects <- c(
    "Arbres", "Cycles", "Data", "Dispositifs", "IdArbres", 
    "Livret_INPUT", "Tableaux", "TabPla", "var", "Var1", 
    "Var2", "Var5", "Var6", "Var7"
  )
  create_null(objects)
  
  ##### 1/ Initialisation #####
  # -- Répertoire de travail
  setwd(repPSDRF)
  load("tables/psdrfCodes.Rdata")
  load("tables/psdrfDonneesBrutes.Rdata")
  load("tables/psdrfTablesBrutes.Rdata")
  load("tables/psdrf_tables_livret.Rdata")

    ##### 2/ Préparation des données #####
    # -- gestion des noms et num du dispositif
    disp_num <- dispId
    disp_name <- dispName

    disp = paste0(disp_num,"-",dispName)
    # -- arguments relatifs au dispositifs
    ending_year <-
      with(CyclesCodes, DateFin[NumDisp == disp_num & Cycle == last_cycle])
    
    if (length(ending_year) > 1) {
      stop("Correction du classeur administrateur nécessaire : il y a 2 années identiques renseignées dans la feuille Cycles")
    }

    # -- création du dossier de sortie
    figures_dir <- file.path("out", "figures")

    dir.create(figures_dir, showWarnings = F, recursive = T)
    

    repFigures <- file.path(repPSDRF, figures_dir)
    repLogos <- file.path(repPSDRF, "data/images/logos/")
    repOut <- file.path(repPSDRF, "out/")

    
    # -- superassignements
    # répertoire de sauvegarde pour les tables spécifiques du dispositif
    # repSav <<- dirname(repPdf)
    repSav <<- dirname(file.path(repPSDRF, "tables/"))

    # nom de la sortie en .tex
    output_filename <- paste0(
      "carnet_", clean_names(disp_name), 
      "_", ending_year, ".tex"
    )
    output <<- file.path(repOut, output_filename)

    # -- building tables needed for edition
    tryCatch({
      build_tables(
        results_by_plot_to_get, dispId, last_cycle, 
        disp, Placettes, repPSDRF, repSav
      )
    }, error = function(e) {
      print(paste("Error in build_tables call:", e$message))
    })
  # })
  ##### /\ #####


  ##### 3/ Edition du/des carnets PSDRF #####
  # # TODO : supprimer les messages de joining by
  tryCatch({
    knit2pdf(
      input = file.path("template", template),
      output = output,
      compiler = "pdflatex",
      # quiet = TRUE,
    )
  }, error = function(e) {
    print(paste("Error in knit2pdf call:", e$message))
    print(paste("Error in template:", template))
  })

  Rprof(NULL)
}
##### /\ #####


#' Construction de tables de résultats.
#' @description Cette fonction permet de construire les tables de résultats nécessaires à l'édition des livrets AFI.
#'
#' @return sauvegarde 3 archives dans le sous-dossier 'tables' (du dossier out)
#'
#' @param repAFI répertoire administrateur
#' @param repSav répertoire de sauvegarde du livret
#' @param lang = langue sélectionnée ("FRA" ou "ENG")
#' @param disp_num Numéro du dispositif
#' @param continue argument permettant d'éviter l'étape de calcul des résultats par arbre
#'
#' @author Valentin Demets, Bruciamacchie Max
#' @encoding UTF-8
#' @import tcltk
#' @import openxlsx
#' @export

##### fonction pour construire les tables nécessaires à l'édition du carnet #####
build_tables <- function(
  results_by_plot_to_get, dispId, last_cycle, 
  disp, plot_table = NULL,
  repPSDRF = NULL, repSav = NULL
) {
  # -- results : tree scale
  # Réalisation de l'étape de calcul des variables par arbre
  # mem_before <- mem_used()

  tryCatch({
    psdrf_Calculs(repPSDRF, disp, last_cycle)
  }, error = function(e) {
      print(paste("Error in psdrf_Calculs call:", e$message))
  })
  # mem_after <- mem_used()
  # mem_difference <- mem_after - mem_before
  # print("mem difference :")
  # print(mem_difference)
  # print(mem_before)
  # print(mem_after)

  # -- results : plot scale
  # setup (get "tables_list" via load("tables/psdrf_tables_livret.Rdata"))
  load("tables/psdrf_tables_livret.Rdata")
  # construction de la table de combinaison des résultats
  results_by_plot_to_get <- build_combination_table(tables_list)

  # psdrf_AgregArbres call
  # (pour le dispositif en cours d'analyse uniquement)
  tryCatch({
    psdrf_AgregArbres(
      repPSDRF, dispId, last_cycle,
      results_by_plot_to_get
      )
  }, error = function(e) {
      print(paste("Error in psdrf_AgregArbres call:", e$message))
  })
  
  # -- results : group scale
  # setup : table listant les ensembles à prendre en compte (individuellement) dans l'agrégation
  # results_by_group_to_get <- build_results_by_group_to_get(
  #   Placettes, disp
  # ) TODO : à revoir pour éviter superassignements (assign ?)
  
  # build results_by_group_to_get & chosen_group_combination
  build_results_by_group(plot_table, disp, last_cycle, repPSDRF, repSav, TabPla)
  
  # -- retour de la fonction build_tables -> cf dossier ../"disp_name"/tables
}
##### /\ #####















##### fonction pour choisir et construire results_by_groups_to_get ####
build_results_by_group <- function(
  plot_table = NULL, disp = NULL, last_cycle = NULL, repPSDRF=NULL, repSav=NULL, TabPla
  ) {

  # -- initialisation
  # parameters
  disp_num <- 
    as.numeric(str_sub(disp, 1, str_locate(disp, "-")[, 1] - 1))
  group_combination <- 
    plot_table %>% 
    filter(NumDisp == disp_num) %>% 
    select(
      NumDisp, Strate, Habitat, Station, Typologie, 
      Groupe, Groupe1, Groupe2, Gestion
    ) %>% 
    rename("Dispositif" = "NumDisp") %>% 
    gather(variable, value) %>% 
    filter(!is.na(value)) %>% 
    mutate(
      variable = factor(
        variable, 
        levels = c(
          "Dispositif", "Strate", "Habitat", "Station", "Typologie", 
          "Groupe", "Groupe1", "Groupe2", "Gestion"
        )
      ),
      call = tolower(variable)
    ) %>% 
    arrange(variable, call, value) %>% 
    distinct()
  # group_list <- unique(group_combination$variable)
  ui_title <- "Choix des agr\u00E9gations par ensembles :"
  

  # # -- choice to make
  # answ <- 
  #   if (dim(group_combination)[1] > 1) {
  #     tk_messageBox(
  #       type = "yesno", 
  #       message = paste0(
  #         "Des ensembles sont renseign\u00E9s dans la table Placettes :\n\n", 
  #         paste0(
  #           unique(group_combination$variable) , 
  #           collapse = ", "
  #         ), 
  #         ".\n\nUtiliser ces ensembles pour r\u00E9aliser l'analyse ?"
  #       ), 
  #       caption = "Ensembles d'analyse d\u00E9tect\u00E9s"
  #     )
  #   } else {
  #     "no"
  #   }

answ = "no"
  
if (answ == "yes") { # TODO : à terminer
  done <- tclVar(0)
  
  # ----- Analyse par ensembles souhaitée. Lancer Agreg_Arbres et AgregPlacettes dans ce sens.
  get_choosing_group_ui <- create_choosing_group_ui(
    group_combination, ui_title
  )
  ui <- get_choosing_group_ui[[1]]
  ui_elements_list <- get_choosing_group_ui[[2]]
  
  ##### ok button #####
  button <- gbutton(
    text = "Ok", container = ui$children[[1]], 
    handler = function(h, ...) {
      # -- set up
      combination_table <- data.frame()
      
      # -- boucle pour récupérer les choix de l'interface
      for (i in 1:length(ui_elements_list)) {
        # print(i) # debug
        # élément
        ui_element <- ui_elements_list[i]
        
        # group choisi ?
        choose_group <- 
          svalue(ui_element[[1]]$group$children[[1]])
        if (choose_group) {
          # get group name
          call_name <- names(ui_element)
          call_name <- str_remove(call_name, "_ui_elements")
          
          # get chosen values
          group_values <- 
            if (call_name != "dispositif") {
              svalue(ui_element[[1]]$frame$children[[1]])
            } else {
              disp_num
            }
          
          # extract group_combination
          tmp <- 
            group_combination %>% 
            filter(
              call == call_name &
                value %in% group_values
            )
          
          # stack chosen group combination
          combination_table <- 
            combination_table %>% rbind(tmp)
        }
      } # end of loop 1:length(a)
      
      # -- superassignements
      # table for knit
      chosen_group_combination <<-
        group_combination %>% 
        filter(variable == "Dispositif") %>% 
        rbind(combination_table) %>% 
        mutate(
          variable = as.character(variable),
          variable = ifelse(
            variable == "Dispositif", "Disp", variable
          )
        ) %>% 
        distinct()
      
      # shape combination table
      results_by_group_to_get <<-
        chosen_group_combination %>% 
        # mutate(
        #   variable = as.character(variable),
        #   variable = ifelse(
        #     variable == "Dispositif", "Disp", variable
        #   )
        # ) %>% 
        distinct(variable) %>% 
        mutate(add_disp_by_default = "Disp") %>% 
        select(add_disp_by_default, variable)
      
      # # security
      # if (dim(chosen_group_combination)[1] == 0) {
      #   stop(
      #     "Aucun ensemble s\u00E9lectionn\u00E9.\nVeuillez choisir un ensemble si analyse par groupe souhaitée" 
      #     )
      # }
      
      group_list <<- unique(chosen_group_combination$variable)
      # psdrf_AgregPlacettes call
      psdrf_AgregPlacettes(
        repPSDRF,
        results_by_group_to_get, 
        repSav, disp, last_cycle
      )
      
      # -- retour de la fonction build_results_by_group_to_get
      # return(list(results_by_group_to_get, chosen_group_combination))
      
      # hide window
      visible(ui) <- FALSE
      
      tclvalue(done) <- 1
    }
  )
  tkwait.variable(done)
  
} else {
  results_by_group_to_get <<- data.frame(
    V1 = "Disp",
    stringsAsFactors = F
  )
  chosen_group_combination <<- data.frame(
      variable = c("Disp"),
      value = disp_num,
      stringsAsFactors = F
    )
  group_list <<- "Disp"
  

  # psdrf_AgregPlacettes call
  psdrf_AgregPlacettes(
    repPSDRF,
    results_by_group_to_get,
    disp, last_cycle #Arguments dispo plus haut dans le script
  )
  # -- retour de la fonction build_results_by_group_to_get
  # return(list(results_by_group_to_get, chosen_group_combination))
} # end of cond answ == "yes"
}
