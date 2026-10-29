"""
Journal des exports Dendro3 → staging (``pr_psdrf_staging.t_dendro3_exports``).

Une ligne est ouverte à la réception d'un export (route
``/export_dispositif_from_dendro3``) puis close par la tâche Celery
``insert_or_update_data`` (succès + compteurs, ou échec + message). Le journal
est un outil de suivi : il ne doit jamais faire échouer un export, d'où les
erreurs avalées (table absente si la migration n'est pas passée, etc.).

Les écritures passent par leur propre connexion (``DB.engine.begin()``) pour
rester indépendantes de la session de l'export, qui peut être annulée.
"""

from __future__ import annotations

import json
import logging

from geonature.utils.env import DB
from sqlalchemy import text

logger = logging.getLogger(__name__)

TABLE = "pr_psdrf_staging.t_dendro3_exports"

# Sous-listes {created, updated, deleted} d'une placette dans le payload
# Dendro3, avec leurs propres sous-listes éventuelles.
_ENTITES_PLACETTE = {
    "arbres": ("arbres_mesures",),
    "bms": ("bm_sup_30_mesures",),
    "reperes": (),
    "corCyclesPlacettes": ("regenerations", "transects"),
}
_CATEGORIES = ("created", "updated", "deleted")


def _items(bloc):
    """Éléments created/updated/deleted d'un bloc du payload."""
    if not isinstance(bloc, dict):
        return []
    return [item for cat in _CATEGORIES for item in (bloc.get(cat) or [])]


def resume_placettes(data: dict) -> list[dict]:
    """Placettes du payload ayant au moins une modification, avec les cycles
    concernés : ``[{num_placette, cycles: [num_cycle], nb_modifications}]``."""
    num_cycles = {c.get("id_cycle"): c.get("num_cycle") for c in data.get("cycles") or []}
    resume = []
    for placette in data.get("placettes") or []:
        nb, id_cycles = 0, set()
        for cle, sous_cles in _ENTITES_PLACETTE.items():
            for item in _items(placette.get(cle)):
                nb += 1
                id_cycles.add(item.get("id_cycle"))
                for sous_cle in sous_cles:
                    for sous_item in _items(item.get(sous_cle)):
                        nb += 1
                        id_cycles.add(sous_item.get("id_cycle"))
        if nb:
            cycles = sorted({num_cycles[i] for i in id_cycles if num_cycles.get(i) is not None})
            resume.append({
                "num_placette": placette.get("id_placette_orig"),
                "cycles": cycles,
                "nb_modifications": nb,
            })
    return resume


def ouvrir_export(data: dict, task_id: str) -> None:
    """Trace la réception d'un export (statut ``en_cours``)."""
    try:
        with DB.engine.begin() as cx:
            cx.execute(text(f"""
                INSERT INTO {TABLE} (task_id, id_dispositif, device, id_role, placettes)
                VALUES (:task_id, :id_dispositif, :device, :id_role, CAST(:placettes AS jsonb))
            """), {
                "task_id": task_id,
                "id_dispositif": data.get("id_dispositif"),
                "device": data.get("device"),
                "id_role": data.get("id_role"),
                "placettes": json.dumps(resume_placettes(data)),
            })
    except Exception:
        logger.exception("[DENDRO3] Journal : réception de l'export %s non tracée", task_id)


def clore_export(task_id: str, statut: str, compteurs: dict | None = None, message: str | None = None) -> None:
    """Clôt la ligne d'un export : ``succes`` (avec compteurs) ou ``echec``."""
    try:
        with DB.engine.begin() as cx:
            cx.execute(text(f"""
                UPDATE {TABLE}
                   SET statut = :statut, message = :message, termine_le = now(),
                       compteurs = CAST(:compteurs AS jsonb)
                 WHERE task_id = :task_id
            """), {
                "task_id": task_id,
                "statut": statut,
                "message": message,
                "compteurs": json.dumps(compteurs) if compteurs is not None else None,
            })
    except Exception:
        logger.exception("[DENDRO3] Journal : fin de l'export %s non tracée", task_id)


