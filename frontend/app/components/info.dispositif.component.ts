import { Component, OnInit } from "@angular/core";
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute, Router, ParamMap } from "@angular/router";
import { AppConfig } from '@geonature_config/app.config';
import { MapListService } from '@geonature_common/map-list/map-list.service';
import { PsdrfDataService } from "../services/route.service";
import { ToastrService } from 'ngx-toastr';
import { ExcelImportService } from "../services/excel.import.service";
import { interval, EMPTY } from 'rxjs';
import { switchMap, catchError, takeWhile, tap, first, timeout} from 'rxjs/operators';


export interface Document {
  name: string;
  toDownload: boolean;
  // color: ThemePalette;
  subdocuments?: Document[];
  activated: boolean;
  documentParameters?: {name: string, text: string, value: boolean}[];
}


@Component({
    selector: "rnf-psdrf-info-dispositif",
    templateUrl: "info.dispositif.component.html",
    styleUrls: ["info.dispositif.component.scss"]
})
export class InfoDispositifComponent implements OnInit {
  public dispositif: any;
  public id: number;
  public apiEndPoint: string;
  public placettesEndPoint: string;
  public allToDownload: boolean = true;

  //Boolean du lancement de la génération du rapport d'un dispositif (vrai si requête en cours)
  analysisLoading = false; 

  //Boolean du lancement de la génération du fichier excel (vrai si requête en cours)
  excelLoading = false; 

  documents: Document = {
      name: 'Tout',
      toDownload: true,
      activated: true,
      subdocuments: [
        {
          name: 'Carnet et figures', 
          toDownload: true, 
          documentParameters: [{
          name: 'Answer_Radar', 
          text: "Réaliser l'analyse de l'état de conservation du dispositif ?",
          value: true
          }
        ],
        activated: true
      },
      {
        name: 'Plan des arbres et figures', 
        toDownload: false, 
        documentParameters:[],
        activated: false
      },
        // {name: 'Table Excel des Résultats Bruts', toDownload: false},
        // {name: 'Plan des arbres', toDownload: false}
      ],
    };

  constructor(
    private _api: HttpClient,
    private _router: Router,
    private _route: ActivatedRoute,
    public mapListService: MapListService, 
    private dataSrv: PsdrfDataService,
    private _toasterService: ToastrService,
    private excelSrv: ExcelImportService
  ) { }

  ngOnInit() {
    this.apiEndPoint = "psdrf/dispositif";
    this.placettesEndPoint = "psdrf/placettes"
    this.dispositif = {"name": '<>'};

    this.mapListService.displayColumns = [
      {name: "id", prop: "id_placette"},
      {name: "id original", prop: "id_placette_orig"}
    ];
    this.mapListService.idName = "id_placette";
    this.mapListService.page.size = 20;

    this._route.params.subscribe(params => {
      this.id = params.id;
      this.placettesEndPoint = "psdrf/placettes/" + this.id;

      this._api.get<any>(`${AppConfig.API_ENDPOINT}/${this.apiEndPoint}/${this.id}`)
          .subscribe(data => {
            this.dispositif = data;

            this.mapListService.getData('psdrf/placettes/' + this.id, [
                {param: "limit", value: 20}
            ])
          });
    })
  }

  /**
   * Quit info page
   */
  returnToPreviousPage(): void {
    this._router.navigate(["psdrf"]);
  }

  onRowSelect(row): void {
    // Vérifie si la géométrie existe bien avant de lancer l'évenement
    const ft = this.mapListService.layerDict[row.selected[0][this.mapListService.idName]];
    if (ft) {
      this.mapListService.onRowSelect(row)
    }
  }

  checkCheckboxDisabled(): boolean{
      return this.mapListService.page.totalElements>150? true: false;
  }

  onDetailPlacette(row): void {
    this._router.navigate(["psdrf/infoplacette", row])
  }

