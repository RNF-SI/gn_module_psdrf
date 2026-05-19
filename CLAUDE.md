# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Nature du projet

`gn_module_psdrf` est un **module GeoNature** (plugin) dédié au Protocole de Suivi Dendrométrique des Réserves Forestières (PSDRF). Il ne fonctionne pas en autonome : il doit être installé dans une instance GeoNature existante (versions 2.6.0 à 3.0.0, cf. `manifest.toml`). Le code d'entrée GeoNature est déclaré dans `setup.py` via `entry_points['gn_module']` (blueprint, schémas de config, migrations, tâches Celery).

## Environnement de travail

Toutes les commandes Python/Flask/R doivent être exécutées en tant que `geonatureadmin` avec le virtualenv GeoNature activé :

```bash
su geonatureadmin
source /home/geonatureadmin/geonature/backend/venv/bin/activate
```

Le dépôt est édité dans `/home/aschlegel/gn_module_psdrf/` mais le module installé est à `/home/geonatureadmin/gn_module_psdrf/` — beaucoup de scripts (génération carnet, logs R) référencent **en dur** le second chemin. Vérifier le chemin attendu avant de lancer un script.

## Commandes courantes

```bash
# Installation du module dans GeoNature
geonature install_gn_module /home/geonatureadmin/gn_module_psdrf/ /cmr

# Dépendances système (LaTeX + ~30 paquets R requis pour la génération du carnet)
bash install_env.sh

# Backend Flask
cd /home/geonatureadmin/geonature && flask run

# Frontend Angular (intégré au shell GeoNature)
cd frontend && npm install && npm run start

# Migrations BDD (alembic, déclenchées par GeoNature)
cd /home/geonatureadmin/geonature && alembic upgrade head

# Redémarrer les services
sudo systemctl restart geonature
```

**Pas de suite de tests pytest** : `backend/tests/` n'existe pas. Le `package.json` du frontend n'a pas non plus de tests configurés. La validation se fait manuellement via l'UI ou via les scripts ci-dessous.

### Test rapide de la génération de carnet

Cycle de développement recommandé sur le template R/LaTeX (voir `DOCUMENTATION_CARNET.md` pour le détail) :

```bash
# Génération complète (UI ou standalone) une première fois pour produire les .Rdata
python generate_carnet_standalone.py <dispositif_id> [--nocarnet] [--plan]

# Itération rapide sur le template (réutilise les .Rdata existants)
bash test_carnet.sh <dispositif_id>

# Nettoyage + régénération
bash clean_and_test.sh <dispositif_id>

# Appel direct du pipeline Python depuis GeoNature
cd /home/geonatureadmin/geonature && python -c \
  "from gn_module_psdrf.data_analysis import data_analysis; \
   data_analysis(<DISP_ID>, False, False, {'Answer_Radar': None})"
```

## Architecture

### Flux de données global

```
Excel utilisateur ──► /validation (data_verification.py)
                          │
                          ▼
                   /integration ──► staging (pr_psdrf_staging.*)
                          │
                          ▼
                   merge ──► production (pr_psdrf.*)
                          │
                          ▼
                   /analysis ──► R (rpy2) ──► LaTeX ──► PDF carnet
```

### Backend (`backend/gn_module_psdrf/`)

- **`blueprint.py`** — Toutes les routes Flask (≈40 endpoints sous `/psdrf/...`). Concentre dispositifs, placettes, arbres, validation, intégration, analyse, gestion des rôles/organismes, exports Excel/Dendro3. Beaucoup de routes utilisent Celery (`/analysis/<id>` → tâche → `/analysis/status/<task_id>` → `/analysis/result/<task_id>`).
- **`models.py`** — Modèles SQLAlchemy des tables de production (schéma `pr_psdrf`) : `TDispositifs`, `TPlacettes`, `TArbres`, `TArbresMesures`, `TBmSup30`, `TBmSup30Mesures`, `TCycles`, `CorCyclesPlacettes`, `TRegenerations`, `TReperes`, `TTransects`, `BibEssences`, `CorDispositifsRoles`.
- **`schemas/`** — Marshmallow schemas pour la sérialisation des modèles **production**.
- **`pr_psdrf_staging_functions/`** — Schéma SQL séparé (`pr_psdrf_staging`) pour l'import en deux temps :
  - `models_staging.py` : modèles SQLAlchemy miroirs des modèles de prod.
  - `insert_or_update_functions/` : un fichier par entité, contient la logique de merge staging → prod.
