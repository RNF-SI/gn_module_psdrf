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
      console.log(data)
      return data;
    }

    public exportToExcelFile(jsonSheets, excelFileName) {
      
      let dataWsTemp = {};
      for(let i = 0; i< this.wsname.length; i++){
        const ws: XLSX.WorkSheet =XLSX.utils.json_to_sheet(jsonSheets[i][0],jsonSheets[i][1]);
        dataWsTemp[this.wsname[i]] = ws;
        
      }
      
      let wb: XLSX.WorkBook = {Sheets: dataWsTemp, SheetNames: this.wsname};
      const fileExtension = excelFileName.split('.').pop()
      const fileName = excelFileName.split('.')[0]
      let date = new Date()
      const dateString: string = date.getHours()+'-'+date.getMinutes()+'_'+date.getDate()+'-'+(date.getMonth()+1)+'-'+date.getUTCFullYear()
      XLSX.writeFile(wb, fileName+'_'+dateString+'.'+fileExtension);
    }

  }