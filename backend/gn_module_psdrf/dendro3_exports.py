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
from collections import Counter
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

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


def appareil_du_payload(data: dict) -> str | None:
    """Tablette la plus fréquente dans les lignes créées ou modifiées du
    payload (``updated_on``, sinon ``created_on``) : Dendro3 renseigne ces
    champs à chaque saisie, y compris dans les anciennes APK."""
    frequences = Counter()

    def compter(item):
        appareil = item.get("updated_on") or item.get("created_on")
        if appareil and appareil != "Unknown":
            frequences[appareil] += 1

    for placette in data.get("placettes") or []:
        for cle, sous_cles in _ENTITES_PLACETTE.items():
            bloc = placette.get(cle) or {}
            for item in (bloc.get("created") or []) + (bloc.get("updated") or []):
                compter(item)
                for sous_cle in sous_cles:
                    sous_bloc = item.get(sous_cle) or {}
                    for sous_item in (sous_bloc.get("created") or []) + (sous_bloc.get("updated") or []):
                        compter(sous_item)
    return frequences.most_common(1)[0][0] if frequences else None


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


def reprendre_archives(dossier: Path, simulation: bool = False, fuseau: str = "UTC") -> dict:
    """Journalise les envois archivés par la route d'export
    (``debug_data/<id_dispositif>/<AAAAMMJJ_HHMMSS>.json``), statut ``archive``
    puisque le résultat du traitement n'est pas connu.

    Le nom de fichier vient de ``datetime.now()`` dans le processus gunicorn,
    qui tourne en UTC en prod (fichier ``…_170733`` écrit à 19:07 heure de
    Paris) : il est lu dans ``fuseau`` puis stocké comme ``now()``, pour rester
    comparable aux lignes directes.

    Relançable : la ligne est identifiée par ``archive:<dispositif>/<fichier>``
    et mise à jour si elle existe déjà (corrige une reprise antérieure) ; un
    envoi déjà journalisé en direct (même dispositif, reçu à moins de
    2 minutes) est ignoré. Contrairement au journal direct, les erreurs
    remontent."""
    zone = ZoneInfo(fuseau)
    bilan = {"ajoutes": 0, "mis_a_jour": 0, "deja_journalises": 0, "ignores": []}
    for fichier in sorted(Path(dossier).glob("*/*.json")):
        try:
            recu_le = datetime.strptime(fichier.stem, "%Y%m%d_%H%M%S").replace(tzinfo=zone)
            data = json.loads(fichier.read_text(encoding="utf-8"))
        except ValueError as e:
            bilan["ignores"].append(f"{fichier.parent.name}/{fichier.name} : {e}")
            continue
        id_dispositif = data.get("id_dispositif")
        if id_dispositif is None and fichier.parent.name.isdigit():
            id_dispositif = int(fichier.parent.name)
        params = {
            "task_id": f"archive:{fichier.parent.name}/{fichier.name}",
            "id_dispositif": id_dispositif,
            "recu_le": recu_le,
            "device": data.get("device") or appareil_du_payload(data),
            "id_role": data.get("id_role"),
            "placettes": json.dumps(resume_placettes(data)),
        }
        with DB.engine.begin() as cx:
            direct = cx.execute(text(f"""
                SELECT 1 FROM {TABLE}
                 WHERE task_id NOT LIKE 'archive:%'
                   AND id_dispositif IS NOT DISTINCT FROM :id_dispositif
                   AND recu_le BETWEEN CAST(:recu_le AS timestamptz) - interval '2 minutes'
                                   AND CAST(:recu_le AS timestamptz) + interval '2 minutes'
                 LIMIT 1
            """), params).first()
            if direct:
                bilan["deja_journalises"] += 1
                continue
            existe = cx.execute(text(f"SELECT 1 FROM {TABLE} WHERE task_id = :task_id"), params).first()
            if not simulation:
                cx.execute(text(f"""
                    INSERT INTO {TABLE} (task_id, id_dispositif, recu_le, statut, device, id_role, placettes)
                    VALUES (:task_id, :id_dispositif, CAST(:recu_le AS timestamptz), 'archive',
                            :device, :id_role, CAST(:placettes AS jsonb))
                    ON CONFLICT (task_id) DO UPDATE
                       SET id_dispositif = EXCLUDED.id_dispositif, recu_le = EXCLUDED.recu_le,
                           device = EXCLUDED.device, id_role = EXCLUDED.id_role,
                           placettes = EXCLUDED.placettes
                     WHERE {TABLE}.statut = 'archive'
                """), params)
            bilan["mis_a_jour" if existe else "ajoutes"] += 1
    return bilan


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


