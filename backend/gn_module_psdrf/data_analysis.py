"""Module for analyzing PSDRF data and generating R-based reports."""

import os
import shutil
from pathlib import Path

import pandas as pd
import rpy2
import rpy2.robjects as ro
import rpy2.robjects as robjects
from celery.utils.log import get_task_logger
from geonature.utils.env import DB
from ref_geo.models import BibAreasTypes, LAreas, LiMunicipalities
from rpy2.rinterface_lib.embedded import RRuntimeError
from rpy2.robjects import pandas2ri
from rpy2.robjects.conversion import localconverter
from rpy2.robjects.packages import STAP
from sqlalchemy import select
from sqlalchemy.orm import scoped_session
from sqlalchemy.sql.expression import func

from .geonature_PSDRF_function import (
    get_cd_nomenclature_from_id_type_and_id_nomenclature,
    get_id_type_from_mnemonique)
from .models import (BibEssences, CorCyclesPlacettes, TArbres, TArbresMesures,
                     TBmSup30, TBmSup30Mesures, TCycles, TDispositifs,
                     TPlacettes, TRegenerations, TReperes, TTransects,
                     dispositifs_area_assoc)

logger = get_task_logger(__name__)

# Constants
RSCRIPTS_DIR = Path('/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts')
OUTPUT_DIR = RSCRIPTS_DIR / 'out'
FIGURES_DIR = OUTPUT_DIR / 'figures'

def data_analysis(dispId, isCarnetToDownload, isPlanDesArbresToDownload, carnetToDownloadParameters):
    """Analyze PSDRF data and generate R-based reports.
    
    Args:
        dispId: ID of the dispositif (study area)
        isCarnetToDownload: Boolean indicating if carnet should be downloaded
        isPlanDesArbresToDownload: Boolean indicating if tree plan should be downloaded
        carnetToDownloadParameters: Dictionary containing parameters for carnet download
    
    Raises:
        Exception: If there's an error during data analysis
    """
    # Clean output directory
    _clean_output_directory()
    os.mkdir(FIGURES_DIR)

    r = ro.r
    session = scoped_session(DB.session)

    try:
        # Get dispositif name and last cycle
        dispName, r_lastCycle = _get_dispositif_info(session, dispId)
        
        # Format database data for R processing
        formatBdd2RData(r, dispId, r_lastCycle, dispName, isCarnetToDownload, 
                       isPlanDesArbresToDownload, carnetToDownloadParameters)

    except Exception as e:
        logger.error(f'Error in data_analysis: {e}')
        raise
    finally:
        session.remove()
    
    del r


def _clean_output_directory():
    """Clean the output directory by removing all files except .gitignore."""
    for filename in os.listdir(OUTPUT_DIR):
        if filename != ".gitignore":
            file_path = OUTPUT_DIR / filename
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                logger.error(f'Failed to delete {file_path}. Reason: {e}')

def _get_dispositif_info(session, dispId):
    """Get dispositif name and last cycle information.
    
    Args:
        session: Database session
        dispId: ID of the dispositif
        
    Returns:
        tuple: (dispositif_name, r_lastCycle)
    """
    # Get dispositif name
    dispNameQuery = session.query(TDispositifs.name).filter(TDispositifs.id_dispositif == dispId)
    with DB.engine.connect() as conn:
        dispName = dispNameQuery.scalar()
        dispName = str(dispName)

        lastCycleQuery = session.query(func.max(TCycles.num_cycle)).filter(TCycles.id_dispositif == dispId)
        lastCycle = lastCycleQuery.scalar()

    return dispName, lastCycle

