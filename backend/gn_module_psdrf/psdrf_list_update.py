from math import isnan
import rpy2
import rpy2.robjects as robjects
from rpy2.robjects.packages import STAP
import pandas as pd
from geonature.utils.env import DB
from .models import TCycles
import datetime

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
    pd.read_excel(open("/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/psdrf_liste/PsdrfListes.xlsx", 'rb'), sheet_name='Cycles').to_pickle("/home/geonatureadmin/gn_module_psdrf/data/CyclesCodes") 

    df = pd.read_excel(open("/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/psdrf_liste/PsdrfListes.xlsx", 'rb'), sheet_name='Cycles')
    for index, row in df.iterrows():
        add_cycle(row)

    psdrf_Codes.psdrf_Codes('/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/')



def add_cycle(row):
    """
    Add new cycle to db if it doesn't exist, update it if it does
    """
    
    try:
        # Check if primary key exists already in table
        cycleDispList = DB.session.query(TCycles).filter(TCycles.id_dispositif == row["NumDisp"])
        dup_cycleDispList = cycleDispList.first()
        cycleList = DB.session.query(TCycles).filter((TCycles.id_dispositif == row["NumDisp"]) & (TCycles.num_cycle == row["Cycle"]))
        dup_cycleList = cycleList.first()
        if dup_cycleList:
            # Si le le disp a ce cycle est déjà en bdd, update des valeurs
            cycleList.update(
                {
                    v: (row[k] 
                    if k not in ['DateIni', 'DateFin'] 
                    else (None if isnan(row[k]) else (datetime.date(int(row[k]), 12, 31) if k=='DateFin' else datetime.date(int(row[k]), 1, 1))))
                    for k, v in {'NumDisp': 'id_dispositif', 'Cycle': 'num_cycle', 'Monitor': 'monitor', 'DateIni': 'date_debut', 'DateFin': 'date_fin'}.items()
                    if k in row.index 
                }

            )
        elif dup_cycleDispList:
            # Si le le disp existe mais pas à ce cycle, création de la valeur
            new_cycle =TCycles(
                **{
                    v: (row[k] 
                    if k not in ['DateIni', 'DateFin'] 
                    else (None if isnan(row[k]) else (datetime.date(int(row[k]), 12, 31) if k=='DateFin' else datetime.date(int(row[k]), 1, 1))))
                    for k, v in {'NumDisp': 'id_dispositif', 'Cycle': 'num_cycle', 'Monitor': 'monitor', 'DateIni': 'date_debut', 'DateFin': 'date_fin'}.items()
                    if k in row.index 
                }
            )    
            DB.session.add(new_cycle)  # Add current row
        DB.session.commit()
    except Exception as e:
        # Rollback and print error
        DB.session.rollback()
        print(e)