_STATUTS = ("succes", "echec", "en_cours", "archive")

# Nombre de lignes envoyées, d'après le résumé par placette : même mesure pour
# les exports directs et les archives (qui n'ont pas de compteurs).
_NB_MODIFICATIONS_SQL = """
    COALESCE((SELECT sum((p->>'nb_modifications')::int)
                FROM jsonb_array_elements(COALESCE(e.placettes, '[]'::jsonb)) p), 0)
"""


def _mois_manquants(mois_presents) -> list[str]:
    """Mois ``AAAA-MM`` absents entre le premier et le dernier présent : une
    série continue garde visibles les mois sans activité."""
    if not mois_presents:
        return []
    annee, num = map(int, min(mois_presents).split("-"))
    fin, manquants = max(mois_presents), []
    while f"{annee:04d}-{num:02d}" <= fin:
        cle = f"{annee:04d}-{num:02d}"
        if cle not in mois_presents:
            manquants.append(cle)
        annee, num = (annee + 1, 1) if num == 12 else (annee, num + 1)
    return manquants


def statistiques_exports(id_dispositif: int | None = None) -> dict:
    """Agrégats du journal pour les graphiques de suivi : envois par mois
    (par statut, mois sans envoi compris), par dispositif et par modèle
    d'appareil (sans la version d'Android, que Dendro3 accole au modèle)."""
    filtre = "WHERE e.id_dispositif = :id_dispositif" if id_dispositif is not None else ""
    params = {"id_dispositif": id_dispositif}
    vide = {"par_mois": [], "par_dispositif": [], "par_appareil": []}
    try:
        mois = DB.session.execute(text(f"""
            SELECT to_char(date_trunc('month', e.recu_le), 'YYYY-MM') AS mois, e.statut,
                   count(*) AS envois, sum({_NB_MODIFICATIONS_SQL}) AS modifications
              FROM {TABLE} e {filtre}
             GROUP BY 1, 2
        """), params).mappings().all()
        dispositifs = DB.session.execute(text(f"""
            SELECT e.id_dispositif, d.name AS nom_dispositif, count(*) AS envois,
                   sum({_NB_MODIFICATIONS_SQL}) AS modifications
              FROM {TABLE} e
              LEFT JOIN pr_psdrf.t_dispositifs d ON d.id_dispositif = e.id_dispositif
              {filtre}
             GROUP BY 1, 2
             ORDER BY envois DESC, nom_dispositif
        """), params).mappings().all()
        appareils = DB.session.execute(text(f"""
            SELECT COALESCE(NULLIF(regexp_replace(e.device, '\\s*-\\s*Android.*$', ''), ''), '(inconnu)') AS appareil,
                   count(*) AS envois
              FROM {TABLE} e {filtre}
             GROUP BY 1
             ORDER BY envois DESC, appareil
        """), params).mappings().all()
    except Exception:
        DB.session.rollback()
        logger.exception("[DENDRO3] Statistiques du journal illisibles")
        return vide

    par_mois = {}
    for r in mois:
        m = par_mois.setdefault(r["mois"], {"mois": r["mois"], "envois": 0, "modifications": 0,
                                            **{s: 0 for s in _STATUTS}})
        m["envois"] += r["envois"]
        m["modifications"] += int(r["modifications"] or 0)
        if r["statut"] in _STATUTS:
            m[r["statut"]] += r["envois"]
    for cle in _mois_manquants(par_mois):
        par_mois[cle] = {"mois": cle, "envois": 0, "modifications": 0, **{s: 0 for s in _STATUTS}}

    return {
        "par_mois": [par_mois[k] for k in sorted(par_mois)],
        "par_dispositif": [{**dict(r), "modifications": int(r["modifications"] or 0)} for r in dispositifs],
        "par_appareil": [dict(r) for r in appareils],
    }


