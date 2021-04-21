import json
import pandas as pd
import numpy as np
import datetime

from pathlib import Path

from varname import nameof

# Fonction principale de vérification des données du PSDRF
def data_verification(data):
  # TODO: Expliquer à quoi sert cette variable
  Test = 0

  # TODO: Expliquer à quoi sert ce tableau une fois le fichier R traduit
  error = []

  tableDict = {}
  # Initialisation des données du dispositif testée dans des dataframes Pandas
  tableDict["Placettes"]=pd.json_normalize(data[0]) 
  tableDict["Cycles"] = pd.json_normalize(data[1])
  tableDict["Arbres"]=pd.json_normalize(data[2])
  tableDict["Reges"] = pd.json_normalize(data[3])
  tableDict["Transect"]=pd.json_normalize(data[4])
  tableDict["BMSsup30"] = pd.json_normalize(data[5])
  tableDict["Reperes"]=pd.json_normalize(data[6])

  # Trouver le chemin d'accès au dossier data, qui contient les tables nécessaires aux tests
  ROOT_DIR_PSDRF = Path(__file__).absolute().parent.parent
  DATA_DIR_PSDRF = ROOT_DIR_PSDRF / "data"

  #chargement des tables nécessaires aux tests 
  tableDict["CodeEssence"] = pd.read_pickle(DATA_DIR_PSDRF / 'CodeEssence')
  tableDict["CyclesCodes"] = pd.read_pickle(DATA_DIR_PSDRF / 'CyclesCodes')
  tableDict["Dispositifs"] = pd.read_pickle(DATA_DIR_PSDRF / 'Dispositifs')
  tableDict["CodeDurete"] = pd.read_pickle(DATA_DIR_PSDRF / 'CodeDurete')
  tableDict["EssReg"] = pd.read_pickle(DATA_DIR_PSDRF / 'EssReg')
  tableDict["Communes"] = pd.read_pickle(DATA_DIR_PSDRF / 'Communes')
  tableDict["Referents"] = pd.read_pickle(DATA_DIR_PSDRF / 'Referents')
  tableDict["Tarifs"] = pd.read_pickle(DATA_DIR_PSDRF / 'Tarifs')

  An = datetime.datetime.now().year
  #Creation du tableau de vérification qui sera retourné:
  # - chaque élément du tableau correspond à une erreur différente
  # - errorList correspond à la liste des éléments qui ont cette erreur
  # - correctionList correspond aux solutions possible pour résoudre cette erreur
  verificationList = []

  disp_num = 1
  last_cycle = tableDict["Cycles"][tableDict["Cycles"]["NumDisp"] == disp_num]["Cycle"].max()
  tables =["Placettes", "Cycles", "Arbres", "Reges", 
         "Transect", "BMSsup30", "Reperes", 
         "CyclesCodes", "Dispositifs", 
         "EssReg", "Communes", "Referents", "Tarifs"] 

  # tableDict= filter_by_disp(tables, disp_num, last_cycle, tableDict, disp_num)
  
  # soundness_code = "de décomposition"
  # check_code_Error_List = check_code(tableDict["CodeDurete"], tableDict["Arbres"], soundness_code, "Arbres")
  # if len(check_code_Error_List) >0:
  #   verificationList.append({'errorName': 'Contrôle Stade dans Arbres', 'errorType': 'blockingError', 'errorList': check_code_Error_List, 'correctionList': tableDict["CodeDurete"]['Code'].tolist()})


  # check_cycle_Error_List = check_cycle(tableDict["BMSsup30"], Test, tableDict["CyclesCodes"], "BMSsup30", An, tableDict["Dispositifs"])
  # if len(check_cycle_Error_List) >0:
  #   verificationList.append({'errorName': 'Contrôle cycles dans BMSsup30', 'errorType': 'nonBlockingError', 'errorList': check_cycle_Error_List})

  #Appel des fonctions de test
  check_species_Error_List = check_species(tableDict["BMSsup30"], tableDict["CodeEssence"], Test, "BMSsup30")
  if len(check_species_Error_List) >0:
    verificationList.append({'errorName': 'Essence dans BMSsup30', 'errorList': check_species_Error_List, 'correctionList': tableDict["CodeEssence"]['Essence'].tolist()})
  # check_species_Error_List = check_species(BMSsup30, CodeEssence, Test, "BMSsup30")
  # if len(check_species_Error_List) >0:
  #   verificationList.append({'errorName': 'Essence dans BMSsup30', 'errorList': check_species_Error_List, 'correctionList': CodeEssence['Essence'].tolist()})


  soundness_code = "de décomposition"
  check_code_Error_List = check_code(tableDict["CodeDurete"], tableDict["Arbres"], soundness_code, "Arbres")
  if len(check_code_Error_List) >0:
    verificationList.append({'errorName': 'Contrôle Stade dans Arbres', 'errorList': check_code_Error_List, 'correctionList': tableDict["CodeDurete"]['Code'].tolist()})

  verificationObj = json.dumps(verificationList, cls=NumpyEncoder)


  return verificationObj

