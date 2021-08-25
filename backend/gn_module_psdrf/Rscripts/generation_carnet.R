

##### --- PSDRF data processing (without ui) --- #####
library(easypackages)
library(lubridate)  # gestion des dates

suppressMessages(
  packages(
    "stringr", "openxlsx", "rmarkdown", "tools",
    "tidyr", "dplyr", "gWidgets2", "gWidgets2tcltk", "knitr", "maptools",
    "xtable", "ggplot2", "ggrepel", "ggthemes", "scales", "gridExtra",
    "rgeos", "rgdal", "gdata", "grid", "fmsb", "rlang", "tcltk","reshape2", "sf"
  )
)

# library("stringr")
# library("openxlsx") 
# library("rmarkdown") 
# library("tools")
# library("tidyr")
# library("dplyr") 
# library("gWidgets2")
# library("gWidgets2tcltk")
# library("knitr")
# library("maptools")
# library("xtable")
# library("ggplot2")
# library("ggrepel") 
# library("ggthemes")
# library("scales")
# library("gridExtra")
# library("rgeos")
# library("rgdal")
# library("gdata") 
# library("grid")
# library("fmsb")
# library("rlang")
# library("tcltk")
# library("reshape2")
# library("sf")



setwd('/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts')

repPSDRF <- '/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts'

source(
  file.path("./psdrf_EditCarnet.R"), 
  encoding = 'UTF-8', echo = TRUE
)

source(
  file.path("./annexes.R"), 
  encoding = 'UTF-8', echo = TRUE
)

psdrf_EditCarnet(repPSDRF)