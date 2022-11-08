import rpy2
import rpy2.robjects as robjects
from rpy2.robjects.packages import STAP

# from werkzeug import FileStorage

def psdrf_list_update(psdrf_list_file):

    with open('/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/psdrf_Codes.R', 'r') as f:
        string = f.read()
    psdrf_Codes = STAP(string, "psdrf_Codes")
    
    psdrf_list_file.save("/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/psdrf_liste/PsdrfListes.xlsx")

    psdrf_Codes.psdrf_Codes('/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/')

