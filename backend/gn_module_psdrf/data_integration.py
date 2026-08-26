import json
import pandas as pd
from sqlalchemy.sql.expression import false, null
from geonature.utils.env import DB
from .models import TDispositifs, TPlacettes, TArbres, TCycles, \
    CorCyclesPlacettes, TArbresMesures, TReperes, BibEssences, TRegenerations, TBmSup30,TBmSup30Mesures, TTransects
from .geonature_PSDRF_function import get_id_type_from_mnemonique, get_id_nomenclature_from_id_type_and_cd_nomenclature
from .psdrf_tables import TablesPsdrfError, unpack_tables
from datetime import datetime
from math import isnan

import traceback


def _placette_key(value):
    """Clé de correspondance avec id_placette_orig (varchar en base).

    Le numéro de placette arrive tantôt en texte, tantôt en nombre selon
    l'onglet Excel : on le normalise toujours en chaîne (et on retire le `.0`
    des entiers déguisés en flottant) pour éviter la comparaison
    `varchar = integer`, refusée par Postgres.
    """
    if value is None:
        return None
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _int_key(value):
    """Numéro de cycle / d'arbre / de BMS normalisé en entier.

    Les fichiers Excel donnent tantôt 2, tantôt '2', tantôt '2.0'.
    """
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(float(value))


def _require(mapping, key, label):
    """Equivalent des anciens `.one()` : erreur explicite si la clé est absente."""
    value = mapping.get(key)
    if value is None:
        raise ValueError("{} introuvable en base pour la valeur {!r}".format(label, key))
    return value


def _build_nomenclature_getter():
    """Mémoïse les identifiants de nomenclature.

    Il n'existe qu'une poignée de codes distincts (stades de dureté / d'écorce)
    pour des dizaines de milliers de lignes : une requête par ligne était le
    principal poste de lenteur de l'import.
    """
    cache = {}

    def get(id_type, cd_nomenclature):
        key = (id_type, cd_nomenclature)
        if key not in cache:
            cache[key] = get_id_nomenclature_from_id_type_and_cd_nomenclature(
                id_type, cd_nomenclature
            )
        return cache[key]

    return get


def _load_placettes_map(id_dispositif):
    """id_placette_orig -> id_placette, pour le dispositif."""
    return {
        _placette_key(orig): placette_id
        for placette_id, orig in DB.session.query(
            TPlacettes.id_placette, TPlacettes.id_placette_orig
        ).filter(TPlacettes.id_dispositif == id_dispositif)
    }


def _load_cycles_map(id_dispositif):
    """num_cycle -> id_cycle, pour le dispositif."""
    return {
        _int_key(num_cycle): cycle_id
        for cycle_id, num_cycle in DB.session.query(
            TCycles.id_cycle, TCycles.num_cycle
        ).filter(TCycles.id_dispositif == id_dispositif)
    }


def _load_cor_cycles_placettes_map(id_dispositif):
    """(id_cycle, id_placette) -> id_cycle_placette, pour le dispositif."""
    return {
        (cycle_id, placette_id): id_cycle_placette
        for id_cycle_placette, cycle_id, placette_id in DB.session.query(
            CorCyclesPlacettes.id_cycle_placette,
            CorCyclesPlacettes.id_cycle,
            CorCyclesPlacettes.id_placette,
        )
        .join(TPlacettes, CorCyclesPlacettes.id_placette == TPlacettes.id_placette)
        .filter(TPlacettes.id_dispositif == id_dispositif)
    }


def _error_response(message, exception=None):
    """Réponse 500 : on annule la transaction avant de rendre la main.

    Sans ce rollback, la suppression des placettes resterait en attente dans la
    session ; elle n'est jamais commitée, mais mieux vaut l'annuler explicitement.
    """
    DB.session.rollback()
    payload = {'success': False, "message": message}
    if exception is not None:
        payload["error_detail"] = ''.join(
            traceback.format_exception(Exception, exception, exception.__traceback__)
        )
    return (json.dumps(payload), 500, {'ContentType': 'application/json'})