- **`staging_schemas/`** — Marshmallow schemas pour les modèles staging.
- **`data_verification.py`** (≈146 KB) — Validation des fichiers Excel en entrée, détection d'erreurs cellule par cellule. Sortie consommée par le frontend pour affichage des erreurs.
- **`data_integration.py`** — Insertion validée vers les tables staging.
- **`data_analysis.py`** — Pont Python/R via rpy2 : extrait les données de la BDD, les convertit en DataFrames, lance les scripts R. Délègue d'abord à `generate_carnet_web.py` (à la racine du repo) et a un fallback vers l'ancien chemin R direct.
- **`tasks.py`** — Tâches Celery (`test_celery` = génération carnet asynchrone, `fetch_dispositif_data`, `fetch_updated_data`, `insert_or_update_data`). Les exports lourds passent par là pour ne pas bloquer Flask.
- **`migrations/`** — Migrations Alembic spécifiques au module (création schéma, switch UUID, ajout colonnes cycles).
- **`Rscripts/`** — Toute la chaîne d'analyse R :
  - `psdrf_Xls2Rdata.R`, `BDD2RData.R` — entrée des données vers RData.
  - `psdrf_Calculs.R`, `psdrf_AgregArbres.R`, `psdrf_AgregPlacettes.R` — calculs dendrométriques.
  - `psdrf_EditCarnet.R`, `template/psdrf_Carnet_V3.Rnw`, `generation_carnet.R` — génération du PDF via knit2pdf.
  - `out/` — répertoire de sortie (PDF, TEX, figures). **Toujours nettoyé** avant chaque génération.

### Génération du carnet (chemin critique)

Deux entrées possibles convergent vers les mêmes scripts R :
1. Via l'API : `/analysis/<id>` → Celery `test_celery` → `data_analysis()` → `generate_carnet_web()` (script à la racine `generate_carnet_web.py`).
2. En autonome : `generate_carnet_standalone.py <id>` lit `config/settings.ini`, se connecte directement en SQLAlchemy, appelle les mêmes scripts R. Utile pour tester hors GeoNature.

Le pipeline R produit des `.Rdata` intermédiaires dans `Rscripts/tables/`, puis le template Rnw (LaTeX + chunks R) est compilé en PDF. `test_carnet_only.R` réutilise ces `.Rdata` pour itérer rapidement sur le template sans rejouer les requêtes SQL.

### Frontend (`frontend/app/`)

Module Angular qui s'intègre dans le shell GeoNature via `GN2CommonModule`. Routes déclarées dans `gnModule.module.ts` :
- `/` → `DispositifsComponent` (liste + carte)
- `/infodispositif/:id` → `InfoDispositifComponent` (détail + lancement carnet)
- `/importdonnees` → `ImportDonneesComponent` (import Excel + correction d'erreurs)
- `/adminPage` → `AdminComponent` (rôles, organismes)
- `/download-mobile-app` → `DendroDownloadComponent`

Services clés : `route.service.ts` (PsdrfDataService — toutes les requêtes API), `excel.import.service.ts` (parsing xlsx côté client), `error.history.service.ts` + `error.correction.service.ts` (état de l'import). `package.json` ne déclare que `xlsx` ; toutes les autres dépendances Angular/Material viennent de l'app GeoNature parente.

## Conventions de code

- **Python** : snake_case (variables/fonctions), CamelCase (classes), imports groupés (stdlib / externes / locaux).
- **TypeScript** : camelCase (variables/fonctions), PascalCase (interfaces/composants).
- **R** : commentaires Roxygen pour les paramètres et valeurs de retour.
- **LaTeX dans Rnw** : passer les chaînes par `sanitize_latex_output()` ; protéger les filtres contre les NA via `safe_filter_vha()` (cf. `DOCUMENTATION_CARNET.md`).

## Configuration

- `manifest.toml` — code du module (`PSDRF`), versions GeoNature compatibles.
- `conf_gn_module.toml` — `api_url = '/psdrf'`, `id_application = 7`, chemins `PSDRF_DATA_DIR`/`PSDRF_UPLOAD_DIR`/`PSDRF_EXPORT_DIR` sous `media/psdrf/`, `CELERY_IMPORTS` pointant vers le blueprint.
- `config/settings.ini.sample` — exemple pour `generate_carnet_standalone.py` (db_uri + chemins).
- `requirements.in` — dépendances Python pinnées : Flask ≥ 2.2.2, **rpy2 == 3.5.1** (figée, sensible), excel2json, openpyxl.

## Debugging

- Logs GeoNature : `sudo journalctl -u geonature`
- Logs R (génération carnet) : `/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/out/` + `carnet_generation.log` à la racine du module.
- En cas d'erreur opaque côté carnet, commencer par `clean_and_test.sh` (purge les `.tex/.pdf/.aux` orphelins qui font échouer knit2pdf silencieusement).

## Documentation

- `README.rst` — installation rapide.
- `DOCUMENTATION_CARNET.md` — **référence détaillée** sur la génération du carnet (architecture, scripts de test, workflow de modification du template). À lire avant toute intervention sur la chaîne R/LaTeX.
