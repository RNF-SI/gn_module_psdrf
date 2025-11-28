import json
import pandas as pd
from sqlalchemy.sql.expression import false, null
from geonature.utils.env import DB
from .models import TDispositifs, TPlacettes, TArbres, TCycles, \
    CorCyclesPlacettes, TArbresMesures, TReperes, BibEssences, TRegenerations, TBmSup30,TBmSup30Mesures, TTransects
from .geonature_PSDRF_function import get_id_type_from_mnemonique, get_id_nomenclature_from_id_type_and_cd_nomenclature
from datetime import datetime
from math import isnan

import traceback

def data_integration(dispId, dispName, data):
    try:
        

        Placettes = data[0]
        Cycles = data[1]
        Arbres = data[2]
        Regeneration = data[3]
        Transect = data[4]
        BMSsup30 = data[5]
        Reperes = data[6]

        # Arreter si le dispositif n'existe pas dans la bdd (donc n'est pas dans PSDRFListe) 
        id_dispositif = int(dispId)
        if( DB.session.query(TDispositifs.id_dispositif).filter_by(id_dispositif=id_dispositif).first() is not None):
            TPlacettes.query.filter_by(id_dispositif=id_dispositif).delete()
            # TCycles.query.filter_by(id_dispositif=id_dispositif).delete()
            DB.session.commit()
        else : 
            return (json.dumps({'success': False, "message":"Le dispositif n'a pas ete prealablement ajoute a la table des dispositif. Veuillez contacter un administrateur."}), 500, {'ContentType':'application/json'})
        # Arreter si tous les cycles du dispositif ne sont pas dans la table des cycles de la bdd (donc dans PSDRFListe)
        # Créer la liste de cycle du dispositif (numCycle)
        cycleList = []
        for cycle in Cycles:
            if int(cycle["Cycle"]) not in cycleList:
                cycleList.append(int(cycle['Cycle']))
        print('r')
        # print(DB.session.query(TCycles.id_cycle).filter_by(id_dispositif=id_dispositif, num_cycle=cycle).first())
        print('r')

        # Vérifier que tous les cycles du dispositif sont dans la table des cycles de la bdd
        for cycle in cycleList:
            print(cycle)
            if( DB.session.query(TCycles.id_cycle).filter_by(id_dispositif=id_dispositif, num_cycle=cycle).first() is None):
                return (json.dumps({'success': False, "message":"Le cycle "+str(cycle)+" pour le dispositif "+ str(id_dispositif) +" n'a pas ete prealablement ajoute a la table des cycles. Veuillez contacter un administrateur."}), 500, {'ContentType':'application/json'})
            else: 
                print("Le cycle "+str(cycle)+" pour le dispositif "+ str(id_dispositif) +" est bien présent dans la table des cycles de la bdd")

        print("Tous les cycles du fichiers sont bien présent dans la table des cycles de la bdd")

        try: 
            # Placettes 
            newPlacettesList = []
            placettesIdOrigInDisp = []
            for placette in Placettes:
                if placette["NumPlac"] not in placettesIdOrigInDisp:
                    newPlacettesList.append(TPlacettes(
                        id_dispositif= int(id_dispositif),
                        id_placette_orig= placette['NumPlac'],
                        strate= int(placette['Strate']) if placette['Strate'] else None,
                        pente= float(placette['Pente']) if placette['Pente'] else None,
                        poids_placette= float(placette['PoidsPlacette']) if placette['PoidsPlacette'] else None,
                        correction_pente= True if placette['CorrectionPente'] =='t' else False if placette['CorrectionPente'] =='f' else placette['CorrectionPente'],
                        exposition= int(placette['Exposition']) if placette['Exposition'] else None,
                        habitat= placette["Habitat"],
                        station= placette["Station"],
                        typologie= placette["Typologie"],
                        groupe= placette["Groupe"],
                        groupe1= placette["Groupe1"],
                        groupe2= placette["Groupe2"],
                        ref_habitat= placette["Ref_Habitat"],
                        precision_habitat= placette["Precision_Habitat"],
                        ref_station= placette["Ref_Station"],
                        ref_typologie= placette["Ref_Typologie"],
                        descriptif_groupe= placette["Descriptif_Groupe"],
                        descriptif_groupe1= placette["Descriptif_Groupe1"],
                        descriptif_groupe2= placette["Descriptif_Groupe2"],
                        )
                    )
                    placettesIdOrigInDisp.append(placette['NumPlac'])
            DB.session.bulk_save_objects(newPlacettesList)
            DB.session.flush()
        except Exception as e:
            tb_str = traceback.format_exception(Exception, e, e.__traceback__)
            message = ''.join(tb_str)
            return (json.dumps({'success': False, "message":"Erreur lors de l'insertion des placettes dans la bdd. Veuillez contacter un administrateur.", "error_detail": message}), 500, {'ContentType':'application/json'})

        try:
            # Reperes 
            newReperesList = []
            for repere in Reperes:
                if repere["NumPlac"]:
                    idPlacette_repere_row = (
                        DB.session.query(TPlacettes.id_placette)
                        .filter((TPlacettes.id_placette_orig == repere["NumPlac"]) & (TPlacettes.id_dispositif == id_dispositif))
                        .one()
                    )
                    # Extract scalar value from Row object
                    idPlacette_repere = idPlacette_repere_row[0]

                    if repere["Azimut"]:
                        repere["Azimut"] = float(repere["Azimut"].replace(',', '.'))
                    if repere["Dist"]:
                        repere["Dist"] = float(repere["Dist"].replace(',', '.'))
                    if repere["Diam"]:
                        repere["Diam"] = float(repere["Diam"].replace(',', '.'))

                    newReperesList.append(TReperes(
                        id_placette=idPlacette_repere,
                        azimut=repere["Azimut"],
                        distance=repere["Dist"],
                        diametre=repere["Diam"],
                        repere=repere["Repere"],
                        observation=repere["Observation"]
                    ))

            DB.session.bulk_save_objects(newReperesList)
            DB.session.flush()
        except Exception as e:
            tb_str = traceback.format_exception(Exception, e, e.__traceback__)
            message = ''.join(tb_str)
            return (json.dumps({'success': False, "message": "Erreur lors de l'insertion des reperes dans la bdd. Veuillez contacter un administrateur.", "error_detail": message}), 500, {'ContentType': 'application/json'})
        # CorCyclePlacettes
        # Récupérer les cycles présents dans le dispositif
        try:
            new_cor_cycle_placette_array = []
            for cycle in Cycles:
                placette_id_row = DB.session.query(TPlacettes.id_placette).filter(
                    (TPlacettes.id_dispositif == id_dispositif) & (TPlacettes.id_placette_orig == cycle["NumPlac"])
                ).one()
                cycle_id_row = DB.session.query(TCycles.id_cycle).filter(
                    (TCycles.id_dispositif == id_dispositif) & (TCycles.num_cycle == int(cycle["Cycle"]))
                ).one()

                # Extract scalar values
                placette_id = placette_id_row[0]
                cycle_id = cycle_id_row[0]

                for placette in Placettes:
                    if ((str(placette["NumPlac"]) == str(cycle["NumPlac"])) & (int(cycle["Cycle"]) == int(placette["Cycle"]))):
                        new_cor_cycle_placette = CorCyclesPlacettes(
                            id_cycle=cycle_id,
                            id_placette=placette_id,
                            date_releve=datetime.strptime(cycle["Date"], '%d/%m/%Y') if cycle["Date"] else cycle["Date"],
                            annee=cycle["Ann\u00E9e"],
                            date_intervention=placette["Date_Intervention"],
                            nature_intervention=placette["Nature_Intervention"],
                            gestion_placette=placette["Gestion"],
                            coeff=int(cycle["Coeff"]) if cycle["Coeff"] else None,
                            diam_lim=float(cycle["DiamLim"]) if cycle["DiamLim"] else None,
                        )
                        new_cor_cycle_placette_array.append(new_cor_cycle_placette)
            DB.session.bulk_save_objects(new_cor_cycle_placette_array)
            DB.session.flush()
        except Exception as e:
            print(e)
            tb_str = traceback.format_exception(Exception, e, e.__traceback__)
            message = ''.join(tb_str)
            return (json.dumps({'success': False, "message": "Erreur lors de l'insertion des cor_cycles_placette dans la bdd. Veuillez contacter un administrateur.", "error_detail": message}), 500, {'ContentType': 'application/json'})


        # #CorCyclesRoles
        # TODO: Remplir avec userHub

        #TArbres
        try:
            new_arbres_array = []
            list_arbres_id = []
            for arbre in Arbres:
                if (str(arbre["NumPlac"]), int(arbre["NumArbre"]))  not in list_arbres_id:

                    placette_id = DB.session.query(TPlacettes.id_placette).filter(
                        (TPlacettes.id_dispositif == id_dispositif) & (TPlacettes.id_placette_orig == str(arbre["NumPlac"]))
                    ).one()[0]
                    arbre["Azimut"]=float(arbre["Azimut"].replace(',', '.'))
                    arbre["Dist"]=float(arbre["Dist"].replace(',', '.'))
                    new_arbre = TArbres(
                        id_arbre_orig = int(arbre["NumArbre"]),
                        id_placette =  placette_id,
                        code_essence = arbre["Essence"],
                        azimut = arbre["Azimut"],
                        distance = arbre["Dist"],
                        taillis = True if arbre['Taillis'] =='t' else False if arbre['Taillis'] =='f' else arbre['Taillis'],
                        observation = arbre["Observation"]
                    )
                    new_arbres_array.append(new_arbre)
                    list_arbres_id.append((str(arbre["NumPlac"]), int(arbre["NumArbre"])))
            DB.session.bulk_save_objects(new_arbres_array)
            DB.session.flush()
        except Exception as e:
            tb_str = traceback.format_exception(Exception, e, e.__traceback__)
            message = ''.join(tb_str)
            return (json.dumps({'success': False, "message":"Erreur lors de l'insertion des arbres dans la bdd. Veuillez contacter un administrateur.", "error_detail": message}), 500, {'ContentType':'application/json'})


        # #TArbresMesurés
        try:
            new_arbres_mesures_array = []
            id_type_durete = get_id_type_from_mnemonique("PSDRF_DURETE")
            id_type_ecorce = get_id_type_from_mnemonique("PSDRF_ECORCE")

            # Pré-charger les placettes pour éviter les requêtes en boucle
            placettes_map = {}
            placettes_query = DB.session.query(TPlacettes.id_placette, TPlacettes.id_placette_orig).filter(
                TPlacettes.id_dispositif == id_dispositif
            ).all()
            for placette_id, placette_orig in placettes_query:
                placettes_map[str(placette_orig)] = placette_id

            # Pré-charger les cycles pour éviter les requêtes en boucle  
            cycles_map = {}
            cycles_query = DB.session.query(TCycles.id_cycle, TCycles.num_cycle).filter(
                TCycles.id_dispositif == id_dispositif
            ).all()
            for cycle_id, num_cycle in cycles_query:
                cycles_map[num_cycle] = cycle_id

            # Pré-charger les arbres pour éviter les requêtes en boucle
            arbres_map = {}
            arbres_query = DB.session.query(TArbres.id_arbre, TArbres.id_arbre_orig, TArbres.id_placette).join(
                TPlacettes, TArbres.id_placette == TPlacettes.id_placette
            ).filter(TPlacettes.id_dispositif == id_dispositif).all()
            for arbre_id, arbre_orig, placette_id in arbres_query:
                arbres_map[(arbre_orig, placette_id)] = arbre_id

            for arbre in Arbres:
                placette_id = placettes_map.get(str(arbre["NumPlac"]))
                if not placette_id:
                    continue
                
                arbre_id = arbres_map.get((int(arbre["NumArbre"]), placette_id))
                if not arbre_id:
                    continue
                
                cycle_id = cycles_map.get(int(arbre["Cycle"]))
                if not cycle_id:
                    continue

                if arbre["Diam1"]:
                    arbre["Diam1"] = float(arbre["Diam1"].replace(',', '.')) if isinstance(arbre["Diam1"], str) else float(arbre["Diam1"])
                if arbre["Diam2"]:
                    arbre["Diam2"] = float(arbre["Diam2"].replace(',', '.')) if isinstance(arbre["Diam2"], str) else float(arbre["Diam2"])
                if arbre["Haut"]:
                    arbre["Haut"] = float(arbre["Haut"].replace(',', '.')) if isinstance(arbre["Haut"], str) else float(arbre["Haut"])

                new_arbre_mesure = TArbresMesures(
                    id_arbre=arbre_id,
                    id_cycle=cycle_id,
                    diametre1=arbre["Diam1"],
                    diametre2=float(arbre["Diam2"]) if arbre["Diam2"] else None,
                    type=arbre["Type"],
                    hauteur_totale=float(arbre["Haut"]) if arbre["Haut"] else None,
                    stade_durete=get_id_nomenclature_from_id_type_and_cd_nomenclature(id_type_durete, arbre["StadeD"]) if arbre["StadeD"] else None,
                    stade_ecorce=get_id_nomenclature_from_id_type_and_cd_nomenclature(id_type_ecorce, arbre["StadeE"]) if arbre["StadeE"] else None,
                    coupe="C" if (arbre["Coupe"] == "chablis" or arbre["Coupe"] == "Chablis" or arbre["Coupe"] == "CHABLIS") else "E" if (arbre["Coupe"] == "exploité" or arbre["Coupe"] == "Exploité" or arbre["Coupe"] == "EXPLOITE") else arbre["Coupe"],
                    limite=True if arbre["Limite"] == "t" else False if arbre["Limite"] == "f" else False,
                    code_ecolo=arbre["CodeEcolo"],
                    ref_code_ecolo=arbre["Ref_CodeEcolo"],
                    observation=arbre["Observation"]
                )
                new_arbres_mesures_array.append(new_arbre_mesure)
            DB.session.bulk_save_objects(new_arbres_mesures_array)
            DB.session.flush()
        except Exception as e:
            tb_str = traceback.format_exception(Exception, e, e.__traceback__)
            message = ''.join(tb_str)
            return (json.dumps({'success': False, "message": "Erreur lors de l'insertion des arbres mesurés dans la bdd. Veuillez contacter un administrateur.", "error_detail": message}), 500, {'ContentType': 'application/json'})


        # TRegenerations
        try:
            listRege = []
            id_type_abroutis = get_id_type_from_mnemonique("PSDRF_ABROUTIS")
            for reges in Regeneration:
                placette_id_row = DB.session.query(TPlacettes.id_placette).filter(
                    (TPlacettes.id_dispositif == id_dispositif) & (TPlacettes.id_placette_orig == str(reges["NumPlac"]))
                ).one()
                placette_id = placette_id_row[0]

                cycle_id_row = DB.session.query(TCycles.id_cycle).filter(
                    (TCycles.num_cycle == reges["Cycle"]) & (TCycles.id_dispositif == id_dispositif)
                ).one()
                cycle_id = cycle_id_row[0]

                cycle_reges_id_row = DB.session.query(CorCyclesPlacettes.id_cycle_placette).filter(
                    (CorCyclesPlacettes.id_cycle == cycle_id) & (CorCyclesPlacettes.id_placette == placette_id)
                ).one()
                cycle_reges_id = cycle_reges_id_row[0]

                if reges["Class1"]:
                    reges["Class1"] = int(reges["Class1"])
                if reges["Class2"]:
                    reges["Class2"] = int(reges["Class2"])
                if reges["Class3"]:
                    reges["Class3"] = int(reges["Class3"])

                new_regeneration = TRegenerations(
                    id_cycle_placette=cycle_reges_id,
                    sous_placette=int(reges["SsPlac"]),
                    code_essence=reges["Essence"],
                    recouvrement=reges["Recouv"] if reges["Recouv"] else 0,
                    classe1=reges["Class1"],
                    classe2=reges["Class2"],
                    classe3=reges["Class3"],
                    taillis=True if reges["Taillis"] == "t" else False if ((reges["Taillis"] == "f") | (reges["Taillis"] == "0")) else reges["Taillis"],
                    abroutissement=True if reges["Abroutis"] == "t" else False if ((reges["Abroutis"] == "f") | (reges["Abroutis"] == "0")) else reges["Abroutis"],
                    observation=reges["Observation"]
                )
                listRege.append(new_regeneration)
            DB.session.bulk_save_objects(listRege)
            DB.session.flush()
        except Exception as e:
            tb_str = traceback.format_exception(Exception, e, e.__traceback__)
            message = ''.join(tb_str)
            return (json.dumps({'success': False, "message": "Erreur lors de l'insertion des regenerations dans la bdd. Veuillez contacter un administrateur.", "error_detail": message}), 500, {'ContentType': 'application/json'})

        
        # TCategories

        # BMSsup30
        try:
            list_bms_id = []
            bmsSup30List = []
            for bmsSup30 in BMSsup30:
                if (str(bmsSup30["NumPlac"]), int(bmsSup30["Id"])) not in list_bms_id:
                    placette_id_row = DB.session.query(TPlacettes.id_placette).filter(
                        (TPlacettes.id_dispositif == id_dispositif) & (TPlacettes.id_placette_orig == bmsSup30["NumPlac"])
                    ).one()
                    placette_id = placette_id_row[0]

                    if bmsSup30["Azimut"]:
                        bmsSup30["Azimut"] = float(bmsSup30["Azimut"].replace(',', '.'))
                    if bmsSup30["Dist"]:
                        bmsSup30["Dist"] = float(bmsSup30["Dist"].replace(',', '.'))

                    new_bmsSup30 = TBmSup30(
                        id_bm_sup_30_orig=int(bmsSup30["Id"]),
                        id_placette=placette_id,
                        id_arbre=int(bmsSup30["NumArbre"]) if bmsSup30["NumArbre"] else None,
                        code_essence=bmsSup30["Essence"],
                        azimut=bmsSup30["Azimut"],
                        distance=bmsSup30["Dist"],
                        observation=bmsSup30["Observation"]
                    )
                    bmsSup30List.append(new_bmsSup30)
                    list_bms_id.append((str(bmsSup30["NumPlac"]), int(bmsSup30["Id"])))
            DB.session.bulk_save_objects(bmsSup30List)
            DB.session.flush()
        except Exception as e:
            tb_str = traceback.format_exception(Exception, e, e.__traceback__)
            message = ''.join(tb_str)
            return (json.dumps({'success': False, "message": "Erreur lors de l'insertion des BMSsup30 dans la bdd. Veuillez contacter un administrateur.", "error_detail": message}), 500, {'ContentType': 'application/json'})

        # # # BMSsup30Mesurés
        try:
            bmsSup30MesuresList = []
            for bmsSup30 in BMSsup30:
                if bmsSup30["DiamIni"]:
                    bmsSup30["DiamIni"] = float(bmsSup30["DiamIni"].replace(',', '.')) if isinstance(bmsSup30["DiamIni"], str) else float(bmsSup30["DiamIni"])
                else:
                    bmsSup30["DiamIni"] = None
                if bmsSup30["DiamMed"]:
                    bmsSup30["DiamMed"] = float(bmsSup30["DiamMed"].replace(',', '.')) if isinstance(bmsSup30["DiamMed"], str) else float(bmsSup30["DiamMed"])
                else:
                    bmsSup30["DiamMed"] = None
                if bmsSup30["DiamFin"]:
                    bmsSup30["DiamFin"] = float(bmsSup30["DiamFin"].replace(',', '.')) if isinstance(bmsSup30["DiamFin"], str) else float(bmsSup30["DiamFin"])
                else:
                    bmsSup30["DiamFin"] = None
                if bmsSup30["Longueur"]:
                    bmsSup30["Longueur"] = float(bmsSup30["Longueur"].replace(',', '.'))
                if bmsSup30["Contact"] != "f":
                    bmsSup30["Contact"] = 0
                elif bmsSup30["Contact"] != "t":
                    bmsSup30["Contact"] = 51
                elif bmsSup30["Contact"]:
                    bmsSup30["Contact"] = float(bmsSup30["Contact"].replace(',', '.'))

                placette_id_row = DB.session.query(TPlacettes.id_placette).filter(
                    (TPlacettes.id_dispositif == id_dispositif) & (TPlacettes.id_placette_orig == bmsSup30["NumPlac"])
                ).one()
                placette_id = placette_id_row[0]

                bmsSup30_id_row = DB.session.query(TBmSup30.id_bm_sup_30).filter(
                    (TBmSup30.id_bm_sup_30_orig == bmsSup30["Id"]) & (TBmSup30.id_placette == placette_id)
                ).one()
                bmsSup30_id = bmsSup30_id_row[0]

                cycle_id_row = DB.session.query(TCycles.id_cycle).filter(
                    (TCycles.num_cycle == bmsSup30["Cycle"]) & (TCycles.id_dispositif == id_dispositif)
                ).one()
                cycle_id = cycle_id_row[0]

                new_bmsSup30Mesures = TBmSup30Mesures(
                    id_bm_sup_30=bmsSup30_id,
                    id_cycle=cycle_id,
                    diametre_ini=bmsSup30["DiamIni"],
                    diametre_med=bmsSup30["DiamMed"],
                    diametre_fin=bmsSup30["DiamFin"],
                    longueur=bmsSup30["Longueur"],
                    contact=bmsSup30["Contact"],
                    chablis=True if bmsSup30["Chablis"] == "t" else False if bmsSup30["Chablis"] == "f" else bmsSup30["Chablis"],
                    stade_durete=get_id_nomenclature_from_id_type_and_cd_nomenclature(id_type_durete, bmsSup30["StadeD"]) if bmsSup30["StadeD"] else None,
                    stade_ecorce=get_id_nomenclature_from_id_type_and_cd_nomenclature(id_type_ecorce, bmsSup30["StadeE"]) if bmsSup30["StadeE"] else None,
                    observation=bmsSup30["Observation"]
                )
                bmsSup30MesuresList.append(new_bmsSup30Mesures)
            DB.session.bulk_save_objects(bmsSup30MesuresList)
            DB.session.flush()
        except Exception as e:
            tb_str = traceback.format_exception(Exception, e, e.__traceback__)
            message = ''.join(tb_str)
            return (json.dumps({'success': False, "message": "Erreur lors de l'insertion des BMSsup30Mesures dans la bdd. Veuillez contacter un administrateur.", "error_detail": message}), 500, {'ContentType': 'application/json'})

        try:
            transectList = []
            for transect in Transect:
                placette_id_row = DB.session.query(TPlacettes.id_placette).filter(
                    (TPlacettes.id_dispositif == id_dispositif) & (TPlacettes.id_placette_orig == str(transect["NumPlac"]))
                ).one()
                placette_id = placette_id_row[0]

                cycle_id_row = DB.session.query(TCycles.id_cycle).filter(
                    (TCycles.num_cycle == transect["Cycle"]) & (TCycles.id_dispositif == id_dispositif)
                ).one()
                cycle_id = cycle_id_row[0]

                cycle_transect_id_row = DB.session.query(CorCyclesPlacettes.id_cycle_placette).filter(
                    (CorCyclesPlacettes.id_cycle == cycle_id) & (CorCyclesPlacettes.id_placette == placette_id)
                ).one()
                cycle_transect_id = cycle_transect_id_row[0]

                if transect["Dist"]:
                    transect["Dist"] = float(transect["Dist"].replace(',', '.'))
                if transect["Diam"]:
                    transect["Diam"] = float(transect["Diam"].replace(',', '.'))

                new_transect = TTransects(
                    id_cycle_placette=cycle_transect_id,
                    id_transect_orig=transect['Id'],
                    code_essence=transect['Essence'],
                    ref_transect=transect['Transect'],
                    distance=float(transect['Dist']) if transect['Dist'] else None,
                    diametre=float(transect['Diam']) if transect['Diam'] else None,
                    contact=True if transect["Contact"] == "t" else False if transect["Contact"] == "f" else transect["Contact"],
                    angle=transect['Angle'],
                    chablis=True if transect["Chablis"] == "t" else False if transect["Chablis"] == "f" else transect["Chablis"],
                    stade_durete=get_id_nomenclature_from_id_type_and_cd_nomenclature(id_type_durete, transect["StadeD"]) if transect["StadeD"] else None,
                    stade_ecorce=get_id_nomenclature_from_id_type_and_cd_nomenclature(id_type_ecorce, transect["StadeE"]) if transect["StadeE"] else None,
                    observation=transect['Observation']
                )
                transectList.append(new_transect)
            DB.session.bulk_save_objects(transectList)
            DB.session.flush()
        except Exception as e:
            tb_str = traceback.format_exception(Exception, e, e.__traceback__)
            message = ''.join(tb_str)
            return (json.dumps({'success': False, "message": "Erreur lors de l'insertion des transects dans la bdd. Veuillez contacter un administrateur.", "error_detail": message}), 500, {'ContentType': 'application/json'})

        DB.session.commit()
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
    except Exception as e:
        # Rollback and print error
        DB.session.rollback()
        print(e)
        tb_str = traceback.format_exception(Exception, e, e.__traceback__)
        message = ''.join(tb_str)
        return (json.dumps({'success': False, "message":"Une erreur inconnue a eu lieu. Veuillez contacter un administrateur.", "error_detail": message}), 500, {'ContentType':'application/json'})


