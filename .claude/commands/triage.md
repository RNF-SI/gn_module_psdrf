---
description: Analyse plusieurs issues et propose des lots par fichiers probablement touchés
argument-hint: <numéros d'issues séparés par espace>
allowed-tools: Bash(gh:*), Bash(grep:*), Read
---

Issues à analyser : $ARGUMENTS

Pour chacune : lis-la (`gh issue view <n>`), puis devine les fichiers impactés.
Repères (backend = `backend/gn_module_psdrf/`, frontend = `frontend/app/`) :
- import Excel : `data_verification.py` (règles métier), `data_integration.py`,
  `frontend/app/components/import/`, `excel.import.service.ts` ;
- synchro Dendro3 / staging : `tasks.py` (`insert_or_update_data`,
  `fetch_*`), `pr_psdrf_staging_functions/` (modèles + merge), routes
  `export_dispositif_from_dendro3` / `dispositif-synchronisation` de `blueprint.py` ;
  côté appli : `~/dendro3` ;
- carnet / plan : `data_analysis.py`, `psdrf_py/` (pont), `tasks.py`
  (`test_celery`, ZIP) ; le calcul et le gabarit LaTeX sont dans le
  sous-module PermPSDRF4py → issue à porter sur `RNF-SI/PermPSDRF4py` ;
- fiche dispositif / comparaison : `psdrf_py/etat_cycles.py`, routes
  `/dispositif/<id>/…`, `info.dispositif.component.*`, `comparaison.staging.component.*` ;
- admin : `components/admin/`, routes rôles/organismes/`psdrfListe` ;
- export Excel : `bddToExcel.py` ; schéma BDD : `models.py`, `migrations/`.

Rends UNIQUEMENT un plan (ne corrige rien) :
- Lots « mêmes fichiers » → /fix-lot, en SÉQUENTIEL dans une même session ;
- Issues indépendantes → /fix-issue, parallélisables en worktrees ;
- Issues à isoler (bac C probable, needs: discussion, ou relevant de Dendro3 /
  PermPSDRF4py) → à ne pas automatiser ;
- pour chaque lot : migration BDD (oui/non), régénération de carnet à prévoir
  en fin de lot (oui/non, quel dispositif).

Format : tableau lot / issues / fichiers estimés / séquentiel-ou-parallèle / migration / carnet.
