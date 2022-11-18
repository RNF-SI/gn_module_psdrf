import rpy2
import rpy2.robjects as robjects
from rpy2.robjects.packages import STAP
import pandas as pd


# from werkzeug import FileStorage

def psdrf_list_update(psdrf_list_file):

    with open('/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/psdrf_Codes.R', 'r') as f:
        string = f.read()
    psdrf_Codes = STAP(string, "psdrf_Codes")

    psdrf_list_file.save("/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/psdrf_liste/PsdrfListes.xlsx")
    pd.read_excel(open("/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/psdrf_liste/PsdrfListes.xlsx", 'rb'), sheet_name='CodeDurete').to_pickle("/home/geonatureadmin/gn_module_psdrf/data/CodeDurete") 
    pd.read_excel(open("/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/psdrf_liste/PsdrfListes.xlsx", 'rb'), sheet_name='CodeEcologie').to_pickle("/home/geonatureadmin/gn_module_psdrf/data/CodeEcologie") 
    pd.read_excel(open("/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/psdrf_liste/PsdrfListes.xlsx", 'rb'), sheet_name='CodeEcorce').to_pickle("/home/geonatureadmin/gn_module_psdrf/data/CodeEcorce") 
    pd.read_excel(open("/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/psdrf_liste/PsdrfListes.xlsx", 'rb'), sheet_name='CodeEssence').to_pickle("/home/geonatureadmin/gn_module_psdrf/data/CodeEssence") 
    pd.read_excel(open("/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/psdrf_liste/PsdrfListes.xlsx", 'rb'), sheet_name='CodeTypoArbres').to_pickle("/home/geonatureadmin/gn_module_psdrf/data/CodeTypoArbres") 
    pd.read_excel(open("/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/psdrf_liste/PsdrfListes.xlsx", 'rb'), sheet_name='Communes').to_pickle("/home/geonatureadmin/gn_module_psdrf/data/Communes") 
    pd.read_excel(open("/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/psdrf_liste/PsdrfListes.xlsx", 'rb'), sheet_name='Dispositifs').to_pickle("/home/geonatureadmin/gn_module_psdrf/data/Dispositifs") 
    pd.read_excel(open("/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/psdrf_liste/PsdrfListes.xlsx", 'rb'), sheet_name='EssReg').to_pickle("/home/geonatureadmin/gn_module_psdrf/data/EssReg") 
    pd.read_excel(open("/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/psdrf_liste/PsdrfListes.xlsx", 'rb'), sheet_name='Referents').to_pickle("/home/geonatureadmin/gn_module_psdrf/data/Referents") 
    pd.read_excel(open("/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/psdrf_liste/PsdrfListes.xlsx", 'rb'), sheet_name='Tarifs').to_pickle("/home/geonatureadmin/gn_module_psdrf/data/Tarifs") 

    

    psdrf_Codes.psdrf_Codes('/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/')

