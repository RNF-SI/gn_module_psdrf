from rpy2.robjects import pandas2ri
from rpy2.robjects.conversion import localconverter
import rpy2.robjects as ro
import os, shutil

from sqlalchemy import select
from sqlalchemy.sql.expression import func
import pandas as pd
import rpy2
import rpy2.robjects as robjects
from rpy2.robjects.packages import STAP
from geonature.utils.env import DB

from geonature.core.ref_geo.models import LiMunicipalities, LAreas, BibAreasTypes
from .models import TDispositifs, TPlacettes, TArbres, TCycles, \
    CorCyclesPlacettes, TArbresMesures, TReperes, BibEssences, TRegenerations,\
    TBmSup30,TBmSup30Mesures, TTransects, dispositifs_area_assoc

def data_analysis(dispId, isCarnetToDownload, isPlanDesArbresToDownload, carnetToDownloadParameters):

    # Suppression des fichiers de sortie 
    folder = '/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/out'
    for filename in os.listdir(folder):
        if (filename != ".gitignore") :
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    os.mkdir("/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/out/figures")

    r = robjects.r
    dispNameQuery = DB.session.query(
        TDispositifs.name
        ).filter(
            (TDispositifs.id_dispositif == dispId)
        )
    dispName = pd.read_sql(dispNameQuery.statement, dispNameQuery.session.bind)
    dispName=str(dispName.iloc[0]["name"])

    lastCycleQuery = DB.session.query(
        func.max(TCycles.num_cycle)
        ).filter(
            (TCycles.id_dispositif == dispId)
        )
    lastCycledf = pd.read_sql(lastCycleQuery.statement, lastCycleQuery.session.bind)

    with localconverter(ro.default_converter + pandas2ri.converter):
        r_lastCycle = ro.conversion.py2rpy(lastCycledf)

    formatBdd2RData(r, dispId, r_lastCycle, dispName, isCarnetToDownload, isPlanDesArbresToDownload, carnetToDownloadParameters)

