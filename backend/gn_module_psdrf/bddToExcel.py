from geonature.utils.env import DB
import json
import numpy as np
from .models import TDispositifs, TPlacettes, TArbres, TCycles, \
    CorCyclesPlacettes, TArbresMesures, TReperes, BibEssences, TRegenerations,\
    TBmSup30,TBmSup30Mesures, TTransects, dispositifs_area_assoc


def bddToExcel(dispId):

    placettesQuery = DB.session.query(
        TPlacettes.id_dispositif, TPlacettes.id_placette_orig, TCycles.num_cycle, TPlacettes.strate, TPlacettes.poids_placette,
        TPlacettes.pente, TPlacettes.correction_pente, TPlacettes.exposition, TPlacettes.habitat,
        TPlacettes.station, TPlacettes.typologie, TPlacettes.groupe,
        TPlacettes.groupe1, TPlacettes.groupe2, TPlacettes.ref_habitat, TPlacettes.precision_habitat,
        TPlacettes.ref_station, TPlacettes.ref_typologie, TPlacettes.descriptif_groupe, TPlacettes.descriptif_groupe1,
        TPlacettes.descriptif_groupe2,
        CorCyclesPlacettes.date_intervention, CorCyclesPlacettes.nature_intervention,
        CorCyclesPlacettes.gestion_placette, TPlacettes.precision_gps, TPlacettes.cheminement
        ).filter(
            (TPlacettes.id_dispositif == dispId)
        ).join(
            CorCyclesPlacettes, CorCyclesPlacettes.id_placette == TPlacettes.id_placette
        ).join(
            TCycles, TCycles.id_cycle == CorCyclesPlacettes.id_cycle
        )
    Placettes = [placette for placette in placettesQuery]

    cyclesQuery = DB.session.query(
        TPlacettes.id_dispositif, TPlacettes.id_placette_orig, TCycles.num_cycle,
        TCycles.coeff, TCycles.diam_lim, CorCyclesPlacettes.date_releve, CorCyclesPlacettes.annee
        ).filter(
            (TPlacettes.id_dispositif == dispId)
        ).join(
            CorCyclesPlacettes, CorCyclesPlacettes.id_placette == TPlacettes.id_placette
        ).join(
            TCycles, TCycles.id_cycle == CorCyclesPlacettes.id_cycle
        )
    Cycles = [cycle for cycle in cyclesQuery]

    arbresQuery = DB.session.query(
        TPlacettes.id_dispositif, TPlacettes.id_placette_orig, 
        TArbres.id_arbre_orig, TCycles.num_cycle, TArbres.code_essence, TArbres.azimut,
        TArbres.distance, TArbresMesures.diametre1, TArbresMesures.diametre2, 
        TArbresMesures.type, TArbresMesures.hauteur_totale, 
        TArbresMesures.stade_durete, TArbresMesures.stade_ecorce, TArbres.taillis, 
        TArbresMesures.coupe, TArbresMesures.limite, 
        TArbresMesures.code_ecolo, TArbresMesures.ref_code_ecolo, 
        TArbresMesures.observation
        ).filter(
            (TPlacettes.id_dispositif == dispId)
        ).join(
            TArbres, TArbres.id_placette == TPlacettes.id_placette
        ).join(
            TArbresMesures
        ).join(
            TCycles, TCycles.id_cycle == TArbresMesures.id_cycle
        )
    Arbres = [arbre for arbre in arbresQuery]

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
        )
    Regenerations = [rege for rege in regesQuery]

    transectsQuery = DB.session.query(
        TPlacettes.id_dispositif, TPlacettes.id_placette_orig, TTransects.id_transect_orig,
        TCycles.num_cycle, TTransects.code_essence, TTransects.ref_transect, TTransects.distance,
        TTransects.diametre, TTransects.contact, TTransects.angle, TTransects.chablis, 
        TTransects.stade_durete, TTransects.stade_ecorce, TTransects.observation
        ).filter(
            (TPlacettes.id_dispositif == dispId)
        ).join(
            CorCyclesPlacettes, CorCyclesPlacettes.id_placette == TPlacettes.id_placette
        ).join(
            TCycles, TCycles.id_cycle == CorCyclesPlacettes.id_cycle
        ).join(
            TTransects, TTransects.id_cycle_placette == CorCyclesPlacettes.id_cycle_placette
        )
    Transects = [transect for transect in transectsQuery]

    bmsQuery = DB.session.query(
        TPlacettes.id_dispositif, TPlacettes.id_placette_orig, TBmSup30.id_bm_sup_30_orig,
        TBmSup30.id_arbre, TCycles.num_cycle, TBmSup30.code_essence, TBmSup30.azimut,
        TBmSup30.distance, TBmSup30Mesures.diametre_ini, TBmSup30Mesures.diametre_med,
        TBmSup30Mesures.diametre_fin, TBmSup30Mesures.longueur, TBmSup30Mesures.contact,
        TBmSup30Mesures.chablis, TBmSup30Mesures.stade_durete, TBmSup30Mesures.stade_ecorce,
        TBmSup30Mesures.observation
        ).filter(
            (TPlacettes.id_dispositif == dispId)
        ).join(
            TBmSup30, TBmSup30.id_placette == TPlacettes.id_placette
        ).join(
            TBmSup30Mesures
        ).join(
            TCycles, TCycles.id_cycle == TBmSup30Mesures.id_cycle
        )
    BMSsup30 = [bms for bms in bmsQuery]

    reperesQuery = DB.session.query(
        TPlacettes.id_dispositif, TPlacettes.id_placette_orig, TReperes.azimut,
        TReperes.distance, TReperes.diametre, TReperes.repere, TReperes.observation
        ).filter(
            (TPlacettes.id_dispositif == dispId)
        ).join(
            TReperes, TReperes.id_placette == TPlacettes.id_placette
        )
    Reperes = [repere for repere in reperesQuery]
    data = []

    data.append(convertToJsonObject("Placettes", Placettes))
    data.append(convertToJsonObject("Cycles", Cycles))
    data.append(convertToJsonObject("Arbres", Arbres))
    data.append(convertToJsonObject("Rege", Regenerations))
    data.append(convertToJsonObject("Transects", Transects))
    data.append(convertToJsonObject("BMSsup30", BMSsup30))
    data.append(convertToJsonObject("Reperes", Reperes))

    excelData = {"data": data}
    excelJson = json.dumps(excelData, cls=NumpyEncoder)
   
    return excelJson 

