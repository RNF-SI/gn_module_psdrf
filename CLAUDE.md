# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Nature du projet

`gn_module_psdrf` est un **module GeoNature** (plugin) dédié au Protocole de Suivi Dendrométrique des Réserves Forestières (PSDRF). Il ne fonctionne pas en autonome : il doit être installé dans une instance GeoNature existante (versions 2.6.0 à 3.0.0, cf. `manifest.toml`). Le code d'entrée GeoNature est déclaré dans `setup.py` via `entry_points['gn_module']` (blueprint, schémas de config, migrations, tâches Celery).

> **Bascule R → Python (en cours / fait).** La génération du carnet, du plan des
> arbres et des référentiels ne passe plus par R/rpy2 : elle s'appuie sur le
> pipeline Python pur **PermPSDRF4py**, intégré en **sous-module git** dans
> `backend/gn_module_psdrf/PermPSDRF4py`. Après clonage : `git submodule update --init`.
> Le pont vit dans le package `backend/gn_module_psdrf/psdrf_py/`. R, rpy2 et le
> dossier `Rscripts/` ont été retirés ; **LaTeX (pdflatex) reste requis** pour
> compiler le PDF.

## Environnement de travail

Toutes les commandes Python/Flask doivent être exécutées en tant que `geonatureadmin` avec le virtualenv GeoNature activé :

```bash
su geonatureadmin
source /home/geonatureadmin/geonature/backend/venv/bin/activate
```

Le dépôt est édité dans `/home/aschlegel/gn_module_psdrf/` mais le module installé est à `/home/geonatureadmin/gn_module_psdrf/` — certains chemins peuvent référencer **en dur** le second chemin. Vérifier le chemin attendu avant de lancer un script.

## Commandes courantes

```bash
# Récupérer le sous-module Python (obligatoire avant install)
git submodule update --init --recursive

# Installation du module dans GeoNature (install éditable : le sous-module reste sur disque)
geonature install_gn_module /home/geonatureadmin/gn_module_psdrf/ /cmr

# Dépendances système (LaTeX/pdflatex uniquement — plus aucun paquet R)
bash install_env.sh

# Backend Flask
cd /home/geonatureadmin/geonature && flask run

# Frontend Angular (intégré au shell GeoNature)
cd frontend && npm install && npm run start

# Migrations BDD — TOUJOURS via la CLI GeoNature, JAMAIS `alembic` en direct.
# GeoNature agrège les migrations de tous les modules (branches Alembic multiples) :
# un `alembic upgrade head` nu échoue sur « Multiple head revisions are present ».
# Les migrations de ce module portent le branch label `psdrf` → cibler ce head :
cd /home/geonatureadmin/geonature && geonature db upgrade psdrf@head
# (revenir en arrière d'un cran : geonature db downgrade psdrf@-1)

# Redémarrer les services
sudo systemctl restart geonature
```

**Pas de suite de tests pytest** : `backend/tests/` n'existe pas. Le `package.json` du frontend n'a pas non plus de tests configurés. La validation se fait manuellement via l'UI ou via les scripts ci-dessous.

### Test rapide de la génération de carnet

La génération est en Python pur. Deux niveaux de test :

