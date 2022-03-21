editDocuments <- function(dispId, lastCycle, dispName, placettes, arbres, bms, reges, transects, reperes, cycles, isCarnetToDownload, isPlanDesArbresToDownload){

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

    
    lastCycle = lastCycle[1,1]
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

    # construction de la table de combinaison des résultats
    results_by_plot_to_get <- build_combination_table(tables_list)

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

    if (isCarnetToDownload == 'true'){
        psdrf_EditCarnet(repPSDRF, dispId, lastCycle, dispName, results_by_plot_to_get)
    } 
    if (isPlanDesArbresToDownload == 'true'){
        psdrf_EditPlansArbres(repPSDRF, dispId, lastCycle, dispName, results_by_plot_to_get)
    }
    

}
