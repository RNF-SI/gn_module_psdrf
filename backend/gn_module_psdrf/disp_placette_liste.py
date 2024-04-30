from math import isnan
import rpy2
import rpy2.robjects as robjects
from rpy2.robjects.packages import STAP
import pandas as pd
from geonature.utils.env import DB
from .models import TPlacettes
import datetime
import os
import logging


def disp_placette_liste_add(disp_placette_liste_file):
    """
    Add new placette of a dispositif if it does not exist, update it if it does.
    """
    try:
        print(disp_placette_liste_file)
        
        # Load the Excel file into a Pandas DataFrame
        placettes_df = pd.read_excel(disp_placette_liste_file)

        added_count = 0
        updated_count = 0

        print(placettes_df)

        # Iterate over the DataFrame
        for index, row in placettes_df.iterrows():

            # Convert row["NumPlac"] to string if it is int
            if type(row["NumPlac"]) == int:
                row["NumPlac"] = str(row["NumPlac"])
            # Check if the placette exists already in the database
            existing_placette = TPlacettes.query.filter_by(id_placette_orig=row["NumPlac"], id_dispositif=row["NumDisp"],).first()

           # Create a new placette or update the existing one
            placette = existing_placette if existing_placette else TPlacettes()

            # Update or set the fields for the placette
            placette.id_placette_orig = row["NumPlac"]
            placette.id_dispositif = row["NumDisp"]
            placette.strate = row["Strate"]
            placette.pente = row["Pente"]
            placette.poids_placette = row["PoidsPlacette"]
            placette.correction_pente = row["CorrectionPente"] == 't'
            placette.exposition = row["Exposition"]
            placette.habitat = row["Habitat"]
            placette.station = row["Station"]
            placette.typologie = row["Typologie"]
            placette.groupe = row["Groupe"]
            placette.groupe1 = row["Groupe1"]
            placette.groupe2 = row["Groupe2"]
            placette.ref_habitat = row["Ref_Habitat"]
            placette.precision_habitat = row["Precision_Habitat"]
            placette.ref_station = row["Ref_Station"]
            placette.ref_typologie = row["Ref_Typologie"]
            placette.descriptif_groupe = row["Descriptif_Groupe"]
            placette.descriptif_groupe1 = row["Descriptif_Groupe1"]
            placette.descriptif_groupe2 = row["Descriptif_Groupe2"]
            placette.precision_gps = row["PrecisionGPS"]
            placette.cheminement = row["Cheminement"]

            # Add the new placette if it did not exist
            if existing_placette:
                updated_count += 1
            else:    
                DB.session.add(placette)
            
        # Commit the changes to the database
        DB.session.commit()
        return f"{added_count} nouvelles placettes ajoutées et {updated_count} placettes ajoutées."

    except KeyError as e:
        logging.critical(f"Column or sheet not found: {e}")
        return {"error": f"Column or sheet not found: {e}"}, 400
    except Exception as e:
        logging.critical(f"Error processing file: {e}")
        return {"error": f"Error processing file: {e}"}, 500