```bash
# 1/ Pipeline autonome (sous-module), sur les données Excel de test data/ (parité R)
cd backend/gn_module_psdrf/PermPSDRF4py
python -m python.script.run_load          --project . --disp 239 --cycle 2
python -m python.script.run_calculs       --rep <REP> --disp 239
python -m python.script.run_agreg_arbres  --rep <REP> --disp 239 --tables @tables
python -m python.script.run_agreg_placettes --rep <REP> --disp 239 --groups Strate
python -m python.template.carnet.run_edit_carnet --project . --disp 239 --out-dir <REP> --pdf

# 2/ Chaîne web complète depuis GeoNature (BDD → carnet via le pont psdrf_py)
cd /home/geonatureadmin/geonature && python -c \
  "from gn_module_psdrf.data_analysis import data_analysis; \
   print(data_analysis(239, 'true', 'false', {'Answer_Radar': None}))"
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
                   /analysis ──► pipeline Python (PermPSDRF4py) ──► LaTeX ──► PDF carnet
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
- **`data_analysis.py`** — Point d'entrée appelé par Celery : délègue au pont `psdrf_py.run_pipeline` (plus aucun R/rpy2).
- **`psdrf_py/`** — Pont vers le pipeline Python (sous-module) :
  - `__init__.py` : bootstrap (ajoute le sous-module au `sys.path`, force matplotlib `Agg`).
  - `db_to_campagne.py` : adaptateur BDD → dossier « campagne » (écrit `psdrfDonneesBrutes.pkl` + `psdrfCodes.pkl`), remplace l'import Excel du pipeline.
  - `run_pipeline.py` : orchestration `psdrf_calculs → psdrf_agreg_arbres → psdrf_agreg_placettes → psdrf_edit_carnet` (+ `psdrf_edit_plans_arbres`).
  - `carnet_tables.py` : liste figée des 97 tables `psdrfPla*` nécessaires à un carnet complet.
- **`PermPSDRF4py/`** — **Sous-module git** : le pipeline Python autonome (calculs, agrégation, carnet/plans). Consommé en lecture seule via `psdrf_py`.
- **`tasks.py`** — Tâches Celery (`test_celery` = génération carnet/plan async puis ZIP des PDF sous `PSDRF_EXPORT_DIR/zip` + purge du dossier de travail ; `fetch_dispositif_data`, `fetch_updated_data`, `insert_or_update_data`).
- **`migrations/`** — Migrations Alembic spécifiques au module (création schéma, switch UUID, ajout colonnes cycles).

### Génération du carnet (chemin critique)

`/analysis/<id>` → Celery `test_celery` → `data_analysis()` → `run_psdrf_pipeline()` :
1. `db_to_campagne.build_campagne_from_db()` interroge `pr_psdrf` et écrit, dans un dossier campagne temporaire sous `PSDRF_EXPORT_DIR`, les pickles d'entrée (`psdrfDonneesBrutes.pkl` depuis la BDD, `psdrfCodes.pkl` depuis PsdrfListes/`PSDRF_DATA_DIR`).
2. Les étapes du sous-module s'enchaînent sur ce dossier (`rep_psdrf == rep_sav == campagne`), produisant les pickles intermédiaires puis le `.tex` compilé en PDF par **pdflatex** (figures matplotlib).
3. Les PDF sont zippés ; le dossier de travail est purgé.

Référentiels (`codes`) : décision projet = source **PsdrfListes** (comme l'ancien `psdrf_Codes.R`), gérée à l'upload `/psdrfListe` → `psdrf_codes()` écrit `psdrfCodes.pkl` dans `PSDRF_DATA_DIR/tables/`.

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
- **Pipeline Python (sous-module)** : code en français (docstrings/commentaires) ; ne pas modifier le sous-module depuis ce dépôt — les évolutions du pipeline se font dans `RNF-SI/PermPSDRF4py` puis bump du pointeur de sous-module.

## Configuration

- `manifest.toml` — code du module (`PSDRF`), versions GeoNature compatibles.
- `conf_gn_module.toml` — `api_url = '/psdrf'`, `id_application = 7`, chemins `PSDRF_DATA_DIR`/`PSDRF_UPLOAD_DIR`/`PSDRF_EXPORT_DIR` sous `media/psdrf/`, `CELERY_IMPORTS` pointant vers le blueprint.
- `requirements.in` — dépendances Python : Flask, openpyxl, pandas, numpy, scipy, matplotlib, jinja2 (rpy2 retiré).
- `.gitmodules` — déclare le sous-module `backend/gn_module_psdrf/PermPSDRF4py` (dépôt `RNF-SI/PermPSDRF4py`, branche `main`).

### Première installation / mise en service

Après `install_gn_module`, avant toute génération : **charger `PsdrfListes` via la route `/psdrfListe`** (page admin). Cet upload écrit `PsdrfListes.xlsx` + `tables/psdrfCodes.pkl` dans `PSDRF_DATA_DIR`, peuple Dispositifs/Cycles et la nomenclature `PSDRF_ECOLOGIE`. Sans lui, la génération échoue (« Référentiel introuvable… »). Les nomenclatures `PSDRF_DURETE`/`PSDRF_ECORCE` viennent des migrations. Un dispositif doit être présent dans PsdrfListes (Cycles/Tarifs/EssReg/Cat) avant de générer son carnet. Détails : `README.rst`. Ne pas copier de fichiers à la main — tout passe par l'upload.

## Debugging

- Logs GeoNature : `sudo journalctl -u geonature`
- Logs génération carnet : logs Celery/worker (préfixe `[PSDRF]` / `[TASK]`).
- Carnet PDF non produit → vérifier que `pdflatex` est installé (le pipeline lève une erreur explicite sinon) et que le dispositif est présent dans PsdrfListes (onglets Cycles/Tarifs/EssReg).
- Pour itérer sur le template du carnet, travailler dans le sous-module `PermPSDRF4py` (entrée Excel + `--pdf`), pas dans le module web.

## Documentation

- `README.rst` — installation rapide.
- Pipeline de calcul/carnet : voir la doc du sous-module `PermPSDRF4py/` (`CLAUDE.md`, `docs/contrat_donnees_carnet.md`, `python/script/README.md`).
- `DOCUMENTATION_CARNET.md` — **obsolète** (ancienne chaîne R/Rnw), conservé pour archive.
