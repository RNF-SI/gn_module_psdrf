# Installs required packages in R

packages <- c("doBy","stringr","tcltk","openxlsx","rmarkdown","tools","dplyr",
         "gWidgets2","gWidgets2tcltk","reshape2","rgdal",
         "ggplot2","grid","tidyr","xtable","rgeos","gridExtra",
         "ggmap","ggsn","scales","broom","ggthemes","rlang","knitr")

repos <- "https://mirror.ibcp.fr/pub/CRAN/"

install.packages(packages, repos=repos)

# TODO: install PSDRF package