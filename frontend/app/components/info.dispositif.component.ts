import { Component, OnInit } from "@angular/core";
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute, Router, ParamMap } from "@angular/router";
import { AppConfig } from '@geonature_config/app.config';
import { MapListService } from '@geonature_common/map-list/map-list.service';
import { PsdrfDataService } from "../services/route.service";
import { ToastrService } from 'ngx-toastr';
import { ExcelImportService } from "../services/excel.import.service";




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
  public editing: boolean = false;

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

  onEditDispositif(): void {
    this.editing = ! this.editing;
  }

  onDispositifSaved(saved: boolean) {
    // Masque le formulaire après enregistrement
    this.editing = !saved;
    // Rechargement des données
    if (saved) this.ngOnInit();
  }

  onDispositifFormCanceled(canceled: boolean) {
    if (canceled) this.editing = false;
  }

  onRowSelect(row): void {
    // Vérifie si la géométrie existe bien avant de lancer l'évenement
    const ft = this.mapListService.layerDict[row.selected[0][this.mapListService.idName]];
    if (ft) {
      this.mapListService.onRowSelect(row)
    }
  }

  onDetailPlacette(row): void {
    this._router.navigate(["psdrf/infoplacette", row])
  }

  launchAnalysis(): void{
    this.dataSrv
      .psdrf_data_analysis(this.id)
      .subscribe(
        data => {
          var file = new Blob([data.pdf], { type: 'application/pdf' })
          var fileURL = URL.createObjectURL(file);

          // if you want to open PDF in new tab
          // window.open(fileURL); 
          var a         = document.createElement('a');
          a.href        = fileURL; 
          a.target      = '_blank';
          a.download    = data.filename;
          document.body.appendChild(a);
          a.click();
        },
        (error) => {
          this._toasterService.error(error.message, "Génération du rapport PSDRF");
        }
      );
  }

  importExcel(): void{
    this.dataSrv
      .getExcelData(this.id)
      .subscribe(
        data => {
          let psdrfArrayObj = JSON.parse(data)
          console.log(psdrfArrayObj)
          this.exportTableToExcel(psdrfArrayObj.data)
        }, 
        (error) => {
          this._toasterService.error(error.message, "Génération du rapport PSDRF");
        }
        ) 
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
      console.log(this.dispositif)
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

}