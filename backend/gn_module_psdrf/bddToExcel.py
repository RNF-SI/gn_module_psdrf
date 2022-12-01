from geonature.utils.env import DB
import json
import numpy as np
from .models import TDispositifs, TPlacettes, TArbres, TCycles, \
    CorCyclesPlacettes, TArbresMesures, TReperes, BibEssences, TRegenerations,\
    TBmSup30,TBmSup30Mesures, TTransects, dispositifs_area_assoc
from .geonature_PSDRF_function import get_id_type_from_mnemonique, get_cd_nomenclature_from_id_type_and_id_nomenclature
from datetime import date, datetime


def bddToExcel(dispId):

    id_type_durete = get_id_type_from_mnemonique("PSDRF_DURETE")
    id_type_ecorce = get_id_type_from_mnemonique("PSDRF_ECORCE")

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
        TCycles.coeff, CorCyclesPlacettes.date_releve, TCycles.diam_lim, CorCyclesPlacettes.annee
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
        TCycles.num_cycle, TArbres.id_arbre_orig, TArbres.code_essence, TArbres.azimut,
        TArbres.distance, TArbresMesures.diametre1, TArbresMesures.diametre2, 
        TArbresMesures.type, TArbresMesures.hauteur_totale, 
        TArbresMesures.stade_durete, 
        TArbresMesures.stade_ecorce,
        TArbres.taillis, TArbresMesures.coupe, TArbresMesures.limite, 
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
    Arbres = [cdNomemclatureEdition(arbre, 11, 12, id_type_durete, id_type_ecorce) for arbre in Arbres]

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
        )
    Transects = [transect for transect in transectsQuery]
    Transects = [cdNomemclatureEdition(transect, 11, 12, id_type_durete, id_type_ecorce) for transect in Transects]

    bmsQuery = DB.session.query(
        TPlacettes.id_dispositif, TPlacettes.id_placette_orig, TBmSup30.id_bm_sup_30_orig,
        TBmSup30.id_arbre, TCycles.num_cycle, TBmSup30.code_essence, TBmSup30.azimut,
        TBmSup30.distance, TBmSup30Mesures.diametre_ini, TBmSup30Mesures.diametre_med,
        TBmSup30Mesures.diametre_fin, TBmSup30Mesures.longueur, TBmSup30Mesures.contact,
        TBmSup30Mesures.chablis, 
        TBmSup30Mesures.stade_durete,
        TBmSup30Mesures.stade_ecorce,
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
    BMSsup30 = [cdNomemclatureEdition(bms, 14, 15, id_type_durete, id_type_ecorce) for bms in BMSsup30]


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
    excelJson = json.dumps(excelData, cls=NumpyEncoder,default=json_serial)
   
    return excelJson 

def convertToJsonObject(sheetName, tuples):
    finalObj = []
    columnNamesObj = getColumnObject(sheetName)
    columnNames = columnNamesObj["Columns"]
    booleanColumnNames = columnNamesObj["BooleanColumn"]
    for tuple in tuples:
        listObj = list(tuple)
        obj = {}
        for i in range(len(listObj)):
            if columnNames[i] in booleanColumnNames: 
                if listObj[i] == True:
                    obj[columnNames[i]] = "t"
                else:
                    obj[columnNames[i]] = "f"
            else:
                obj[columnNames[i]]= listObj[i]
        finalObj.append(obj)
    return finalObj


def getColumnObject(sheetName):
    allColumnObject = { 
        "Placettes": {
            "Columns": [
                "NumDisp", "NumPlac", "Cycle", "Strate", "PoidsPlacette", "Pente", "CorrectionPente", 
                "Exposition", "Habitat", "Station", "Typologie", "Groupe", "Groupe1", 
                "Groupe2", "Ref_Habitat", "Precision_Habitat", "Ref_Station", 
                "Ref_Typologie", "Descriptif_Groupe", "Descriptif_Groupe1", 
                "Descriptif_Groupe2", "Date_Intervention", "Nature_Intervention", 
                "Gestion", "PrecisionGPS", "Cheminement"
                ], 
            "BooleanColumn": [
                "CorrectionPente"    
            ]
        },
        "Cycles": {
            "Columns": [
                "NumDisp", "NumPlac", "Cycle", "Coeff", "Date", "DiamLim", "Année"
                ],
            "BooleanColumn": [  
            ]
        }, 
        "Arbres": {
            "Columns":[  
                "NumDisp", "NumPlac", "Cycle", "NumArbre", "Essence", "Azimut", "Dist", "Diam1", "Diam2", 
                "Type", "Haut", "StadeD", "StadeE", "Taillis", "Coupe", "Limite", "CodeEcolo", 
                "Ref_CodeEcolo", "Observation"
            ], 
            "BooleanColumn": [  
                "Taillis", "Limite"
            ]
        },
        "Rege": {
            "Columns":[
                "NumDisp", "NumPlac", "SsPlac", 
                "Cycle", "Essence", "Recouv", "Class1", "Class2", 
                "Class3", "Taillis", "Abroutis", "Observation"
            ],
            "BooleanColumn": [  
                "Taillis", "Abroutis"
            ]
        },
        "Transects":{
            "Columns":[  
                "NumDisp", "NumPlac", "Id", "Cycle", "Transect", 
                "Essence", "Dist", "Diam", "Angle", "Contact", 
                "Chablis", "StadeD", "StadeE", "Observation"
            ], 
            "BooleanColumn": [  
                "Contact", "Chablis"
            ]
        },
        "BMSsup30":{
            "Columns":[
                "NumDisp", "NumPlac", "Id", "NumArbre", 
                "Cycle", "Essence", "Azimut", "Dist", "DiamIni", 
                "DiamMed", "DiamFin", "Longueur", "Contact", 
                "Chablis", "StadeD", "StadeE", "Observation"
            ], 
            "BooleanColumn": [  
                "Chablis"
            ]
        },
        "Reperes": {
            "Columns": [
                "NumDisp", "NumPlac", "Azimut", 
                "Dist", "Diam", "Repere", "Observation"
            ],
            "BooleanColumn": [  
            ]
        }
      }
    return allColumnObject[sheetName]

def cdNomemclatureEdition(obj, stadeDIdx, stadeEIdx, id_type_durete, id_type_ecorce):
    finalObjtemp = list(obj)
    if (finalObjtemp[stadeDIdx] != None):
        finalObjtemp[stadeDIdx] = get_cd_nomenclature_from_id_type_and_id_nomenclature(id_type_durete, finalObjtemp[stadeDIdx])
    
    if(finalObjtemp[stadeEIdx] != None):
        finalObjtemp[stadeEIdx] = get_cd_nomenclature_from_id_type_and_id_nomenclature(id_type_ecorce, finalObjtemp[stadeEIdx])
    
    finalObj = tuple(finalObjtemp)

    return finalObj

# Fonction d'encodage en Json
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.strftime("%d/%m/%Y")
    raise TypeError ("Type %s not serializable" % type(obj))