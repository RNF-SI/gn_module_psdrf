import {
  Component,
  ViewChildren,
  QueryList,
  ViewChild,
  ElementRef,
  ChangeDetectorRef,
  OnInit,
} from "@angular/core";
import { MatPaginator } from "@angular/material/paginator";
import { MatTableDataSource } from "@angular/material/table";
import { HttpClient } from "@angular/common/http";
import { Router } from "@angular/router";
import * as _ from "lodash";
import { ExcelImportService } from "../../services/excel.import.service";
import { PsdrfDataService } from "../../services/route.service";
import { ErrorHistoryService } from "../../services/error.history.service";
import { ErrorCorrectionService } from "../../services/error.correction.service";
import { SharedService } from "../../services/shared.service";
import {
  PsdrfError,
  PsdrfErrorCoordinates,
} from "../../models/psdrfObject.model";
import { StepperSelectionEvent } from "@angular/cdk/stepper";
import { MatStepper } from "@angular/material/stepper";
import { AuthService } from '@geonature/components/auth/auth.service';
import { CommonService } from '@geonature/GN2CommonModule/service/common.service';
import { ToastrService } from 'ngx-toastr';




@Component({
  selector: "rnf-psdrf-import-donnees",
  templateUrl: "import.donnees.component.html",
  styleUrls: ["import.donnees.component.scss"],
})
export class ImportDonneesComponent  implements OnInit{
  userDisps: number[] = [];
  currentUser: any; 
  isPSDRFadmin: boolean;

  //Tableau qui contient au départ les données du fichier excel. Il est actualisé au fur et à mesure que les erreurs sont corrigées
  psdrfArray: any[][] = [];

  tableColumnsArray: string[][] = [];
  tableDataSourceArray: MatTableDataSource<any>[] = []; //Tableau des Datasource de chaque onglet

  indexLabelMatTabGroup: string[] = [
    "Placettes",
    "Cycles",
    "Arbres",
    "Regeneration",
    "Transect",
    "BMSsup30",
    "Reperes",
  ]; //Tableau des titres d'onglet
  excelFile: any = null;
  excelFileName: any;

  shapeFile: any = null;

  isDataCharging: boolean = false; // Vrai lorsque le fichier Excel est entrain de charger
  isExcelLoaded: boolean = false; // Faux lorsqu'on n'a pas encore choisi de fichier
  isVerificationObjLoaded: boolean = false;
  isShapeCharged: boolean = false;
  isFileContainingFatalError: boolean = false; 

  indexMatTabGroup: number = 0; //Index de l'onglet sélectionné
  errorsPsdrfList: {
    errorList: PsdrfError[];
    errorType: string;
    isFatalError: boolean;
  }[] = []; //Tableau des erreurs retournées par la requête psdrf_data_verification
  mainStepNameArr: string[] = []; // Tableau des titres des main step(affichés dans les main steps)
  mainStepTextArr: string[] = []; //Tableau des textes d'erreurs pour chaque mainstep
  errorElementArr: PsdrfErrorCoordinates[] = []; //Tableau de toutes les erreurs
  modifiedElementArr: PsdrfErrorCoordinates[] = []; //Tableau des erreurs qui ont été modifiées
  selectedErrorElementArr: PsdrfErrorCoordinates; //Erreur qui est actuellement sélectionnée
  deletedElementArr: PsdrfErrorCoordinates[] = [];//Tableau des erreurs supprimées
  totallyModifiedMainStepperArr: number[] = []; //Tableau des indexs des mainstep qui ont été complètement modifiés
  totalErrorNumber: number = 0; //Correspond au nombre de rowButton total. Sert à la barre de progression
  progressBarValue: number = 0;
  extensionIcon: string = "unfold_more";

  @ViewChildren(MatPaginator) paginator = new QueryList<MatPaginator>(); //liste des 8 paginators

