"""
Complétion des dispositifs entre cycles (#77) : pour chaque dispositif, part des
placettes du cycle précédent relevées au dernier cycle (en production et, à
part, en plus dans le staging-terrain), et part des arbres retrouvés.

Une placette compte comme relevée dès que son association cycle/placette porte
une année, comme dans ``psdrf_py.etat_cycles`` : les copies de la production
renvoyées par Dendro3 sans date de relevé (RNF-SI/dendro3#82) n'y comptent pas.
Les placettes sont rapprochées entre production et staging par
``id_placette_orig``.
"""

from __future__ import annotations

import logging
from collections import defaultdict

from geonature.utils.env import DB
from sqlalchemy import text

logger = logging.getLogger(__name__)

_RELEVES_SQL = """
    SELECT 'production' AS source, p.id_dispositif, c.num_cycle, p.id_placette_orig
      FROM pr_psdrf.cor_cycles_placettes cp
      JOIN pr_psdrf.t_cycles c ON c.id_cycle = cp.id_cycle
      JOIN pr_psdrf.t_placettes p ON p.id_placette = cp.id_placette
     WHERE cp.annee IS NOT NULL
    UNION
    SELECT 'staging', p.id_dispositif, c.num_cycle, p.id_placette_orig
      FROM pr_psdrf_staging.cor_cycles_placettes cp
      JOIN pr_psdrf_staging.t_cycles c ON c.id_cycle = cp.id_cycle
      JOIN pr_psdrf_staging.t_placettes p ON p.id_placette = cp.id_placette
     WHERE cp.annee IS NOT NULL
"""

_DISPOSITIFS_SQL = """
    SELECT d.id_dispositif, d.name AS nom, count(p.id_placette) AS nb_placettes
      FROM pr_psdrf.t_dispositifs d
      LEFT JOIN pr_psdrf.t_placettes p ON p.id_dispositif = d.id_dispositif
     GROUP BY 1, 2
"""

# Arbres (production) : sur les placettes relevées aux deux derniers cycles
# relevés en production, arbres mesurés au cycle précédent et, parmi eux, ceux
# remesurés au dernier. Un arbre est identifié par sa placette et son numéro
# (``id_arbre_orig``), stable d'un cycle à l'autre même si un import a créé un
# nouvel enregistrement. Un arbre abattu ou disparu compte comme non retrouvé.
_ARBRES_SQL = """
    WITH rel AS (
        SELECT DISTINCT p.id_dispositif, c.num_cycle, p.id_placette
          FROM pr_psdrf.cor_cycles_placettes cp
          JOIN pr_psdrf.t_cycles c ON c.id_cycle = cp.id_cycle
          JOIN pr_psdrf.t_placettes p ON p.id_placette = cp.id_placette
         WHERE cp.annee IS NOT NULL
    ), rang AS (
        SELECT id_dispositif, num_cycle,
               dense_rank() OVER (PARTITION BY id_dispositif ORDER BY num_cycle DESC) AS r
          FROM (SELECT DISTINCT id_dispositif, num_cycle FROM rel) x
    ), d AS (
        SELECT id_dispositif,
               max(num_cycle) FILTER (WHERE r = 1) AS dernier,
               max(num_cycle) FILTER (WHERE r = 2) AS precedent
          FROM rang GROUP BY 1
        HAVING max(num_cycle) FILTER (WHERE r = 2) IS NOT NULL
    ), pl AS (
        SELECT rel.id_dispositif, rel.id_placette
          FROM rel JOIN d ON d.id_dispositif = rel.id_dispositif
         WHERE rel.num_cycle IN (d.dernier, d.precedent)
         GROUP BY 1, 2
        HAVING count(DISTINCT rel.num_cycle) = 2
    ), arbres AS (
        SELECT pl.id_dispositif, a.id_placette, a.id_arbre_orig,
               bool_or(c.num_cycle = d.precedent) AS au_precedent,
               bool_or(c.num_cycle = d.dernier) AS au_dernier
          FROM pr_psdrf.t_arbres_mesures am
          JOIN pr_psdrf.t_arbres a ON a.id_arbre = am.id_arbre
          JOIN pl ON pl.id_placette = a.id_placette
          JOIN d ON d.id_dispositif = pl.id_dispositif
          JOIN pr_psdrf.t_cycles c ON c.id_cycle = am.id_cycle
         WHERE c.num_cycle IN (d.dernier, d.precedent) AND a.id_arbre_orig IS NOT NULL
         GROUP BY 1, 2, 3
    )
    SELECT d.id_dispositif, d.dernier, d.precedent,
           count(*) FILTER (WHERE au_precedent) AS arbres_cycle_precedent,
           count(*) FILTER (WHERE au_precedent AND au_dernier) AS arbres_retrouves
      FROM d LEFT JOIN arbres ON arbres.id_dispositif = d.id_dispositif
     GROUP BY 1, 2, 3
"""


