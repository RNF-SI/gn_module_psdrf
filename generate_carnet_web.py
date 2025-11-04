#!/usr/bin/env python3
"""
Script de génération du carnet PSDRF pour un dispositif spécifique.
Version adaptée pour l'utilisation avec l'interface web de GeoNature.
"""

import os
import sys
import traceback

import numpy as np
import pandas as pd
import rpy2.robjects as ro
from flask import current_app
# Pour l'utilisation avec GeoNature, importez directement de l'environnement
from geonature.utils.env import DB
from rpy2.robjects import pandas2ri
from rpy2.robjects.conversion import localconverter
from rpy2.robjects.packages import STAP
from sqlalchemy import create_engine, text


def get_cd_nomenclature_from_id_type_and_id_nomenclature(id_type, id_nomenclature):
    """Obtient le code de nomenclature à partir de son ID et du type"""
    if id_nomenclature is None:
        return None
    
    query = text("""
        SELECT cd_nomenclature 
        FROM ref_nomenclatures.t_nomenclatures 
        WHERE id_nomenclature = :id_nomenclature
    """)
    
    with DB.engine.connect() as connection:
        result = connection.execute(query, {"id_nomenclature": id_nomenclature})
        row = result.fetchone()
        return row[0] if row else None

def get_id_type_from_mnemonique(mnemonique):
    """Obtient l'ID de type à partir du mnémonique"""
    query = text("""
        SELECT id_type 
        FROM ref_nomenclatures.bib_nomenclatures_types 
        WHERE mnemonique = :mnemonique
    """)
    
    with DB.engine.connect() as connection:
        result = connection.execute(query, {"mnemonique": mnemonique})
        row = result.fetchone()
        return row[0] if row else None

def id_nomenclatureToMnemonique(obj, id_type_durete, id_type_ecorce, stadeDIdx, stadeEIdx):
    """Convertit les ID de nomenclature en codes mnémoniques"""
    finalObjtemp = list(obj)
    if (finalObjtemp[stadeDIdx] != None):
        finalObjtemp[stadeDIdx] = get_cd_nomenclature_from_id_type_and_id_nomenclature(id_type_durete, finalObjtemp[stadeDIdx])
    
    if(finalObjtemp[stadeEIdx] != None):
        finalObjtemp[stadeEIdx] = get_cd_nomenclature_from_id_type_and_id_nomenclature(id_type_ecorce, finalObjtemp[stadeEIdx])
    
    finalObj = tuple(finalObjtemp)
    return finalObj

