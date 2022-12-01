#' Edition des fichiers plans d'arbres relevés sur la placette.
#' @description La fonction édite les plans d'arbres par placettes (PDF) pour chaque dispositif retenu.
#'
#' @param repPSDRF = répertoire de travail
#'
#' @author Bruciamacchie Max, Demets Valentin
#' 
#' @importFrom stringr str_sub
#' @importFrom stringr str_locate
#' @importFrom stringr str_replace_all
#' @importFrom knitr knit2pdf
#' 
#' @export

psdrf_EditPlansArbres <- function(
  repPSDRF = NULL, dispId, last_cycle, dispName, results_by_plot_to_get, continue = T, 
  template = "psdrf_PlanArbres.Rnw"
  ) {

  # -- définition nulle des variables utilisées
  objects <- 
    c("Dispositifs", "IdArbres", "nom1", "Nom1", "ValArbres")
  create_null(objects)
  
  ##### 1/ Initialisation #####
  # -- choix du répertoire de travail
  setwd(repPSDRF)
  
  # -- gestion des archives


  
  # -- chargement des données dans un nouvel environnement
  load("tables/psdrfDonneesBrutes.Rdata")
  load("tables/psdrfCodes.Rdata")  

  disp_name <- dispName
 
  ##### 2/ Edition des plans d'arbres #####
  # for (disp in disp_list) {
    
  # with(db, {
    # # -- gestion des noms et num du dispositif
    disp_num <- dispId
    disp_disp_name <- dispName
    disp = paste0(disp_num,"-",dispName)

    # -- arguments relatifs au dispositifs
    last_cycle <- 
      with(Cycles, max(Cycle[NumDisp == disp_num], na.rm = T))
    ending_year <-
      with(CyclesCodes, DateFin[NumDisp == disp_num & Cycle == last_cycle])
    
    if (length(ending_year) > 1) {
      stop("Correction du classeur administrateur nécessaire : il y a 2 années identiques renseignées dans la feuille Cycles")
    }
    
    # -- création du dossier de sortie
    output_dir <- file.path("out", "remesures/plans_arbres")
    dir.create(output_dir, showWarnings = F, recursive = T)
    
    # -- définition des arguments nécessaires au knit
    repOut <- file.path(repPSDRF, "out/")
    repPlansArbres <- file.path(repOut, "remesures/plans_arbres/")
    repPlansArbresFigures <- file.path(repPlansArbres, "figures/")
    dir.create(repPlansArbresFigures, showWarnings = F, recursive = T)


    # -- superassignements
    # nom de la sortie en .tex
    output_filename <-
      paste0(disp_num, "_plans_arbres_",  ending_year, ".tex")

    output <<- file.path(repPlansArbres, output_filename)

  # -- édition des plans arbres
  knit2pdf(
    input = paste0("template/", template),
    output = output,
    compiler = "pdflatex", 
    # quiet = TRUE,
  )
  # clean_after_knit(output)
}
