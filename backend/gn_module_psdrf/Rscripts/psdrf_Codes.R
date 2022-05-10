#' Importation des données administrateur de la base PSDRF contenues dans le classeurs psdrfListes.xlsx
#' @description Création d'une archive .Rdata a partir du classeur Excel PsdrfListes.xlsx.
#' 
#' @author Bruciamacchie Max, Demets Valentin
#' 
#' @param repPSDRF = répertoire de travail
#' @param file = classeur psdrfListes
#' 
#' @import openxlsx
#' @import tcltk
#' 
#' @export

psdrf_Codes <- function(repPSDRF, file) {
  ##### 1/ Initialisation #####
  # -- Choix du répertoire de travail
  setwd(repPSDRF)
  
  # -- TODO : rajouter une sécurité pour contrôler que file est bien renseigné ?
  
  ##### / \ #####
  
  
  ##### 2/ Import des données #####
  # -- tables administrateurs
  Dispositifs <- 
    read.xlsx(file, sheet = "Dispositifs", detectDates = T) %>%
    select(
      NumDisp, Nom, 
      Nom1, Statut1, Code1, DateCreation1, Surface1, 
      Nom2, Statut2, Code2, DateCreation2, Surface2
      ) %>% 
    mutate(
      DateCreation1 = parse_date_time(
        DateCreation1, 
        orders = c('mdy', 'dmy', 'ymd')
      ),
        DateCreation2 = parse_date_time(
          DateCreation2, 
          orders = c('mdy', 'dmy', 'ymd')
        )
    )
    
  Communes <- 
    read.xlsx(file, sheet = "Communes")%>%
    select(NumDisp, Nom, CPT, Ville, Dep)
  
  CyclesCodes <- 
    read.xlsx(file, sheet = "Cycles")%>%
    select(NumDisp, Nom, Cycle, Monitor, DateIni, DateFin)
  
  Referents <-
    read.xlsx(file, sheet = "Referents")%>%
    select(
      NumDisp, Nom, Cycle, 
      NumRef1, NomRef1, 
      NumRef2, NomRef2, 
      NumRef3, NomRef3, 
      NumRef4, NomRef4, 
      NumRef5, NomRef5
    )
  
  Tarifs <- 
    read.xlsx(file, sheet = "Tarifs")%>%
    select(NumDisp, Essence, TypeTarif, NumTarif, TypeTarifIFN, NumTarifIFN)
  
  Tiers <- 
    read.xlsx(file, sheet = "Tiers")%>%
    select(
      Id, Nom, CPT, Ville, Adresse1, Adresse2, Pays, 
      "E-Mail", Tel, Port, Organisme, Role, Commentaire
      )
  
  # -- tables de codification
  CodeEssence <- 
    read.xlsx(file, sheet = "CodeEssence")%>%
    select(Id, Nom, Essence, Latin, EssReg, Couleur)
  
  EssReg <- 
    read.xlsx(file, sheet = "EssReg")%>%
    select(NumDisp, Essence, EssRegPar, Couleur)
  CodeDurete <- 
    read.xlsx(file, sheet = "CodeDurete") %>% 
    select(Id, Code, Descriptif, Observation)
  
  CodeEcologie <- 
    read.xlsx(file, sheet = "CodeEcologie") %>%
    select(Codification, Code, Descriptif, Couleur)
  
  CodeEcorce <- 
    read.xlsx(file, sheet = "CodeEcorce") %>%
    select(Id, Code, Descriptif, Observation)
  
  CodeTypoArbres <- 
    read.xlsx(file, sheet = "CodeTypoArbres")%>%
    select(Id, Code, Descriptif, Observation)
  
  Cat <-
    read.xlsx(file, sheet = "Cat")%>%
    select(NumDisp, PB, BM, GB, TGB)
  
  # -- table de suivi
  Suivi <- 
    read.xlsx(file, sheet = "Suivi")%>%
    select(
      Nom, NumDisp, Cycle, Strate, PoidsPlacette, 
      Annee, Coeff, DiamLim, # paramétrage échantillonnage
      CorrectionPente, Gestion, NbPlac, NbPlacTot, Ref_CodeEcolo, Surface1, SIG, 
      Id_Formation, Hôte_Formation, Année_Formation, Formation_Dendro, # formation
      Data_State, # suivi
      Commentaires
    )
  
  ##### / \ #####
  
  ##### 3/ Sauvegarde #####
  # -- dossier
  dir.create("tables", showWarnings = F)
  save(
    Tiers, CodeEcorce, CodeEcologie, CodeEssence, CodeDurete, Dispositifs, 
    Tarifs, CodeTypoArbres, Communes, 
    CyclesCodes, Referents, EssReg, Cat, Suivi,  
    file = "tables/psdrfCodes.Rdata"
  )
  
  # -- message fin
  Msg <- tk_messageBox(
    type = "ok",
    message = "Importation du fichier psdrfListes termin\u00E9e",
    icon = "info"
  )
  ##### / \ #####
}