def formatBdd2RData(r, dispId, lastCycle, dispName, isCarnetToDownload, isPlanDesArbresToDownload, carnetToDownloadParameters):
    """Format database data for R processing.
    
    Args:
        r: R instance
        dispId: ID of the dispositif
        lastCycle: Last cycle data
        dispName: Name of the dispositif
        isCarnetToDownload: Boolean indicating if carnet should be downloaded
        isPlanDesArbresToDownload: Boolean indicating if tree plan should be downloaded
        carnetToDownloadParameters: Dictionary containing parameters for carnet download
        
    Raises:
        RRuntimeError: If there's an error during R processing
    """
    # Get nomenclature types
    id_type_durete = get_id_type_from_mnemonique("PSDRF_DURETE")
    id_type_ecorce = get_id_type_from_mnemonique("PSDRF_ECORCE")

    # Query data from database
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
        TArbresMesures.observation, TCycles.num_cycle
    ).filter(
        TPlacettes.id_dispositif == dispId
    ).join(
        TArbres, TArbres.id_placette == TPlacettes.id_placette
    ).join(
        TArbresMesures
    ).join(
        TCycles, TCycles.id_cycle == TArbresMesures.id_cycle
    ).all()

    # Process nomenclature for arbres
    stadeDIdxArbre = 11
    stadeEIdxArbre = 12
    Arbres = [id_nomenclatureToMnemonique(arbre, id_type_durete, id_type_ecorce, stadeDIdxArbre, stadeEIdxArbre) 
              for arbre in arbresQuery]

    # Create pandas DataFrame for arbres
    arbresPandas = pd.DataFrame(Arbres, columns=[
        'id_dispositif', 'id_placette_orig', 'id_arbre_orig', 'code_essence', 
        'azimut', 'distance', 'taillis', 'diametre1', 'diametre2', 'type', 
        'hauteur_totale', 'stade_durete', 'stade_ecorce', 'coupe', 'limite',
        'code_ecolo', 'ref_code_ecolo', 'id_nomenclature_code_sanitaire',
        'hauteur_branche', 'ratio_hauteur', 'observation', 'num_cycle'
    ])

    # Query and process BMS data
    bmsQuery = DB.session.query(
        TPlacettes.id_dispositif, TPlacettes.id_placette_orig, 
        TBmSup30.id_bm_sup_30_orig, TBmSup30.id_arbre, TCycles.num_cycle,
        TBmSup30.code_essence, TBmSup30.azimut, TBmSup30.distance,
        TBmSup30Mesures.diametre_ini, TBmSup30Mesures.diametre_med,
        TBmSup30Mesures.diametre_fin, TBmSup30Mesures.longueur,
        TBmSup30Mesures.contact, TBmSup30Mesures.chablis,
        TBmSup30Mesures.stade_durete, TBmSup30Mesures.stade_ecorce,
        TBmSup30Mesures.observation, TBmSup30Mesures.diametre_130,
        TBmSup30.azimut_souche, TBmSup30.distance_souche,
        TBmSup30Mesures.ratio_hauteur, TBmSup30.orientation
    ).filter(
        TPlacettes.id_dispositif == dispId
    ).join(
        TBmSup30, TBmSup30.id_placette == TPlacettes.id_placette
    ).join(
        TBmSup30Mesures
    ).join(
        TCycles, TCycles.id_cycle == TBmSup30Mesures.id_cycle
    ).all()

    # Process nomenclature for BMS
    stadeDIdxBms = 14
    stadeEIdxBms = 15
    Bms = [id_nomenclatureToMnemonique(bms, id_type_durete, id_type_ecorce, stadeDIdxBms, stadeEIdxBms) 
           for bms in bmsQuery]

    bmsPandas = pd.DataFrame(Bms, columns=[
        'id_dispositif', 'id_placette_orig', 'id_bm_sup_30_orig', 'id_arbre',
        'num_cycle', 'code_essence', 'azimut', 'distance', 'diametre_ini',
        'diametre_med', 'diametre_fin', 'longueur', 'contact', 'chablis',
        'stade_durete', 'stade_ecorce', 'observation', 'diametre_130',
        'azimut_souche', 'distance_souche', 'ratio_hauteur', 'orientation'
    ])

    # Query placettes data
    placettesQuery = DB.session.query(
        TPlacettes.id_dispositif, TPlacettes.id_placette_orig, TPlacettes.strate,
        TPlacettes.poids_placette, TPlacettes.pente, TPlacettes.correction_pente,
        TPlacettes.exposition, TPlacettes.habitat, TPlacettes.precision_gps,
        TPlacettes.station, TPlacettes.typologie, TPlacettes.groupe,
        TPlacettes.groupe1, TPlacettes.groupe2, TPlacettes.ref_habitat,
        TPlacettes.precision_habitat, TPlacettes.ref_station, TPlacettes.ref_typologie,
        TPlacettes.descriptif_groupe, TPlacettes.descriptif_groupe1,
        TPlacettes.descriptif_groupe2, TPlacettes.cheminement,
        CorCyclesPlacettes.date_intervention, CorCyclesPlacettes.nature_intervention,
        CorCyclesPlacettes.gestion_placette, TCycles.num_cycle
    ).filter(
        TPlacettes.id_dispositif == dispId
    ).join(
        CorCyclesPlacettes, CorCyclesPlacettes.id_placette == TPlacettes.id_placette
    ).join(
        TCycles, TCycles.id_cycle == CorCyclesPlacettes.id_cycle
    ).all()

    placettesPandas = pd.DataFrame(placettesQuery, columns=[
        'id_dispositif', 'id_placette_orig', 'strate', 'poids_placette',
        'pente', 'correction_pente', 'exposition', 'habitat', 'precision_gps',
        'station', 'typologie', 'groupe', 'groupe1', 'groupe2', 'ref_habitat',
        'precision_habitat', 'ref_station', 'ref_typologie', 'descriptif_groupe',
        'descriptif_groupe1', 'descriptif_groupe2', 'cheminement',
        'date_intervention', 'nature_intervention', 'gestion_placette', 'num_cycle'
    ])

    # Query regeneration data
    regesQuery = DB.session.query(
        TPlacettes.id_dispositif, TPlacettes.id_placette_orig,
        TRegenerations.sous_placette, TCycles.num_cycle,
        TRegenerations.code_essence, TRegenerations.recouvrement,
        TRegenerations.classe1, TRegenerations.classe2, TRegenerations.classe3,
        TRegenerations.taillis, TRegenerations.abroutissement,
        TRegenerations.observation
    ).filter(
        TPlacettes.id_dispositif == dispId
    ).join(
        CorCyclesPlacettes, CorCyclesPlacettes.id_placette == TPlacettes.id_placette
    ).join(
        TCycles, TCycles.id_cycle == CorCyclesPlacettes.id_cycle
    ).join(
        TRegenerations, TRegenerations.id_cycle_placette == CorCyclesPlacettes.id_cycle_placette
    ).all()

    regesPandas = pd.DataFrame(regesQuery, columns=[
        'id_dispositif', 'id_placette_orig', 'sous_placette', 'num_cycle',
        'code_essence', 'recouvrement', 'classe1', 'classe2', 'classe3',
        'taillis', 'abroutissement', 'observation'
    ])

    # Query transects data
    transectsQuery = DB.session.query(
        TPlacettes.id_dispositif, TPlacettes.id_placette_orig,
        TTransects.id_transect_orig, TCycles.num_cycle, TTransects.ref_transect,
        TTransects.code_essence, TTransects.distance, TTransects.diametre,
        TTransects.angle, TTransects.contact, TTransects.chablis,
        TTransects.stade_durete, TTransects.stade_ecorce, TTransects.observation
    ).filter(
        TPlacettes.id_dispositif == dispId
    ).join(
        CorCyclesPlacettes, CorCyclesPlacettes.id_placette == TPlacettes.id_placette
    ).join(
        TCycles, TCycles.id_cycle == CorCyclesPlacettes.id_cycle
    ).join(
        TTransects, TTransects.id_cycle_placette == CorCyclesPlacettes.id_cycle_placette
    ).all()

    # Process nomenclature for transects
    stadeDIdxTransect = 11
    stadeEIdxTransect = 12
    Transects = [id_nomenclatureToMnemonique(transect, id_type_durete, id_type_ecorce, stadeDIdxTransect, stadeEIdxTransect) 
                 for transect in transectsQuery]

    transectsPandas = pd.DataFrame(Transects, columns=[
        'id_dispositif', 'id_placette_orig', 'id_transect_orig', 'num_cycle',
        'ref_transect', 'code_essence', 'distance', 'diametre', 'angle',
        'contact', 'chablis', 'stade_durete', 'stade_ecorce', 'observation'
    ])

    # Query reperes data
    reperesQuery = DB.session.query(
        TPlacettes.id_dispositif, TPlacettes.id_placette_orig,
        TReperes.azimut, TReperes.distance, TReperes.diametre,
        TReperes.repere, TReperes.observation
    ).filter(
        TPlacettes.id_dispositif == dispId
    ).join(
        TReperes, TReperes.id_placette == TPlacettes.id_placette
    ).all()

    reperesPandas = pd.DataFrame(reperesQuery, columns=[
        'id_dispositif', 'id_placette_orig', 'azimut', 'distance',
        'diametre', 'repere', 'observation'
    ])

    # Query cycles data
    cyclesQuery = DB.session.query(
        TPlacettes.id_dispositif, TPlacettes.id_placette_orig,
        CorCyclesPlacettes.annee, TCycles.num_cycle,
        CorCyclesPlacettes.coeff, CorCyclesPlacettes.diam_lim
    ).filter(
        TPlacettes.id_dispositif == dispId
    ).join(
        CorCyclesPlacettes, CorCyclesPlacettes.id_placette == TPlacettes.id_placette
    ).join(
        TCycles, TCycles.id_cycle == CorCyclesPlacettes.id_cycle
    ).all()

    cyclesPandas = pd.DataFrame(cyclesQuery, columns=[
        'id_dispositif', 'id_placette_orig', 'annee', 'num_cycle',
        'coeff', 'diam_lim'
    ])

    # Create list of tables for processing
    tableList = [
        {'name': 'Arbres', 'table': arbresPandas},
        {'name': 'BMSsup30', 'table': bmsPandas},
        {'name': 'Placettes', 'table': placettesPandas},
        {'name': 'Rege', 'table': regesPandas},
        {'name': 'Transects', 'table': transectsPandas},
        {'name': 'Cycles', 'table': cyclesPandas},
        {'name': 'Reperes', 'table': reperesPandas}
    ]

    # Process boolean and NA values
    for table in tableList:
        for bc in getBooleanColumnsByTable(table['name']):
            table['table'][bc] = table['table'][bc].map(booleanToChar)
        for bc in getNaColumnsByTable(table['name']):
            table['table'][bc] = table['table'][bc].map(noValueToNa)

    # Convert to R dataframes
    r_dataframes = {}
    for table in tableList:
        df = table['table']
        if len(df) > 0:  # Vérifier si le DataFrame n'est pas vide
            # Créer un dictionnaire de colonnes pour R
            r_dict = {}
            for col in df.columns:
                r_dict[col] = ro.StrVector(df[col].astype(str).values)
            
            # Créer le DataFrame R
            with localconverter(ro.default_converter + pandas2ri.converter):
                r_df = ro.r['data.frame'](**r_dict)
        else:
            # Créer un DataFrame R vide avec les bonnes colonnes
            empty_dict = {col: ro.StrVector([]) for col in df.columns}
            r_df = ro.r['data.frame'](**empty_dict)
        
        r_dataframes[table['name']] = r_df

    # Run R analysis
    with open(RSCRIPTS_DIR / 'BDD2RData.R', 'r') as f:
        string = f.read()
    BDD2Rdata = STAP(string, "BDD2Rdata")

    Answer_Radar = (ro.NULL if carnetToDownloadParameters['Answer_Radar'] is None 
                   else carnetToDownloadParameters['Answer_Radar'])

    try:
        BDD2Rdata.editDocuments(
            dispId, lastCycle, dispName,
            r_dataframes['Placettes'], r_dataframes['Arbres'],
            r_dataframes['BMSsup30'], r_dataframes['Rege'],
            r_dataframes['Transects'], r_dataframes['Reperes'],
            r_dataframes['Cycles'], isCarnetToDownload,
            isPlanDesArbresToDownload, Answer_Radar
        )
    except RRuntimeError as e:
        logger.error(f"R runtime error occurred: {e}")
        raise

