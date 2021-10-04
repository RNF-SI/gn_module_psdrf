import { Injectable } from "@angular/core";


@Injectable()
export class ErrorCorrectionService {

  //Object containing all the correction for columns of selectionErrorList
  selectionErrorObject={};

  constructor(
  ) {}

  numberErrorList: string[] = ['NumDisp', 'NumPlac', 'Cycle', 'Strate', 'PoidsPlacette', 'Pente',
   'Exposition', 'Date_Intervention', 'PrecisionGPS', 'Cheminement', 'Coeff', 'DiamLim', 'Année', 'NumArbre',
   'SsPlac', 'Recouv', 'Class1', 'Class2', 'Class3','Id', 'Transect', 'Angle', 'Azimut'];

  selectionErrorList: string[] = ['Essence', 'Type', 'StadeD', 'StadeE','Ref_CodeEcolo',];

  booleanErrorList: string[] = ['Taillis', 'Limite', 'CorrectionPente', 'Contact', 'Chablis' ];

  stringErrorList: string[] = ['Ref_Habitat', 'Nature_Intervention', 'Gestion', 'Date', 'CodeEcolo', 'Dist', 'Longueur', 'Diam1', 'Diam2', 'DiamIni', 'DiamMed', 'DiamFin', 'Haut'];

  /**
  *  Return type  of an error when a column name is given 
  * @param colName Column Name
  */
  getErrorType(colName: string){
    let errorType: string;
    if (this.numberErrorList.includes(colName)){
        errorType= "numberError";
    } else if (this.selectionErrorList.includes(colName)){
        errorType= "selectionError";
    }
    return errorType
  }

  /**
  *  Set the selectionErrorObject; Called when a new excel file is chosen
  */
  setSelectionErrorObj(selectionErrorObject: any): void{
    this.selectionErrorObject= selectionErrorObject
  }

  /**
  *  Return the possible corrections for a column name
  * @param colName Column Name
  */
  getColListCorrection(colName: string): any{
    return this.selectionErrorObject[colName]
  }

}


      
  
      
      
      