  // Main Paginator
  // Max number of steps to show at a time in view, Change this to fit your need
  MAX_STEP = 5;
  // Total steps included in mat-stepper in template, Change this to fit your need
  totalSteps = 0;
  // Current page from paginator
  page = 0;
  // Current active step in mat-stepper
  step = 0;
  // Min index of step to show in view
  minStepAllowed = 0;
  // Max index of step to show in view
  maxStepAllowed = this.MAX_STEP - 1;
  // Number of total possible pages
  totalPages = 0;
  //Visibilité des labels du mainStep
  isLabelVisible: boolean = true;
  //Boolean de l'intégration des données à la BD (vrai si requête en cours)
  integrationLoading = false; 

  @ViewChild("mainStepper") private mainStepper: MatStepper;

  @ViewChild("stepperPart") stepperPart: ElementRef;

  constructor(
    private http: HttpClient,
    private excelSrv: ExcelImportService,
    private dataSrv: PsdrfDataService,
    private correctionService: ErrorCorrectionService,
    private historyService: ErrorHistoryService,
    private _router: Router,
    private changeDetector: ChangeDetectorRef,
    private elementRef: ElementRef,
    private _authService: AuthService,
    private _commonService: CommonService,
    private sharedSrv: SharedService,
    private _toasterService: ToastrService
  ) {}

  ngOnInit(){
    this.currentUser = this._authService.getCurrentUser()
    this.getUserDisps(this.currentUser.id_role);
    if (this.sharedSrv.getPsdrfAdmin() == null) {
      this.sharedSrv.setPsdrfAdmin()
        .subscribe(
          isPSDRFadmin  => {
            this.isPSDRFadmin = isPSDRFadmin;
          },
          error => {
            this._toasterService.error(error.message, "Vérification des droits PSDRF");
          }
          )
    } else {
      this.isPSDRFadmin = this.sharedSrv.getPsdrfAdmin();
    }
  }

  getUserDisps(userId): void{
    this.dataSrv
      .getUserDisps(userId)
      .subscribe(
        dispsList => {
          this.userDisps = dispsList;
        },
        error =>{
          this._toasterService.error(error.message, "Recherche des dispositif de l'utilisateur courant");
        }
      )
  }

  /**
   * Triggered function on D&D event
   * @param event Drag and Drop event
   */
  onFileDropped(event: DragEvent): void {
    let af = [
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      "application/vnd.ms-excel",
    ];
    let files = event.dataTransfer.files;
    if (files.length !== 1) throw new Error("Cannot use multiple files");
    const file = files[0];
    if (!_.includes(af, file.type)) {
      alert("Only EXCEL Docs Allowed!");
    } else {
      this.excelFile = file;
      const target: DataTransfer = event.dataTransfer;
      this.onFileLoad(target);
    }
  }

  /**
   *  Triggered function on file selection (a file is chosen)
   * @param event Selection File Event
   */
  onFileSelect(event): void {
    const target: DataTransfer = <DataTransfer>event.target;
    if (target.files.length !== 1) throw new Error("Cannot use multiple files");
    this.excelFile = target.files[0];
    this.onFileLoad(target);
  }

