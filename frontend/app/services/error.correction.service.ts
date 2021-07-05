import { Injectable } from "@angular/core";


@Injectable()
export class ErrorCorrectionService {

  selectionErrorObject={};

  constructor(
  ) {}

  numberErrorList: string[] = ['NumDisp', 'NumPlac', 'Cycle', 'Strate', 'PoidsPlacette', 'Pente',
   'Exposition', 'Date_Intervention', 'PrecisionGPS', 'Cheminement', 'Coeff', 'DiamLim', 'Année', 'NumArbre', 'Azimut', 'Dist',
    'Diam1', 'Diam2', 'Haut', 'SsPlac', 'Recouv', 'Class1', 'Class2', 'Class3','Id', 'Transect', 'Dist', 'Angle', 'Azimut',
   'DiamIni', 'DiamMed', 'DiamFin', 'Longueur'];

  selectionErrorList: string[] = ['Essence', 'Type', 'StadeD', 'StadeE','Ref_CodeEcolo',];

  booleanErrorList: string[] = ['Taillis', 'Limite', 'CorrectionPente', 'Contact', 'Chablis' ];

  stringErrorList: string[] = ['Ref_Habitat', 'Nature_Intervention', 'Gestion', 'Date', 'CodeEcolo'];

  getErrorType(colName: string){
    let errorType: string;
    if (this.numberErrorList.includes(colName)){
        errorType= "numberError";
    } else if (this.selectionErrorList.includes(colName)){
        errorType= "selectionError";
    }
    return errorType
  }

  setSelectionErrorObj(selectionErrorObject: any): void{
    this.selectionErrorObject= selectionErrorObject
  }

  getColListCorrection(psdrfCol: string): any{
    console.log(this.selectionErrorObject[psdrfCol])
    return this.selectionErrorObject[psdrfCol]
  }

}


      
  
      
      
      