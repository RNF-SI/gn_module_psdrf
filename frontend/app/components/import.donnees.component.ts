import {Component, ViewChild, ElementRef } from '@angular/core';
import {MatPaginator} from '@angular/material/paginator';
import {MatTableDataSource} from '@angular/material/table';
import { HttpClient } from '@angular/common/http';
import {ImportDonneesService} from './import.donnees-service';
import * as _ from 'lodash';
import {Placette} from '../models/placette.model';

@Component({
  selector: "rnf-psdrf-import-donnees",
  templateUrl: "import.donnees.component.html",
  styleUrls: ["import.donnees.component.scss"]
})
export class ImportDonneesComponent{
  placetteColumns:string[] = Object.keys( new Placette() );
  placetteDataSource: MatTableDataSource<any> = new MatTableDataSource();;
  excelFile: any = null;
  isLoadingResults: boolean = false;
  isCurrentVerification: boolean= false;

  @ViewChild('UploadFileInput') uploadFileInput: ElementRef;

  @ViewChild('scheduledOrdersPaginator') set paginator(pager:MatPaginator) {
    if (pager) this.placetteDataSource.paginator = pager;
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

    let importPlacettes: Placette[] = [];
    let data, header;
    const reader: FileReader = new FileReader();

    reader.onload = (e: any) => {
      const bstr: string = e.target.result;
      data = this.excelSrv.importFromFile(bstr);
      const header: string[] = this.placetteColumns;
      const importedData = data.slice(1, -1);
      importPlacettes = importedData.map(arr => {
        const obj = {};
        for (let i = 0; i < header.length; i++) {
          const k = header[i];
          obj[k] = arr[i];
        }
        return <Placette>obj;
      })
    };

    reader.readAsBinaryString(target.files[0]);

    reader.onloadend = (e) => {
      this.placetteDataSource = new MatTableDataSource(importPlacettes);
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