# Fonction d'encodage en Json
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

##### fonction pour filtrer les tables selon une liste de dispositifs #####
def filter_by_disp(tables, disp_list, cycle, tableDict, disp_num) :
  num_list = disp_num
  for tmp in tables:
      tmp_NAME = tmp
      tmp = tableDict[tmp]
      
      if isinstance(tmp, pd.DataFrame):
          if tmp.shape[0] > 0:
              tmp = tmp[tmp['NumDisp']==num_list]
              tableDict[tmp_NAME] = tmp
              
              # -- filtre selon le cycle
              if "Cycle" in tmp.columns:
                  tmp = tmp[tmp['Cycle'] == cycle]
                  tableDict[tmp_NAME] = tmp
                  
              if cycle == 1 : 
                  tmp = tmp.assign(AcctGper = None, 
                                  AcctVper = None, 
                                  AcctD = None)
                  tableDict[tmp_NAME] = tmp
  return tableDict  

# fonction contrôle des essences rencontrées
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
            "message": "L'essence "+ i + " figure dans la table "+ tablename +"mais ne figure pas dans la table 'CodeEssence' (fichier administrateur) ",
            "table": tablename,
            "column": 'Essence',
            "row": species_list_temp.index[species_list_temp['Essence']==i].tolist(),
            "value": i,
          }
          error.append(err)
  return error

##### fonction contrôle des Cycles ####
def check_cycle(table_to_test, status, cycle_admin, tablename, An, Dispositifs): 
    if table_to_test.shape[1] > 0 :
      error = []
      temp = table_to_test.assign(Mark = 1) # add marker

      cycle_table =  pd.merge(cycle_admin, temp[["NumDisp", "Cycle", "Mark"]], how='outer').drop_duplicates()
      
      # test si éléments de la table sont absents de la table Cycle (avec DateIni est bien inférieur à l'année en cours 'An')
      pos = np.array(np.where((cycle_table['Mark'].isna()) & (cycle_table['DateIni'] < An))).tolist()[0]

      if len(pos)>0:
        if status >= 2:
            status = status
        else:
            status = 2
            
        # liste des tuples NumDisp + Cycle qui ne figurent pas dans la table testée
        vecttemp = cycle_table.loc[pos,["NumDisp", "Cycle"]].drop_duplicates()
        
        for index, row in vecttemp.iterrows() :
          nomDisp =  Dispositifs[Dispositifs["NumDisp"]==row["NumDisp"]]["Nom"].item()
          err = {
            "message": "La table Cycles du fichier administrateur contient le cycle "+ str(row['Cycle']) + " pour le dispositif " + str(row['NumDisp'])+ "-"+ nomDisp + ", mais ce dernier n'apparaît pas dans la table" + tablename +".",
            "table": tablename,
            "column": 'Cycle',
          }
          error.append(err)

    else:
        status = 1
        label = "La feuille"+ tablename +" ne contient pas de données."
    
    return error


##### fonction contrôle des stades écorce et de décomposition #####
def check_code(code_admin, table_to_test, code_to_check, tableName):
  error = []

  if code_to_check == "écorce":
      stade = "StadeE"
  else:
      stade= "StadeD"

  column =["NumDisp", "NumPlac", "NumArbre", "Id", "Cycle", stade]

  # détection des codes non conformes
  df1 = table_to_test[~table_to_test['StadeD'].isin(np.append(np.nan, code_admin['Code'].values)) ]

  df = df1.loc[:,df1.columns.isin(["NumDisp", "NumPlac", "NumArbre", "Id", "Cycle", stade])]


  if df.shape[0]>0:
      for i in df['StadeD'].drop_duplicates():
          err= {
            "message": "Stade(s) "+code_to_check+" "+ str(int(i)) +" non conforme(s) dans la table" +tableName,
            "table": tableName,
            "column": 'StadeD',
            "row": df.index[df['StadeD']==i].tolist(),
            "value": i,
          }
          error.append(err)


  return(error)


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



