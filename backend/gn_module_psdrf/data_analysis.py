from rpy2.robjects import pandas2ri
from rpy2.robjects.conversion import localconverter
import rpy2.robjects as ro
from rpy2.rinterface_lib.embedded import RRuntimeError
import os, shutil

from sqlalchemy import select
from sqlalchemy.sql.expression import func
import pandas as pd
import rpy2
import rpy2.robjects as robjects
from rpy2.robjects.packages import STAP
from geonature.utils.env import DB

from ref_geo.models import LiMunicipalities, LAreas, BibAreasTypes
from .models import TDispositifs, TPlacettes, TArbres, TCycles, \
    CorCyclesPlacettes, TArbresMesures, TReperes, BibEssences, TRegenerations,\
    TBmSup30,TBmSup30Mesures, TTransects, dispositifs_area_assoc
from .geonature_PSDRF_function import get_cd_nomenclature_from_id_type_and_id_nomenclature, get_id_type_from_mnemonique
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

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
    del r

def formatBdd2RData(r, dispId, lastCycle, dispName, isCarnetToDownload, isPlanDesArbresToDownload, carnetToDownloadParameters):

    id_type_durete = get_id_type_from_mnemonique("PSDRF_DURETE")
    id_type_ecorce = get_id_type_from_mnemonique("PSDRF_ECORCE")

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
        TArbresMesures.ratio_hauteur, 
        TArbresMesures.observation, TCycles.num_cycle, 
        ).filter(
            (TPlacettes.id_dispositif == dispId)
        ).join(
            TArbres, TArbres.id_placette == TPlacettes.id_placette
        ).join(
            TArbresMesures
        ).join(
            TCycles, TCycles.id_cycle == TArbresMesures.id_cycle
        ).all()

    stadeDIdxArbre=11
    stadeEIdxArbre=12
    Arbres = [arbre for arbre in arbresQuery]
    Arbres = [id_nomenclatureToMnemonique(arbre, id_type_durete, id_type_ecorce, stadeDIdxArbre, stadeEIdxArbre) for arbre in Arbres]

    bmsQuery = DB.session.query(
        TPlacettes.id_dispositif, TPlacettes.id_placette_orig, 
        TBmSup30.id_bm_sup_30_orig,
        TBmSup30.id_arbre, TCycles.num_cycle, TBmSup30.code_essence, TBmSup30.azimut,
        TBmSup30.distance, TBmSup30Mesures.diametre_ini, TBmSup30Mesures.diametre_med,
        TBmSup30Mesures.diametre_fin, TBmSup30Mesures.longueur, TBmSup30Mesures.contact,
        TBmSup30Mesures.chablis, 
        TBmSup30Mesures.stade_durete,
        TBmSup30Mesures.stade_ecorce,
        TBmSup30Mesures.observation,
        TBmSup30Mesures.diametre_130,
        TBmSup30.azimut_souche,
        TBmSup30.distance_souche,
        TBmSup30Mesures.ratio_hauteur,
        TBmSup30.orientation,
        TCycles.num_cycle
        ).filter(
            (TPlacettes.id_dispositif == dispId)
        ).join(
            TBmSup30, TBmSup30.id_placette == TPlacettes.id_placette
        ).join(
            TBmSup30Mesures
        ).join(
            TCycles, TCycles.id_cycle == TBmSup30Mesures.id_cycle
        ).all()
    stadeDIdxBms=14
    stadeEIdxBms=15
    bmsSup30 = [bms for bms in bmsQuery]
    bmsSup30 = [id_nomenclatureToMnemonique(bms, id_type_durete, id_type_ecorce, stadeDIdxBms, stadeEIdxBms) for bms in bmsSup30]



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
        ).all()

    regesQuery = DB.session.query(
        TPlacettes.id_dispositif, TPlacettes.id_placette_orig, TRegenerations.sous_placette,
         TCycles.num_cycle, TRegenerations.code_essence, TRegenerations.recouvrement,
         TRegenerations.classe1, TRegenerations.classe2, TRegenerations.classe3, 
         TRegenerations.taillis, TRegenerations.abroutissement, TRegenerations.observation
        ).filter(
            (TPlacettes.id_dispositif == dispId)
        ).join(
            CorCyclesPlacettes, CorCyclesPlacettes.id_placette == TPlacettes.id_placette
        ).join(
            TCycles, TCycles.id_cycle == CorCyclesPlacettes.id_cycle
        ).join(
            TRegenerations, TRegenerations.id_cycle_placette == CorCyclesPlacettes.id_cycle_placette
        ).all()

    transectsQuery = DB.session.query(
        TPlacettes.id_dispositif, TPlacettes.id_placette_orig, TTransects.id_transect_orig,
        TCycles.num_cycle, TTransects.ref_transect, TTransects.code_essence, TTransects.distance,
        TTransects.diametre, TTransects.angle, TTransects.contact,  TTransects.chablis, 
        TTransects.stade_durete, 
        TTransects.stade_ecorce,
        TTransects.observation
        ).filter(
            (TPlacettes.id_dispositif == dispId)
        ).join(
            CorCyclesPlacettes, CorCyclesPlacettes.id_placette == TPlacettes.id_placette
        ).join(
            TCycles, TCycles.id_cycle == CorCyclesPlacettes.id_cycle
        ).join(
            TTransects, TTransects.id_cycle_placette == CorCyclesPlacettes.id_cycle_placette
        ).all()
    stadeDIdxTransect=11
    stadeEIdxTransect=12
    transects = [transect for transect in transectsQuery]
    transects = [id_nomenclatureToMnemonique(transect, id_type_durete, id_type_ecorce, stadeDIdxTransect, stadeEIdxTransect) for transect in transects]

    reperesQuery = DB.session.query(
        TPlacettes.id_dispositif, TPlacettes.id_placette_orig, TReperes.azimut,
        TReperes.distance, TReperes.diametre, TReperes.repere, TReperes.observation        ).filter(
            (TPlacettes.id_dispositif == dispId)
        ).join(
            TReperes, TReperes.id_placette == TPlacettes.id_placette
        ).all()

    cyclesQuery = DB.session.query(
        TPlacettes.id_dispositif, TPlacettes.id_placette_orig,
        CorCyclesPlacettes.annee, TCycles.num_cycle, CorCyclesPlacettes.coeff, 
        CorCyclesPlacettes.diam_lim
        ).filter(
            (TPlacettes.id_dispositif == dispId)
        ).join(
            CorCyclesPlacettes, CorCyclesPlacettes.id_placette == TPlacettes.id_placette
        ).join(
            TCycles, TCycles.id_cycle == CorCyclesPlacettes.id_cycle
        ).all()

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
    # arbresPandas = pd.read_sql(arbresQuery.statement, arbresQuery.session.bind)
    arbresPandas = pd.DataFrame(Arbres, columns=['id_dispositif', 'id_placette_orig', 'id_arbre_orig', 'code_essence', 
    'azimut', 'distance', 'taillis', 'diametre1', 'diametre2', 'type', 'hauteur_totale', 'stade_durete', 
    'stade_ecorce', 'coupe', 'limite','code_ecolo','ref_code_ecolo','id_nomenclature_code_sanitaire',
    'hauteur_branche', 'ratio_hauteur', 'observation','num_cycle'])

    
    # bmsPandas = pd.read_sql(bmsQuery.statement, bmsQuery.session.bind)
    bmsPandas = pd.DataFrame(bmsSup30, columns=['id_dispositif', 'id_placette_orig', 'id_bm_sup_30_orig', 'id_arbre', 'num_cycle', 
    'code_essence', 'azimut', 'distance', 'diametre_ini', 'diametre_med', 'diametre_fin', 
    'longueur', 'contact', 'chablis', 'stade_durete', 'stade_ecorce','observation', 
    'diametre_130', 'azimut_souche', 'distance_souche', 'ratio_hauteur', 
    'orientation', 'num_cycle'])

    # placettesPandas = pd.read_sql(placettesQuery.statement, placettesQuery.session.bind)
    placettesPandas = pd.DataFrame(placettesQuery, columns=['id_dispositif', 'id_placette_orig', 
    'strate', 'poids_placette', 'pente', 'correction_pente', 'exposition', 
    'habitat', 'precision_gps', 'station', 'typologie', 'groupe', 
    'groupe1', 'groupe2', 'ref_habitat', 'precision_habitat', 'ref_station', 'ref_typologie', 
    'descriptif_groupe', 'descriptif_groupe1','descriptif_groupe2','cheminement','date_intervention', 
    'date_intervention','nature_intervention','gestion_placette','num_cycle'])

    regesPandas = pd.DataFrame(regesQuery, columns=['id_dispositif', 'id_placette_orig', 'sous_placette',
     'num_cycle', 'code_essence', 'recouvrement', 'classe1', 'classe2', 'classe3', 
     'taillis', 'abroutissement', 'observation'])

    transectsPandas = pd.DataFrame(transects, columns=['id_dispositif', 'id_placette_orig', 'id_transect_orig', 
    'num_cycle', 'ref_transect', 'code_essence', 'distance', 'diametre', 
    'angle', 'contact', 'chablis', 'stade_durete', 'stade_ecorce', 'observation'])

    reperesPandas = pd.DataFrame(reperesQuery, columns=["id_dispositif", "id_placette_orig", "azimut", 
    "distance", "diametre", "repere", "observation"])
    cyclesPandas = pd.DataFrame(cyclesQuery, columns=['id_dispositif', 'id_placette_orig', 'annee', 'num_cycle', 'coeff', 'diam_lim'])

    tableList = [
        {'name':'Arbres', 'table': arbresPandas},
        {'name':'BMSsup30', 'table': bmsPandas},
        {'name':'Placettes', 'table': placettesPandas},
        {'name':'Rege', 'table': regesPandas},
        {'name':'Transects', 'table': transectsPandas},
        {'name':'Cycles', 'table': cyclesPandas},
        {'name':'Reperes', 'table': reperesPandas}
    ]
    for table in tableList:
        for bc in getBooleanColumnsByTable(table['name']):
            table['table'][bc] = table['table'][bc].map(booleanToChar)

    for table in tableList:
        for bc in getNaColumnsByTable(table['name']):
            table['table'][bc] = table['table'][bc].map(noValueToNa)

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

    # Scripts pour le debuggage
    # robjects.r.assign("myplacettes", r_placettes)
    # robjects.r("save(myplacettes, file='{}')".format('/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/debugfiles/placette_temp.Rdata'))

    # robjects.r.assign("myarbres", r_arbres)
    # robjects.r("save(myarbres, file='{}')".format('/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/debugfiles/arbre_temp.Rdata'))
    
    # robjects.r.assign("mybmss", r_bmss)
    # robjects.r("save(mybmss, file='{}')".format('/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/debugfiles/bms_temp.Rdata'))

    # robjects.r.assign("myreges", r_reges)
    # robjects.r("save(myreges, file='{}')".format('/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/debugfiles/rege_temp.Rdata'))

    # robjects.r.assign("mytransects", r_transects)
    # robjects.r("save(mytransects, file='{}')".format('/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/debugfiles/transect_temp.Rdata'))

    # robjects.r.assign("myreperes", r_reperes)
    # robjects.r("save(myreperes, file='{}')".format('/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/debugfiles/repere_temp.Rdata'))

    # robjects.r.assign("mycycles", r_cycles)
    # robjects.r("save(mycycles, file='{}')".format('/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/debugfiles/cycle_temp.Rdata'))
    
    # robjects.r.assign("mylastCycle", lastCycle)
    # robjects.r("save(mylastCycle, file='{}')".format('/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/debugfiles/lastCycle'))

    # robjects.r.assign("mydispName", dispName)
    # robjects.r("save(mydispName, file='{}')".format('/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/debugfiles/dispName'))



    # 2/ Formater dans le bon format en modifiant XLs2Rdata
    with open('/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/BDD2RData.R', 'r') as f:
        string = f.read()
    BDD2Rdata = STAP(string, "BDD2Rdata")
    print(carnetToDownloadParameters)
    if carnetToDownloadParameters['Answer_Radar'] == None:
        Answer_Radar = ro.NULL
    else:
        try: 
            Answer_Radar = carnetToDownloadParameters['Answer_Radar']
        except RRuntimeError as e:
            logger.error(f"R runtime error occurred: {e}")

    try:  
        BDD2Rdata.editDocuments(dispId, lastCycle, dispName, r_placettes, r_arbres, r_bmss, r_reges, r_transects, r_reperes, r_cycles, isCarnetToDownload, isPlanDesArbresToDownload, Answer_Radar)
    except RRuntimeError as e:
        logger.error(f"R runtime error occurred: {e}")

