#!/bin/bash
# Script bash pour l'installation de paquets Linux

# Linux
sudo apt install libudunits2-dev
sudo apt-get install texlive-latex-extra

# Voir si les 2 packages suivant sont nécessaires (Très lourds)
# sudo apt-get install texlive-latex-base
# sudo apt-get install texlive-full

cd /home/geonatureadmin/geonature/backend/
source venv/bin/activate
# Packages Python
pip install -r /home/geonatureadmin/gn_module_psdrf/requirements.txt

# Packages R
sudo su - -c "R -e \"install.packages('stringr')\""
sudo su - -c "R -e \"install.packages('openxlsx')\""
sudo su - -c "R -e \"install.packages('rmarkdown')\""
sudo su - -c "R -e \"install.packages('tools')\""
sudo su - -c "R -e \"install.packages('')\""
sudo su - -c "R -e \"install.packages('tidyr')\""
sudo su - -c "R -e \"install.packages('dplyr')\""
sudo su - -c "R -e \"install.packages('gWidgets2')\""
sudo su - -c "R -e \"install.packages('knitr')\""
sudo su - -c "R -e \"install.packages('maptools')\""
sudo su - -c "R -e \"install.packages('xtable')\""
sudo su - -c "R -e \"install.packages('ggplot2')\""
sudo su - -c "R -e \"install.packages('ggrepel')\""
sudo su - -c "R -e \"install.packages('ggthemes')\""
sudo su - -c "R -e \"install.packages('scales')\""
sudo su - -c "R -e \"install.packages('gridExtra')\""
sudo su - -c "R -e \"install.packages('rgeos')\""
sudo su - -c "R -e \"install.packages('rgdal')\""
sudo su - -c "R -e \"install.packages('gdata')\""
sudo su - -c "R -e \"install.packages('grid')\""
sudo su - -c "R -e \"install.packages('fmsb')\""
sudo su - -c "R -e \"install.packages('rlang')\""
sudo su - -c "R -e \"install.packages('tcltk')\""
sudo su - -c "R -e \"install.packages('reshape2')\""
sudo su - -c "R -e \"install.packages('sf')\""
sudo su - -c "R -e \"install.packages('sf')\""
sudo su - -c "R -e \"install.packages('ggmap')\""
sudo su - -c "R -e \"install.packages('dichromat')\""
sudo su - -c "R -e \"install.packages('stringi')\""
sudo su - -c "R -e \"install.packages('gtools')\""
sudo su - -c "R -e \"install.packages('broom')\""
sudo su - -c "R -e \"install.packages('gtable')\""
  
geonature update_configuration

deactivate