def _statut(ligne: dict) -> str:
    """complet / a_importer (complet avec le staging) / en_cours (staging
    partiel) / incomplet / premier_cycle / aucun_releve."""
    if ligne["dernier_cycle"] is None:
        return "aucun_releve"
    if ligne["cycle_precedent"] is None:
        return "premier_cycle"
    attendues = ligne["placettes_attendues"]
    if ligne["placettes_production"] >= attendues:
        return "complet"
    if ligne["placettes_production"] + ligne["placettes_staging"] >= attendues:
        return "a_importer"
    if ligne["placettes_staging"]:
        return "en_cours"
    return "incomplet"


def completion_dispositifs() -> list[dict]:
    """Une ligne par dispositif de production, triée par nom."""
    try:
        releves = DB.session.execute(text(_RELEVES_SQL)).mappings().all()
        dispositifs = DB.session.execute(text(_DISPOSITIFS_SQL)).mappings().all()
        arbres = {r["id_dispositif"]: r for r in DB.session.execute(text(_ARBRES_SQL)).mappings().all()}
    except Exception:
        DB.session.rollback()
        logger.exception("[PSDRF] Complétion des dispositifs illisible")
        return []

    # {dispositif: {cycle: {"production": set(placettes), "staging": set(...)}}}
    par_disp = defaultdict(lambda: defaultdict(lambda: {"production": set(), "staging": set()}))
    for r in releves:
        par_disp[r["id_dispositif"]][r["num_cycle"]][r["source"]].add(r["id_placette_orig"])

    lignes = []
    for d in dispositifs:
        cycles = par_disp.get(d["id_dispositif"], {})
        nums = sorted(cycles)
        dernier = nums[-1] if nums else None
        # Cycle de référence : le dernier cycle antérieur relevé en production.
        precedents = [n for n in nums if n != dernier and cycles[n]["production"]]
        precedent = precedents[-1] if precedents else None
        attendues = cycles[precedent]["production"] if precedent is not None else set()
        prod = cycles[dernier]["production"] if dernier is not None else set()
        stag = cycles[dernier]["staging"] if dernier is not None else set()
        a = arbres.get(d["id_dispositif"])
        ligne = {
            "id_dispositif": d["id_dispositif"],
            "nom": d["nom"],
            "nb_placettes": d["nb_placettes"],
            "cycles": [
                {
                    "num_cycle": n,
                    "production": len(cycles[n]["production"]),
                    # Relevés du staging pas encore en production.
                    "staging": len(cycles[n]["staging"] - cycles[n]["production"]),
                }
                for n in nums
            ],
            "dernier_cycle": dernier,
            "cycle_precedent": precedent,
            "placettes_attendues": len(attendues),
            "placettes_production": len(attendues & prod),
            "placettes_staging": len((attendues & stag) - prod),
            # Arbres : deux derniers cycles relevés en production (peuvent
            # différer de dernier/précédent si le dernier n'est qu'en staging).
            "arbres_cycles": [a["precedent"], a["dernier"]] if a else None,
            "arbres_cycle_precedent": a["arbres_cycle_precedent"] if a else None,
            "arbres_retrouves": a["arbres_retrouves"] if a else None,
        }
        ligne["statut"] = _statut(ligne)
        lignes.append(ligne)
    return sorted(lignes, key=lambda l: (l["nom"] or "").strip().lower())
