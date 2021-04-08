import json
import pandas as pd
import numpy as np

from pathlib import Path

from varname import nameof

# Fonction principale de vérification des données du PSDRF
def data_verification(data):
  # TODO: Expliquer à quoi sert cette variable
  Test = 0

  # TODO: Expliquer à quoi sert ce tableau une fois le fichier R traduit
  error = []

  # Initialisation des données du dispositif testée dans des dataframes Pandas
  Placettes=pd.json_normalize(data[0]) 
  Cycles = pd.json_normalize(data[1])
  Arbres=pd.json_normalize(data[2])
  Rege = pd.json_normalize(data[3])
  Transect=pd.json_normalize(data[4])
  BMSsup30 = pd.json_normalize(data[5])
  Reperes=pd.json_normalize(data[6])

  # Trouver le chemin d'accès au dossier data, qui contient les tables nécessaires aux tests
  ROOT_DIR_PSDRF = Path(__file__).absolute().parent.parent
  DATA_DIR_PSDRF = ROOT_DIR_PSDRF / "data"

  #chargement des tables nécessaires aux tests 
  CodeEssence = pd.read_pickle(DATA_DIR_PSDRF / 'CodeEssence')
  
  #Creation du tableau de vérification qui sera retourné:
  # - chaque élément du tableau correspond à une erreur différente
  # - errorList correspond à la liste des éléments qui ont cette erreur
  # - correctionList correspond aux solutions possible pour résoudre cette erreur
  verificationList = []
  #Appel des fonctions de test
  check_species_Error_List = check_species(BMSsup30, CodeEssence, Test, "BMSsup30")
  if len(check_species_Error_List) >0:
    verificationList.append({'errorName': 'Essence de BMSsup30', 'errorList': check_species_Error_List, 'correctionList': CodeEssence['Essence'].tolist()})
  check_species_Error_List = check_species(BMSsup30, CodeEssence, Test, "BMSsup30")
  if len(check_species_Error_List) >0:
    verificationList.append({'errorName': 'Essence de BMSsup30', 'errorList': check_species_Error_List, 'correctionList': CodeEssence['Essence'].tolist()})

  verificationObj = json.dumps(verificationList, cls=NumpyEncoder)
  return verificationObj

# Fonction d'encodage en Json
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

# Fonction de vérification des espèces 
def check_species(table_to_test, species, status, tablename):
  error = []

  # Récupérer les essences qui apparaissent dans table_to_test mais pas dans species
  species_list_temp = table_to_test[(~table_to_test['Essence'].isin(species['Essence'])) & (~table_to_test['Essence'].isna())]\
  [['Essence']]
  species_list = species_list_temp.drop_duplicates()['Essence'].tolist()

  if len(species_list) > 0:
      status = np.where(status >= 2, status, 2)
      for i in species_list:
          err= {
            "message": "l'essence"+ i + "figure dans la table "+ tablename +"mais ne figure pas dans la table 'CodeEssence' (fichier administrateur) ",
            "table": tablename,
            "column": 'Essence',
            "row": species_list_temp.index[species_list_temp['Essence']==i].tolist(),
            "value": i,
          }
          error.append(err)
  return error

##### fonction contrôle des Cycles ####

##### fonction contrôle des essences rencontrées #####


##### fonction contrôle des stades écorce et de décomposition #####



##### fonction pour filtrer les tables selon une liste de dispositifs #####



##### fonction pour tester si résultats par placettes vides #####



##### fonction pour tester si coordonnées placettes vides #####



##### fonction de vérification du sf #####
# contrôle : 1/ présence des colonnes NumDisp et NumPlac
#            2/ valeurs vides dans les colonnes NumDisp et NumPlac
#            3/ coordonnées vides ?



##### fonction choix du shape des placettes #####



# -- construction table Arbres