def convertToJsonObject(sheetName, tuples):
    finalObj = []
    columnNames = getColumnObject(sheetName)
    print("")
    print(sheetName)
    for tuple in tuples:
        listObj = list(tuple)
        obj = {}
        print("/n")
        print("/n")
        for i in range(len(listObj)):
            print(columnNames[i])
            print(listObj[i])
            obj[columnNames[i]]= listObj[i]
        finalObj.append(obj)
    return finalObj


def getColumnObject(sheetName):
    allColumnObject = { 
        "Placettes": [
          "NumDisp", "NumPlac", "Cycle", "Strate", "PoidsPlacette", "Pente", "CorrectionPenteboolean", 
          "Exposition", "Habitat", "Station", "Typologie", "Groupe", "Groupe1", 
          "Groupe2", "Ref_Habitat", "Precision_Habitat", "Ref_Station", 
          "Ref_Typologie", "Descriptif_Groupe", "Descriptif_Groupe1", 
          "Descriptif_Groupe2", "Date_Intervention", "Nature_Intervention", 
          "Gestion", "PrecisionGPS", "Cheminement"
        ], 
        "Cycles": [
          "NumDisp", "NumPlac", "Cycle", "Coeff", "Date", "DiamLim", "Année"
        ],
        "Arbres": [  
          "NumDisp", "NumPlac", "Cycle", "NumArbre", "Essence", "Azimut", "Dist", "Diam1", "Diam2", 
          "Type", "Haut", "StadeD", "StadeE", "Taillis", "Coupe", "Limite", "CodeEcolo", 
          "Ref_CodeEcolo", "NumPlacObservation"
        ], 
        "Rege": [
          "NumDisp", "NumPlac", "SsPlac", 
          "Cycle", "Essence", "Recouv", "Class1", "Class2", 
          "Class3", " Taillis", "Abroutis", "Observation"
        ], 
        "Transects": [  
          "NumDisp", "NumPlac", "Id", "Cycle", "Transect", 
          "Essence", "Dist", "Diam", "Angle", "Contact", 
          "Chablis", "StadeD", "StadeE", "Observation"
        ], 
        "BMSsup30": [
          "NumDisp", "NumPlac", "Id", "NumArbre", 
          "Cycle", "Essence", "Azimut", "Dist", "DiamIni", 
          "DiamMed", "DiamFin", "Longueur", "Contact", 
          "Chablis", "StadeD", "StadeE", "Observation"
        ], 
        "Reperes": [
          "NumDisp", "NumPlac", "Azimut", 
          "Dist", "Diam", "Repere", "Observation"
        ]
      }
    return allColumnObject[sheetName]

# Fonction d'encodage en Json
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)