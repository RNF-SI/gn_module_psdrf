import { Component, OnInit } from "@angular/core";
import { HttpClient } from '@angular/common/http';
import { AppConfig } from '@geonature_config/app.config';
import { MapListService } from '@geonature_common/map-list/map-list.service';


@Component({
    selector: "rnf-psdrf-dispositifs",
    templateUrl: "dispositifs.component.html"
  })
  export class DispositifsComponent implements OnInit {
    public dispositifs: Array<any>;
    public apiEndPoint: string;

    constructor(private _api: HttpClient, public mapListService: MapListService) { }

    ngOnInit() {
        this.mapListService.displayColumns = [{name: "Nom", prop: "name"}];
        this.mapListService.idName = "id_dispositif";

        this.apiEndPoint = "psdrf/dispositifs";

        this.mapListService.getData('psdrf/dispositifs', [
            {param: "limit", value: 20}
        ])
    }

    onRowSelect(row): void {
      // Vérifie si la géométrie existe bien avant de lancer l'évenement
      const ft = this.mapListService.layerDict[row.selected[0][this.mapListService.idName]];
      if (ft) {
        this.mapListService.onRowSelect(row)
      }
    }
  }