import { Injectable } from '@angular/core';
import * as XLSX from 'xlsx';


@Injectable({
    providedIn: 'root'
  })
  export class ImportDonneesService {
  
    constructor() { }
  
    public importFromFile(bstr: string): XLSX.AOA2SheetOpts[] {
      /* read workbook */
      const wb: XLSX.WorkBook = XLSX.read(bstr, { type: 'binary' });
  
      let data:  XLSX.AOA2SheetOpts[]= [];
      for(let i = 0; i< wb.SheetNames.length; i++){

        /* grab first sheet */
        const wsname: string = wb.SheetNames[i];
        const ws: XLSX.WorkSheet = wb.Sheets[wsname];
    
        /* save data */
        data.push(<XLSX.AOA2SheetOpts>(XLSX.utils.sheet_to_json(ws, { header: 1 })));

      }

      return data;
    }

  }