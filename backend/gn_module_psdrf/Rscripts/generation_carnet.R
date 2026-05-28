

##### --- PSDRF data processing (without ui) --- #####
# library(easypackages)  # fonction libraries() jamais appelée; install CRAN échoue sur R 4.5
library(lubridate)  # gestion des dates

# suppressMessages(
#   packages(
#     "stringr", "openxlsx", "rmarkdown", "tools",
#     "tidyr", "dplyr", "gWidgets2", "gWidgets2tcltk", "knitr", "maptools",
#     "xtable", "ggplot2", "ggrepel", "ggthemes", "scales", "gridExtra",
#     "rgeos", "rgdal", "gdata", "grid", "fmsb", "rlang", "tcltk","reshape2", "sf"
#   )
# )

  # install.packages(c("stringr", "openxlsx", "rmarkdown", "tools",
  # "tidyr", "dplyr", "gWidgets2", "gWidgets2tcltk", "knitr", "maptools",

  # "xtable", "ggplot2", "ggrepel", "ggthemes", "scales", "gridExtra",
  # "rgeos", "rgdal", "gdata", "grid", "fmsb", "rlang", "tcltk","reshape2", "sf", 'doBy'))

library("stringr")
library("openxlsx") 
library("rmarkdown") 
library("tools")
library("tidyr")
library("dplyr") 
library("gWidgets2")
# library("gWidgets2tcltk")
library("knitr")
# library("maptools")  # retiré CRAN 2023-10, non utilisé
library("xtable")
library("ggplot2")
library("ggrepel")
library("ggthemes")
library("scales")
library("gridExtra")
# library("rgeos")  # retiré CRAN 2023-10, non utilisé
# library("rgdal")  # retiré CRAN 2023-10, non utilisé
library("gdata") 
library("grid")
library("fmsb")
library("rlang")
library("tcltk")
library("reshape2")
library("sf")



psdrf_module_root <- Sys.getenv("PSDRF_MODULE_ROOT")
if (!nzchar(psdrf_module_root)) {
  stop("PSDRF_MODULE_ROOT environment variable is not set. It must be exported by the Python caller.")
}
repPSDRF <- file.path(psdrf_module_root, "backend", "gn_module_psdrf", "Rscripts")
setwd(repPSDRF)

source(
  file.path("./psdrf_EditCarnet.R"), 
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



psdrf_EditCarnet(repPSDRF)