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
  tmp <- table %>% filter(variable %in% group_name)
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


##### fonction pour construire les tables nécessaires à l'édition du carnet #####
build_tables <- function(
  results_by_plot_to_get, dispId, last_cycle, 
  psdrfTablesBrutes, disp, plot_table = NULL,
  repPSDRF = NULL, repSav = NULL
) {
  
  # psdrf_AgregArbres call
  # (pour le dispositif en cours d'analyse uniquement)
  TabPla = psdrf_AgregArbres(
    repPSDRF, dispId, last_cycle,
    results_by_plot_to_get
    )
  
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
