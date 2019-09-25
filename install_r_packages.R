# Installs required packages in R

packages <- c("doBy","stringr","openxlsx","rmarkdown","tools","dplyr",
         "reshape2","rgdal","ggplot2","grid","tidyr","xtable","rgeos","gridExtra",
         "ggmap","ggsn","scales","broom","ggthemes","rlang","knitr")

repos <- "https://mirror.ibcp.fr/pub/CRAN/"

install.packages(packages, repos=repos)

# TODO: install PSDRF package