def formatBdd2RData(r, dispId, lastCycle, dispName, isCarnetToDownload, isPlanDesArbresToDownload, carnetToDownloadParameters):
    #### 1/ Rechercher les données dans la base de données
    # ---- Création des Requêtes pour les données des réserves
    arbresQuery = DB.session.query(
        TPlacettes.id_dispositif, TPlacettes.id_placette_orig, 
        TArbres.id_arbre_orig, TArbres.code_essence, TArbres.azimut,
        TArbres.distance, TArbres.taillis,  
        TArbresMesures.diametre1, TArbresMesures.diametre2, 
        TArbresMesures.type, TArbresMesures.hauteur_totale, 
        TArbresMesures.stade_durete, TArbresMesures.stade_ecorce, 
        TArbresMesures.coupe, TArbresMesures.limite, 
        TArbresMesures.code_ecolo, TArbresMesures.ref_code_ecolo, 
        TArbresMesures.id_nomenclature_code_sanitaire, TArbresMesures.hauteur_branche, 
        TArbresMesures.observation, TCycles.num_cycle, 
        ).filter(
            (TPlacettes.id_dispositif == dispId)
        ).join(
            TArbres, TArbres.id_placette == TPlacettes.id_placette
        ).join(
            TArbresMesures
        ).join(
            TCycles, TCycles.id_cycle == TArbresMesures.id_cycle
        )

    bmsQuery = DB.session.query(
        TPlacettes.id_dispositif, TPlacettes.id_placette_orig, TBmSup30, TBmSup30Mesures, TCycles.num_cycle
        ).filter(
            (TPlacettes.id_dispositif == dispId)
        ).join(
            TBmSup30, TBmSup30.id_placette == TPlacettes.id_placette
        ).join(
            TBmSup30Mesures
        ).join(
            TCycles, TCycles.id_cycle == TBmSup30Mesures.id_cycle
        )

    placettesQuery = DB.session.query(
        TPlacettes.id_dispositif, TPlacettes.id_placette_orig, TPlacettes.strate, TPlacettes.poids_placette,
        TPlacettes.pente, TPlacettes.correction_pente, TPlacettes.exposition, TPlacettes.habitat,
        TPlacettes.precision_gps, TPlacettes.station, TPlacettes.typologie, TPlacettes.groupe,
        TPlacettes.groupe1, TPlacettes.groupe2, TPlacettes.ref_habitat, TPlacettes.precision_habitat,
        TPlacettes.ref_station, TPlacettes.ref_typologie, TPlacettes.descriptif_groupe, TPlacettes.descriptif_groupe1,
        TPlacettes.descriptif_groupe2, TPlacettes.cheminement,
        CorCyclesPlacettes.date_intervention, CorCyclesPlacettes.date_intervention, CorCyclesPlacettes.nature_intervention,
        CorCyclesPlacettes.gestion_placette, TCycles.num_cycle
        ).filter(
            (TPlacettes.id_dispositif == dispId)
        ).join(
            CorCyclesPlacettes, CorCyclesPlacettes.id_placette == TPlacettes.id_placette
        ).join(
            TCycles, TCycles.id_cycle == CorCyclesPlacettes.id_cycle
        )

    regesQuery = DB.session.query(
        TPlacettes.id_dispositif, TPlacettes.id_placette_orig,
         TCycles.num_cycle, TRegenerations
        ).filter(
            (TPlacettes.id_dispositif == dispId)
        ).join(
            CorCyclesPlacettes, CorCyclesPlacettes.id_placette == TPlacettes.id_placette
        ).join(
            TCycles, TCycles.id_cycle == CorCyclesPlacettes.id_cycle
        ).join(
            TRegenerations, TRegenerations.id_cycle_placette == CorCyclesPlacettes.id_cycle_placette
        )

    transectsQuery = DB.session.query(
        TPlacettes.id_dispositif, TPlacettes.id_placette_orig,
         TCycles.num_cycle, TTransects
        ).filter(
            (TPlacettes.id_dispositif == dispId)
        ).join(
            CorCyclesPlacettes, CorCyclesPlacettes.id_placette == TPlacettes.id_placette
        ).join(
            TCycles, TCycles.id_cycle == CorCyclesPlacettes.id_cycle
        ).join(
            TTransects, TTransects.id_cycle_placette == CorCyclesPlacettes.id_cycle_placette
        )

    reperesQuery = DB.session.query(
        TPlacettes.id_dispositif, TPlacettes.id_placette_orig, TReperes
        ).filter(
            (TPlacettes.id_dispositif == dispId)
        ).join(
            TReperes, TReperes.id_placette == TPlacettes.id_placette
        )

    cyclesQuery = DB.session.query(
        TPlacettes.id_dispositif, TPlacettes.id_placette_orig,
        CorCyclesPlacettes.annee, TCycles.num_cycle, TCycles.coeff, 
        TCycles.diam_lim
        ).filter(
            (TPlacettes.id_dispositif == dispId)
        ).join(
            CorCyclesPlacettes, CorCyclesPlacettes.id_placette == TPlacettes.id_placette
        ).join(
            TCycles, TCycles.id_cycle == CorCyclesPlacettes.id_cycle
        )

    # TODO: Ajouter les documents administrateur dans la base de données
    # ---- Création des Requêtes pour les données administrateur
    # dispositifsQuery = DB.session.query(
    #     TDispositifs.id_dispositif, TDispositifs.name, dispositifs_area_assoc, LAreas.id_area, LAreas.area_name, BibAreasTypes.type_name
    #     ).filter(
    #         (TDispositifs.id_dispositif == dispId)
    #     ).join(
    #         dispositifs_area_assoc, dispositifs_area_assoc.columns.id_dispositif == TDispositifs.id_dispositif
    #     ).join(
    #         LAreas, LAreas.id_area == dispositifs_area_assoc.columns.id_area
    #     ).join(
    #         BibAreasTypes, BibAreasTypes.id_type == LAreas.id_type
    #     )

    # dispositifsPandas = pd.read_sql(dispositifsQuery.statement, dispositifsQuery.session.bind)
    
    #--- Convertion du résultat en pd dataframe
    arbresPandas = pd.read_sql(arbresQuery.statement, arbresQuery.session.bind)
    bmsPandas = pd.read_sql(bmsQuery.statement, bmsQuery.session.bind)
    placettesPandas = pd.read_sql(placettesQuery.statement, placettesQuery.session.bind)
    regesPandas = pd.read_sql(regesQuery.statement, regesQuery.session.bind)
    transectsPandas = pd.read_sql(transectsQuery.statement, transectsQuery.session.bind)
    reperesPandas = pd.read_sql(reperesQuery.statement, reperesQuery.session.bind)
    cyclesPandas = pd.read_sql(cyclesQuery.statement, cyclesQuery.session.bind)

    #--- Convertion du df Pandas en rdataframe
    with localconverter(ro.default_converter + pandas2ri.converter):
        r_placettes = ro.conversion.py2rpy(placettesPandas)
    with localconverter(ro.default_converter + pandas2ri.converter):
        r_arbres = ro.conversion.py2rpy(arbresPandas)
    with localconverter(ro.default_converter + pandas2ri.converter):
        r_bmss = ro.conversion.py2rpy(bmsPandas)
    with localconverter(ro.default_converter + pandas2ri.converter):
        r_reges = ro.conversion.py2rpy(regesPandas)
    with localconverter(ro.default_converter + pandas2ri.converter):
        r_transects = ro.conversion.py2rpy(transectsPandas)
    with localconverter(ro.default_converter + pandas2ri.converter):
        r_reperes = ro.conversion.py2rpy(reperesPandas)   
    with localconverter(ro.default_converter + pandas2ri.converter):
        r_cycles = ro.conversion.py2rpy(cyclesPandas)             

    # 2/ Formater dans le bon format en modifiant XLs2Rdata
    with open('/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/BDD2RData.R', 'r') as f:
        string = f.read()
    BDD2Rdata = STAP(string, "BDD2Rdata")
    print(carnetToDownloadParameters)
    BDD2Rdata.editDocuments(dispId, lastCycle, dispName, r_placettes, r_arbres, r_bmss, r_reges, r_transects, r_reperes, r_cycles, isCarnetToDownload, isPlanDesArbresToDownload, carnetToDownloadParameters['Answer_Radar'])