def data_integration(dispId, dispName, data):
    try:
        # Dépaquetage positionnel : on contrôle la forme du classeur avant de
        # toucher à quoi que ce soit (cf. psdrf_tables).
        try:
            tables = unpack_tables(data)
        except TablesPsdrfError as e:
            return (
                json.dumps({'success': False, "message": str(e)}),
                400,
                {'ContentType': 'application/json'},
            )

        Placettes = tables[0]
        Cycles = tables[1]
        Arbres = tables[2]
        Regeneration = tables[3]
        Transect = tables[4]
        BMSsup30 = tables[5]
        Reperes = tables[6]

        id_dispositif = int(dispId)

        # --- Contrôles préalables -------------------------------------------
        # Ils sont faits AVANT toute suppression : un fichier refusé ne doit pas
        # laisser le dispositif amputé en base.

        # Arreter si le dispositif n'existe pas dans la bdd (donc n'est pas dans PSDRFListe)
        if DB.session.query(TDispositifs.id_dispositif).filter_by(
            id_dispositif=id_dispositif
        ).first() is None:
            return _error_response(
                "Le dispositif n'a pas ete prealablement ajoute a la table des dispositif. Veuillez contacter un administrateur."
            )

        # Arreter si tous les cycles du dispositif ne sont pas dans la table des cycles de la bdd (donc dans PSDRFListe)
        cycles_map = _load_cycles_map(id_dispositif)
        cycleList = []
        for cycle in Cycles:
            num_cycle = _int_key(cycle["Cycle"])
            if num_cycle not in cycleList:
                cycleList.append(num_cycle)
        for num_cycle in cycleList:
            if num_cycle not in cycles_map:
                return _error_response(
                    "Le cycle " + str(num_cycle) + " pour le dispositif " + str(id_dispositif)
                    + " n'a pas ete prealablement ajoute a la table des cycles. Veuillez contacter un administrateur."
                )

        # --- Import ----------------------------------------------------------
        # Suppression + réinsertion dans UNE SEULE transaction (flush, pas commit) :
        # si l'import échoue ou si le worker est tué, le rollback restaure les
        # données précédentes au lieu de laisser le dispositif vide.
        TPlacettes.query.filter_by(id_dispositif=id_dispositif).delete()
        DB.session.flush()

        get_nomenclature = _build_nomenclature_getter()
        id_type_durete = get_id_type_from_mnemonique("PSDRF_DURETE")
        id_type_ecorce = get_id_type_from_mnemonique("PSDRF_ECORCE")

        try:
            # Placettes
            newPlacettesList = []
            placettesIdOrigInDisp = set()
            for placette in Placettes:
                num_plac = _placette_key(placette["NumPlac"])
                if num_plac not in placettesIdOrigInDisp:
                    newPlacettesList.append(TPlacettes(
                        id_dispositif= int(id_dispositif),
                        id_placette_orig= num_plac,
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
                    placettesIdOrigInDisp.add(num_plac)
            DB.session.bulk_save_objects(newPlacettesList)
            DB.session.flush()
        except Exception as e:
            return _error_response(
                "Erreur lors de l'insertion des placettes dans la bdd. Veuillez contacter un administrateur.", e
            )

        # bulk_save_objects ne renseigne pas les clés primaires : on relit les
        # identifiants une fois pour toutes plutôt qu'une requête par ligne.
        placettes_map = _load_placettes_map(id_dispositif)

        try:
            # Reperes
            newReperesList = []
            for repere in Reperes:
                if repere["NumPlac"]:
                    idPlacette_repere = _require(
                        placettes_map, _placette_key(repere["NumPlac"]), "Placette"
                    )

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
            return _error_response(
                "Erreur lors de l'insertion des reperes dans la bdd. Veuillez contacter un administrateur.", e
            )

        # CorCyclePlacettes
        # Récupérer les cycles présents dans le dispositif
        try:
            # Indexation des placettes par (NumPlac, Cycle) : l'ancienne boucle
            # imbriquée sur Placettes coûtait O(Cycles x Placettes).
            placettes_par_cle = {}
            for placette in Placettes:
                cle = (_placette_key(placette["NumPlac"]), _int_key(placette["Cycle"]))
                placettes_par_cle.setdefault(cle, []).append(placette)

            new_cor_cycle_placette_array = []
            for cycle in Cycles:
                cle = (_placette_key(cycle["NumPlac"]), _int_key(cycle["Cycle"]))
                placette_id = _require(placettes_map, cle[0], "Placette")
                cycle_id = _require(cycles_map, cle[1], "Cycle")

                for placette in placettes_par_cle.get(cle, []):
                    new_cor_cycle_placette = CorCyclesPlacettes(
                        id_cycle=cycle_id,
                        id_placette=placette_id,
                        date_releve=datetime.strptime(cycle["Date"], '%d/%m/%Y') if cycle["Date"] else cycle["Date"],
                        annee=cycle["Année"],
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
            return _error_response(
                "Erreur lors de l'insertion des cor_cycles_placette dans la bdd. Veuillez contacter un administrateur.", e
            )

        cor_cycles_placettes_map = _load_cor_cycles_placettes_map(id_dispositif)

        # #CorCyclesRoles
        # TODO: Remplir avec userHub

        #TArbres
        try:
            new_arbres_array = []
            list_arbres_id = set()
            for arbre in Arbres:
                cle_arbre = (_placette_key(arbre["NumPlac"]), _int_key(arbre["NumArbre"]))
                if cle_arbre not in list_arbres_id:
                    placette_id = _require(placettes_map, cle_arbre[0], "Placette")
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
                    list_arbres_id.add(cle_arbre)
            DB.session.bulk_save_objects(new_arbres_array)
            DB.session.flush()
        except Exception as e:
            return _error_response(
                "Erreur lors de l'insertion des arbres dans la bdd. Veuillez contacter un administrateur.", e
            )


        # #TArbresMesurés
        try:
            new_arbres_mesures_array = []

            # Pré-charger les arbres pour éviter les requêtes en boucle
            arbres_map = {}
            arbres_query = DB.session.query(TArbres.id_arbre, TArbres.id_arbre_orig, TArbres.id_placette).join(
                TPlacettes, TArbres.id_placette == TPlacettes.id_placette
            ).filter(TPlacettes.id_dispositif == id_dispositif).all()
            for arbre_id, arbre_orig, placette_id in arbres_query:
                arbres_map[(arbre_orig, placette_id)] = arbre_id

            for arbre in Arbres:
                placette_id = placettes_map.get(_placette_key(arbre["NumPlac"]))
                if not placette_id:
                    continue

                arbre_id = arbres_map.get((int(arbre["NumArbre"]), placette_id))
                if not arbre_id:
                    continue

                cycle_id = cycles_map.get(_int_key(arbre["Cycle"]))
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
                    stade_durete=get_nomenclature(id_type_durete, arbre["StadeD"]) if arbre["StadeD"] else None,
                    stade_ecorce=get_nomenclature(id_type_ecorce, arbre["StadeE"]) if arbre["StadeE"] else None,
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
            return _error_response(
                "Erreur lors de l'insertion des arbres mesurés dans la bdd. Veuillez contacter un administrateur.", e
            )


        # TRegenerations
        try:
            listRege = []
            id_type_abroutis = get_id_type_from_mnemonique("PSDRF_ABROUTIS")
            for reges in Regeneration:
                placette_id = _require(
                    placettes_map, _placette_key(reges["NumPlac"]), "Placette"
                )
                cycle_id = _require(cycles_map, _int_key(reges["Cycle"]), "Cycle")
                cycle_reges_id = _require(
                    cor_cycles_placettes_map,
                    (cycle_id, placette_id),
                    "Association cycle/placette",
                )

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
            return _error_response(
                "Erreur lors de l'insertion des regenerations dans la bdd. Veuillez contacter un administrateur.", e
            )


        # TCategories

        # BMSsup30
        try:
            list_bms_id = set()
            bmsSup30List = []
            for bmsSup30 in BMSsup30:
                cle_bms = (_placette_key(bmsSup30["NumPlac"]), _int_key(bmsSup30["Id"]))
                if cle_bms not in list_bms_id:
                    placette_id = _require(placettes_map, cle_bms[0], "Placette")

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
                    list_bms_id.add(cle_bms)
            DB.session.bulk_save_objects(bmsSup30List)
            DB.session.flush()
        except Exception as e:
            return _error_response(
                "Erreur lors de l'insertion des BMSsup30 dans la bdd. Veuillez contacter un administrateur.", e
            )

        # # # BMSsup30Mesurés
        try:
            # (id_bm_sup_30_orig, id_placette) -> id_bm_sup_30
            bms_map = {
                (_int_key(orig), placette_id): bms_id
                for bms_id, orig, placette_id in DB.session.query(
                    TBmSup30.id_bm_sup_30, TBmSup30.id_bm_sup_30_orig, TBmSup30.id_placette
                )
                .join(TPlacettes, TBmSup30.id_placette == TPlacettes.id_placette)
                .filter(TPlacettes.id_dispositif == id_dispositif)
            }

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

                placette_id = _require(
                    placettes_map, _placette_key(bmsSup30["NumPlac"]), "Placette"
                )
                bmsSup30_id = _require(
                    bms_map, (_int_key(bmsSup30["Id"]), placette_id), "Bois mort sur pied"
                )
                cycle_id = _require(cycles_map, _int_key(bmsSup30["Cycle"]), "Cycle")

                new_bmsSup30Mesures = TBmSup30Mesures(
                    id_bm_sup_30=bmsSup30_id,
                    id_cycle=cycle_id,
                    diametre_ini=bmsSup30["DiamIni"],
                    diametre_med=bmsSup30["DiamMed"],
                    diametre_fin=bmsSup30["DiamFin"],
                    longueur=bmsSup30["Longueur"],
                    contact=bmsSup30["Contact"],
                    chablis=True if bmsSup30["Chablis"] == "t" else False if bmsSup30["Chablis"] == "f" else bmsSup30["Chablis"],
                    stade_durete=get_nomenclature(id_type_durete, bmsSup30["StadeD"]) if bmsSup30["StadeD"] else None,
                    stade_ecorce=get_nomenclature(id_type_ecorce, bmsSup30["StadeE"]) if bmsSup30["StadeE"] else None,
                    observation=bmsSup30["Observation"]
                )
                bmsSup30MesuresList.append(new_bmsSup30Mesures)
            DB.session.bulk_save_objects(bmsSup30MesuresList)
            DB.session.flush()
        except Exception as e:
            return _error_response(
                "Erreur lors de l'insertion des BMSsup30Mesures dans la bdd. Veuillez contacter un administrateur.", e
            )

        try:
            transectList = []
            for transect in Transect:
                placette_id = _require(
                    placettes_map, _placette_key(transect["NumPlac"]), "Placette"
                )
                cycle_id = _require(cycles_map, _int_key(transect["Cycle"]), "Cycle")
                cycle_transect_id = _require(
                    cor_cycles_placettes_map,
                    (cycle_id, placette_id),
                    "Association cycle/placette",
                )

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
                    stade_durete=get_nomenclature(id_type_durete, transect["StadeD"]) if transect["StadeD"] else None,
                    stade_ecorce=get_nomenclature(id_type_ecorce, transect["StadeE"]) if transect["StadeE"] else None,
                    observation=transect['Observation']
                )
                transectList.append(new_transect)
            DB.session.bulk_save_objects(transectList)
            DB.session.flush()
        except Exception as e:
            return _error_response(
                "Erreur lors de l'insertion des transects dans la bdd. Veuillez contacter un administrateur.", e
            )

        DB.session.commit()
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
    except Exception as e:
        # Rollback and print error
        print(e)
        return _error_response(
            "Une erreur inconnue a eu lieu. Veuillez contacter un administrateur.", e
        )
