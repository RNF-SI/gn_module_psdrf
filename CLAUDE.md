# CLAUDE.md - GN_MODULE_PSDRF Guide

## GeoNature Module

Ce projet est un module du projet [GeoNature](https://github.com/PnX-SI/GeoNature). Il doit être installé dans une instance de GeoNature existante.

## Virtual Environment

Avant toute exécution des commandes Python, assurez-vous de vous connecter en tan que geonatureadmin d'activer l'environnement virtuel de GeoNature :

- su geoatureadmin
- Activer l'environnement virtuel: `source /home/geonatureadmin/geonature/backend/venv/bin/activate`

## Build & Run Commands

- Install module: `geonature install_gn_module /path/to/module/ /cmr`
- Run backend server (avec env virtuel actif): `cd /home/geonatureadmin/geonature && flask run`
- Install frontend deps: `cd frontend && npm install`
- Run frontend: `cd frontend && npm run start`

## Testing

- Backend: `python -m pytest backend/tests/`
- Frontend: `cd frontend && npm test`

## Code Style

- **Python**: snake_case for variables and functions, CamelCase for classes
- **TypeScript**: camelCase for variables/functions, PascalCase for interfaces/components
- **Imports**: Group imports (standard lib, external, local) with blank line between groups
- **Error handling**: Use try/except blocks with specific exceptions
- **R scripts**: Document parameters and return values with Roxygen-style comments

## Project Structure

- Backend: Flask API with R integration via rpy2
- Frontend: Angular-based web interface
- Data flow: Excel/CSV imports → Python processing → R analysis
- Key dependencies: Flask, rpy2, openpyxl, Angular

## Common Tasks

- Run R analysis (avec env virtuel actif): `cd /home/geonatureadmin/geonature && python -c "from gn_module_psdrf.data_analysis import data_analysis; data_analysis(DISPOSITIF_ID, False, False, {'Answer_Radar': None})"`
- Database migrations: `cd /home/geonatureadmin/geonature && alembic upgrade head`
- Restart GeoNature services: `sudo systemctl restart geonature`

## Debugging

- Logs GeoNature: `sudo journalctl -u geonature`
- Erreurs R: Vérifier `/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/out/` pour les logs d'erreur R