def getBooleanColumnsByTable(tableName):
    """Get boolean columns for a given table.
    
    Args:
        tableName: Name of the table
        
    Returns:
        list: List of boolean column names
    """
    return {
        "Placettes": ["correction_pente"],
        "Cycles": [],
        "Arbres": ["taillis", "limite", "ratio_hauteur"],
        "Rege": ["taillis", "abroutissement"],
        "Transects": ["contact", "chablis"],
        "BMSsup30": ["ratio_hauteur", "chablis"],
        "Reperes": []
    }[tableName]

def getNaColumnsByTable(tableName):
    """Get columns that may contain NA values for a given table.
    
    Args:
        tableName: Name of the table
        
    Returns:
        list: List of column names that may contain NA values
    """
    return {
        "Placettes": [],
        "Cycles": [],
        "Arbres": ["type"],
        "Rege": [],
        "Transects": [],
        "BMSsup30": [],
        "Reperes": []
    }[tableName]

def booleanToChar(booleanVar):
    """Convert boolean to character representation.
    
    Args:
        booleanVar: Boolean value
        
    Returns:
        str: 't' for True, 'f' for False
    """
    return 't' if booleanVar else 'f'

def noValueToNa(value):
    """Convert empty string to None (NA in R).
    
    Args:
        value: Input value
        
    Returns:
        The input value or None if input is empty string
    """
    return None if value == '' else value

def id_nomenclatureToMnemonique(obj, id_type_durete, id_type_ecorce, stadeDIdx, stadeEIdx):
    """Convert nomenclature IDs to mnemoniques for durete and ecorce.
    
    Args:
        obj: Object containing nomenclature IDs
        id_type_durete: ID of durete nomenclature type
        id_type_ecorce: ID of ecorce nomenclature type
        stadeDIdx: Index of stade durete in obj
        stadeEIdx: Index of stade ecorce in obj
        
    Returns:
        tuple: Object with converted nomenclature values
    """
    finalObjtemp = list(obj)
    
    if finalObjtemp[stadeDIdx] is not None:
        finalObjtemp[stadeDIdx] = get_cd_nomenclature_from_id_type_and_id_nomenclature(
            id_type_durete, finalObjtemp[stadeDIdx]
        )
    
    if finalObjtemp[stadeEIdx] is not None:
        finalObjtemp[stadeEIdx] = get_cd_nomenclature_from_id_type_and_id_nomenclature(
            id_type_ecorce, finalObjtemp[stadeEIdx]
        )
    
    return tuple(finalObjtemp)