def id_nomenclatureToMnemonique(obj,id_type_durete,id_type_ecorce, stadeDIdx, stadeEIdx):
    finalObjtemp = list(obj)
    if (finalObjtemp[stadeDIdx] != None):
        finalObjtemp[stadeDIdx] = get_cd_nomenclature_from_id_type_and_id_nomenclature(id_type_durete, finalObjtemp[stadeDIdx])
    
    if(finalObjtemp[stadeEIdx] != None):
        finalObjtemp[stadeEIdx] = get_cd_nomenclature_from_id_type_and_id_nomenclature(id_type_ecorce, finalObjtemp[stadeEIdx])
    
    finalObj = tuple(finalObjtemp)

    return finalObj

def getBooleanColumnsByTable(tableName):
    allColumnObject = { 
        "Placettes": ["correction_pente"],
        "Cycles":  [], 
        "Arbres": ["taillis", "limite", "ratio_hauteur"],
        "Rege": ["taillis", "abroutissement"],
        "Transects": ["contact", "chablis"],
        "BMSsup30":["ratio_hauteur", "chablis"],
        "Reperes": []
      }
    return allColumnObject[tableName]

# Function for column with no value (which might be NA)
def getNaColumnsByTable(tableName):
    allColumnObject = { 
        "Placettes": [],
        "Cycles":  [], 
        "Arbres": ["type"],
        "Rege": [],
        "Transects": [],
        "BMSsup30":[],
        "Reperes": []
      }
    return allColumnObject[tableName]

def booleanToChar(booleanVar):
    if booleanVar:
        return 't'
    else :
        return 'f'

def noValueToNa(value):
    if value =='':
        return None
    else :
        return value
