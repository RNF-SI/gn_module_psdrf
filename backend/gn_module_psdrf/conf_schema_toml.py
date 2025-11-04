"""
   Spécification du schéma toml des paramètres de configurations
   La classe doit impérativement s'appeller GnModuleSchemaConf
   Fichier spécifiant les types des paramètres et leurs valeurs par défaut
   Fichier à ne pas modifier. Paramètres surcouchables dans config/config_gn_module.tml
"""

from marshmallow import Schema, fields
import os


class FormConfig(Schema):
    pass


class GnModuleSchemaConf(Schema):
    # Répertoire de stockage des données PSDRF
    PSDRF_DATA_DIR = fields.String(
        load_default="media/psdrf/data",
        metadata={"description": "Répertoire pour stocker les données PSDRF"}
    )
    
    # Répertoire temporaire pour les fichiers d'upload
    PSDRF_UPLOAD_DIR = fields.String(
        load_default="media/psdrf/uploads",
        metadata={"description": "Répertoire temporaire pour les uploads"}
    )
    
    # Répertoire pour les exports
    PSDRF_EXPORT_DIR = fields.String(
        load_default="media/psdrf/exports", 
        metadata={"description": "Répertoire pour les exports"}
    )
