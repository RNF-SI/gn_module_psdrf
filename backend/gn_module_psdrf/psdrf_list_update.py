import datetime
import logging
from math import isnan
from pathlib import Path

import pandas as pd
from flask import current_app
from geonature.utils.env import DB

from .models import TCycles, TDispositifs
# Déclenche le bootstrap (sys.path vers le sous-module PermPSDRF4py).
from .psdrf_py import SUBMODULE_ROOT  # noqa: F401
from python.script.psdrf_codes import psdrf_codes  # noqa: E402


def psdrf_list_update(psdrf_list_file, update_code_ecologie):
    try:
        # Répertoire de données depuis la configuration GeoNature.
        data_dir = Path(current_app.config["ROOT_PATH"]) / current_app.config.get("PSDRF_DATA_DIR", "media/psdrf/data")
        upload_dir = Path(current_app.config["ROOT_PATH"]) / current_app.config.get("PSDRF_UPLOAD_DIR", "media/psdrf/uploads")
        data_dir.mkdir(parents=True, exist_ok=True)
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Sauvegarder le classeur PsdrfListes dans le répertoire de données :
        # c'est la source des référentiels (codes) consommée à la génération.
        excel_file_path = data_dir / "PsdrfListes.xlsx"
        psdrf_list_file.save(str(excel_file_path))

        sheet_names = ['CodeDurete', 'CodeEcologie', 'CodeEcorce', 'CodeEssence', 'CodeTypoArbres',
                       'Communes', 'Dispositifs', 'EssReg', 'Referents', 'Tarifs', 'Cycles']

        for sheet_name in sheet_names:
            try:
                df = pd.read_excel(open(excel_file_path, 'rb'), sheet_name=sheet_name)
                csv_file_path = data_dir / f"{sheet_name}.csv"
                df.to_csv(csv_file_path, index=False)
            except Exception as e:
                logging.error(f"Error processing sheet {sheet_name}: {e}")

        if update_code_ecologie:
            process_code_ecologie(excel_file_path)

        df = pd.read_excel(open(excel_file_path, 'rb'), sheet_name='Cycles')
        for index, row in df.iterrows():
            add_dispositif(row)
            add_cycle(row)

        # Référentiels Python (remplace psdrf_Codes.R) : écrit data_dir/tables/psdrfCodes.pkl
        psdrf_codes(data_dir, excel_file_path)

    except Exception as e:
        logging.critical(f"Error in psdrf_list_update: {e}")
        raise

def process_code_ecologie(excel_file_path):
    try:
        df = pd.read_excel(open(excel_file_path, 'rb'), sheet_name='CodeEcologie')
        for index, row in df.iterrows():
            add_or_update_code_ecologie(row)
    except Exception as e:
        logging.critical(f"Error in process_code_ecologie: {e}")
        raise

def add_or_update_code_ecologie(row):
    """
    Add new code ecologie to db if it doesn't exist, update it if it does
    """
    try:
        # Construct mnemonique
        mnemonique = f"{row['Codification']}_{row['Code']}"

        # Check if the record already exists
        existing_record = DB.session.execute(
            """
            SELECT id_nomenclature 
            FROM ref_nomenclatures.t_nomenclatures 
            WHERE id_type = ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE')
              AND cd_nomenclature = CAST(:code AS VARCHAR)
            """,
            {'code': str(row['Code'])}  # Ensure code is treated as a string
        ).fetchone()

        if existing_record:
            # Update existing record
            sql = """
            UPDATE ref_nomenclatures.t_nomenclatures 
            SET mnemonique = :mnemonique,
                label_default = :label_default,
                label_fr = :label_fr
            WHERE id_nomenclature = :id
            """
            params = {
                'mnemonique': mnemonique,
                'label_default': f"{row['Code']} - {row['Descriptif']}",
                'label_fr': f"{row['Code']} - {row['Descriptif']}",
                'id': existing_record['id_nomenclature']
            }
        else:
            # Insert new record
            sql = """
            INSERT INTO ref_nomenclatures.t_nomenclatures 
            (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
            VALUES 
            (
                ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'),
                :code,
                :mnemonique,
                :label_default,
                NULL,
                :label_fr,
                NULL,
                'PSDRF',
                'Validé',
                true
            )
            """
            params = {
                'code': str(row['Code']),  # Ensure code is treated as a string
                'mnemonique': mnemonique,
                'label_default': f"{row['Code']} - {row['Descriptif']}",
                'label_fr': f"{row['Code']} - {row['Descriptif']}"
            }

        DB.session.execute(sql, params)
        DB.session.commit()
    except Exception as e:
        logging.critical(f"Error in add_or_update_code_ecologie: {e}")
        DB.session.rollback()
        raise

def add_dispositif(row):
    """
    Add new dispositif to db if it doesn't exist, update it if it does
    """
    try:
        dispList = DB.session.query(TDispositifs).filter(TDispositifs.id_dispositif == row["NumDisp"])
        dup_dispList = dispList.first()
        if dup_dispList:
            dispList.update(
                {
                    TDispositifs.name: row["Nom"],
                }
            )
            DB.session.commit()
        else:
            new_disp = TDispositifs(
                id_dispositif=row["NumDisp"],
                name=row["Nom"],
                id_organisme=-1,
                alluvial=False
            )
            DB.session.add(new_disp)
            DB.session.commit()
    except Exception as e:
        logging.critical(f"Error in add_dispositif: {e}")
        DB.session.rollback()
        raise

def add_cycle(row):
    """
    Add new cycle to db if it doesn't exist, update it if it does
    """
    def parse_date(value, is_end_date=False):
        """
        Helper function to parse dates. Returns None if the value is not a valid date.
        """
        try:
            if isnan(value):
                return None
            year = int(value)
            return datetime.date(year, 12, 31) if is_end_date else datetime.date(year, 1, 1)
        except (ValueError, TypeError):
            return None

    try:
        cycleList = DB.session.query(TCycles).filter((TCycles.id_dispositif == row["NumDisp"]) & (TCycles.num_cycle == row["Cycle"]))
        dup_cycleList = cycleList.first()

        if dup_cycleList:
            cycleList.update(
                {
                    v: (row[k] 
                    if k not in ['DateIni', 'DateFin'] 
                    else parse_date(row[k], is_end_date=(k=='DateFin')))
                    for k, v in {'NumDisp': 'id_dispositif', 'Cycle': 'num_cycle', 'Monitor': 'monitor', 'DateIni': 'date_debut', 'DateFin': 'date_fin'}.items()
                    if k in row.index 
                }
            )
        else:
            new_cycle = TCycles(
                **{
                    v: (row[k] 
                    if k not in ['DateIni', 'DateFin'] 
                    else parse_date(row[k], is_end_date=(k=='DateFin')))
                    for k, v in {'NumDisp': 'id_dispositif', 'Cycle': 'num_cycle', 'Monitor': 'monitor', 'DateIni': 'date_debut', 'DateFin': 'date_fin'}.items()
                    if k in row.index 
                }
            )    
            DB.session.add(new_cycle)
        DB.session.commit()
    except Exception as e:
        logging.critical(f"Error in add_cycle: {e}")
        DB.session.rollback()
        raise
