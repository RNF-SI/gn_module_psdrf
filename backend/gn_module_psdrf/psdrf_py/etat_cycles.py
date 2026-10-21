"""
État des cycles d'un dispositif et avertissements associés à la génération.

Un cycle peut être annoncé par PsdrfListes (``t_cycles``) sans avoir encore de
relevé en production, ou n'être relevé que sur une partie des placettes. Ce
module dresse cet état et rédige les avertissements correspondants, affichés à
la fois avant le lancement (fiche dispositif) et avec le résultat de la
génération : les deux reposent sur les mêmes fonctions, donc le même texte.

Un relevé compte dès que l'association cycle/placette porte une année, comme
le contrôle de la campagne (``campagne_year_rule_c``) l'exige.
"""

from __future__ import annotations

from typing import Optional

from geonature.utils.env import DB
from sqlalchemy import text

_ETAT_SQL = """
    SELECT c.num_cycle,
           max(extract(year FROM c.date_debut))::int AS annee_annoncee,
           count(DISTINCT cp.id_placette) FILTER (WHERE cp.annee IS NOT NULL)
               AS nb_placettes_relevees
      FROM {schema}.t_cycles c
      LEFT JOIN {schema}.cor_cycles_placettes cp ON cp.id_cycle = c.id_cycle
     WHERE c.id_dispositif = :id_dispositif
     GROUP BY c.num_cycle
     ORDER BY c.num_cycle
"""

_NB_PLACETTES_SQL = """
    SELECT count(*) FROM {schema}.t_placettes WHERE id_dispositif = :id_dispositif
"""


def _etat_schema(schema: str, disp_id: int) -> dict:
    params = {"id_dispositif": disp_id}
    cycles = DB.session.execute(text(_ETAT_SQL.format(schema=schema)), params).mappings().all()
    nb_placettes = DB.session.execute(text(_NB_PLACETTES_SQL.format(schema=schema)), params).scalar()
    return {
        "nb_placettes": nb_placettes or 0,
        "cycles": [dict(c) for c in cycles],
    }


def etat_cycles(disp_id: int, *, avec_staging: bool = False) -> dict:
    """
    État par cycle en production (et, sur demande, en staging).

    Returns
    -------
    dict
        ``{"nb_placettes": int, "cycles": [{"num_cycle", "annee_annoncee",
        "nb_placettes_relevees", "nb_placettes_staging"?}], "cycles_disponibles":
        [int], "cycle_defaut": int | None}`` — ``cycles_disponibles`` liste les
        cycles ayant au moins un relevé en production, ``cycle_defaut`` le
        dernier d'entre eux.
    """
    etat = _etat_schema("pr_psdrf", disp_id)
    if avec_staging:
        try:
            staging = {
                c["num_cycle"]: c["nb_placettes_relevees"]
                for c in _etat_schema("pr_psdrf_staging", disp_id)["cycles"]
            }
        except Exception:
            # Schéma staging absent : l'état de production reste exploitable.
            DB.session.rollback()
            staging = {}
        connus = {c["num_cycle"] for c in etat["cycles"]}
        for c in etat["cycles"]:
            c["nb_placettes_staging"] = staging.get(c["num_cycle"], 0)
        for num_cycle in sorted(set(staging) - connus):
            etat["cycles"].append({
                "num_cycle": num_cycle,
                "annee_annoncee": None,
                "nb_placettes_relevees": 0,
                "nb_placettes_staging": staging[num_cycle],
            })
        etat["cycles"].sort(key=lambda c: c["num_cycle"])

    disponibles = [c["num_cycle"] for c in etat["cycles"] if c["nb_placettes_relevees"] > 0]
    etat["cycles_disponibles"] = disponibles
    etat["cycle_defaut"] = disponibles[-1] if disponibles else None
    return etat


def _libelle_cycle(c: dict) -> str:
    annee = f" ({c['annee_annoncee']})" if c.get("annee_annoncee") else ""
    return f"cycle {c['num_cycle']}{annee}"


def avertissements(etat: dict, cycle: Optional[int]) -> list[str]:
    """Avertissements pour une génération arrêtée au cycle ``cycle``."""
    if cycle is None:
        return []
    messages = []
    par_num = {c["num_cycle"]: c for c in etat["cycles"]}
    nb_total = etat["nb_placettes"]

    # Cycles annoncés (PsdrfListes) ou présents en staging, sans relevé en production.
    for c in etat["cycles"]:
        annonce = c.get("annee_annoncee") is not None
        if c["nb_placettes_relevees"] == 0 and (annonce or c.get("nb_placettes_staging")):
            msg = (
                f"Le {_libelle_cycle(c)} "
                + ("est annoncé dans PsdrfListes mais " if annonce else "")
                + "n'a aucun relevé en production : il n'apparaîtra pas dans les documents."
            )
            if c.get("nb_placettes_staging"):
                msg += (
                    f" {c['nb_placettes_staging']} placette(s) de ce cycle sont en "
                    "staging : elles doivent être importées en production pour être "
                    "prises en compte."
                )
            messages.append(msg)

    # Génération volontairement arrêtée avant le dernier cycle disponible.
    plus_recents = [n for n in etat["cycles_disponibles"] if n > cycle]
    if plus_recents:
        messages.append(
            f"Documents arrêtés au cycle {cycle} : les données du ou des cycles "
            f"{', '.join(str(n) for n in plus_recents)} ne sont pas utilisées."
        )

    # Cycle choisi relevé sur une partie seulement des placettes.
    choisi = par_num.get(cycle)
    if choisi and 0 < choisi["nb_placettes_relevees"] < nb_total:
        n = choisi["nb_placettes_relevees"]
        msg = (
            f"Cycle {cycle} incomplet : {n} placette(s) relevée(s) sur {nb_total}. "
            f"Le bilan du cycle {cycle} est calculé sur ces {n} placettes seulement : "
            "les estimations sont moins précises (erreur relative et intervalles de "
            "confiance plus larges) et peuvent ne pas représenter l'ensemble du "
            f"dispositif. Le plan des arbres ne couvre que ces {n} placettes."
        )
        precedents = [
            par_num[p] for p in etat["cycles_disponibles"] if p < cycle and p in par_num
        ]
        if precedents:
            detail = ", ".join(
                f"cycle {p['num_cycle']} sur {p['nb_placettes_relevees']} placettes"
                for p in precedents
            )
            msg += (
                f" Le chapitre « Évolution » compare des cycles calculés sur des "
                f"placettes différentes ({detail}, cycle {cycle} sur {n}) : les écarts "
                "mêlent l'évolution réelle du peuplement et la différence d'échantillon, "
                "ils ne doivent pas être lus comme une évolution du dispositif."
            )
        messages.append(msg)
    return messages