  /**
   *  Loading function of the PSDRF excel file:
   * - Excel file data loaded in psrfArray
   * - psdrf_data_verification is lauched to analyse the excel data
   * @param target DataTransfertObject
   */
  onFileLoad(target: DataTransfer): void {
    let excelData;
    const reader: FileReader = new FileReader();
    this.excelFileName = target.files[0].name;
    
    let numDisp = this.excelFileName.split("-")[0];
    if (this.userDisps.includes(parseInt(numDisp)) || this.isPSDRFadmin){
      this.isDataCharging = true;


      //Chargement des données du fichier excel dans la variable psdrfArray
      reader.onload = (e: any) => {
        const bstr: string = e.target.result;
        excelData = this.excelSrv.importFromExcelFile(bstr);
        for (let i = 0; i < excelData.length; i++) {
          // const header: string[] = this.tableColumnsArray[i];
          let columnNames = excelData[i].slice(0, 1)[0];
          this.tableColumnsArray[i] = columnNames;
          const header: string[] = columnNames;
          const importedData = excelData[i].slice(1);
          this.psdrfArray.push(
            importedData.map((arr) => {
              const obj = {};
              for (let j = 0; j < header.length; j++) {
                const k = header[j];
                obj[k] = arr[j];
              }
              return obj;
            })
          );
        }

        //Création du binding entre les MatTable datasources et les données affichée dans la tableau
        //Remarque: Tout changement dans psdrfArray s'applique automatiquement au tableau
        for (let i = 0; i < this.psdrfArray.length; i++) {
          this.tableDataSourceArray.push(
            new MatTableDataSource(this.psdrfArray[i])
          );
          this.tableDataSourceArray[i].paginator = this.paginator.toArray()[i];
        }

        this.isExcelLoaded = true;
      };
      reader.readAsBinaryString(target.files[0]);
      //Lancement de la requête psdrf_data_verification avec les données Excel chargée
      reader.onloadend = (e) => {
        this.dataSrv
          .psdrf_data_verification(
            JSON.stringify(this.psdrfArray, (k, v) =>
              v === undefined ? null : v
            )
          )
          .subscribe(
            verificationJson => {
              let verificationObj = JSON.parse(verificationJson);

              //Récupération de toutes les corrections possibles pour les champs prédéfinis objet de correction 
              this.correctionService.setSelectionErrorObj(
                verificationObj["correctionList"]
              );

              let errorsPsdrfListTemp = verificationObj["verificationObj"];
              this.mainStepNameArr = [];
              this.totalErrorNumber = 0;
              
              this.jsonObjectToPsdrfObject(errorsPsdrfListTemp);
              this.totalSteps = errorsPsdrfListTemp.length;
              this.totalPages = Math.ceil(this.totalSteps / this.MAX_STEP);

              this.isVerificationObjLoaded = true;

              let fistSelected = new PsdrfErrorCoordinates(
                this.errorsPsdrfList[0].errorList[0].table,
                this.errorsPsdrfList[0].errorList[0].column,
                this.errorsPsdrfList[0].errorList[0].row
              );
              this.selectedErrorElementArr = fistSelected;
              //Using setTimeout to be sure that the ngIf stepperPart has taken effect
              setTimeout(() => {
                this.rerender();
                //Affichage de la toute première erreur de errorsPsdrfList dans le MatTab
                this.displayErrorOnMatTab(fistSelected);
              }, 0);
            },
            error => {
              this._toasterService.error(error.message, "Vérification des données PSDRF");
              this.isDataCharging = false;
              this.isExcelLoaded = false;
              this.isVerificationObjLoaded = false;
            }
          );
      };
    } else {
      this._commonService.regularToaster('error', "Vous n'avez pas les droits d'édition sur le Dispositif "+ this.excelFileName)
    }
  }

  /**
   *  Convert verification object to list of PSDRF error
   */
  jsonObjectToPsdrfObject(errorsPsdrfListTemp){
    
    errorsPsdrfListTemp.forEach((mainError) => {

      if(mainError.isFatalError){
        this.isFileContainingFatalError=true;
      }
      let errorListTemp = [];
      if(mainError.errorType == "PsdrfError"){
        this.mainStepNameArr.push(mainError.errorName);
        this.mainStepTextArr.push(mainError.errorText);
        mainError.errorList.forEach((error) => {
          errorListTemp.push(
            new PsdrfError(
              error.message,
              error.table,
              error.column,
              error.row,
              JSON.parse(error.value)
            )
          );
          this.errorElementArr.push(
            new PsdrfErrorCoordinates(error.table, error.column, error.row)
          );
          error.row.forEach((idx) => {
            this.totalErrorNumber++;
          });
        });
        this.errorsPsdrfList.push({
          errorList: errorListTemp,
          errorType: "PsdrfError",
          isFatalError: mainError.isFatalError,
        });
      } else {
        this.mainStepNameArr.push(mainError.errorName);
        this.mainStepTextArr.push(mainError.errorText);
        mainError.errorList.forEach((error) => {
          errorListTemp.push(
            new PsdrfError(
              error.message,
              null,
              null,
              null,
              null
            )
          );
        });
        this.errorsPsdrfList.push({
          errorList: errorListTemp,
          errorType: "PsdrfErrorColonnes",
          isFatalError: mainError.isFatalError,
        });
      }
    });
  }