# Lignes Dendro3 conservées en staging, datées par la tablette (dernière
# modification, sinon création) : mesures d'arbres, de bois morts et relevés
# de placette. `tablette` est vide pour les copies de la production
# téléchargées puis renvoyées par l'appli (RNF-SI/dendro3#82) : ce ne sont
# pas des saisies.
_SAISIES_STAGING_SQL = """
    SELECT p.id_dispositif, 'arbres' AS type, coalesce(m.updated_at, m.created_at) AS saisi_le,
           NULLIF(coalesce(m.updated_on, m.created_on), '') AS tablette
      FROM pr_psdrf_staging.t_arbres_mesures m
      JOIN pr_psdrf_staging.t_arbres a ON a.id_arbre = m.id_arbre
      JOIN pr_psdrf_staging.t_placettes p ON p.id_placette = a.id_placette
    UNION ALL
    SELECT p.id_dispositif, 'bois_morts', coalesce(m.updated_at, m.created_at),
           NULLIF(coalesce(m.updated_on, m.created_on), '')
      FROM pr_psdrf_staging.t_bm_sup_30_mesures m
      JOIN pr_psdrf_staging.t_bm_sup_30 b ON b.id_bm_sup_30 = m.id_bm_sup_30
      JOIN pr_psdrf_staging.t_placettes p ON p.id_placette = b.id_placette
    UNION ALL
    SELECT p.id_dispositif, 'releves', coalesce(cp.updated_at, cp.created_at),
           NULLIF(coalesce(cp.updated_on, cp.created_on), '')
      FROM pr_psdrf_staging.cor_cycles_placettes cp
      JOIN pr_psdrf_staging.t_placettes p ON p.id_placette = cp.id_placette
"""
_TYPES_SAISIE = ("arbres", "bois_morts", "releves")


def activite_terrain(id_dispositif: int | None = None) -> dict:
    """Activité de terrain d'après les horodatages des saisies Dendro3 en
    staging (#76) : saisies par mois et par type, et par dispositif (premier /
    dernier mois). Indépendant du journal des envois, donc couvre aussi les
    campagnes antérieures à sa mise en place. Une ligne modifiée compte au
    mois de sa dernière modification ; les imports Excel n'y figurent pas.
    Les lignes sans tablette (copies téléchargées renvoyées) sont écartées et
    seulement dénombrées (``sans_tablette``)."""
    filtre = "AND s.id_dispositif = :id_dispositif" if id_dispositif is not None else ""
    vide = {"par_mois": [], "par_dispositif": [], "sans_tablette": 0}
    try:
        rows = DB.session.execute(text(f"""
            WITH s AS ({_SAISIES_STAGING_SQL})
            SELECT s.id_dispositif, coalesce(d.name, ds.name) AS nom_dispositif, s.type,
                   to_char(date_trunc('month', s.saisi_le), 'YYYY-MM') AS mois, count(*) AS nb
              FROM s
              LEFT JOIN pr_psdrf.t_dispositifs d ON d.id_dispositif = s.id_dispositif
              LEFT JOIN pr_psdrf_staging.t_dispositifs ds ON ds.id_dispositif = s.id_dispositif
             WHERE s.saisi_le IS NOT NULL AND s.tablette IS NOT NULL {filtre}
             GROUP BY 1, 2, 3, 4
        """), {"id_dispositif": id_dispositif}).mappings().all()
        sans_tablette = DB.session.execute(text(f"""
            WITH s AS ({_SAISIES_STAGING_SQL})
            SELECT count(*) FROM s WHERE s.tablette IS NULL {filtre}
        """), {"id_dispositif": id_dispositif}).scalar()
    except Exception:
        DB.session.rollback()
        logger.exception("[DENDRO3] Activité de terrain illisible")
        return vide

    par_mois, par_dispositif = {}, {}
    for r in rows:
        m = par_mois.setdefault(r["mois"], {"mois": r["mois"], **{t: 0 for t in _TYPES_SAISIE}, "total": 0})
        m[r["type"]] += r["nb"]
        m["total"] += r["nb"]
        d = par_dispositif.setdefault(r["id_dispositif"], {
            "id_dispositif": r["id_dispositif"], "nom_dispositif": r["nom_dispositif"],
            "saisies": 0, "premier": r["mois"], "dernier": r["mois"]})
        d["saisies"] += r["nb"]
        d["premier"], d["dernier"] = min(d["premier"], r["mois"]), max(d["dernier"], r["mois"])
    for cle in _mois_manquants(par_mois):
        par_mois[cle] = {"mois": cle, **{t: 0 for t in _TYPES_SAISIE}, "total": 0}
    return {
        "par_mois": [par_mois[k] for k in sorted(par_mois)],
        "par_dispositif": sorted(par_dispositif.values(),
                                 key=lambda d: (-d["saisies"], d["nom_dispositif"] or "")),
        "sans_tablette": sans_tablette,
    }


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


def suivi_dispositif(id_dispositif: int, nb_exports: int = 500) -> dict:
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
