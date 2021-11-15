import { Injectable } from '@angular/core';
import * as XLSX from 'xlsx';


@Injectable({
    providedIn: 'root'
  })
  export class ExcelImportService {
    wsname: string [];
    excelFileName: string; 

    constructor() { }
  
    public importFromExcelFile(bstr: string): XLSX.AOA2SheetOpts[] {
      /* read workbook */
      const wb: XLSX.WorkBook = XLSX.read(bstr, { type: 'binary' , cellDates: true, dateNF: 'dd/mm/yyyy;@'});
      this.wsname = wb.SheetNames;
      let data:  XLSX.AOA2SheetOpts[]= [];
      for(let i = 0; i< wb.SheetNames.length; i++){
        /* grab first sheet */
        const ws: XLSX.WorkSheet = wb.Sheets[wb.SheetNames[i]];  
        /* save data */
        data.push(<XLSX.AOA2SheetOpts>(XLSX.utils.sheet_to_json(ws, { header: 1, raw:false})));
      }
      return data;
    }

    public exportToExcelFile(jsonSheets, excelFileName, isDateNameWanted, sheetNames?) {
      let wsname;
      if(sheetNames){
        wsname = sheetNames
      } else {
        wsname = this.wsname
      }
      let dataWsTemp = {};
      for(let i = 0; i< wsname.length; i++){
        const ws: XLSX.WorkSheet =XLSX.utils.json_to_sheet(jsonSheets[i][0],jsonSheets[i][1]);
        dataWsTemp[wsname[i]] = ws;
        
      }
      
      let wb: XLSX.WorkBook = {Sheets: dataWsTemp, SheetNames: wsname};
      let finalFileName
      if(isDateNameWanted){
        finalFileName = this.excelNameWithDate(excelFileName)
      } else {
        finalFileName = excelFileName + ".xlsx"
      }
      XLSX.writeFile(wb, finalFileName);
    }

    public excelNameWithDate(entireExcelFileName){
      let nameWithDate;
      const fileExtension = entireExcelFileName.split('.').pop()
      const fileNameTemp = entireExcelFileName.split('.')[0]
      const fileName = fileNameTemp.split('_')[0]
      let date = new Date()
      const dateString: string = date.getHours()+'-'+date.getMinutes()+'_'+date.getDate()+'-'+(date.getMonth()+1)+'-'+date.getUTCFullYear()
      nameWithDate = fileName+'_'+dateString+'.'+fileExtension;
      return nameWithDate
    }

    public getColumnNames(){
      return { 
        "Placettes": [
          "NumDisp", "NumPlac", "Cycle", "Strate", "PoidsPlacette", "Pente", "CorrectionPente", 
          "Exposition", "Habitat", "Station", "Typologie", "Groupe", "Groupe1", 
          "Groupe2", "Ref_Habitat", "Precision_Habitat", "Ref_Station", 
          "Ref_Typologie", "Descriptif_Groupe", "Descriptif_Groupe1", 
          "Descriptif_Groupe2", "Date_Intervention", "Nature_Intervention", 
          "Gestion", "PrecisionGPS", "Cheminement"
        ], 
        "Cycles": [
          "NumDisp", "NumPlac", "Cycle", "Coeff", "Date", "DiamLim", "Année"
        ],
        "Arbres": [  
          "NumDisp", "NumPlac", "Cycle", "NumArbre", "Essence", "Azimut", "Dist", "Diam1", "Diam2", 
          "Type", "Haut", "StadeD", "StadeE", "Taillis", "Coupe", "Limite", "CodeEcolo", 
          "Ref_CodeEcolo", "Observation"
        ], 
        "Rege": [
          "NumDisp", "NumPlac", "SsPlac", 
          "Cycle", "Essence", "Recouv", "Class1", "Class2", 
          "Class3", " Taillis", "Abroutis", "Observation"
        ], 
        "Transect": [  
          "NumDisp", "NumPlac", "Id", "Cycle", "Transect", 
          "Essence", "Dist", "Diam", "Angle", "Contact", 
          "Chablis", "StadeD", "StadeE", "Observation"
        ], 
        "BMSsup30": [
          "NumDisp", "NumPlac", "Id", "NumArbre", 
          "Cycle", "Essence", "Azimut", "Dist", "DiamIni", 
          "DiamMed", "DiamFin", "Longueur", "Contact", 
          "Chablis", "StadeD", "StadeE", "Observation"
        ], 
        "Reperes": [
          "NumDisp", "NumPlac", "Azimut", 
          "Dist", "Diam", "Repere", "Observation"
        ]
      }
    }

  }