  /**
   *  export all the modified data in a new PSDRF File
   */
  exportTableToExcel() {
    let excelData = [];
    this.psdrfArray.forEach((table, i) => {
      excelData.push([table, { header: this.tableColumnsArray[i] }]);
    });
    this.excelSrv.exportToExcelFile(excelData, this.excelFileName, true);
  }

  /**
   *  Return the paginator associated to one of the name table
   * @param tableName Table Name
   */
  getPaginatorFromTableName(tableName: string): MatPaginator {
    return this.tableDataSourceArray[
      this.indexLabelMatTabGroup.indexOf(tableName)
    ].paginator;
  }

  /**
   *  Return the global index of an element according to the table name and the index inside the page
   * @param table Name of the current table
   * @param i Index of the line inside the page
   */
  getRowIndexFromPaginatorProperties(table: string, i: number): number {
    let tablePaginator = this.getPaginatorFromTableName(table);
    return i + tablePaginator.pageIndex * tablePaginator.pageSize;
  }

  /**
   *  In parameter takes the coordinates of a case in the mat-table
   *  Return true if this case is an error
   * @param table Name of the current table
   * @param column Name of the column
   * @param i Index of the line inside the page
   */
  checkErrorCell(table: string, column: string, i: number): boolean {
    if (this.isVerificationObjLoaded) {
      let row = this.getRowIndexFromPaginatorProperties(table, i);
      return this.errorElementArr.some(
        (obj) =>
          obj.table == table &&
          obj.column.includes(column) &&
          obj.row.includes(row)
      );
    } else {
      return false;
    }
  }

  /**
   *  In parameter takes the coordinates of a case in the mat-table
   *  Return true if this case was an error and has been modified
   * @param table Name of the current table
   * @param column Name of the column
   * @param i Index of the line inside the page
   */
  checkModifiedErrorCell(table: string, column: string, i: number): boolean {
    if (this.isVerificationObjLoaded) {
      let row = this.getRowIndexFromPaginatorProperties(table, i);
      return this.modifiedElementArr.some(
        (obj) =>
          obj.table == table &&
          obj.column.includes(column) &&
          obj.row.includes(row)
      );
    } else {
      return false;
    }
  }

    /**
   *  In parameter takes the coordinates of a case in the mat-table
   *  Return true if this case as been deleted
   * @param table Name of the current table
   * @param i Index of the line inside the page
   */
  checkDeletedErrorCell(table: string, i: number): boolean{
    if (this.isVerificationObjLoaded) {
      let row = this.getRowIndexFromPaginatorProperties(table, i);
      return this.deletedElementArr.some(
        (obj) =>
          obj.table == table &&
          obj.row.includes(row)
      );
    } else {
      return false;
    }
  }

  /**
   *  In parameter takes the coordinates of a case in the mat-table
   *  Return true if this case was an error and has been modified
   * @param table Name of the current table
   * @param column Name of the column
   * @param i Index of the line inside the page
   */
  checkSelectedErrorCell(table: string, column: string, i: number): boolean {
    if (this.isVerificationObjLoaded) {
      let row = this.getRowIndexFromPaginatorProperties(table, i);
      return (
        this.selectedErrorElementArr.table == table &&
        this.selectedErrorElementArr.column.includes(column) &&
        this.selectedErrorElementArr.row.includes(row)
      );
    } else {
      return false;
    }
  }

  /**
   * Triggered when a substep is clicked.
   * Display the last error which was selected on this substep. If none, display the first one
   * @param stepperSelectionObj Object wityh 2 attributes: {mainStepIndex: number, subStepIndex: number}
   */
  displayOnSubStepClick(stepperSelectionObj: {
    mainStepIndex: number;
    subStepIndex: number;
  }): void {
    if (
      this.historyService.isMainStepHasAlreadyBeenClicked(
        stepperSelectionObj.mainStepIndex
      ) &&
      this.historyService.isSubStepHasAlreadyBeenClicked(
        stepperSelectionObj.mainStepIndex,
        stepperSelectionObj.subStepIndex
      )
    ) {
      this.displayErrorOnMatTab(
        this.historyService.getLastSelectedCoordinates(
          stepperSelectionObj.mainStepIndex
        )
      );
    } else {
      let error =
        this.errorsPsdrfList[stepperSelectionObj.mainStepIndex].errorList[
          stepperSelectionObj.subStepIndex
        ];
      this.displayErrorOnMatTab(error.toPsdrfErrorCoordinates());
    }
  }

