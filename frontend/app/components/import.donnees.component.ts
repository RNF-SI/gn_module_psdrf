import {Component, ViewChild, ElementRef } from '@angular/core';
import {MatPaginator} from '@angular/material/paginator';
import {MatTableDataSource} from '@angular/material/table';
import { HttpClient } from '@angular/common/http';
import {ImportDonneesService} from './import.donnees-service';
import * as _ from 'lodash';
import {Placette} from '../models/placette.model';
import {Arbre} from '../models/arbre.model';
import {Rege} from '../models/rege.model';
import {Transect} from '../models/transect.model';
import {BMSsup30} from '../models/bmssup30.model';
import {Repere} from '../models/repere.model';
import {Cycle} from '../models/cycle.model';

@Component({
  selector: "rnf-psdrf-import-donnees",
  templateUrl: "import.donnees.component.html",
  styleUrls: ["import.donnees.component.scss"]
})
export class ImportDonneesComponent{
  tableColumnsArray:string[][] = [Object.keys(new Placette()), Object.keys(new Cycle()), Object.keys(new Arbre()), Object.keys(new Rege()), Object.keys(new Transect()), Object.keys(new BMSsup30()), Object.keys(new Repere())];
  tableDataSourceArray: MatTableDataSource<any> []=[new MatTableDataSource(), new MatTableDataSource(),new MatTableDataSource(),new MatTableDataSource(), new MatTableDataSource(), new MatTableDataSource(), new MatTableDataSource() ];
  excelFile: any = null;
  isLoadingResults: boolean = false;
  isCurrentVerification: boolean= false;

  @ViewChild('UploadFileInput') uploadFileInput: ElementRef;

  @ViewChild('placettePaginator') set paginator1(pager:MatPaginator) {
    if (pager) this.tableDataSourceArray[0].paginator = pager;
  }

  @ViewChild('cyclePaginator') set paginator2(pager:MatPaginator) {
    if (pager) this.tableDataSourceArray[1].paginator = pager;
  }

  @ViewChild('arbrePaginator') set paginator3(pager:MatPaginator) {
    if (pager) this.tableDataSourceArray[2].paginator = pager;
  }

  @ViewChild('regePaginator') set paginator4(pager:MatPaginator) {
    if (pager) this.tableDataSourceArray[3].paginator = pager;
  }

  @ViewChild('transectPaginator') set paginator5(pager:MatPaginator) {
    if (pager) this.tableDataSourceArray[4].paginator = pager;
  }

  @ViewChild('bmssup30Paginator') set paginator6(pager:MatPaginator) {
    if (pager) this.tableDataSourceArray[5].paginator = pager;
  }

  @ViewChild('reperePaginator') set paginator7(pager:MatPaginator) {
    if (pager) this.tableDataSourceArray[6].paginator = pager;
  }

  constructor(
    private http: HttpClient,
    private excelSrv: ImportDonneesService,
  ) { 
  }

  onFileDropped(event: DragEvent) {
    let af = ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel']
    let files= event.dataTransfer.files;
    if (files.length !== 1) throw new Error('Cannot use multiple files');
    const file = files[0];
    if (!_.includes(af, file.type)) {
      alert('Only EXCEL Docs Allowed!');
    } else {     
      this.excelFile = file;
      const target: DataTransfer = event.dataTransfer;
      this.onFileLoad(target);   
    }
  }

  onFileSelect(event) {
    const target: DataTransfer = <DataTransfer>(event.target);
    if (target.files.length !== 1) throw new Error('Cannot use multiple files');
    this.excelFile = target.files[0];
    this.onFileLoad(target);
  }

  onFileLoad (target){
    this.isCurrentVerification = true;
    this.isLoadingResults = true;

    let importPlacettes : any[][]= [];
    let data, header;
    const reader: FileReader = new FileReader();

    reader.onload = (e: any) => {
      const bstr: string = e.target.result;
      data = this.excelSrv.importFromFile(bstr);

      for(let i=0; i<data.length; i++){

        const header: string[] = this.tableColumnsArray[i];
        const importedData = data[i].slice(1, -1);
        importPlacettes.push(importedData.map(arr => {
          const obj = {};
          for (let i = 0; i < header.length; i++) {
            const k = header[i];
            obj[k] = arr[i];
          }
          return obj;
        }))

      }

    };

    reader.readAsBinaryString(target.files[0]);

    reader.onloadend = (e) => {
      console.log(importPlacettes);
      for(let i =0; i<importPlacettes.length; i++){
        this.tableDataSourceArray[i] = new MatTableDataSource(importPlacettes[i]);
      }
      this.isLoadingResults = false;
    }
  }

  deleteFile(){
    this.isCurrentVerification = false;
    this.excelFile = null;
  }

    /**
   * format bytes
   * @param bytes (File size in bytes)
   * @param decimals (Decimals point)
   */
  formatBytes(bytes, decimals = 2) {
    if (bytes === 0) {
      return "0 Bytes";
    }
    const k = 1024;
    const dm = decimals <= 0 ? 0 : decimals;
    const sizes = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
  }
}