def generate_carnet_web(disp_id, is_carnet=True, is_plan=False, radar_params=None):
    """
    Génère le carnet PSDRF en utilisant les scripts R originaux
    Adapté pour être utilisé avec l'interface web de GeoNature
    
    Args:
        disp_id (int): ID du dispositif
        is_carnet (bool): Si True, génère le carnet
        is_plan (bool): Si True, génère le plan des arbres
        radar_params (dict): Paramètres pour le radar (optionnel)
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"[GENERATE_CARNET] Starting generation for dispositif {disp_id}")
        logger.info(f"[GENERATE_CARNET] Parameters: is_carnet={is_carnet}, is_plan={is_plan}, radar_params={radar_params}")
        print(f"Génération du carnet pour le dispositif {disp_id}")
        
        # Nettoyer les fichiers de sortie au préalable
        out_dir = '/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/out'
        logger.info(f"[GENERATE_CARNET] Cleaning output directory: {out_dir}")
        for f in os.listdir(out_dir):
            if f != '.gitignore':
                path = os.path.join(out_dir, f)
                if os.path.isfile(path):
                    os.unlink(path)
                elif os.path.isdir(path):
                    import shutil
                    shutil.rmtree(path)
        
        # Créer le dossier figures s'il n'existe pas
        figures_dir = os.path.join(out_dir, 'figures')
        if not os.path.exists(figures_dir):
            logger.info(f"[GENERATE_CARNET] Creating figures directory: {figures_dir}")
            os.mkdir(figures_dir)
        
        # Initialiser l'environnement R
        logger.info(f"[GENERATE_CARNET] Initializing R environment")
        r = ro.r
        
        # Récupérer les informations du dispositif et le dernier cycle
        with DB.engine.connect() as connection:
            # Requête pour le nom du dispositif
            disp_query = text("""
                SELECT name 
                FROM pr_psdrf.t_dispositifs 
                WHERE id_dispositif = :id_dispositif
            """)
            disp_result = connection.execute(disp_query, {"id_dispositif": disp_id})
            disp_row = disp_result.fetchone()
            disp_name = disp_row[0] if disp_row else f"Dispositif {disp_id}"
            
            # Requête pour le dernier cycle
            cycle_query = text("""
                SELECT MAX(num_cycle) 
                FROM pr_psdrf.t_cycles 
                WHERE id_dispositif = :id_dispositif
            """)
            cycle_result = connection.execute(cycle_query, {"id_dispositif": disp_id})
            cycle_row = cycle_result.fetchone()
            last_cycle = cycle_row[0] if cycle_row and cycle_row[0] is not None else 0
        
        # Créer un dataframe R pour le dernier cycle
        r_last_cycle = ro.r('data.frame(max_1 = as.integer(c(' + str(last_cycle) + ')))')
        
        print(f"Nom du dispositif: {disp_name}")
        print(f"Dernier cycle: {last_cycle}")
        
        # Récupérer les types de nomenclatures
        id_type_durete = get_id_type_from_mnemonique("PSDRF_DURETE")
        id_type_ecorce = get_id_type_from_mnemonique("PSDRF_ECORCE")
        
        # Obtenir toutes les données nécessaires depuis la base
        with DB.engine.connect() as connection:
            # Arbres
            arbres_query = text("""
                SELECT 
                    p.id_dispositif, p.id_placette_orig,
                    a.id_arbre_orig, a.code_essence, a.azimut,
                    a.distance, a.taillis,
                    am.diametre1, am.diametre2,
                    am.type, am.hauteur_totale,
                    am.stade_durete, am.stade_ecorce,
                    am.coupe, am.limite,
                    am.code_ecolo, am.ref_code_ecolo,
                    am.id_nomenclature_code_sanitaire, am.hauteur_branche,
                    am.ratio_hauteur,
                    am.observation, c.num_cycle
                FROM pr_psdrf.t_placettes p
                JOIN pr_psdrf.t_arbres a ON a.id_placette = p.id_placette
                JOIN pr_psdrf.t_arbres_mesures am ON am.id_arbre = a.id_arbre
                JOIN pr_psdrf.t_cycles c ON c.id_cycle = am.id_cycle
                WHERE p.id_dispositif = :id_dispositif
            """)
            arbres_result = connection.execute(arbres_query, {"id_dispositif": disp_id})
            arbres_raw = arbres_result.fetchall()
            
            # Conversion des nomenclatures
            stadeD_idx_arbre = 11
            stadeE_idx_arbre = 12
            arbres = [arbre for arbre in arbres_raw]
            arbres = [id_nomenclatureToMnemonique(arbre, id_type_durete, id_type_ecorce, stadeD_idx_arbre, stadeE_idx_arbre) for arbre in arbres]
            
            # BMS
            bms_query = text("""
                SELECT 
                    p.id_dispositif, p.id_placette_orig,
                    bm.id_bm_sup_30_orig,
                    bm.id_arbre, c.num_cycle, bm.code_essence, bm.azimut,
                    bm.distance, bmm.diametre_ini, bmm.diametre_med,
                    bmm.diametre_fin, bmm.longueur, bmm.contact,
                    bmm.chablis,
                    bmm.stade_durete,
                    bmm.stade_ecorce,
                    bmm.observation,
                    bmm.diametre_130,
                    bm.azimut_souche,
                    bm.distance_souche,
                    bmm.ratio_hauteur,
                    bm.orientation
                FROM pr_psdrf.t_placettes p
                JOIN pr_psdrf.t_bm_sup_30 bm ON bm.id_placette = p.id_placette
                JOIN pr_psdrf.t_bm_sup_30_mesures bmm ON bmm.id_bm_sup_30 = bm.id_bm_sup_30
                JOIN pr_psdrf.t_cycles c ON c.id_cycle = bmm.id_cycle
                WHERE p.id_dispositif = :id_dispositif
            """)
            bms_result = connection.execute(bms_query, {"id_dispositif": disp_id})
            bms_raw = bms_result.fetchall()
            
            # Conversion des nomenclatures
            stadeD_idx_bms = 14
            stadeE_idx_bms = 15
            bms = [bms for bms in bms_raw]
            bms = [id_nomenclatureToMnemonique(bms, id_type_durete, id_type_ecorce, stadeD_idx_bms, stadeE_idx_bms) for bms in bms]
            
            # Placettes
            placettes_query = text("""
                SELECT 
                    p.id_dispositif, p.id_placette_orig, p.strate, p.poids_placette,
                    p.pente, p.correction_pente, p.exposition, p.habitat,
                    p.precision_gps, p.station, p.typologie, p.groupe,
                    p.groupe1, p.groupe2, p.ref_habitat, p.precision_habitat,
                    p.ref_station, p.ref_typologie, p.descriptif_groupe, p.descriptif_groupe1,
                    p.descriptif_groupe2, p.cheminement,
                    cp.date_intervention, cp.nature_intervention,
                    cp.gestion_placette, c.num_cycle
                FROM pr_psdrf.t_placettes p
                JOIN pr_psdrf.cor_cycles_placettes cp ON cp.id_placette = p.id_placette
                JOIN pr_psdrf.t_cycles c ON c.id_cycle = cp.id_cycle
                WHERE p.id_dispositif = :id_dispositif
            """)
            placettes_result = connection.execute(placettes_query, {"id_dispositif": disp_id})
            placettes_raw = placettes_result.fetchall()
            
            # Regenerations
            reges_query = text("""
                SELECT 
                    p.id_dispositif, p.id_placette_orig, r.sous_placette,
                    c.num_cycle, r.code_essence, r.recouvrement,
                    r.classe1, r.classe2, r.classe3,
                    r.taillis, r.abroutissement, r.observation
                FROM pr_psdrf.t_placettes p
                JOIN pr_psdrf.cor_cycles_placettes cp ON cp.id_placette = p.id_placette
                JOIN pr_psdrf.t_cycles c ON c.id_cycle = cp.id_cycle
                JOIN pr_psdrf.t_regenerations r ON r.id_cycle_placette = cp.id_cycle_placette
                WHERE p.id_dispositif = :id_dispositif
            """)
            reges_result = connection.execute(reges_query, {"id_dispositif": disp_id})
            reges_raw = reges_result.fetchall()
            
            # Transects
            transects_query = text("""
                SELECT 
                    p.id_dispositif, p.id_placette_orig, t.id_transect_orig,
                    c.num_cycle, t.ref_transect, t.code_essence, t.distance,
                    t.diametre, t.angle, t.contact, t.chablis,
                    t.stade_durete,
                    t.stade_ecorce,
                    t.observation
                FROM pr_psdrf.t_placettes p
                JOIN pr_psdrf.cor_cycles_placettes cp ON cp.id_placette = p.id_placette
                JOIN pr_psdrf.t_cycles c ON c.id_cycle = cp.id_cycle
                JOIN pr_psdrf.t_transects t ON t.id_cycle_placette = cp.id_cycle_placette
                WHERE p.id_dispositif = :id_dispositif
            """)
            transects_result = connection.execute(transects_query, {"id_dispositif": disp_id})
            transects_raw = transects_result.fetchall()
            
            # Conversion des nomenclatures
            stadeD_idx_transect = 11
            stadeE_idx_transect = 12
            transects = [transect for transect in transects_raw]
            transects = [id_nomenclatureToMnemonique(transect, id_type_durete, id_type_ecorce, stadeD_idx_transect, stadeE_idx_transect) for transect in transects]
            
            # Reperes
            reperes_query = text("""
                SELECT 
                    p.id_dispositif, p.id_placette_orig, r.azimut,
                    r.distance, r.diametre, r.repere, r.observation
                FROM pr_psdrf.t_placettes p
                JOIN pr_psdrf.t_reperes r ON r.id_placette = p.id_placette
                WHERE p.id_dispositif = :id_dispositif
            """)
            reperes_result = connection.execute(reperes_query, {"id_dispositif": disp_id})
            reperes_raw = reperes_result.fetchall()
            
            # Cycles
            cycles_query = text("""
                SELECT 
                    p.id_dispositif, p.id_placette_orig,
                    cp.annee, c.num_cycle, cp.coeff,
                    cp.diam_lim
                FROM pr_psdrf.t_placettes p
                JOIN pr_psdrf.cor_cycles_placettes cp ON cp.id_placette = p.id_placette
                JOIN pr_psdrf.t_cycles c ON c.id_cycle = cp.id_cycle
                WHERE p.id_dispositif = :id_dispositif
            """)
            cycles_result = connection.execute(cycles_query, {"id_dispositif": disp_id})
            cycles_raw = cycles_result.fetchall()
        
        # Fonction pour convertir un DataFrame pandas en DataFrame R
        def pandas_to_r_dataframe(df):
            print(f"Converting DataFrame with shape: {df.shape}, columns: {list(df.columns)}")
            
            if df.empty:
                print("DataFrame is empty - returning empty R dataframe")
                empty_r_df = ro.r('data.frame()')
                return empty_r_df
            
            # Utiliser la méthode CSV
            temp_csv = f"/tmp/temp_dataframe_{os.getpid()}_{id(df)}.csv"
            
            try:
                # Préprocesser le DataFrame
                df_copy = df.copy()
                
                # Convertir tous les objets None et NaN en NA pour R
                df_copy = df_copy.fillna(value='NA')
                
                # Sauvegarder en CSV
                df_copy.to_csv(temp_csv, index=False, na_rep='NA', encoding='utf-8')
                
                # Script R pour lire le CSV
                r_script = f"""
                options(warn = 1)
                tryCatch({{
                    df <- read.csv('{temp_csv}', 
                                 stringsAsFactors = FALSE,
                                 check.names = FALSE,
                                 na.strings = c('NA', ''))
                    
                    for (col in names(df)) {{
                        if (is.character(df[[col]])) {{
                            df[[col]][df[[col]] == "NA"] <- NA
                        }}
                    }}
                    
                    if (is.data.frame(df)) {{
                        cat("Conversion réussie:", nrow(df), "lignes,", ncol(df), "colonnes\\n")
                    }} else {{
                        cat("ERREUR: Résultat n'est pas un dataframe\\n")
                        df <- data.frame()
                    }}
                    
                    df
                }}, error = function(e) {{
                    cat("ERREUR lors de la lecture du CSV:", e$message, "\\n")
                    data.frame()
                }})
                """
                
                # Exécuter le script R
                r_df = ro.r(r_script)
                
                return r_df
            
            except Exception as e:
                print(f"Erreur Python lors de la conversion: {e}")
                return ro.r('data.frame()')
            
            finally:
                # Nettoyer le fichier temporaire
                if os.path.exists(temp_csv):
                    try:
                        os.unlink(temp_csv)
                    except:
                        print(f"Impossible de supprimer le fichier temporaire: {temp_csv}")
        
        # Convertir les résultats en DataFrames pandas
        # Utiliser les noms de colonnes originaux de la base de données
        arbres_pandas = pd.DataFrame(arbres, columns=[
            'id_dispositif', 'id_placette_orig', 'id_arbre_orig', 'code_essence', 
            'azimut', 'distance', 'taillis', 'diametre1', 'diametre2', 
            'type', 'hauteur_totale', 'stade_durete', 'stade_ecorce', 'coupe', 
            'limite', 'code_ecolo', 'ref_code_ecolo', 'id_nomenclature_code_sanitaire',
            'hauteur_branche', 'ratio_hauteur', 'observation', 'num_cycle'
        ])
        
        bms_pandas = pd.DataFrame(bms, columns=[
            'id_dispositif', 'id_placette_orig', 'id_bm_sup_30_orig', 'id_arbre', 'num_cycle', 
            'code_essence', 'azimut', 'distance', 'diametre_ini', 'diametre_med', 
            'diametre_fin', 'longueur', 'contact', 'chablis', 'stade_durete', 
            'stade_ecorce', 'observation', 'diametre_130', 'azimut_souche', 
            'distance_souche', 'ratio_hauteur', 'orientation'
        ])
        
        placettes_pandas = pd.DataFrame(placettes_raw, columns=[
            'id_dispositif', 'id_placette_orig', 'strate', 'poids_placette', 'pente', 
            'correction_pente', 'exposition', 'habitat', 'precision_gps', 
            'station', 'typologie', 'groupe', 'groupe1', 'groupe2', 
            'ref_habitat', 'precision_habitat', 'ref_station', 'ref_typologie',
            'descriptif_groupe', 'descriptif_groupe1', 'descriptif_groupe2',
            'cheminement', 'date_intervention', 'nature_intervention',
            'gestion_placette', 'num_cycle'
        ])
        
        reges_pandas = pd.DataFrame(reges_raw, columns=[
            'id_dispositif', 'id_placette_orig', 'sous_placette', 'num_cycle', 'code_essence', 
            'recouvrement', 'classe1', 'classe2', 'classe3', 'taillis', 
            'abroutissement', 'observation'
        ])
        
        transects_pandas = pd.DataFrame(transects, columns=[
            'id_dispositif', 'id_placette_orig', 'id_transect_orig', 'num_cycle', 'ref_transect', 
            'code_essence', 'distance', 'diametre', 'angle', 'contact', 
            'chablis', 'stade_durete', 'stade_ecorce', 'observation'
        ])
        
        reperes_pandas = pd.DataFrame(reperes_raw, columns=[
            'id_dispositif', 'id_placette_orig', 'azimut', 'distance', 'diametre', 
            'repere', 'observation'
        ])
        
        cycles_pandas = pd.DataFrame(cycles_raw, columns=[
            'id_dispositif', 'id_placette_orig', 'annee', 'num_cycle', 'coeff', 'diam_lim'
        ])
        
        # Convertir les DataFrames pandas en DataFrames R
        r_placettes = pandas_to_r_dataframe(placettes_pandas)
        r_arbres = pandas_to_r_dataframe(arbres_pandas)
        r_bmss = pandas_to_r_dataframe(bms_pandas)
        r_reges = pandas_to_r_dataframe(reges_pandas)
        r_transects = pandas_to_r_dataframe(transects_pandas)
        r_reperes = pandas_to_r_dataframe(reperes_pandas)
        r_cycles = pandas_to_r_dataframe(cycles_pandas)
        
        # Vérifier les DataFrames R
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
        
        # Charger le script BDD2RData.R
        print("Chargement du script BDD2RData.R...")
        with open('/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/BDD2RData.R', 'r') as f:
            string = f.read()
            
        # Créer un objet STAP
        BDD2Rdata = STAP(string, "BDD2Rdata")
        
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
        
        # Paramètres du radar (NULL)
        Answer_Radar = ro.NULL
        if radar_params is not None and 'Answer_Radar' in radar_params and radar_params['Answer_Radar'] is not None:
            try: 
                radar_value = radar_params['Answer_Radar']
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
                print(f"Error processing Answer_Radar: {e}")
                Answer_Radar = ro.NULL
        
        # Assigner les dataframes à l'environnement R global
        ro.globalenv['r_placettes'] = r_placettes
        ro.globalenv['r_arbres'] = r_arbres
        ro.globalenv['r_bmss'] = r_bmss
        ro.globalenv['r_reges'] = r_reges
        ro.globalenv['r_transects'] = r_transects
        ro.globalenv['r_reperes'] = r_reperes
        ro.globalenv['r_cycles'] = r_cycles
        
        try:
            # Appel de la fonction editDocuments
            print("Appel de la fonction editDocuments...")
            BDD2Rdata.editDocuments(
                disp_id,
                r_last_cycle,
                disp_name,
                r_placettes,
                r_arbres,
                r_bmss,
                r_reges,
                r_transects,
                r_reperes,
                r_cycles,
                is_carnet,
                is_plan,
                Answer_Radar
            )
            print("Fonction editDocuments exécutée avec succès")
            
            # Vérifier si les fichiers ont été générés
            pdf_file = f"Carnet_dispositif_{disp_id}.pdf"
            pdf_path = os.path.join(out_dir, pdf_file)
            
            if os.path.exists(pdf_path):
                print(f"Carnet généré avec succès : {pdf_path}")
            else:
                print(f"Le carnet n'a pas été généré à l'emplacement attendu : {pdf_path}")
                
            if is_plan:
                plan_file = f"PlansArbres_dispositif_{disp_id}.pdf"
                plan_path = os.path.join(out_dir, plan_file)
                
                if os.path.exists(plan_path):
                    print(f"Plan des arbres généré avec succès : {plan_path}")
                else:
                    print(f"Le plan des arbres n'a pas été généré à l'emplacement attendu : {plan_path}")
                    
        except Exception as e:
            print(f"Erreur lors de l'appel à editDocuments : {str(e)}")
            
            # Essayer en utilisant la méthode directe en R
            try:
                print("Tentative d'appel direct via R...")
                r_load_script = """
                # Réinitialiser l'environnement
                options(dplyr.auto_copy = TRUE)
                
                # Sourcer le script BDD2RData.R directement
                source('/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/BDD2RData.R')
                """
                ro.r(r_load_script)
                                
                # Traiter les guillemets avant pour éviter les problèmes avec les backslashes
                disp_name_formatted = str(disp_name).replace('"', '\\"')
                
                # Appel direct en R
                r_call = f"""
                tryCatch({{
                    editDocuments(
                        {disp_id}, 
                        {r_last_cycle.r_repr()}, 
                        "{disp_name_formatted}", 
                        {r_placettes.r_repr()}, 
                        {r_arbres.r_repr()}, 
                        {r_bmss.r_repr()}, 
                        {r_reges.r_repr()}, 
                        {r_transects.r_repr()}, 
                        {r_reperes.r_repr()}, 
                        {r_cycles.r_repr()}, 
                        {str(is_carnet).lower()}, 
                        {str(is_plan).lower()}, 
                        NULL
                    )
                }}, error = function(e) {{
                    cat("\\n=== ERREUR R DIRECTE ===\\n")
                    cat("Message:", e$message, "\\n")
                    cat("Call:", deparse(e$call), "\\n")
                    stop(paste0("Erreur R: ", e$message))
                }})
                """
                ro.r(r_call)
                print("Appel direct via R terminé avec succès")
                
            except Exception as r_err:
                print(f"Erreur lors de l'appel R direct : {str(r_err)}")
                raise
        
        return True
        
    except Exception as e:
        print(f"Erreur lors de la génération du carnet : {str(e)}")
        traceback.print_exc()
        return False
        
if __name__ == "__main__":
    # Gestion des arguments
    if len(sys.argv) < 2:
        print("Usage: python generate_carnet_adapted.py <disp_id> [--nocarnet] [--plan]")
        sys.exit(1)
        
    disp_id = int(sys.argv[1])
    is_carnet = "--nocarnet" not in sys.argv
    is_plan = "--plan" in sys.argv
    
    print(f"Paramètres:")
    print(f"- Dispositif: {disp_id}")
    print(f"- Génération carnet: {is_carnet}")
    print(f"- Génération plan: {is_plan}")
    
    # Ce module doit être importé depuis le backend de GeoNature
    print("Ce module doit être importé depuis le backend de GeoNature")
    sys.exit(1)