  /**
   * Triggered when a mainstep is clicked.
   * Display the last error which was selected on this substep. If none, display the first one
   * @param stepperSelectionObj StepperSelectionEvent
   */
  displayOnMainStepClick(stepperSelectionObjEvt: StepperSelectionEvent): void {
    this.step = stepperSelectionObjEvt.selectedIndex;
    if (
      this.historyService.isMainStepHasAlreadyBeenClicked(
        stepperSelectionObjEvt.selectedIndex
      )
    ) {
      this.displayErrorOnMatTab(
        this.historyService.getLastSelectedCoordinates(
          stepperSelectionObjEvt.selectedIndex
        )
      );
    } else {
      let error =
        this.errorsPsdrfList[stepperSelectionObjEvt.selectedIndex].errorList[0];
      this.displayErrorOnMatTab(error.toPsdrfErrorCoordinates());
    }
  }

  /**
   * Display the given Coordinates in the mat-tab
   * @param errorCoordinates PsdrfErrorCoordinates of the error we want to display
   */
  displayErrorOnMatTab(errorCoordinates: PsdrfErrorCoordinates): void {
    if(errorCoordinates.table != null){
      this.selectedErrorElementArr = errorCoordinates;
      this.indexMatTabGroup = this.indexLabelMatTabGroup.indexOf(
        errorCoordinates.table
      );
      let tablePaginator =
        this.tableDataSourceArray[this.indexMatTabGroup].paginator;
      let pageNumber = Math.trunc(
        errorCoordinates.row[0] / tablePaginator.pageSize
      );
  
      (tablePaginator.pageIndex = pageNumber), // number of the page you want to jump.
        tablePaginator.page.next({
          pageIndex: pageNumber,
          pageSize: tablePaginator.pageSize,
          length: tablePaginator.length,
        });
    }
  }

  /**
   * Triggered when validation button has been clicked in a substep:
   * - modify the values in the mat-table
   * - update modifiedElementArr (list of the modified elements)
   * @param modificationErrorObj contains 2 attributes:
   * -errorCoordinates:
   * -newErrorValue: new set of
   */
  modifyErrorValue(modificationErrorObj: {
    errorCoordinates: PsdrfErrorCoordinates;
    newErrorValue: any;
  }): void {
    let indexTable = this.indexLabelMatTabGroup.indexOf(
      modificationErrorObj.errorCoordinates.table
    );
    modificationErrorObj.errorCoordinates.row.forEach((idx, i) => {
      modificationErrorObj.errorCoordinates.column.forEach((colName) => {
        if (
          !this.modifiedElementArr.some(
            (obj) =>
              obj.table == modificationErrorObj.errorCoordinates.table &&
              obj.column.includes(colName) &&
              obj.row.includes(idx)
          )
        ) {
          this.modifiedElementArr.push(modificationErrorObj.errorCoordinates);
        }

        this.psdrfArray[indexTable][idx][colName] =
          modificationErrorObj.newErrorValue[i][colName];
      });
    });
    this.progressBarValue =
      (this.modifiedElementArr.length * 100) / this.totalErrorNumber;
  }

  
    /**
   * Triggered when deletion button has been clicked in a substep:
   * - put the values red in the mat-table
   * - update deletedElementArr (list of the modified elements)
   * @param modificationErrorObj contains 1 attributes:
   * -errorCoordinates
   */
    deleteErrorValue(deletionErrorObj: {
      errorCoordinates: PsdrfErrorCoordinates;
    }): void {
      let indexTable = this.indexLabelMatTabGroup.indexOf(
      deletionErrorObj.errorCoordinates.table
      );
      deletionErrorObj.errorCoordinates.row.forEach((idx, i) => {
        // deletionErrorObj.errorCoordinates.column.forEach((colName) => {
          if (
              !this.elementIsInDeletionList(deletionErrorObj.errorCoordinates.table, deletionErrorObj.errorCoordinates.column, idx)
              ) {
                this.deletedElementArr.push(deletionErrorObj.errorCoordinates);
          }else {
            let indexEle = this.deletedElementArr.findIndex(delEle => (
              delEle.table == deletionErrorObj.errorCoordinates.table &&
              delEle.column == deletionErrorObj.errorCoordinates.column &&
              delEle.row.includes(idx)
            ))
            this.deletedElementArr.splice(indexEle, 1);
          }
        // });
      });

      this.progressBarValue =
        (this.modifiedElementArr.length * 100) / this.totalErrorNumber;
    }
    
