import {Component,ViewChildren, QueryList, ViewChild, ElementRef  } from '@angular/core';
import {MatPaginator} from '@angular/material/paginator';
import {MatTableDataSource} from '@angular/material/table';
import { HttpClient } from '@angular/common/http';
import * as _ from 'lodash';
import {ExcelImportService} from '../../services/excel.import.service';
import {PsdrfDataService} from '../../services/route.service';
import {ErrorHistoryService } from '../../services/error.history.service';
import {Placette} from '../../models/placette.model';
import {Arbre} from '../../models/arbre.model';
import {Rege} from '../../models/rege.model';
import {Transect} from '../../models/transect.model';
import {BMSsup30} from '../../models/bmssup30.model';
import {Repere} from '../../models/repere.model';
import {Cycle} from '../../models/cycle.model';
import {PsdrfError, PsdrfErrorCoordinates} from '../../models/psdrfObject.model';
import {StepperSelectionEvent} from '@angular/cdk/stepper';


@Component({
  selector: "rnf-psdrf-import-donnees",
  templateUrl: "import.donnees.component.html",
  styleUrls: ["import.donnees.component.scss"]
})
export class ImportDonneesComponent{

  psdrfArray : any[][]= []; //Tableau qui contient au départ les données du fichier excel. Il est actualisé au fur et à mesure que les erreurs sont corrigées 
  tableColumnsArray:string[][] = [Object.keys(new Placette()), Object.keys(new Cycle()), Object.keys(new Arbre()), Object.keys(new Rege()), 
    Object.keys(new Transect()), Object.keys(new BMSsup30()), Object.keys(new Repere())];//Tableau contenant les titres des colonnes pour chaque table
  tableDataSourceArray: MatTableDataSource<any> []= [];//Tableau des Datasource de chaque onglet
  
  
  indexLabelMatTabGroup: string[]= ["Placette", "Cycle", "Arbre", "Rege", "Transect", "BMSsup30", "Repere"];//Tableau des titres d'onglet
  excelFile: any = null;
  isLoadingResults: boolean = false;
  isLoadingErrors: boolean = false;
  isCurrentVerification: boolean= false;
  indexMatTabGroup: number=0; //Index de l'onglet sélectionné 
  errorsPsdrfList: {'errorList': PsdrfError[], 'correctionList': any}[] = []; //Tableau des erreurs retournées par la requête psdrf_data_verification
  errorElementArr: PsdrfErrorCoordinates[] = []; //Tableau des erreurs
  modifiedElementArr:PsdrfErrorCoordinates[] = []; //Tableau des erreurs qui ont été modifiées
  selectedErrorElementArr:PsdrfErrorCoordinates; //Erreur qui est actuellement sélectionnée
  totallyModifiedMainStepperArr: number[]=[]; //Tableau des indexs des mainstep qui ont été complètement modifiés

  @ViewChildren(MatPaginator) paginator = new QueryList<MatPaginator>(); //liste des 8 paginators

  constructor(
    private http: HttpClient,
    private excelSrv: ExcelImportService,
    private dataSrv: PsdrfDataService,
    private historyService:ErrorHistoryService
  ) { 
  }

