from geonature.utils.env import DB
import json
import numpy as np
from .models import TDispositifs, TPlacettes, TArbres, TCycles, \
    CorCyclesPlacettes, TArbresMesures, TReperes, BibEssences, TRegenerations,\
    TBmSup30,TBmSup30Mesures, TTransects, dispositifs_area_assoc
from .pr_psdrf_staging_functions.models_staging import TDispositifsStaging, TPlacettesStaging, TArbresStaging, TCyclesStaging, \
    CorCyclesPlacettesStaging, TArbresMesuresStaging, TReperesStaging, TRegenerationsStaging,\
    TBmSup30Staging,TBmSup30MesuresStaging, TTransectsStaging, dispositifs_area_assoc
from .geonature_PSDRF_function import get_id_type_from_mnemonique, get_cd_nomenclature_from_id_type_and_id_nomenclature
from datetime import date, datetime

def bddToExcel(dispId, database='production'):
    if database == 'production':
        db_session = DB.session
        TDispositifsTemp = TDispositifs
        TPlacettesTemp = TPlacettes
        TReperesTemp = TReperes
        TCyclesTemp = TCycles
        CorCyclesPlacettesTemp = CorCyclesPlacettes
        TArbresTemp = TArbres
        TArbresMesuresTemp = TArbresMesures
        TRegenerationsTemp = TRegenerations
        TTransectsTemp = TTransects
        TBmSup30Temp = TBmSup30
        TBmSup30MesuresTemp = TBmSup30Mesures
    else:
        db_session = DB.session
        TDispositifsTemp = TDispositifsStaging
        TPlacettesTemp = TPlacettesStaging
        TReperesTemp = TReperesStaging
        TCyclesTemp = TCyclesStaging
        CorCyclesPlacettesTemp = CorCyclesPlacettesStaging
        TArbresTemp = TArbresStaging
        TArbresMesuresTemp = TArbresMesuresStaging
        TRegenerationsTemp = TRegenerationsStaging
        TTransectsTemp = TTransectsStaging
        TBmSup30Temp = TBmSup30Staging
        TBmSup30MesuresTemp = TBmSup30MesuresStaging

    id_type_durete = get_id_type_from_mnemonique("PSDRF_DURETE")
    id_type_ecorce = get_id_type_from_mnemonique("PSDRF_ECORCE")

    placettesQuery = db_session.query(
        TPlacettesTemp.id_dispositif, TPlacettesTemp.id_placette_orig, TCyclesTemp.num_cycle, TPlacettesTemp.strate, TPlacettesTemp.poids_placette,
        TPlacettesTemp.pente, TPlacettesTemp.correction_pente, TPlacettesTemp.exposition, TPlacettesTemp.habitat,
        TPlacettesTemp.station, TPlacettesTemp.typologie, TPlacettesTemp.groupe,
        TPlacettesTemp.groupe1, TPlacettesTemp.groupe2, TPlacettesTemp.ref_habitat, TPlacettesTemp.precision_habitat,
        TPlacettesTemp.ref_station, TPlacettesTemp.ref_typologie, TPlacettesTemp.descriptif_groupe, TPlacettesTemp.descriptif_groupe1,
        TPlacettesTemp.descriptif_groupe2,
        CorCyclesPlacettesTemp.date_intervention, CorCyclesPlacettesTemp.nature_intervention,
        CorCyclesPlacettesTemp.gestion_placette, TPlacettesTemp.precision_gps, TPlacettesTemp.cheminement
        ).filter(
            (TPlacettesTemp.id_dispositif == dispId)
        ).join(
            CorCyclesPlacettesTemp, CorCyclesPlacettesTemp.id_placette == TPlacettesTemp.id_placette
        ).join(
            TCyclesTemp, TCyclesTemp.id_cycle == CorCyclesPlacettesTemp.id_cycle
        )
    Placettes = [placette for placette in placettesQuery]

    cyclesQuery = db_session.query(
        TPlacettesTemp.id_dispositif, TPlacettesTemp.id_placette_orig, TCyclesTemp.num_cycle,
        CorCyclesPlacettesTemp.coeff, CorCyclesPlacettesTemp.date_releve, CorCyclesPlacettesTemp.diam_lim, CorCyclesPlacettesTemp.annee
                ).filter(
                    (TPlacettesTemp.id_dispositif == dispId)
                ).join(
                    CorCyclesPlacettesTemp, CorCyclesPlacettesTemp.id_placette == TPlacettesTemp.id_placette
                ).join(
                    TCyclesTemp, TCyclesTemp.id_cycle == CorCyclesPlacettesTemp.id_cycle
                )
    Cycles = [cycle for cycle in cyclesQuery]

    arbresQuery = db_session.query(
        TPlacettesTemp.id_dispositif, TPlacettesTemp.id_placette_orig, 
        TCyclesTemp.num_cycle, TArbresTemp.id_arbre_orig, TArbresTemp.code_essence, TArbresTemp.azimut,
        TArbresTemp.distance, TArbresMesuresTemp.diametre1, TArbresMesuresTemp.diametre2, 
        TArbresMesuresTemp.type, TArbresMesuresTemp.hauteur_totale, 
        TArbresMesuresTemp.stade_durete, 
        TArbresMesuresTemp.stade_ecorce,
        TArbresTemp.taillis, TArbresMesuresTemp.coupe, TArbresMesuresTemp.limite, 
        TArbresMesuresTemp.code_ecolo, TArbresMesuresTemp.ref_code_ecolo, 
        TArbresMesuresTemp.observation
        ).filter(
            (TPlacettesTemp.id_dispositif == dispId)
        ).join(
            TArbresTemp, TArbresTemp.id_placette == TPlacettesTemp.id_placette
        ).join(
            TArbresMesuresTemp
        ).join(
            TCyclesTemp, TCyclesTemp.id_cycle == TArbresMesuresTemp.id_cycle
        )
    Arbres = [arbre for arbre in arbresQuery]
    Arbres = [cdNomemclatureEdition(arbre, 11, 12, id_type_durete, id_type_ecorce) for arbre in Arbres]

    regesQuery = db_session.query(
        TPlacettesTemp.id_dispositif, TPlacettesTemp.id_placette_orig, TRegenerationsTemp.sous_placette,
            TCyclesTemp.num_cycle, TRegenerationsTemp.code_essence, TRegenerationsTemp.recouvrement,
            TRegenerationsTemp.classe1, TRegenerationsTemp.classe2, TRegenerationsTemp.classe3, 
            TRegenerationsTemp.taillis, TRegenerationsTemp.abroutissement, TRegenerationsTemp.observation
        ).filter(
            (TPlacettesTemp.id_dispositif == dispId)
        ).join(
            CorCyclesPlacettesTemp, CorCyclesPlacettesTemp.id_placette == TPlacettesTemp.id_placette
        ).join(
            TCyclesTemp, TCyclesTemp.id_cycle == CorCyclesPlacettesTemp.id_cycle
        ).join(
            TRegenerationsTemp, TRegenerationsTemp.id_cycle_placette == CorCyclesPlacettesTemp.id_cycle_placette
        )
    Regenerations = [rege for rege in regesQuery]

    transectsQuery = db_session.query(
        TPlacettesTemp.id_dispositif, TPlacettesTemp.id_placette_orig, TTransectsTemp.id_transect_orig,
        TCyclesTemp.num_cycle, TTransectsTemp.ref_transect, TTransectsTemp.code_essence, TTransectsTemp.distance,
        TTransectsTemp.diametre, TTransectsTemp.angle, TTransectsTemp.contact,  TTransectsTemp.chablis, 
        TTransectsTemp.stade_durete, 
        TTransectsTemp.stade_ecorce,
        TTransectsTemp.observation
        ).filter(
            (TPlacettesTemp.id_dispositif == dispId)
        ).join(
            CorCyclesPlacettesTemp, CorCyclesPlacettesTemp.id_placette == TPlacettesTemp.id_placette
        ).join(
            TCyclesTemp, TCyclesTemp.id_cycle == CorCyclesPlacettesTemp.id_cycle
        ).join(
            TTransectsTemp, TTransectsTemp.id_cycle_placette == CorCyclesPlacettesTemp.id_cycle_placette
        )
    Transects = [transect for transect in transectsQuery]
    Transects = [cdNomemclatureEdition(transect, 11, 12, id_type_durete, id_type_ecorce) for transect in Transects]

    bmsQuery = db_session.query(
        TPlacettesTemp.id_dispositif, TPlacettesTemp.id_placette_orig, TBmSup30Temp.id_bm_sup_30_orig,
        TBmSup30Temp.id_arbre, TCyclesTemp.num_cycle, TBmSup30Temp.code_essence, TBmSup30Temp.azimut,
        TBmSup30Temp.distance, TBmSup30MesuresTemp.diametre_ini, TBmSup30MesuresTemp.diametre_med,
        TBmSup30MesuresTemp.diametre_fin, TBmSup30MesuresTemp.longueur, TBmSup30MesuresTemp.contact,
        TBmSup30MesuresTemp.chablis, 
        TBmSup30MesuresTemp.stade_durete,
        TBmSup30MesuresTemp.stade_ecorce,
        TBmSup30MesuresTemp.observation
        ).filter(
            (TPlacettesTemp.id_dispositif == dispId)
        ).join(
            TBmSup30Temp, TBmSup30Temp.id_placette == TPlacettesTemp.id_placette
        ).join(
            TBmSup30MesuresTemp
        ).join(
            TCyclesTemp, TCyclesTemp.id_cycle == TBmSup30MesuresTemp.id_cycle
        )
    BMSsup30 = [bms for bms in bmsQuery]
    BMSsup30 = [cdNomemclatureEdition(bms, 14, 15, id_type_durete, id_type_ecorce) for bms in BMSsup30]


    reperesQuery = db_session.query(
        TPlacettesTemp.id_dispositif, TPlacettesTemp.id_placette_orig, TReperesTemp.azimut,
        TReperesTemp.distance, TReperesTemp.diametre, TReperesTemp.repere, TReperesTemp.observation
        ).filter(
            (TPlacettesTemp.id_dispositif == dispId)
        ).join(
            TReperesTemp, TReperesTemp.id_placette == TPlacettesTemp.id_placette
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
    excelJson = json.dumps(excelData, cls=NumpyEncoder, default=json_serial)
    
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