  elementIsInDeletionList(table, columns, idx){
    return this.deletedElementArr.some(
      (obj) =>
        obj.table == table &&
        obj.column == columns &&
        obj.row.includes(idx)
    )
  }

  /**
   * Update list of modified Main step and go to the next main step
   * @param mainStepIndex index of the main step
   */
  modifyMainStepperAppearance(mainStepIndex: number) {
    this.mainStepper.selected.completed = true;
    this.goForward();
    this.totallyModifiedMainStepperArr.push(mainStepIndex);
  }

  /**
   * Delete the loaded Excel file
   */
  deleteFile(): void {
    this.isExcelLoaded = false;
    this.excelFile = null;
    this.isDataCharging = false;
    this.psdrfArray = [];
    this.reInitializeCorrection();
    this.reInitializeValues();
  }

  /**
   * Reinitialize parameters
   */
  reInitializeValues(): void {
    this.tableDataSourceArray = [];
    this.selectedErrorElementArr = null;
    this.tableColumnsArray = [];
    this.excelFile = null;
    this.excelFileName = "";
    this.isExcelLoaded = false;
  }

  reInitializeCorrection(): void {
    this.isVerificationObjLoaded = false;
    this.totallyModifiedMainStepperArr = [];
    this.indexMatTabGroup = 0;
    this.errorsPsdrfList = [];
    this.mainStepNameArr = [];
    this.errorElementArr = [];
    this.modifiedElementArr = [];
    this.deletedElementArr = [];
    this.totalErrorNumber = 0;
    this.progressBarValue = 0;
    this.mainStepTextArr = [];
    this.isLabelVisible = true;
    this.MAX_STEP = 5;
    this.totalSteps = 0;
    this.page = 0;
    this.step = 0;
    this.totalPages = 0;
    this.minStepAllowed = 0;
    this.maxStepAllowed = this.MAX_STEP - 1;
    this.isFileContainingFatalError = false;
    this.historyService.reInitialize();
  }