  launchAnalysis(): void{
    let isCarnetToDownload= this.documents.subdocuments.find(element => element['name']=='Carnet et figures')['toDownload'];
    let isPlanDesArbresToDownload= this.documents.subdocuments.find(element => element['name']=='Plan des arbres et figures')['toDownload'];

    // Création de l'objet contenant tous les paramètres
    let parameters = []
    this.documents.subdocuments.forEach(subdoc => {
      if (subdoc.toDownload){
        subdoc.documentParameters.forEach(param => {
          parameters.push(param);
        });
      }
    })

    if(isCarnetToDownload || isPlanDesArbresToDownload){
      if(!this.analysisLoading){
        this.analysisLoading = true;
        this._toasterService.info("La génération des documents peut prendre plusieurs minutes", "Information");
  
        this.dataSrv.psdrf_data_analysis(this.id, isCarnetToDownload, isPlanDesArbresToDownload, parameters)
        .subscribe(
          taskId => {
            this.analysisLoading = true;
  
            const statusCheck$ = interval(20000).pipe(
              switchMap(() => this.dataSrv.get_task_status(taskId)),
              tap(taskStatus => {
                console.log(taskStatus);

                console.log('Inside observable:', taskStatus.state);
                // Check if the task state is 'FAILURE' and handle it
                if (taskStatus.state === 'FAILURE') {
                  this._toasterService.error("La génération du document a échoué.", "Échec de la génération", {
                    closeButton: true,
                    disableTimeOut: true,
                  });
                  this.analysisLoading = false;
                  // Here you might want to throw an error to stop the observable
                  throw new Error('Task failed');
                }
              }),
              takeWhile(taskStatus => taskStatus.state !== 'SUCCESS', true), // Include the last emission; adjust condition as needed
              timeout(1500000), // Set timeout to 1500 seconds
              catchError(error => {
                // This block will execute if the task times out, if there's an HTTP error, or if an error is thrown manually
                this.analysisLoading = false;
                if (error.name && error.name === 'TimeoutError') {
                  this._toasterService.error("La génération du document a pris trop de temps et a été interrompue.", "Erreur de Délai", {
                    closeButton: true,
                    disableTimeOut: true,
                  });
                } else {
                  this._toasterService.error("Une erreur est survenue lors de la vérification du statut de la tâche.", "Erreur", {
                    closeButton: true,
                    disableTimeOut: true,
                  });
                }
                return EMPTY;
              })
            );
  
            statusCheck$.subscribe(
              taskStatus => {
                if (taskStatus.state === 'SUCCESS') {
                  this.analysisLoading = false;
                  // Success logic here
                  this.dataSrv.get_task_result(taskId, this.id).subscribe(
                    data => {
                      var file = new Blob([data.zip], { type: 'octet/stream' });
                      var fileURL = URL.createObjectURL(file);
  
                      var a = document.createElement('a');
                      a.href = fileURL; 
                      a.target = '_blank';
                      a.download = data.filename;
                      document.body.appendChild(a);
                      a.click();
                      this._toasterService.success("Les documents ont bien été générés.", "Génération des documents réussie");
                    },
                    error => {
                      // This catch block is for handling errors thrown from within the subscription itself
                      this.analysisLoading = false;
                      this._toasterService.error("Une erreur est survenue.", "Erreur", {
                        closeButton: true,
                        disableTimeOut: true,
                      });
                    }
                  );
                } else if (taskStatus.state === 'FAILURE') {
                  // Display error from the task state check
                  this._toasterService.error("La génération du document a échoué.", "Échec de la génération", {
                    closeButton: true,
                    disableTimeOut: true,
                  });
                }
              },

              error => {
                console.error("Task failed with error:", error);
                this._toasterService.error("Error: " + (error.error.message || "Unknown error"), "Task Failure", {
                  closeButton: true,
                  disableTimeOut: true,
                });

              }
            );
          },
          error => {
            this.analysisLoading = false;
            this._toasterService.error("Une erreur est survenue lors de la demande de génération du document.", "Erreur", {
              closeButton: true,
              disableTimeOut: true,
            });
          }
        );
      }
    }
  }

  importExcel(): void{
    if(!this.excelLoading){
      this.excelLoading = true;
      this.dataSrv
        .getExcelData(this.id)
        .subscribe(
          data => {
            let psdrfArrayObj = JSON.parse(data)
            this.exportTableToExcel(psdrfArrayObj.data)
            this.excelLoading = false;
            this._toasterService.success("Le fichier excel a bien été généré.", "Génération du fichier excel");
          }, 
          (error) => {
            this._toasterService.error(error.message, "Génération du fichier excel", {
              closeButton: true,
              disableTimeOut: true,
            });
            this.excelLoading = false;
          }
        ) 
    }
  }

  /**
   *  export all the modified data in a new PSDRF File
   */
     exportTableToExcel(psdrfArray: any) {
      let excelData = [];
      let tableColumnsArray = ["Placettes", "Cycles", "Arbres", "Rege", "Transect", "BMSsup30", "Reperes"];
      let excelFileName = this.dispositif.id.toString() + "-"+ this.dispositif.name;
      let columns = this.excelSrv.getColumnNames()
      let currentSheet;
      psdrfArray.forEach((table, i) => {
        currentSheet= tableColumnsArray[i];
        excelData.push([table, { header: columns[currentSheet] }]);
      });
      this.excelSrv.exportToExcelFile(excelData, excelFileName, false, tableColumnsArray);
    }

  importTableur(): void{
    
  }

  importSIG(): void{
    
  }

  updateAllToDownload() {
    this.allToDownload = this.documents.subdocuments != null && this.documents.subdocuments.every(t => t.toDownload);
  }

  someToDownload(): boolean {
    if (this.documents.subdocuments == null) {
      return false;
    }
    return this.documents.subdocuments.filter(t => t.toDownload).length > 0 && !this.allToDownload;
  }

  setAll(toDownload: boolean) {
    this.allToDownload = toDownload;
    if (this.documents.subdocuments == null) {
      return;
    }
    this.documents.subdocuments.forEach(t => {
      if(t.activated){
        t.toDownload = toDownload;
      }
    });
  }
}
