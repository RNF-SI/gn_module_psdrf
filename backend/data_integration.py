import json
import pandas as pd
from sqlalchemy.sql.expression import false, null
from geonature.utils.env import DB
from .models import TDispositifs, TPlacettes, TArbres, TCycles, \
    CorCyclesPlacettes, TArbresMesures, TReperes, BibEssences, TRegenerations, TBmSup30
from .geonature_PSDRF_function import get_id_type_from_mnemonique, get_id_nomenclature_from_id_type_and_cd_nomenclature
from datetime import datetime


def data_integration(data):
    Placettes = data[0]
    Cycles = data[1]
    Arbres = data[2]
    Regeneration = data[3]
    Transect = data[4]
    BMSsup30 = data[5]
    Reperes = data[6]

    id_dispositif = int(data[0][0]['NumDisp'])
    if( DB.session.query(TDispositifs.id_dispositif).filter_by(id_dispositif=id_dispositif).first() is not None):
        delete_obj = TDispositifs.query.filter_by(id_dispositif=id_dispositif).one()
        DB.session.delete(delete_obj)
        DB.session.commit()

    # # Dispositif
    # disp_request = DB.session.query(TDispositifs).all()
    # dispositifs = [disp.id_dispositif for disp in disp_request]

    # # TODO: Faire passer en argument num disp et id disp 
    # if id_dispositif in dispositifs:
    #     print("Ce dispositif existe déjà")
    # else :

    new_disp= TDispositifs( 
        id_dispositif = id_dispositif,
        name = 'Chalmessin',
        alluvial = False
    )
    DB.session.add(new_disp)
    DB.session.commit()

    # Placettes 
    newPlacettesList = []
    # Récupérer les placettes présentes dans le dispositif
    # placettes_in_disp = DB.session.query(TPlacettes.id_placette_orig).filter(
    #     TPlacettes.id_dispositif == id_dispositif
    # )
    # placettesIdOrigInDisp = [placette.id_placette_orig for placette in placettes_in_disp]
    placettesIdOrigInDisp = []
    # print(placettes_in_disp)
    # placettes_in_db_id_placette_orig = [placette.id_placette_orig for placette in placettes_in_disp]
    print(placettesIdOrigInDisp)
    for placette in Placettes:
        if placette["NumPlac"] not in placettesIdOrigInDisp:
            newPlacettesList.append(TPlacettes(
                id_dispositif=id_dispositif,
                id_placette_orig=placette['NumPlac'],
                strate=placette['Strate'],
                pente=placette['Pente'],
                poids_placette=placette['PoidsPlacette'],
                correction_pente= True if placette['CorrectionPente'] =='t' else False,
                exposition=placette['Exposition'],
                habitat=placette["Habitat"],
                station=placette["Station"],
                typologie=placette["Typologie"],
                groupe=placette["Groupe"],
                groupe1=placette["Groupe1"],
                groupe2=placette["Groupe2"],
                ref_habitat=placette["Ref_Habitat"],
                precision_habitat=placette["Precision_Habitat"],
                ref_station=placette["Ref_Station"],
                ref_typologie=placette["Ref_Typologie"],
                descriptif_groupe=placette["Descriptif_Groupe"],
                descriptif_groupe1=placette["Descriptif_Groupe1"],
                descriptif_groupe2=placette["Descriptif_Groupe2"],
                )
            )
            placettesIdOrigInDisp.append(placette['NumPlac'])
    DB.session.bulk_save_objects(newPlacettesList)
    DB.session.commit()


    # Reperes 
    # TODO: La méthode pour voir si le repère est déjà présent est elle bonne?
    newReperesList = []
    for repere in Reperes:
        idPlacette_repere = (
            DB.session.query(TPlacettes.id_placette)
            .filter((TPlacettes.id_placette_orig == repere["NumPlac"]) & (TPlacettes.id_dispositif == id_dispositif))
            .one()
        )
        repere["Azimut"]=float(repere["Azimut"].replace(',', '.'))
        repere["Dist"]=float(repere["Dist"].replace(',', '.'))
        repere["Diam"]=float(repere["Diam"].replace(',', '.'))

        # repereBoolean = DB.session.query(
        #         DB.session.query(TReperes)
        #         .filter((TReperes.id_placette == idPlacette_repere) & (TReperes.azimut == repere["Azimut"]) & (TReperes.distance == repere["Dist"]))
        #         .exists() 
        #     ).scalar()

        # DB.session.query(TDispositifs.id_dispositif).filter_by(id_dispositif=id_dispositif).first() is not None

        # if repereBoolean:
        #     print("Repere existe déjà dans la base de donnée")
        # else: 
        newReperesList.append(TReperes(
            id_placette = idPlacette_repere,
            azimut = repere["Azimut"], 
            distance = repere["Dist"],
            diametre = repere["Diam"],
            observation = repere["Observation"]
        ))
    DB.session.bulk_save_objects(newReperesList)
    DB.session.commit()

    # Cycle
    # Récupérer les cycles présents dans le dispositif
    # cycles_in_disp_Query = DB.session.query(TCycles.num_cycle).filter(
    #     TCycles.id_dispositif == id_dispositif
    # )
    # cycles_id_in_disp = [cycle.num_cycle for cycle in cycles_in_disp_Query]

    cycles_id_in_disp = []
    for cycle in Cycles:
        if int(cycle["Cycle"]) not in cycles_id_in_disp:
            # new_cycle =TCycles(
            #     id_dispositif = id_dispositif,
            #     num_cycle = cycle["Cycle"],
            #     coeff = cycle["Coeff"],
            #     date_debut = datetime.strptime(cycle["Date"], '%d/%m/%Y') if cycle["Date"] else None,
            #     date_fin = datetime.strptime(cycle["Date"], '%d/%m/%Y') if cycle["Date"] else None,
            #     diam_lim = cycle["DiamLim"]
            # )
            cycles_id_in_disp.append(int(cycle["Cycle"]))
            # print(cycles_id_in_disp)
            # DB.session.add(new_cycle)
            # DB.session.commit()

    for cycleNum in cycles_id_in_disp:
        min_date = None
        max_date = None
        for cycle in Cycles:
            if int(cycle["Cycle"]) == cycleNum:

                if cycle["Date"] is not None:
                    if  min_date is None:
                        min_date = datetime.strptime(cycle["Date"], '%d/%m/%Y')
                    elif (min_date > datetime.strptime(cycle["Date"], '%d/%m/%Y')):
                        min_date = datetime.strptime(cycle["Date"], '%d/%m/%Y')
                    if  max_date is None:
                        max_date = datetime.strptime(cycle["Date"], '%d/%m/%Y')
                    elif (max_date < datetime.strptime(cycle["Date"], '%d/%m/%Y')):
                        max_date = datetime.strptime(cycle["Date"], '%d/%m/%Y')
                diam_lim = cycle["DiamLim"]
                

        new_cycle =TCycles(
            id_dispositif = id_dispositif,
            num_cycle = cycleNum,
            coeff = cycle["Coeff"],
            date_debut = min_date,
            date_fin = max_date,
            diam_lim = diam_lim
        )    
        DB.session.add(new_cycle)
        DB.session.commit()   

        # tCycleQuery = DB.session.query(TCycles).filter(
        #     (TCycles.id_dispositif == id_dispositif) & (TCycles.num_cycle == cycleNum)
        # ).first()
        # tCycleQuery.date_debut = min_date
        # tCycleQuery.date_fin = max_date
        # DB.session.flush()
    # version de départ, ajout dans la base
    # cycles_in_disp_Query = DB.session.query(TCycles.num_cycle).filter(
    #     TCycles.id_dispositif == id_dispositif
    # )
    # cycles_id_in_disp = [cycle.num_cycle for cycle in cycles_in_disp_Query]
    # for cycle in Cycles:
    #     if int(cycle["Cycle"]) not in cycles_id_in_disp:
    #         new_cycle =TCycles(
    #             id_dispositif = id_dispositif,
    #             num_cycle = cycle["Cycle"],
    #             coeff = cycle["Coeff"],
    #             date_debut = datetime.strptime(cycle["Date"], '%d/%m/%Y') if cycle["Date"] else None,
    #             date_fin = datetime.strptime(cycle["Date"], '%d/%m/%Y') if cycle["Date"] else None,
    #             diam_lim = cycle["DiamLim"]
    #         )
    #         cycles_id_in_disp.append(int(cycle["Cycle"]))
    #         print(cycles_id_in_disp)
    #         DB.session.add(new_cycle)
    #         DB.session.commit()

    # for cycleNum in cycles_id_in_disp:
    #     min_date = None
    #     max_date = None
    #     for cycle in Cycles:
    #         if int(cycle["Cycle"]) == cycleNum:

    #             if cycle["Date"] is not None:
    #                 if  min_date is None:
    #                     min_date = datetime.strptime(cycle["Date"], '%d/%m/%Y')
    #                 elif (min_date > datetime.strptime(cycle["Date"], '%d/%m/%Y')):
    #                     min_date = datetime.strptime(cycle["Date"], '%d/%m/%Y')
    #                 if  max_date is None:
    #                     max_date = datetime.strptime(cycle["Date"], '%d/%m/%Y')
    #                 elif (max_date < datetime.strptime(cycle["Date"], '%d/%m/%Y')):
    #                     max_date = datetime.strptime(cycle["Date"], '%d/%m/%Y')

    #     tCycleQuery = DB.session.query(TCycles).filter(
    #         (TCycles.id_dispositif == id_dispositif) & (TCycles.num_cycle == cycleNum)
    #     ).first()
    #     tCycleQuery.date_debut = min_date
    #     tCycleQuery.date_fin = max_date
    #     DB.session.flush()
    
    

    # #VERSION AVEC différents fichiers excel
    # #  
    # # for cycle in Cycles:
    # #     if cycle not in cycles_id_in_disp:
    # #         new_cycle =TCycles(
    # #             id_dispositif = id_dispositif,
    # #             num_cycle = cycle["Cycle"],
    # #             coeff = cycle["Coeff"],
    # #             date_debut = min_date,
    # #             date_fin = max_date,
    # #             diam_lim = cycle["DiamLim"]
    # #         )
    # #         cycles_id_in_disp.append(cycle["Cycle"])
    # #         DB.session.add(new_cycle)
    # #         DB.session.flush()

    # # for cycleNum in cycles_id_in_disp:
    # #     tCycleQuery = DB.session.query(TCycles).filter(
    # #         (TCycles.id_dispositif == id_dispositif) & (TCycles.num_cycle == cycleNum).first()
    # #     )
    # #     print(tCycleQuery)
    # #     min_date = tCycleQuery.date_debut
    # #     max_date = tCycleQuery.date_fin
    # #     for cycle in Cycles:
    # #         if cycleNum==cycle["Cycle"]:
    # #             if(min_date & max_date):
    # #                 if cycle["Date"]:
    # #                     date_time_obj = datetime.strptime(cycle["Date"], '%d/%m/%y')
    # #                     if min_date > date_time_obj:
    # #                         min_date = date_time_obj
    # #                         tCycleQuery.date_debut = min_date
    # #                     if max_date < date_time_obj:
    # #                         max_date = date_time_obj
    # #                         tCycleQuery.date_fin = max_date
    # #                     DB.session.flush()
    # #             else: 
    # #                 if cycle["Date"]:
    # #                     date_time_obj = datetime.strptime(cycle["Date"], '%d/%m/%y')
    # #                     tCycleQuery.date_debut = date_time_obj
    # #                     tCycleQuery.date_fin = date_time_obj
    # #                     DB.session.flush()

      

    # # if cycle["Cycle"] in cycles_in_disp:
    # #     print("Cycle numéro" + cycle["Cycle"]+ " existe déjà dans la base de donnée")
    # # else:
    # #     new_cycle =TCycles(
    # #         id_dispositif = id_dispositif,
    # #         num_cycle = cycle["Cycle"],
    # #         coeff = cycle["Coeff"],
    # #         date_debut = cycle[""]
    # #         date_fin = 
    # #         diam_lim = cycle["DiamLim"],
    # #     ))
    # #     cycles_in_disp.append(cycle['Cycle'])
        
    # # DB.session.add(new_cycle)

    # # if newPlacettesList :
    # #     DB.session.bulk_save_objects(newPlacettesList)
    # #     DB.session.flush()
    
    # CorCyclePlacettes
    # Récupérer les cycles présents dans le dispositif
    new_cor_cycle_placette_array = []
    for cycle in Cycles:       
        placette_id = DB.session.query(TPlacettes.id_placette).filter(
            (TPlacettes.id_dispositif == id_dispositif) & (TPlacettes.id_placette_orig == cycle["NumPlac"])
        ).one()
        cycle_id = DB.session.query(TCycles.id_cycle).filter(
            (TCycles.id_dispositif == id_dispositif) & (TCycles.num_cycle == int(cycle["Cycle"]))
        ).one()
        # placettesIdOrigInDisp = [placette.id_placette_orig for placette in placettes_in_disp]

        # placettes_in_cor_cycle_placettes_Query = DB.session.query(CorCyclesPlacettes.id_placette).filter(
        #     CorCyclesPlacettes.id_placette == placette_id
        # )
        # placettes_id_in_cor_cycle_placettes = [cycle.id_cycle for cycle in placettes_in_cor_cycle_placettes_Query]

        # cycles_in_cor_cycle_placettes_Query = DB.session.query(CorCyclesPlacettes.id_cycle).filter(
        #     CorCyclesPlacettes.id_cycle == cycle_id
        # )
        # cycles_id_in_cor_cycle_placettes = [cycle.id_cycle for cycle in cycles_in_cor_cycle_placettes_Query]

        # if (int(cycle["Cycle"]) not in placettes_id_in_cor_cycle_placettes) & (int(cycle["Cycle"]) not in placettes_id_in_cor_cycle_placettes):

        for placette in Placettes:
            if ((int(placette["NumPlac"])==int(cycle["NumPlac"])) & (int(cycle["Cycle"])==int(placette["Cycle"]))):
                new_cor_cycle_placette =CorCyclesPlacettes(
                    id_cycle = cycle_id,
                    id_placette = placette_id,
                    date_releve = datetime.strptime(cycle["Date"], '%d/%m/%Y') if cycle["Date"] else cycle["Date"],
                    date_intervention = placette["Date_Intervention"],
                    nature_intervention = placette["Nature_Intervention"],
                    gestion_placette = placette["Gestion"]
                )
                new_cor_cycle_placette_array.append(new_cor_cycle_placette)
    DB.session.bulk_save_objects(new_cor_cycle_placette_array)
    DB.session.commit()


    # # BibEssences

    # #CorCyclesRoles
    

    #TArbres
    new_arbres_array = []
    list_arbres_id = []

    for arbre in Arbres:
        # print(arbre["NumPlac"])
        # print(type(arbre["NumPlac"]))

        if (int(arbre["NumPlac"]), int(arbre["NumArbre"]))  not in list_arbres_id:

            placette_id = DB.session.query(TPlacettes.id_placette).filter(
                (TPlacettes.id_dispositif == id_dispositif) & (TPlacettes.id_placette_orig == str(arbre["NumPlac"]))
            ).one()[0]
            arbre["Azimut"]=float(arbre["Azimut"].replace(',', '.'))
            arbre["Dist"]=float(arbre["Dist"].replace(',', '.'))
            new_arbre = TArbres(
                id_arbre_orig = arbre["NumArbre"],
                id_placette =  placette_id,
                code_essence = arbre["Essence"],
                azimut = arbre["Azimut"],
                distance = arbre["Dist"],
                taillis = True if arbre['Taillis'] =='t' else False,
                observation = arbre["Observation"]
            )
            new_arbres_array.append(new_arbre)
            list_arbres_id.append((int(arbre["NumPlac"]), int(arbre["NumArbre"])))
    DB.session.bulk_save_objects(new_arbres_array)
    DB.session.commit()

    # print("mid")


    new_arbres_mesures_array = []
    # #TArbresMesurés
    id_type_durete = get_id_type_from_mnemonique("PSDRF_DURETE")
    id_type_ecorce = get_id_type_from_mnemonique("PSDRF_ECORCE")

    for arbre in Arbres:
        placette_id = DB.session.query(TPlacettes.id_placette).filter(
            (TPlacettes.id_dispositif == id_dispositif) & (TPlacettes.id_placette_orig == str(arbre["NumPlac"]))
        ).one()[0]
        # print(arbre["NumArbre"])
        # print(arbre["NumPlac"])
        # print("stades")
        # print(arbre["StadeD"])
        # print(arbre["StadeE"])
        arbre_id = DB.session.query(TArbres.id_arbre).filter(
            (TArbres.id_arbre_orig == int(arbre["NumArbre"])) & (TArbres.id_placette == placette_id) 
        ).one()
        cycle_id = DB.session.query(TCycles.id_cycle).filter(
            (TCycles.num_cycle == arbre["Cycle"]) & (TCycles.id_dispositif == id_dispositif)  
        ).one()

        new_arbre_mesure = TArbresMesures(
            id_arbre = arbre_id,
            id_cycle = cycle_id,
            diametre1 =arbre["Diam1"],
            diametre2 = arbre["Diam2"],
            type = arbre["Type"],
            hauteur_totale = arbre["Haut"],
            stade_durete = get_id_nomenclature_from_id_type_and_cd_nomenclature(id_type_durete, arbre["StadeD"]) if arbre["StadeD"] else None,
            stade_ecorce = get_id_nomenclature_from_id_type_and_cd_nomenclature(id_type_ecorce, arbre["StadeE"]) if arbre["StadeE"] else None,
            coupe = arbre["Coupe"],
            limite = True if arbre["Limite"] == "t" else False,
            code_ecolo = arbre["CodeEcolo"],
            ref_code_ecolo = arbre["Ref_CodeEcolo"],
            observation = arbre["Observation"]
        )
        new_arbres_mesures_array.append(new_arbre_mesure)
    DB.session.bulk_save_objects(new_arbres_mesures_array)
    DB.session.commit()


    # TRegenerations
    listRege = []
    id_type_abroutis = get_id_type_from_mnemonique("PSDRF_ABROUTIS")
    for reges in Regeneration:

        placette_id = DB.session.query(TPlacettes.id_placette).filter(
            (TPlacettes.id_dispositif == id_dispositif) & (TPlacettes.id_placette_orig == str(reges["NumPlac"]))
        ).one()

        cycle_id = DB.session.query(TCycles.id_cycle).filter(
            (TCycles.num_cycle == reges["Cycle"]) & (TCycles.id_dispositif == id_dispositif)  
        ).one()

        cycle_reges_id = DB.session.query(CorCyclesPlacettes.id_cycle_placette).filter(
            (CorCyclesPlacettes.id_cycle == cycle_id) & (CorCyclesPlacettes.id_placette == placette_id)
        ).one()

        new_regeneration =TRegenerations(
            id_cycle_placette = cycle_reges_id,
            sous_placette = reges["SsPlac"],
            code_essence = reges["Essence"],
            recouvrement = reges["Recouv"] if reges["Recouv"] else 0,
            classe1 = reges["Class1"],
            classe2 = reges["Class2"],
            classe3 = reges["Class3"],
            taillis = True if reges["Taillis"] == "t" else False,
            abroutissement = True if reges["Abroutis"] == "t" else False,
            observation = reges["Observation"]
        )
        listRege.append(new_regeneration)
    DB.session.bulk_save_objects(listRege)
    DB.session.commit()



    # BMSsup30
    bmsSup30List = []
    for bmsSup30 in BMSsup30:

        placette_id = DB.session.query(TPlacettes.id_placette).filter(
            (TPlacettes.id_dispositif == id_dispositif) & (TPlacettes.id_placette_orig == bmsSup30["NumPlac"])
        ).one()
        if(bmsSup30["NumArbre"]):
            arbre_id = DB.session.query(TArbres.id_arbre).filter(
                (TArbres.id_arbre_orig == bmsSup30["NumArbre"]) & (TArbres.id_placette == placette_id)
            ).one()
        else :
            arbre_id = None
        new_bmsSup30 = TBmSup30(
            id_bm_sup_30_orig = bmsSup30["NumArbre"],
            id_placette = placette_id,
            id_arbre = arbre_id,
            code_essence = bmsSup30["Essence"],
            azimut = bmsSup30["Azimut"],
            distance = bmsSup30["Dist"],
            observation = bmsSup30["Observation"]
        )
        bmsSup30List.append(new_bmsSup30)
    DB.session.bulk_save_objects(bmsSup30List)
    DB.session.commit()

    # # # BMSsup30Mesurés
    # # for bmsSup30 in BMSsup30:

    # #     id_bm_sup_30 = 
    # #     id_cycle = 
    # #     diametre_ini = 
    # #     diametre_med = 
    # #     diametre_fin = 
    # #     diametre_130 = 
    # #     longueur = 
    # #     ratio_hauteur = 
    # #     contact = 
    # #     chablis = 
    # #     stade_durete = 
    # #     stade_ecorce = 
    # #     observation = 





    # # # Voir si le Cycle existe déjà, sinon on l'ajoute
    # # # Checker si ce Numdisp avec ce Numcycle existe déjà dans la BDD sinon ajouter
    # # for val in data[1]:
    # #     CorCyclesPlacettes(
    # #         id_cycle_placette = 
    # #         id_cycle = 
    # #         id_placette = 
    # #         date_releve = 
    # #         date_intervention = 
    # #         nature_intervention = 
    # #         gestion_placette = 
    # #         id_nomenclature_castor = 
    # #         id_nomenclature_frottis = 
    # #         id_nomenclature_boutis = 
    # #         recouv_herbes_basses = 
    # #         recouv_herbes_hautes = 
    # #         recouv_buissons = 
    # #         recouv_arbres = 
    # #     )







    # # print(data[0])
    # # print("stop")

    # # Placettes = [] 
    # # print(Placettes)
    # # Cycles = pd.json_normalize(data[1])
    # # Arbres = pd.json_normalize(data[2])
    # # Regeneration = pd.json_normalize(data[3])
    # # Transect = pd.json_normalize(data[4])
    # # BMSsup30 = pd.json_normalize(data[5])
    # # Reperes = pd.json_normalize(data[6])
    
    # # for val in data[0]:
    # #     Placettes.append(
    # #         TPlacettes(
    # #             id_placette=val['NumPlac'],
    # #             id_dispositif=val['NumDisp'],
    # #             id_placette_orig=val['NumPlac'],
    # #             strate=val['Strate'],
    # #             pente=val['Pente'],
    # #             poids_placette=val['PoidsPlacette'],
    # #             correction_pente=val['CorrectionPente'],
    # #             exposition=val['Exposition'],
    # #             habitat=val["Habitat"],
    # #             station=val["Station"],
    # #             typologie=val["Typologie"],
    # #             groupe=val["Groupe"],
    # #             groupe1=val["Groupe1"],
    # #             groupe2=val["Groupe2"],
    # #             ref_habitat=val["Ref_Habitat"],
    # #             precision_habitat=val["Precision_Habitat"],
    # #             ref_station=val["Ref_Station"],
    # #             ref_typologie=val["Ref_Typologie"],
    # #             descriptif_groupe=val["Descriptif_Groupe"],
    # #             descriptif_groupe1=val["Descriptif_Groupe1"],
    # #             descriptif_groupe2=val["Descriptif_Groupe2"],
    # #         )
    # #     )
    # #     DB.session.bulk_save_objects(Placettes)
    # #     DB.session.commit()

    #     # CorCyclesPlacettes(
    #     #     # serial?
    #     #     id_cycle_placette = 
    #     #     id_cycle=val['Cycle']
    #     #     id_placette = val['NumPlac']
    #     #     date_releve = 
    #     #     date_intervention = val['Date_Intervention']
    #     #     nature_intervention = val['Nature_Intervention']
    #     #     gestion_placette = val['Gestion']
    #     #     id_nomenclature_castor = 
    #     #     id_nomenclature_frottis = 
    #     #     id_nomenclature_boutis = 
    #     #     recouv_herbes_basses = 
    #     #     recouv_herbes_hautes = 
    #     #     recouv_buissons = 
    #     #     recouv_arbres = 
    #     # )





    # # Placettes_array = []        
    # # for index, row in Placettes.iterrows():
    # #     TPlacettes(
    # #         id_placette=,
    # #         id_dispositif=,
    # #         id_placette_orig=,
    # #         strate=,
    # #         pente=,
    # #         poids_placette=,
    # #         correction_pente=,
    # #         exposition=,
    # #         profondeur_app=,
    # #         profondeur_hydr=,
    # #         texture=,
    # #         habitat=,
    # #         station=,
    # #         typologie=,
    # #         groupe=,
    # #         groupe1=,
    # #         groupe2=,
    # #         ref_habitat=,
    # #         precision_habitat=,
    # #         ref_station=,
    # #         ref_typologie=,
    # #         descriptif_groupe=,
    # #         descriptif_groupe1=,
    # #         descriptif_groupe2=,
    # #         precision_gps=,
    # #         cheminement=,
    # #         geom=,
    # #         geom_wgs84=,

    # #     )



    pass