  /**
   * Quit import page
   */
  returnToPreviousPage(): void {
    this._router.navigate(["psdrf"]);
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

  //* Main Paginator Functions
  /**
   * Change the page in view (next page exist)
   * @param isForward boolean. True if we go to the next page, false if we come back to the previous
   */
  pageChangeLogic(isForward = true) {
    if (this.step < this.minStepAllowed || this.step > this.maxStepAllowed) {
      if (isForward) {
        this.page++;
      } else {
        this.page--;
      }
      this.changeMinMaxSteps(isForward);
    }
  }

  /**
   * Will change min max steps allowed at any time in view
   * @param isForward boolean. True if we go to the next page, false if we come back to the previous
   */
  changeMinMaxSteps(isForward = true) {
    const pageMultiple = this.page * this.MAX_STEP;

    // maxStepAllowed will be the least value between minStep + MAX_STEP and total steps
    // minStepAllowed will be the least value between pageMultiple and maxStep - MAX_STEP
    if (pageMultiple + this.MAX_STEP - 1 <= this.totalSteps - 1) {
      this.maxStepAllowed = pageMultiple + this.MAX_STEP - 1;
      this.minStepAllowed = pageMultiple;
    } else {
      this.maxStepAllowed = this.totalSteps - 1;
      this.minStepAllowed = this.maxStepAllowed - this.MAX_STEP + 1;
    }

    // This will set the next step into view after clicking on back / next paginator arrows
    if (this.step < this.minStepAllowed || this.step > this.maxStepAllowed) {
      if (isForward) {
        this.step = this.minStepAllowed;
      } else {
        this.step = this.maxStepAllowed;
      }
      this.mainStepper.selectedIndex = this.step;
    }

    this.rerender();
  }

  /**
   * Function to go back page from the current step
   */
  paginatorBack() {
    this.page--;
    this.changeMinMaxSteps(false);
  }

  /**
   * Function to go next page from the current step
   */
  paginatorNext() {
    this.page++;
    this.changeMinMaxSteps(true);
  }

  /**
   * Function to go back from the current step (change page if necessary)
   */
  goBack() {
    if (this.step > 0) {
      this.step--;
      this.mainStepper.previous();
      this.pageChangeLogic(false);
    }
  }

  /**
   * Function to go forward from the current step (change page if necessary)
   */
  goForward() {
    if (this.step < this.totalSteps - 1) {
      this.step++;
      this.mainStepper.next();
      this.pageChangeLogic(true);
    }
  }

  /**
   * This will display the steps in DOM based on the min max step indexes allowed in view
   */
  private rerender() {
    const headers = this.stepperPart.nativeElement.querySelectorAll(
      ".mainStepper > div > mat-step-header"
    );

    // If the step index is in between min and max allowed indexes, display it into view, otherwise set as none
    headers.forEach((h, index) => {
      if (index >= this.minStepAllowed && index <= this.maxStepAllowed) {
        h.style.display = "flex";
        h.style.padding = "12px 1px";
      } else {
        h.style.display = "none";
      }
    });

    if (this.isLabelVisible) {
      const labels = this.stepperPart.nativeElement.querySelectorAll(
        ".mainStepper > div > mat-step-header > .mat-step-label"
      );
      labels.forEach((l) => {
        l.style.display = "flex";
      });
    } else {
      // We precise ".mainStepper" to assure that we are not changing substep matstep
      const lines = this.stepperPart.nativeElement.querySelectorAll(
        ".mainStepper > div > mat-step-header > .mat-stepper-horizontal-line"
      );

      // If the line index is between min and max allowed indexes, display it in view, otherwise set as none
      // One thing to note here: length of lines is 1 less than length of headers
      // For eg, if there are 8 steps, there will be 7 lines joining those 8 steps
      lines.forEach((l, index) => {
        if (index >= this.minStepAllowed && index <= this.maxStepAllowed) {
          l.style.display = "block";
        } else {
          l.style.display = "none";
        }
      });

      const labels = this.stepperPart.nativeElement.querySelectorAll(
        ".mainStepper > div > mat-step-header > .mat-step-label"
      );
      labels.forEach((l) => {
        l.style.display = "none";
      });
    }
  }

  /**
   * This will display the steps in DOM based on the min max step indexes allowed in view
   */
  showStepLabels() {
    this.isLabelVisible = !this.isLabelVisible;
    if (this.isLabelVisible) {
      this.extensionIcon = "unfold_more";
      this.MAX_STEP = 5;
    } else {
      this.extensionIcon = "unfold_less";
      this.MAX_STEP = 60;
    }
    this.totalPages = Math.ceil(this.totalSteps / this.MAX_STEP);
    this.page = Math.trunc(this.step / this.MAX_STEP);

    this.changeMinMaxSteps(false);
  }

  /**
   * Check if a main step has been changed. Return a boolean.
   * @param mainStepIndex index of the main step
   */
  checkMainStepCompleted(mainStepIndex: number): boolean {
    return this.totallyModifiedMainStepperArr.includes(mainStepIndex);
  }

  /**
   * TODO: Implémenter la fonction de relance du fichier original
   */
  dataVerifOriginalFile(): void {}

  /**
   *
   */
  dataVerifModifiedFile(): void {
    //Supprimer les éléments au dernier moment
    if(this.deletedElementArr.length > 0){
      let deleteObject = {}
      //Remplir l'objet avec les indexs
      this.deletedElementArr.forEach(element => {
        if (!deleteObject.hasOwnProperty(element.table)){
          deleteObject[element.table] = []
        }
        element.row.forEach(i => {
          if(deleteObject[element.table].indexOf(i) === -1 ){
            deleteObject[element.table].push(i)
          }
        })
      })
      for (const property in deleteObject){
        //classer les index dans l'ordre décroissant
        deleteObject[property].sort((a, b) => b - a )
        let indexTable = this.indexLabelMatTabGroup.indexOf(
          property
        );
        // Supprimer les index un par un
        deleteObject[property].forEach(i => {
          this.psdrfArray[indexTable].splice(i, 1)
        })
      }
    }
    this.reInitializeCorrection();
    this.dataSrv
      .psdrf_data_verification(
        JSON.stringify(this.psdrfArray, (k, v) => (v === undefined ? null : v))
      )
      .subscribe(
        verificationJson => {
          let verificationObj = JSON.parse(verificationJson);
          this.correctionService.setSelectionErrorObj(
            verificationObj["correctionList"]
          );
          let errorsPsdrfListTemp = verificationObj["verificationObj"];

          this.mainStepNameArr = [];
          this.totalErrorNumber = 0;

          this.jsonObjectToPsdrfObject(errorsPsdrfListTemp);
          this.isVerificationObjLoaded = true;

          this.totalSteps = errorsPsdrfListTemp.length;
          this.totalPages = Math.ceil(this.totalSteps / this.MAX_STEP);

          let fistSelected = new PsdrfErrorCoordinates(
            this.errorsPsdrfList[0].errorList[0].table,
            this.errorsPsdrfList[0].errorList[0].column,
            this.errorsPsdrfList[0].errorList[0].row
          );
          this.selectedErrorElementArr = fistSelected;
          //Using setTimeout to be sure that the ngIf stepperPart has taken effect
          setTimeout(() => {
            this.rerender();
            //Affichage de la toute première erreur de errorsPsdrfList dans le MatTab
            this.displayErrorOnMatTab(fistSelected);
          }, 0);
        },
        error => {
          this._toasterService.error(error.message, "Vérification des données PSDRF");
        }
      );
  }

  importShape($event): void {
    const target: DataTransfer = <DataTransfer>$event.target;
    if (target.files.length !== 1) throw new Error("Cannot use multiple files");
    this.shapeFile = target.files[0];
    this.isShapeCharged = true;
  }

  dataVerifWithShape(): void {
    let excelAndShapeData: FormData = new FormData();
    excelAndShapeData.append("file", this.shapeFile);

    let overrides = JSON.stringify(this.psdrfArray, (k, v) =>
      v === undefined ? null : v
    );
    const blobOverrides = new Blob([overrides], {
      type: "application/json",
    });
    excelAndShapeData.append("overrides", blobOverrides);

    this.dataSrv
      .psdrf_data_verification_with_shape(excelAndShapeData)
      .subscribe((res) => console.log(res));
  }

  deleteShapeFile(): void {
    this.shapeFile = null;
    this.isShapeCharged = false;
  }

  integrationToDatabase(): void{
    if(!this.integrationLoading){
      let idAndData: FormData = new FormData();
  
      let dispositifId = this.excelFileName.split(".")[0].split("_")[0].split("-")[0]
      idAndData.append("dispositifId", dispositifId.toString());
  
      let dispositifName = this.excelFileName.split(".")[0].split("_")[0].split("-")[1]
      idAndData.append("dispositifName", dispositifName);
  
      let psdrfDataJson = JSON.stringify(this.psdrfArray, (k, v) =>
        v === undefined ? null : v
      )
      const blobPsdrf = new Blob([psdrfDataJson], {
        type: "application/json",
      });
      idAndData.append("psdrfData", blobPsdrf);
      
      this.integrationLoading = true;   
      this.dataSrv
      .psdrfIntegrationToDatabase(idAndData)
      .subscribe(
        integrationJson => {
          let integrationObj = JSON.parse(integrationJson);
          this.integrationLoading = false;
          if(integrationObj.success){
            this._toasterService.error("Les données ont bien été ajoutées à la BDD", "");
          }
        }, 
        error => {
          this._toasterService.error(error.message, "Intégration des données en BDD");
        });

    }
  }
}
