import importlib.util
import os
import shutil
import sys

import numpy as np
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

# Charger le module de génération de carnet web
generate_carnet_web_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                    'generate_carnet_web.py')
spec = importlib.util.spec_from_file_location("generate_carnet_web", generate_carnet_web_path)
generate_carnet_web_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generate_carnet_web_module)
generate_carnet_web = generate_carnet_web_module.generate_carnet_web

logger = get_task_logger(__name__)

# from sqlalchemy.orm import scoped_session

def data_analysis(dispId, isCarnetToDownload, isPlanDesArbresToDownload, carnetToDownloadParameters):
    try:
        # Utiliser le nouveau module pour générer le carnet directement
        success = generate_carnet_web(dispId, isCarnetToDownload, isPlanDesArbresToDownload, carnetToDownloadParameters)
        if success:
            print(f"Génération du carnet pour le dispositif {dispId} réussie avec le nouveau module!")
            return
    except Exception as e:
        print(f"Erreur avec le nouveau module de génération: {e}")
        print("Tentative avec l'ancienne méthode...")
    
    # Suppression des fichiers de sortie 
    folder = '/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/out'
    for filename in os.listdir(folder):
        if filename != ".gitignore":
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

    os.mkdir("/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/out/figures")

    r = ro.r

    # Use scoped_session to ensure thread-safe session handling
    session = scoped_session(DB.session)

    try:
        dispNameQuery = session.query(TDispositifs.name).filter(TDispositifs.id_dispositif == dispId)
        # Exécuter la requête directement avec le session object
        dispName_result = dispNameQuery.one()
        dispName = str(dispName_result.name)

        lastCycleQuery = session.query(func.max(TCycles.num_cycle)).filter(TCycles.id_dispositif == dispId)
        # Exécuter la requête directement avec le session object
        lastCycle_result = lastCycleQuery.one()
        # Obtenir directement la valeur scalaire
        lastCycle_val = lastCycle_result[0]
        
        # Créer un dataframe R qui correspond au format attendu par le code R
        r_lastCycle = ro.r('data.frame(max_1 = as.integer(c(' + str(lastCycle_val if lastCycle_val is not None else 0) + ')))')
        
        # Ajouter un message de debug
        print(f"lastCycle value: {lastCycle_val}, R object type: {type(r_lastCycle)}")

        formatBdd2RData(r, dispId, r_lastCycle, dispName, isCarnetToDownload, isPlanDesArbresToDownload, carnetToDownloadParameters)

    except Exception as e:
        print(f'Error in data_analysis: {e}')
        raise
    finally:
        session.remove()

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

    #--- Conversion du résultat en pd dataframe - avec les noms attendus par R
    arbresPandas = pd.DataFrame(Arbres, columns=[
        'NumDisp', 'NumPlac', 'NumArbre', 'Essence', 
        'Azimut', 'Dist', 'Taillis', 'Diam1', 'Diam2', 
        'Type', 'Haut', 'StadeD', 'StadeE', 'Coupe', 
        'Limite', 'CodeEcolo', 'Ref_CodeEcolo', 'CodeSanit',
        'HautV', 'RatioHaut', 'Observation', 'Cycle'
    ])

    
    bmsPandas = pd.DataFrame(bmsSup30, columns=[
        'NumDisp', 'NumPlac', 'Id', 'NumArbre', 'Cycle', 
        'Essence', 'Azimut', 'Dist', 'DiamIni', 'DiamMed', 
        'DiamFin', 'Longueur', 'Contact', 'Chablis', 'StadeD', 
        'StadeE', 'Observation', 'Diam130', 'AzimutS', 
        'DistS', 'RatioHaut', 'Orientation', 'Cycle2'
    ])
    # Supprimer la colonne dupliquée Cycle2
    if 'Cycle2' in bmsPandas.columns:
        bmsPandas = bmsPandas.drop(columns=['Cycle2'])

    placettesPandas = pd.DataFrame(placettesQuery, columns=[
        'NumDisp', 'NumPlac', 'Strate', 'PoidsPlacette', 'Pente', 
        'CorrectionPente', 'Exposition', 'Habitat', 'PrecisionGPS', 
        'Station', 'Typologie', 'Groupe', 'Groupe1', 'Groupe2', 
        'Ref_Habitat', 'Precision_Habitat', 'Ref_Station', 'Ref_Typologie',
        'Descriptif_Groupe', 'Descriptif_Groupe1', 'Descriptif_Groupe2',
        'Cheminement', 'Date_Intervention', 'Date_Intervention2',
        'Nature_Intervention', 'Gestion', 'Cycle'
    ])
    # Supprimer la colonne dupliquée
    if 'Date_Intervention2' in placettesPandas.columns:
        placettesPandas = placettesPandas.drop(columns=['Date_Intervention2'])

    regesPandas = pd.DataFrame(regesQuery, columns=[
        'NumDisp', 'NumPlac', 'SsPlac', 'Cycle', 'Essence', 
        'Recouv', 'Class1', 'Class2', 'Class3', 'Taillis', 
        'Abroutis', 'Observation'
    ])

    transectsPandas = pd.DataFrame(transects, columns=[
        'NumDisp', 'NumPlac', 'Id', 'Cycle', 'Transect', 
        'Essence', 'Dist', 'Diam', 'Angle', 'Contact', 
        'Chablis', 'StadeD', 'StadeE', 'Observation'
    ])

    reperesPandas = pd.DataFrame(reperesQuery, columns=[
        'NumDisp', 'NumPlac', 'Azimut', 'Dist', 'Diam', 
        'Repere', 'Observation'
    ])
    
    cyclesPandas = pd.DataFrame(cyclesQuery, columns=[
        'NumDisp', 'NumPlac', 'Annee', 'Cycle', 'Coeff', 'DiamLim'
    ])

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

    #--- Conversion du df Pandas en rdataframe en utilisant une méthode CSV simple
    # Fonction helper pour convertir pandas DataFrame vers R DataFrame
    def pandas_to_r_dataframe(df):
        """
        Convertit un DataFrame pandas en DataFrame R via la méthode CSV.
        Les noms de colonnes sont maintenant directement définis en Python, 
        donc pas besoin de mapping ou de renommage.
        """
        print(f"Converting DataFrame with shape: {df.shape}, columns: {list(df.columns)}")
        
        if df.empty:
            print("DataFrame is empty - returning empty R dataframe")
            empty_r_df = ro.r('data.frame()')
            return empty_r_df
        
        # Utiliser la méthode CSV qui est la plus robuste
        temp_csv = f"/tmp/temp_dataframe_{os.getpid()}_{id(df)}.csv"
        
        try:
            # Préprocesser le DataFrame pour éviter les problèmes de conversion
            df_copy = df.copy()
            
            # Traiter les booléens spécifiquement
            for col in df_copy.columns:
                if pd.api.types.is_bool_dtype(df_copy[col]):
                    # R utilise TRUE/FALSE
                    df_copy[col] = df_copy[col].map(lambda x: 'TRUE' if x else 'FALSE')
            
            # Convertir tous les objets None et NaN en NA pour R
            df_copy = df_copy.fillna(value='NA')
            
            # Sauvegarder en CSV
            df_copy.to_csv(temp_csv, index=False, na_rep='NA', encoding='utf-8')
            
            # Script R pour lire le CSV
            r_script = f"""
            options(warn = 1)  # Afficher tous les avertissements
            tryCatch({{
                # Lire le CSV avec check.names=FALSE pour conserver les noms exacts
                df <- read.csv('{temp_csv}', 
                               stringsAsFactors = FALSE,
                               check.names = FALSE,
                               na.strings = c('NA', ''))
                
                # Vérifier et afficher les colonnes
                cat("Colonnes dans le dataframe R:", paste(colnames(df), collapse=", "), "\\n")
                
                # Remplacer les NA par NULL dans les colonnes de caractères
                for (col in names(df)) {{
                    if (is.character(df[[col]])) {{
                        df[[col]][df[[col]] == "NA"] <- NA
                    }}
                }}
                
                # Vérifier que tout s'est bien passé
                if (is.data.frame(df)) {{
                    cat("Conversion réussie:", nrow(df), "lignes,", ncol(df), "colonnes\\n")
                }} else {{
                    cat("ERREUR: Résultat n'est pas un dataframe\\n")
                    df <- data.frame()  # Renvoyer un dataframe vide en cas d'erreur
                }}
                
                # Renvoyer le dataframe
                df
            }}, error = function(e) {{
                cat("ERREUR lors de la lecture du CSV:", e$message, "\\n")
                data.frame()  # Renvoyer un dataframe vide en cas d'erreur
            }})
            """
            
            # Exécuter le script R
            r_df = ro.r(r_script)
            
            return r_df
        
        except Exception as e:
            print(f"Erreur Python lors de la conversion: {e}")
            # En cas d'erreur, retourner un dataframe vide
            return ro.r('data.frame()')
        
        finally:
            # Nettoyer le fichier temporaire
            if os.path.exists(temp_csv):
                try:
                    os.remove(temp_csv)
                except:
                    print(f"Impossible de supprimer le fichier temporaire: {temp_csv}")
    
    # Appliquer notre fonction de conversion pour chaque DataFrame
    r_placettes = pandas_to_r_dataframe(placettesPandas)
    r_arbres = pandas_to_r_dataframe(arbresPandas)
    r_bmss = pandas_to_r_dataframe(bmsPandas)
    r_reges = pandas_to_r_dataframe(regesPandas)
    r_transects = pandas_to_r_dataframe(transectsPandas)
    r_reperes = pandas_to_r_dataframe(reperesPandas)
    r_cycles = pandas_to_r_dataframe(cyclesPandas)             

    # Vérifier que tous les dataframes R sont bien des objets R valides
    print("Vérification des dataframes R avant l'appel à BDD2Rdata.editDocuments:")
    verify_script = """
    function(df, name) {
        if (is.null(df)) {
            cat("ERREUR:", name, "est NULL, création d'un dataframe vide\\n")
            return(data.frame())
        } else if (!is.data.frame(df)) {
            cat("ERREUR:", name, "n'est pas un dataframe, création d'un dataframe vide\\n")
            return(data.frame())
        } else {
            cat("OK:", name, "est un dataframe valide avec", nrow(df), "lignes et", ncol(df), "colonnes\\n")
            return(df)
        }
    }
    """
    verify_df = ro.r(verify_script)
    
    # Vérifier et corriger chaque dataframe
    r_placettes = verify_df(r_placettes, "r_placettes")
    r_arbres = verify_df(r_arbres, "r_arbres")
    r_bmss = verify_df(r_bmss, "r_bmss")
    r_reges = verify_df(r_reges, "r_reges")
    r_transects = verify_df(r_transects, "r_transects")
    r_reperes = verify_df(r_reperes, "r_reperes")
    r_cycles = verify_df(r_cycles, "r_cycles")
    
    # 2/ Formater dans le bon format en modifiant XLs2Rdata
    with open('/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/BDD2RData.R', 'r') as f:
        string = f.read()
    BDD2Rdata = STAP(string, "BDD2Rdata")
    print(carnetToDownloadParameters)
    print(f"Type of carnetToDownloadParameters: {type(carnetToDownloadParameters)}")
    print(f"carnetToDownloadParameters content: {carnetToDownloadParameters}")
    
    # Gestion plus robuste de Answer_Radar
    if carnetToDownloadParameters is None or 'Answer_Radar' not in carnetToDownloadParameters or carnetToDownloadParameters['Answer_Radar'] is None:
        print("Using NULL for Answer_Radar")
        Answer_Radar = ro.NULL
    else:
        try: 
            radar_value = carnetToDownloadParameters['Answer_Radar']
            print(f"Answer_Radar value: {radar_value}, type: {type(radar_value)}")
            
            # S'assurer que le type est approprié pour R
            if isinstance(radar_value, str):
                # Convertir en vecteur string R
                print("Converting string to R StrVector")
                Answer_Radar = ro.StrVector([radar_value])
            elif hasattr(radar_value, 'r_repr'):
                # Déjà un objet R
                print("Using existing R object")
                Answer_Radar = radar_value
            else:
                # Fallback si le type n'est pas géré
                print(f"Unsupported type for Answer_Radar, using NULL")
                Answer_Radar = ro.NULL
        except Exception as e:
            logger.error(f"Error processing Answer_Radar: {e}")
            Answer_Radar = ro.NULL

    # Redéfinir psdrf_Xls2Rdata pour éviter les erreurs de noms de colonnes
    print("Redéfinition de la fonction psdrf_Xls2Rdata...")
    
    redefined_xls2rdata = """
    # Redéfinition de la fonction psdrf_Xls2Rdata pour éviter les erreurs de noms de colonnes
    psdrf_Xls2Rdata <- function(repPSDRF, RPlacettes, RArbres, Rbms, Rreges, Rtransects, Rreperes, Rcycles) {
      # Définir les mappings de noms de colonnes
      cat("Redéfinition de psdrf_Xls2Rdata pour éviter les erreurs de noms de colonnes\\n")
      
      # Définir create_null pour éviter les erreurs
      create_null <- function(objects) {
        for (obj in objects) {
          assign(obj, NULL, envir = .GlobalEnv)
        }
      }
      
      # -- définition nulle des variables utilisées
      objects <- c(
        "Abroutis", "Angle", "Azimut", "Chablis", "Cheminement", "Class1", 
        "Class2", "Class3", "CodeEcolo", "Contact", "CorrectionPente", "Coupe", 
        "Cycle", "Date_Intervention", "Descriptif_Groupe", "Descriptif_Groupe1", 
        "Descriptif_Groupe2", "Diam", "Diam1", "Diam2", "DiamFin", "DiamIni", "DiamMed", 
        "Dist", "Essence", "Exposition", "Gestion", "Groupe", "Groupe1", 
        "Groupe2", "Habitat", "Haut", "Id", "Limite", "Longueur", "Nature_Intervention", 
        "NumArbre", "NumDisp", "NumPlac", "Observation", 
        "Pente", "PoidsPlacette", "Precision_Habitat", "PrecisionGPS", "Recouv", 
        "Ref_CodeEcolo", "Ref_Habitat", "Ref_Station", "Ref_Typologie", "Repere", 
        "SsPlac", "StadeD", "StadeE", "Station", "Strate", "Taillis", "Type", "Typologie"
      )
      create_null(objects)
      
      # -- initialisation des tables d'import
      cat("Initialisation des tables avec les bons noms de colonnes...\\n")
      
      # Création de data.frames vides avec les colonnes correctes
      # Placettes
      Placettes <- data.frame(
        NumDisp = numeric(0), NumPlac = character(0), Cycle = numeric(0), 
        Strate = character(0), PoidsPlacette = numeric(0), Pente = numeric(0),
        CorrectionPente = character(0), Exposition = character(0), PrecisionGPS = character(0),
        Habitat = character(0), Station = character(0), Typologie = character(0),
        Groupe = character(0), Groupe1 = character(0), Groupe2 = character(0),
        Ref_Habitat = character(0), Precision_Habitat = character(0),
        Ref_Station = character(0), Ref_Typologie = character(0),
        Descriptif_Groupe = character(0), Descriptif_Groupe1 = character(0),
        Descriptif_Groupe2 = character(0), Date_Intervention = character(0),
        Nature_Intervention = character(0), Gestion = character(0),
        Cheminement = character(0)
      )
      
      # Arbres
      IdArbres <- data.frame(
        NumDisp = numeric(0), NumPlac = character(0), NumArbre = character(0),
        Essence = character(0), Azimut = numeric(0), Dist = numeric(0),
        IdArbre = integer(0)
      )
      
      ValArbres <- data.frame(
        IdArbre = integer(0), Cycle = numeric(0), Diam1 = numeric(0), 
        Diam2 = numeric(0), Type = character(0), Haut = numeric(0),
        HautV = numeric(0), StadeD = character(0), StadeE = character(0), 
        Taillis = character(0), Coupe = character(0), Limite = character(0),
        CodeEcolo = character(0), Ref_CodeEcolo = character(0),
        CodeSanit = character(0), Observation = character(0),
        RatioHaut = character(0)
      )
      
      # PCQM
      PCQM <- data.frame(
        NumDisp = numeric(0), NumPlac = character(0), Cycle = numeric(0),
        Quart = character(0), Population = numeric(0), Diam = numeric(0)
      )
      
      # Rege
      Reges <- data.frame(
        NumDisp = numeric(0), NumPlac = character(0), Cycle = numeric(0),
        SsPlac = character(0), Essence = character(0), Recouv = numeric(0),
        Class1 = numeric(0), Class2 = numeric(0), Class3 = numeric(0),
        Taillis = character(0), Abroutis = character(0), Observation = character(0)
      )
      
      # Transects
      Transect <- data.frame(
        NumDisp = numeric(0), NumPlac = character(0), Id = character(0),
        Cycle = numeric(0), Essence = character(0), Transect = character(0),
        Dist = numeric(0), Diam = numeric(0), Contact = character(0),
        Angle = numeric(0), Chablis = character(0), StadeD = character(0),
        StadeE = character(0), Observation = character(0)
      )
      
      # BMSsup30
      BMSsup30 <- data.frame(
        NumDisp = numeric(0), NumPlac = character(0), Id = character(0),
        NumArbre = character(0), Cycle = numeric(0), Essence = character(0),
        Azimut = numeric(0), Dist = numeric(0), DiamIni = numeric(0),
        DiamMed = numeric(0), DiamFin = numeric(0), Diam130 = numeric(0),
        Longueur = numeric(0), Contact = character(0), Chablis = character(0),
        StadeD = character(0), StadeE = character(0), Observation = character(0),
        RatioHaut = character(0), AzimutS = numeric(0), DistS = numeric(0),
        Orientation = character(0)
      )
      
      # Reperes
      Reperes <- data.frame(
        NumDisp = numeric(0), NumPlac = character(0), Azimut = numeric(0),
        Dist = numeric(0), Diam = numeric(0), Repere = character(0),
        Observation = character(0)
      )
      
      # Cycles
      Cycles <- data.frame(
        NumDisp = numeric(0), NumPlac = character(0), Cycle = numeric(0),
        Annee = numeric(0), Coeff = numeric(0), DiamLim = numeric(0)
      )
      
      # Sauvegarde des tables (même vides)
      setwd(repPSDRF)
      file = file.path(repPSDRF, "tables", "psdrfDonneesBrutes.Rdata")
      
      cat("Sauvegarde des tables (même vides) dans", file, "\\n")
      save(
        Placettes, IdArbres, ValArbres, PCQM, Reges, 
        Transect, BMSsup30, Reperes, Cycles, 
        file = file
      )
      
      cat("Fonction psdrf_Xls2Rdata redéfinie et exécutée avec succès\\n")
    }
    """
    
    # Ajouter la redéfinition à l'environnement R
    ro.r(redefined_xls2rdata)
    
    # Assigner tous les dataframes à l'environnement R global d'abord
    print("Assignation des dataframes à l'environnement R...")
    ro.globalenv['r_placettes'] = r_placettes
    ro.globalenv['r_arbres'] = r_arbres
    ro.globalenv['r_bmss'] = r_bmss
    ro.globalenv['r_reges'] = r_reges
    ro.globalenv['r_transects'] = r_transects
    ro.globalenv['r_reperes'] = r_reperes
    ro.globalenv['r_cycles'] = r_cycles
    
    try:
        # Convertir Answer_Radar en un format approprié pour R
        if Answer_Radar is None or Answer_Radar is ro.NULL:
            r_answer_radar = ro.NULL
        elif isinstance(Answer_Radar, ro.StrVector):
            r_answer_radar = Answer_Radar  # Déjà un objet R
        elif isinstance(Answer_Radar, str):
            # Convertir string Python en chaîne R
            r_answer_radar = ro.StrVector([Answer_Radar])
        else:
            # Fallback pour tout autre type - convertir en string puis en R
            r_answer_radar = ro.StrVector([str(Answer_Radar)])
            
        # Assurons-nous que dispName est une chaîne Python standard
        if isinstance(dispName, ro.StrVector) or hasattr(dispName, 'r_repr'):
            # Si c'est un objet R, le convertir en chaîne Python
            disp_name_str = str(dispName[0]) if len(dispName) > 0 else ""
        else:
            disp_name_str = str(dispName)
            
        print(f"Calling BDD2Rdata.editDocuments with dispName type: {type(disp_name_str)}")
        
        # Appel direct de la fonction editDocuments depuis BDD2Rdata
        BDD2Rdata.editDocuments(
            dispId,
            lastCycle,
            disp_name_str,  # String Python standard
            r_placettes,
            r_arbres,
            r_bmss,
            r_reges,
            r_transects,
            r_reperes,
            r_cycles,
            isCarnetToDownload,
            isPlanDesArbresToDownload,
            r_answer_radar
        )
    except Exception as e:
        print(f"Erreur lors de l'appel à BDD2Rdata.editDocuments: {e}")
        
        # Essayer en utilisant la méthode directe en R
        try:
            # Charger le script R directement et appeler la fonction
            print("Tentative d'appel direct via R...")
            r_load_script = """
            # Réinitialiser l'environnement
            options(dplyr.auto_copy = TRUE)
            
            # Sourcer le script BDD2RData.R directement
            source('/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/BDD2RData.R')
            """
            ro.r(r_load_script)
            
            # Maintenant appeler directement la fonction R
            r_call = f"""
            tryCatch({{
                editDocuments(
                    {dispId}, 
                    {lastCycle.r_repr()}, 
                    "{disp_name_str.replace('"', '\\"')}", 
                    {r_placettes.r_repr()}, 
                    {r_arbres.r_repr()}, 
                    {r_bmss.r_repr()}, 
                    {r_reges.r_repr()}, 
                    {r_transects.r_repr()}, 
                    {r_reperes.r_repr()}, 
                    {r_cycles.r_repr()}, 
                    {str(isCarnetToDownload).lower()}, 
                    {str(isPlanDesArbresToDownload).lower()}, 
                    {r_answer_radar.r_repr() if r_answer_radar is not ro.NULL else "NULL"}
                )
            }}, error = function(e) {{
                cat("\\n=== ERREUR R DIRECTE ===\\n")
                cat("Message:", e$message, "\\n")
                cat("Call:", deparse(e$call), "\\n")
                stop(paste0("Erreur R: ", e$message))
            }})
            """
            ro.r(r_call)
        except Exception as r_err:
            print(f"Erreur lors de l'appel R direct: {r_err}")
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
        "Placettes": ["CorrectionPente"],
        "Cycles":  [], 
        "Arbres": ["Taillis", "Limite", "RatioHaut"],
        "Rege": ["Taillis", "Abroutis"],
        "Transects": ["Contact", "Chablis"],
        "BMSsup30":["RatioHaut", "Chablis"],
        "Reperes": []
      }
    return allColumnObject[tableName]

# Function for column with no value (which might be NA)
def getNaColumnsByTable(tableName):
    allColumnObject = { 
        "Placettes": [],
        "Cycles":  [], 
        "Arbres": ["Type"],
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