def derniers_exports(limit: int = 50, id_dispositif: int | None = None) -> list[dict]:
    """Derniers exports, du plus récent au plus ancien, avec le nom du
    dispositif. Liste vide si la table n'existe pas encore."""
    filtre = "WHERE e.id_dispositif = :id_dispositif" if id_dispositif is not None else ""
    try:
        rows = DB.session.execute(text(f"""
            SELECT e.id_export, e.task_id, e.id_dispositif, d.name AS nom_dispositif,
                   e.recu_le, e.termine_le, e.statut, e.message, e.device, e.id_role,
                   e.compteurs, e.placettes
              FROM {TABLE} e
              LEFT JOIN pr_psdrf.t_dispositifs d ON d.id_dispositif = e.id_dispositif
              {filtre}
             ORDER BY e.recu_le DESC
             LIMIT :limit
        """), {"limit": limit, "id_dispositif": id_dispositif}).mappings().all()
    except Exception:
        DB.session.rollback()
        logger.exception("[DENDRO3] Journal des exports illisible")
        return []
    return [
        {
            **dict(r),
            "recu_le": r["recu_le"].isoformat() if r["recu_le"] else None,
            "termine_le": r["termine_le"].isoformat() if r["termine_le"] else None,
        }
        for r in rows
    ]


_RELEVES_STAGING_SQL = """
    SELECT c.num_cycle, p.id_placette_orig AS num_placette, cp.annee, cp.date_releve,
           GREATEST(
               cp.created_at, cp.updated_at,
               (SELECT max(GREATEST(am.created_at, am.updated_at))
                  FROM pr_psdrf_staging.t_arbres a
                  JOIN pr_psdrf_staging.t_arbres_mesures am ON am.id_arbre = a.id_arbre
                 WHERE a.id_placette = p.id_placette AND am.id_cycle = c.id_cycle),
               (SELECT max(GREATEST(bm.created_at, bm.updated_at))
                  FROM pr_psdrf_staging.t_bm_sup_30 b
                  JOIN pr_psdrf_staging.t_bm_sup_30_mesures bm ON bm.id_bm_sup_30 = b.id_bm_sup_30
                 WHERE b.id_placette = p.id_placette AND bm.id_cycle = c.id_cycle)
           ) AS derniere_modif,
           (SELECT count(*)
              FROM pr_psdrf_staging.t_arbres a
              JOIN pr_psdrf_staging.t_arbres_mesures am ON am.id_arbre = a.id_arbre
             WHERE a.id_placette = p.id_placette AND am.id_cycle = c.id_cycle) AS nb_arbres,
           EXISTS (
               SELECT 1
                 FROM pr_psdrf.cor_cycles_placettes pcp
                 JOIN pr_psdrf.t_cycles pc ON pc.id_cycle = pcp.id_cycle
                 JOIN pr_psdrf.t_placettes pp ON pp.id_placette = pcp.id_placette
                WHERE pp.id_dispositif = p.id_dispositif
                  AND pp.id_placette_orig = p.id_placette_orig
                  AND pc.num_cycle = c.num_cycle
                  AND pcp.annee IS NOT NULL
           ) AS en_production
      FROM pr_psdrf_staging.cor_cycles_placettes cp
      JOIN pr_psdrf_staging.t_cycles c ON c.id_cycle = cp.id_cycle
      JOIN pr_psdrf_staging.t_placettes p ON p.id_placette = cp.id_placette
     WHERE p.id_dispositif = :id_dispositif
     ORDER BY derniere_modif DESC NULLS LAST, c.num_cycle DESC, p.id_placette_orig
"""


def _iso(valeur):
    return valeur.isoformat() if valeur is not None else None


def suivi_dispositif(id_dispositif: int, nb_exports: int = 10) -> dict:
    """Suivi Dendro3 d'un dispositif (fiche dispositif) : derniers exports
    journalisés et relevés terrain en staging, placette par placette, du plus
    récemment modifié au plus ancien, avec ``en_production`` (même placette et
    même cycle déjà relevés en production).

    Les relevés staging ne dépendent pas du journal : ils couvrent aussi les
    exports antérieurs à sa mise en place. Les horodatages sont ceux de la
    tablette."""
    try:
        rows = DB.session.execute(
            text(_RELEVES_STAGING_SQL), {"id_dispositif": id_dispositif}
        ).mappings().all()
    except Exception:
        DB.session.rollback()
        logger.exception("[DENDRO3] Relevés staging illisibles (dispositif %s)", id_dispositif)
        rows = []
    placettes = [
        {
            "num_cycle": r["num_cycle"],
            "num_placette": r["num_placette"],
            "annee": r["annee"],
            "date_releve": _iso(r["date_releve"]),
            "derniere_modif": _iso(r["derniere_modif"]),
            "nb_arbres": r["nb_arbres"],
            "en_production": r["en_production"],
        }
        for r in rows
    ]
    exports = derniers_exports(nb_exports, id_dispositif=id_dispositif)
    dates = [p["derniere_modif"] for p in placettes if p["derniere_modif"]]
    return {
        "exports": exports,
        "placettes": placettes,
        "derniere_activite": max(dates) if dates else None,
    }