  /*
    Fonction déclenchée lors du drag&drop d'un fichier
  */
  onFileDropped(event: DragEvent): void {
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

  /*
    Fonction déclenchée lors de la sélection d'un fichier lorsq'uon appui sur le bouton "choisir un fichier"
  */
  onFileSelect(event): void {
    const target: DataTransfer = <DataTransfer>(event.target);
    if (target.files.length !== 1) throw new Error('Cannot use multiple files');
    this.excelFile = target.files[0];
    this.onFileLoad(target);
  }

  /*
    Fonction de chargement du fichier PSDRF excel 
  */
  onFileLoad (target: DataTransfer): void{
    this.isCurrentVerification = true;
    this.isLoadingResults = true;
    this.isLoadingErrors = true;
    let excelData;
    const reader: FileReader = new FileReader();

    //Chargement des données du fichier excel dans la variable psdrfArray
    reader.onload = (e: any) => {
      const bstr: string = e.target.result;
      excelData = this.excelSrv.importFromExcelFile(bstr);
      for(let i=0; i<excelData.length; i++){
        const header: string[] = this.tableColumnsArray[i];
        const importedData = excelData[i].slice(1, -1);
        this.psdrfArray.push(importedData.map(arr => {
          const obj = {};
          for (let j = 0; j < header.length; j++) {
            const k = header[j];
            obj[k] = arr[j];
          }
          return obj;
        }))
      }
    };

    reader.readAsBinaryString(target.files[0]);

    //Lancement de la requête psdrf_data_verification avec les données Excel chargée
    reader.onloadend = (e) => {
      this.dataSrv.psdrf_data_verification(JSON.stringify(this.psdrfArray))
        .subscribe(
          error => {
            this.isLoadingResults = false;
            this.isLoadingErrors = false;
            
            //Création du binding entre les MatTable datasources et les données affichée dans la tableau
            //Remarque: Tout changement dans psdrfArray s'applique automatiquement au tableau
            for(let i =0; i<this.psdrfArray.length; i++){
              this.tableDataSourceArray.push( new MatTableDataSource(this.psdrfArray[i]));
              this.tableDataSourceArray[i].paginator = this.paginator.toArray()[i];
            }
            
            let errorsPsdrfListTemp = JSON.parse(error);
            let errorListTemp;
            let correctionListTemp;
            errorsPsdrfListTemp.forEach(mainError => {
              correctionListTemp = mainError.correctionList;
              errorListTemp = [];
              mainError.errorList.forEach(error => {
                errorListTemp.push(new PsdrfError(error.message, error.table, error.column, error.row, error.value))
              })
              this.errorsPsdrfList.push({'errorList': errorListTemp, 'correctionList': correctionListTemp});
            })

            //Remplissage de errorElementArr avec toutes les erreurs renvoyées
            this.errorsPsdrfList.forEach(mainError => {
              mainError.errorList.forEach(error => {
                error.row.forEach( idx => {
                  this.errorElementArr.push(new PsdrfErrorCoordinates(error.table, error.column, idx));
                })
              })
            });
            
            //Affichage de la toute première erreur de errorsPsdrfList dans le MatTab
            this.displayErrorOnMatTab({table: this.errorsPsdrfList[0].errorList[0].table, column: this.errorsPsdrfList[0].errorList[0].column, row: this.errorsPsdrfList[0].errorList[0].row[0]});
            }
        );
    }
  }

  /*
    Fonction retournant le paginateur d'une table en fonction du nom de la table
  */
  getPaginatorFromTableName(tableName: string): MatPaginator{
    return this.tableDataSourceArray[this.indexLabelMatTabGroup.indexOf(tableName)].paginator;
  }

  /*
    Fonction permettant de retrouver l'index d'un élément en fonction du paginateur de la table
  */
  getRowIndexFromPaginatorProperties(table: string, column: string, i: number): number{
    let tablePaginator = this.getPaginatorFromTableName(table);
    return i + (tablePaginator.pageIndex * tablePaginator.pageSize);
  }

  /*
    Fonction permettant de tester si les coordonnées d'un élément correspondent à une erreur ou non 
  */
  checkErrorCell(table: string, column: string, i: number): boolean{
    let row = this.getRowIndexFromPaginatorProperties(table, column, i);
    return this.errorElementArr.some((obj) => (obj.table== table && obj.column == column && obj.row == row));
  }

  /*
    Fonction permettant de tester si les coordonnées d'un élément correspondent à une erreur modifiée
  */
  checkModifiedErrorCell(table: string, column: string, i: number): boolean{
    let row = this.getRowIndexFromPaginatorProperties(table, column, i);
    return this.modifiedElementArr.some((obj) => (obj.table== table && obj.column == column && obj.row == row));
  }

  /*
    Fonction permettant de voir si une case correspond à celle de l'erreur sélectionnée ou non 
  */
  checkSelectedErrorCell(table: string, column: string, i: number): boolean{
    let row = this.getRowIndexFromPaginatorProperties(table, column, i);
    return this.selectedErrorElementArr.table == table && this.selectedErrorElementArr.column == column && this.selectedErrorElementArr.row == row;
  }

  /*
    Fonction permettant d'afficher le bon endroit du tableau lorsque l'évènement reçu correspond à un substep qui a été cliqué
  */
  displayOnSubStepClick(stepperSelectionObj: {mainStepIndex: number, subStepIndex: number}): void{
    if(this.historyService.isMainStepHasAlreadyBeenClicked(stepperSelectionObj.mainStepIndex) && this.historyService.isSubStepHasAlreadyBeenClicked(stepperSelectionObj.mainStepIndex, stepperSelectionObj.subStepIndex)){
      this.displayErrorOnMatTab(this.historyService.getLastSelectedCoordinates(stepperSelectionObj.mainStepIndex));
    } else {
      let error = this.errorsPsdrfList[stepperSelectionObj.mainStepIndex].errorList[stepperSelectionObj.subStepIndex];
      let rowObj = {table: error.table, column: error.column, row: error.row[0]}
      this.displayErrorOnMatTab(rowObj);
    }
  }

  /*
    Fonction permettant d'afficher le bon endroit du tableau lorsque l'évènement reçu correspond à un mainstep qui a été cliqué
  */
  displayOnMainStepClick(stepperSelectionObj: StepperSelectionEvent): void{
    if(this.historyService.isMainStepHasAlreadyBeenClicked(stepperSelectionObj.selectedIndex)){
      this.displayErrorOnMatTab(this.historyService.getLastSelectedCoordinates(stepperSelectionObj.selectedIndex));
    } else {
      let error = this.errorsPsdrfList[stepperSelectionObj.selectedIndex].errorList[0];
      this.displayErrorOnMatTab(new PsdrfErrorCoordinates(error.table, error.column, error.row[0]));
    }
  }

  /*
    Fonction permettant d'afficher sur le tableau une erreur à l'aide 
    des ses coordonnées
  */
  displayErrorOnMatTab(errorCoordinates: PsdrfErrorCoordinates): void{
    this.selectedErrorElementArr = errorCoordinates;
    this.indexMatTabGroup=this.indexLabelMatTabGroup.indexOf(errorCoordinates.table);
    let tablePaginator = this.tableDataSourceArray[this.indexMatTabGroup].paginator;
    let pageNumber = Math.trunc(errorCoordinates.row/tablePaginator.pageSize);

    tablePaginator.pageIndex = pageNumber, // number of the page you want to jump.
    tablePaginator.page.next({      
         pageIndex: pageNumber,
         pageSize: tablePaginator.pageSize,
         length: tablePaginator.length
       });
  }

  /*
    Fonction permettant de modifier une valeur dans le tableau. Met aussi à jour la liste des éléments modifiés
  */
  modifyErrorValue(modificationErrorObj: {errorCoordinates: PsdrfErrorCoordinates[], newErrorValue: string}): void{
    let indexTable;
    modificationErrorObj.errorCoordinates.forEach(errorCoor => {
      indexTable = this.indexLabelMatTabGroup.indexOf(errorCoor.table);
      this.modifiedElementArr.push({table: errorCoor.table, column:errorCoor.column, row:errorCoor.row});
      this.psdrfArray[indexTable][errorCoor.row][errorCoor.column] = modificationErrorObj.newErrorValue;
    });
  }

  /*
    Modifie la liste des main stepper qui ont été modifiés
  */
  modifyMainStepperAppearance(mainStepIndex: number){
    this.totallyModifiedMainStepperArr.push(mainStepIndex);
  }

  /*
    Fonction permettant de supprimer le fichier excel chargé
  */
  deleteFile(): void{
    this.isCurrentVerification = false;
    this.excelFile = null;
  }

  /**
  * Fonction permetant d'obtenir le nb de bytes
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
