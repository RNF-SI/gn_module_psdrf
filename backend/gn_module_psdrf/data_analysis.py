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
    # Convertir lastCycle en dataframe R pour éviter l'erreur 'nombre de dimensions incorrect'
    try:
        import numpy as np
        # Créer une matrice NumPy avec une seule cellule contenant lastCycle
        lastCycle_matrix = np.array([[lastCycle]])
        # Convertir en matrice R
        lastCycle = ro.r.matrix(ro.FloatVector(lastCycle_matrix.flatten()), nrow=1, ncol=1)
        logger.info(f"lastCycle convertit en matrice R: {lastCycle}")
    except Exception as e:
        logger.warning(f"Échec de conversion de lastCycle en matrice R: {e}. Continuation avec la valeur originale.")
    
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
            # Convertir numériquement les colonnes spécifiques qui doivent être numériques
            if table['name'] == 'Arbres' and 'type' in df.columns:
                # Convertir la colonne 'type' en numérique
                df['type'] = pd.to_numeric(df['type'], errors='coerce')
                logger.info(f"Converted 'type' column to numeric in {table['name']}: {df['type'].dtype}")
            
            # Méthode 1: Conversion manuelle via dictionnaire de colonnes
            try:
                # Créer un dictionnaire de colonnes pour R
                r_dict = {}
                for col in df.columns:
                    # Pour certaines colonnes spécifiques, conserver le type numérique
                    # Liste des colonnes à convertir en numériques
                    numeric_cols = ['type', 'stade_durete', 'stade_ecorce', 'diametre1', 'diametre2', 
                                   'azimut', 'distance', 'num_cycle']
                    
                    if col.lower() in [c.lower() for c in numeric_cols]:
                        # Convertir explicitement en numérique
                        try:
                            numeric_values = pd.to_numeric(df[col], errors='coerce')
                            r_dict[col] = ro.FloatVector(numeric_values.fillna(float('nan')).values)
                            logger.info(f"Converted {col} to numeric in {table['name']}")
                        except Exception as ne:
                            logger.warning(f"Failed to convert {col} to numeric: {ne}, using string")
                            r_dict[col] = ro.StrVector(df[col].astype(str).values)
                    else:
                        # Convertir en string pour éviter les problèmes de conversion
                        r_dict[col] = ro.StrVector(df[col].astype(str).values)
                
                # Créer le DataFrame R
                r_df = ro.r['data.frame'](**r_dict)
                
            except Exception as e:
                logger.warning(f"Méthode 1 de conversion a échoué pour {table['name']}: {e}")
                
                # Méthode 2 (alternative): Utiliser pandas2ri.activate() 
                try:
                    # Initialiser l'activation de la conversion pandas à R
                    pandas2ri.activate()
                    
                    # Assurer que les colonnes numériques sont converties correctement
                    for col in df.columns:
                        if col.lower() in ['type', 'stade_durete', 'stade_ecorce']:
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    # Convertir directement le DataFrame
                    r_df = pandas2ri.py2rpy(df)
                    
                    # Désactiver ensuite pour éviter des effets secondaires
                    pandas2ri.deactivate()
                    
                except Exception as e2:
                    logger.error(f"Les deux méthodes de conversion ont échoué pour {table['name']}: {e2}")
                    # Dernière solution: Créer un dataframe vide
                    empty_dict = {col: ro.StrVector([]) for col in df.columns}
                    r_df = ro.r['data.frame'](**empty_dict)
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

    # Activer la journalisation détaillée dans R avec des fonctions améliorées
    r("""
    # Définir le chemin des logs
    log_dir <- "/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/out"
    error_log_file <- file.path(log_dir, "r_error_log.txt")
    debug_log_file <- file.path(log_dir, "r_debug_log.txt")
    trace_log_file <- file.path(log_dir, "r_trace_log.txt")
    
    # Fonction pour récupérer le nom du fichier source actuel
    get_current_filename <- function() {
      calls <- sys.calls()
      frames <- sys.frames()
      
      for (i in rev(seq_along(calls))) {
        srcref <- attr(calls[[i]], "srcref")
        if (!is.null(srcref)) {
          srcfile <- attr(srcref, "srcfile")
          if (!is.null(srcfile) && !is.null(srcfile$filename)) {
            return(srcfile$filename)
          }
        }
        
        # Essayer de récupérer le fichier source de l'environnement
        env <- frames[[i]]
        if (exists("filename", envir = env, inherits = FALSE)) {
          filename <- get("filename", envir = env)
          if (is.character(filename) && length(filename) == 1) {
            return(filename)
          }
        }
      }
      
      # Si aucun nom de fichier n'est trouvé, essayer d'autres méthodes
      if (exists(".current_source_file")) {
        return(get(".current_source_file"))
      }
      
      return("<unknown>")
    }
    
    # Fonction pour récupérer le numéro de ligne actuel
    get_current_line <- function() {
      calls <- sys.calls()
      for (i in rev(seq_along(calls))) {
        srcref <- attr(calls[[i]], "srcref")
        if (!is.null(srcref)) {
          return(srcref[1])
        }
      }
      return("<unknown>")
    }
    
    # Fonction pour obtenir la pile d'appels formatée
    get_formatted_call_stack <- function() {
      calls <- sys.calls()
      result <- character(length(calls))
      
      for (i in seq_along(calls)) {
        # Récupérer les informations sur la source si disponibles
        srcref <- attr(calls[[i]], "srcref")
        file_info <- ""
        
        if (!is.null(srcref)) {
          srcfile <- attr(srcref, "srcfile")
          if (!is.null(srcfile) && !is.null(srcfile$filename)) {
            file_path <- srcfile$filename
            line_num <- srcref[1]
            file_info <- paste0(" [", basename(file_path), ":", line_num, "]")
          }
        }
        
        # Formater l'appel
        call_text <- trimws(deparse(calls[[i]], width.cutoff = 60)[1])
        if (nchar(call_text) > 100) {
          call_text <- paste0(substr(call_text, 1, 97), "...")
        }
        
        result[i] <- paste0("  ", i, ": ", call_text, file_info)
      }
      
      return(paste(result, collapse = "\n"))
    }
    
    # Configurer les options d'erreur pour enregistrer la trace complète
    options(error = function() {
      err_msg <- geterrmessage()
      current_file <- tryCatch(get_current_filename(), error = function(e) "<unknown>")
      current_line <- tryCatch(get_current_line(), error = function(e) "<unknown>")
      call_stack <- tryCatch(get_formatted_call_stack(), error = function(e) "<no stack available>")
      
      # Afficher dans la console
      cat("\n========== R ERROR ==========\n")
      cat("Time:", as.character(Sys.time()), "\n")
      cat("File:", current_file, "Line:", current_line, "\n")
      cat("Error:", err_msg, "\n")
      cat("Call Stack:\n", call_stack, "\n")
      
      # Variables dans l'environnement d'erreur
      if (exists("last.dump") && !is.null(last.dump)) {
        cat("Variables in error environment:\n")
        var_names <- names(last.dump)
        # Limiter le nombre de variables affichées pour éviter un débordement
        if (length(var_names) > 20) {
          cat(paste(var_names[1:20], collapse = ", "), "... (and", length(var_names) - 20, "more)\n")
        } else {
          cat(paste(var_names, collapse = ", "), "\n")
        }
      }
      
      # Écrire dans le fichier journal
      sink(file = error_log_file, append = TRUE, split = FALSE)
      cat("\n\n========== R ERROR ==========\n")
      cat("Time:", as.character(Sys.time()), "\n")
      cat("File:", current_file, "Line:", current_line, "\n")
      cat("Error:", err_msg, "\n")
      cat("Call Stack:\n", call_stack, "\n")
      
      # Afficher plus de détails sur les variables dans le fichier
      if (exists("last.dump") && !is.null(last.dump)) {
        cat("Variables in error environment:\n")
        var_names <- names(last.dump)
        cat(paste(var_names, collapse = ", "), "\n")
        
        # Afficher les dimensions et classes des dataframes
        for (var_name in var_names) {
          tryCatch({
            var_value <- last.dump[[var_name]]
            if (is.data.frame(var_value)) {
              cat(var_name, ": data.frame [", nrow(var_value), "x", ncol(var_value), "]\n")
              cat("  Columns: ", paste(names(var_value), collapse = ", "), "\n")
            } else if (is.vector(var_value) && length(var_value) < 10) {
              cat(var_name, ": vector [", length(var_value), "] ", paste(var_value, collapse = ", "), "\n")
            } else {
              cat(var_name, ": ", class(var_value)[1], " [", length(var_value), "]\n")
            }
          }, error = function(e) {
            cat(var_name, ": <cannot display>\n")
          })
        }
      }
      
      cat("\n")
      sink()
    })
    
    # Fonction de journalisation améliorée qui inclut le fichier source et la ligne
    log_debug <- function(message, level = "INFO") {
      timestamp <- as.character(Sys.time())
      current_file <- tryCatch(get_current_filename(), error = function(e) "<unknown>")
      current_line <- tryCatch(get_current_line(), error = function(e) "<unknown>")
      
      # Formater le message avec des informations contextuelles
      formatted_msg <- sprintf("[%s] [%s] %s:%s - %s", 
                              timestamp, level, basename(current_file), current_line, message)
      
      # Écrire dans le fichier journal
      sink(file = debug_log_file, append = TRUE, split = FALSE)
      cat(formatted_msg, "\n")
      sink()
      
      # Afficher également dans la console pour un retour immédiat
      cat(formatted_msg, "\n")
    }
    
    # Fonction pour tracer l'entrée et la sortie des fonctions importantes
    trace_function <- function(func_name) {
      timestamp <- as.character(Sys.time())
      current_file <- tryCatch(get_current_filename(), error = function(e) "<unknown>")
      current_line <- tryCatch(get_current_line(), error = function(e) "<unknown>")
      
      # Obtenir les arguments
      parent_frame <- parent.frame()
      args <- as.list(parent_frame)
      args_str <- tryCatch({
        args_names <- names(args)
        if (length(args_names) > 0) {
          args_info <- character(length(args_names))
          for (i in seq_along(args_names)) {
            arg_value <- args[[args_names[i]]]
            if (is.data.frame(arg_value)) {
              args_info[i] <- paste0(args_names[i], "=data.frame[", nrow(arg_value), "x", ncol(arg_value), "]")
            } else if (is.atomic(arg_value) && length(arg_value) == 1) {
              args_info[i] <- paste0(args_names[i], "=", toString(arg_value))
            } else {
              args_info[i] <- paste0(args_names[i], "=", class(arg_value)[1])
            }
          }
          paste(args_info, collapse = ", ")
        } else {
          "no args"
        }
      }, error = function(e) "error getting args")
      
      # Formater le message
      msg <- sprintf("[%s] [TRACE] %s:%s - ENTER %s(%s)", 
                     timestamp, basename(current_file), current_line, func_name, args_str)
      
      # Écrire dans le fichier journal
      sink(file = trace_log_file, append = TRUE, split = FALSE)
      cat(msg, "\n")
      sink()
      
      # Pour faciliter le débogage interactif
      if (getOption("verbose", FALSE)) {
        cat(msg, "\n")
      }
      
      # Enregistrer l'heure d'entrée pour calculer la durée
      enter_time <- Sys.time()
      
      # Retourner une fonction pour tracer la sortie
      function(result = NULL) {
        exit_time <- Sys.time()
        duration <- difftime(exit_time, enter_time, units = "secs")
        
        result_str <- tryCatch({
          if (is.null(result)) {
            "NULL"
          } else if (is.data.frame(result)) {
            paste0("data.frame[", nrow(result), "x", ncol(result), "]")
          } else if (is.atomic(result) && length(result) == 1) {
            toString(result)
          } else {
            paste0(class(result)[1], "[length=", length(result), "]")
          }
        }, error = function(e) "error getting result")
        
        # Formater le message de sortie
        msg <- sprintf("[%s] [TRACE] %s:%s - EXIT %s (duration: %.2f secs) => %s", 
                       as.character(Sys.time()), basename(current_file), current_line,
                       func_name, as.numeric(duration), result_str)
        
        # Écrire dans le fichier journal
        sink(file = trace_log_file, append = TRUE, split = FALSE)
        cat(msg, "\n")
        sink()
        
        # Pour faciliter le débogage interactif
        if (getOption("verbose", FALSE)) {
          cat(msg, "\n")
        }
        
        return(invisible(result))
      }
    }
    
    # Fonctions pour différents niveaux de log
    log_info <- function(message) log_debug(message, "INFO")
    log_warning <- function(message) log_debug(message, "WARNING")
    log_error <- function(message) log_debug(message, "ERROR")
    
    # Créer un environnement pour stocker des variables globales utiles pour le débogage
    .debug_env <- new.env()
    
    # Fonction pour sauvegarder l'état actuel (utile pour le débogage)
    save_state <- function(name = paste0("state_", format(Sys.time(), "%H%M%S"))) {
      state <- list(
        timestamp = Sys.time(),
        call_stack = sys.calls(),
        frames = sys.frames()
      )
      
      # Sauvegarder les variables locales du frame parent
      parent_frame <- parent.frame()
      state$variables <- as.list(parent_frame)
      
      # Stocker dans l'environnement de débogage
      assign(name, state, envir = .debug_env)
      
      log_info(paste("State saved as", name))
      return(invisible(name))
    }
    
    # Fonction pour inspecter un objet
    inspect <- function(obj, name = deparse(substitute(obj))) {
      if (is.data.frame(obj)) {
        log_info(paste0("INSPECT ", name, ": data.frame [", nrow(obj), "x", ncol(obj), "]"))
        log_info(paste0("  Columns: ", paste(names(obj), collapse = ", ")))
        
        # Afficher quelques lignes si pas trop grand
        if (nrow(obj) > 0 && nrow(obj) < 10) {
          sink(file = debug_log_file, append = TRUE, split = FALSE)
          cat("  First rows:\n")
          print(head(obj, 5))
          sink()
        }
      } else if (is.list(obj)) {
        log_info(paste0("INSPECT ", name, ": list of length ", length(obj)))
        log_info(paste0("  Names: ", paste(names(obj), collapse = ", ")))
      } else if (is.vector(obj)) {
        log_info(paste0("INSPECT ", name, ": vector [", length(obj), "]"))
        if (length(obj) < 20) {
          log_info(paste0("  Values: ", paste(obj, collapse = ", ")))
        }
      } else {
        log_info(paste0("INSPECT ", name, ": ", class(obj)[1]))
      }
      
      return(invisible(obj))
    }
    
    # Initialiser les fichiers de log avec un en-tête
    timestamp <- as.character(Sys.time())
    header <- paste0("======== Session started at ", timestamp, " ========\n")
    
    # Initialiser ou vider les fichiers de logs si trop grands
    for (file in c(error_log_file, debug_log_file, trace_log_file)) {
      # Vérifier si le fichier existe et est trop grand (>5MB)
      if (file.exists(file) && file.size(file) > 5*1024*1024) {
        # Sauvegarder l'ancien fichier avec un timestamp
        backup_file <- paste0(file, ".", format(Sys.time(), "%Y%m%d%H%M%S"), ".bak")
        file.rename(file, backup_file)
        log_info(paste("Log file", file, "rotated to", backup_file))
      }
      
      # Écrire l'en-tête
      sink(file = file, append = file.exists(file), split = FALSE)
      cat(header)
      sink()
    }
    
    # Informer que le système de logging est prêt
    log_info("Enhanced R logging system initialized")
    """)
    
    try:
        # Activer l'impression des informations de débogage
        r('log_debug("Starting R analysis with editDocuments function")')
        
        # Assigner les dataframes dans l'environnement R global
        for name, df in r_dataframes.items():
            # Assigner le dataframe à l'environnement R global
            ro.globalenv[name] = df
            # Maintenant on peut accéder à l'objet dans les expressions R
            # Utiliser paste() au lieu de + pour concaténer des chaînes en R
            r(f'log_debug(paste0("DataFrame {name}: ", toString(dim({name})), " rows/cols"))')
            # Vérifier la structure des colonnes clés
            if name in ['Placettes', 'Arbres', 'Cycles']:
                r(f'log_debug(paste0("Types in {name}: NumDisp=", toString(class({name}$NumDisp)), ", Cycle=", toString(class({name}$Cycle))))')
        
        # Exécuter la fonction avec traçage
        BDD2Rdata.editDocuments(
            dispId, lastCycle, dispName,
            r_dataframes['Placettes'], r_dataframes['Arbres'],
            r_dataframes['BMSsup30'], r_dataframes['Rege'],
            r_dataframes['Transects'], r_dataframes['Reperes'],
            r_dataframes['Cycles'], isCarnetToDownload,
            isPlanDesArbresToDownload, Answer_Radar
        )
        r('log_debug("R analysis completed successfully")')
    except RRuntimeError as e:
        logger.error(f"R runtime error occurred: {e}")
        
        # Lire et afficher le fichier de log d'erreur R s'il existe
        error_log_path = "/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/out/r_error_log.txt"
        try:
            with open(error_log_path, 'r') as f:
                error_log = f.read()
                logger.error(f"R error log:\n{error_log}")
        except Exception as log_error:
            logger.error(f"Could not read R error log: {log_error}")
            
        # Afficher le message d'erreur R complet
        r_error_message = str(e)
        logger.error(f"Full R error message: {r_error_message}")
        
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
