from math import isnan
import rpy2
import rpy2.robjects as robjects
from rpy2.robjects.packages import STAP
import pandas as pd
from geonature.utils.env import DB
from .models import TCycles, TDispositifs
import datetime
import os

# from werkzeug import FileStorage

def psdrf_list_update(psdrf_list_file):

    with open('/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/psdrf_Codes.R', 'r') as f:
        string = f.read()
    psdrf_Codes = STAP(string, "psdrf_Codes")


    psdrf_list_file.save("/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/psdrf_liste/PsdrfListes.xlsx")
    
    excel_file_path = "/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/psdrf_liste/PsdrfListes.xlsx"
    
    sheet_names = ['CodeDurete', 'CodeEcologie', 'CodeEcorce', 'CodeEssence', 'CodeTypoArbres',
                   'Communes', 'Dispositifs', 'EssReg', 'Referents', 'Tarifs', 'Cycles']
    
    for sheet_name in sheet_names:
        df = pd.read_excel(open(excel_file_path, 'rb'), sheet_name=sheet_name)
        csv_file_path = os.path.join("/home/geonatureadmin/gn_module_psdrf/data", f"{sheet_name}.csv")
        df.to_csv(csv_file_path, index=False) 

    df = pd.read_excel(open("/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/psdrf_liste/PsdrfListes.xlsx", 'rb'), sheet_name='Cycles')
    for index, row in df.iterrows():
        add_dispositif(row)
        add_cycle(row)

    psdrf_Codes.psdrf_Codes('/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/')


def add_dispositif(row):
    """
    Add new dispositif to db if it doesn't exist, update it if it does
    """
    try:
        # Check if primary key exists already in table
        dispList = DB.session.query(TDispositifs.id_dispositif, TDispositifs.name).filter(TDispositifs.id_dispositif == row["NumDisp"])
        dup_dispList = dispList.first()
        if dup_dispList:
            # # Si le disp est déjà en bdd, update des valeurs
            dispList.update(
                {
                    TDispositifs.name: row["Nom"],
                }
            )
            DB.session.commit()
        else:
            # Si le disp n'est pas en bdd, ajout du nouveau
            new_disp = TDispositifs(
                id_dispositif=row["NumDisp"],
                name=row["Nom"],
                id_organisme=-1,
                alluvial=False
            )
            DB.session.add(new_disp)
            DB.session.commit()
    except Exception as e:
        DB.session.rollback()
        raise e

def add_cycle(row):
    """
    Add new cycle to db if it doesn't exist, update it if it does
    """
    print('a')
    try:
        # Check if primary key exists already in table
        cycleList = DB.session.query(TCycles).filter((TCycles.id_dispositif == row["NumDisp"]) & (TCycles.num_cycle == row["Cycle"]))
        dup_cycleList = cycleList.first()

        if dup_cycleList:
            # Si le disp a ce cycle est déjà en bdd, update des valeurs
            cycleList.update(
                {
                    v: (row[k] 
                    if k not in ['DateIni', 'DateFin'] 
                    else (None if isnan(row[k]) else (datetime.date(int(row[k]), 12, 31) if k=='DateFin' else datetime.date(int(row[k]), 1, 1))))
                    for k, v in {'NumDisp': 'id_dispositif', 'Cycle': 'num_cycle', 'Monitor': 'monitor', 'DateIni': 'date_debut', 'DateFin': 'date_fin'}.items()
                    if k in row.index 
                }

            )
        else:
            # Si le cycle n'est pas présent en bdd l'ajouter
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