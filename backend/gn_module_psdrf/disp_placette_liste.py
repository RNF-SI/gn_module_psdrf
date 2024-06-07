from math import isnan
import pandas as pd
from geonature.utils.env import DB
from .models import TPlacettes
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
            try:
                # Convert row["NumPlac"] to string if it is int
                if isinstance(row["NumPlac"], int):
                    row["NumPlac"] = str(row["NumPlac"])

                # Check if the placette exists already in the database
                existing_placette = TPlacettes.query.filter_by(id_placette_orig=row["NumPlac"], id_dispositif=row["NumDisp"]).first()

                # Create a new placette or update the existing one
                placette = existing_placette if existing_placette else TPlacettes()

                # Handle NaN values and ensure correct data types
                def handle_nan(value):
                    return None if (isinstance(value, float) and isnan(value)) else value

                placette.id_placette_orig = row["NumPlac"]
                placette.id_dispositif = handle_nan(row["NumDisp"])
                placette.strate = handle_nan(row["Strate"])
                placette.pente = handle_nan(row["Pente"])
                placette.poids_placette = handle_nan(row["PoidsPlacette"])
                placette.correction_pente = row["CorrectionPente"] == 't'
                placette.exposition = handle_nan(row["Exposition"])
                placette.habitat = handle_nan(row["Habitat"])
                placette.station = handle_nan(row["Station"])
                placette.typologie = handle_nan(row["Typologie"])
                placette.groupe = handle_nan(row["Groupe"])
                placette.groupe1 = handle_nan(row["Groupe1"])
                placette.groupe2 = handle_nan(row["Groupe2"])
                placette.ref_habitat = row["Ref_Habitat"]
                placette.precision_habitat = handle_nan(row["Precision_Habitat"])
                placette.ref_station = handle_nan(row["Ref_Station"])
                placette.ref_typologie = handle_nan(row["Ref_Typologie"])
                placette.descriptif_groupe = handle_nan(row["Descriptif_Groupe"])
                placette.descriptif_groupe1 = handle_nan(row["Descriptif_Groupe1"])
                placette.descriptif_groupe2 = handle_nan(row["Descriptif_Groupe2"])
                placette.precision_gps = row["PrecisionGPS"]
                placette.cheminement = handle_nan(row["Cheminement"])

                # Add the new placette if it did not exist
                if existing_placette:
                    updated_count += 1
                else:
                    DB.session.add(placette)

            except Exception as row_error:
                logging.critical(f"Error processing row {index}: {row_error}")

        # Commit the changes to the database
        DB.session.commit()
        return f"{added_count} nouvelles placettes ajoutées et {updated_count} placettes ajoutées."

    except KeyError as e:
        logging.critical(f"Column or sheet not found: {e}")
        return {"error": f"Column or sheet not found: {e}"}, 400
    except Exception as e:
        logging.critical(f"Error processing file: {e}")
        return {"error": f"Error processing file: {e}"}, 500
