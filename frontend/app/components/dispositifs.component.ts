import { Component, OnInit } from "@angular/core";
import { HttpClient } from '@angular/common/http';
import { Router } from "@angular/router";
import { AppConfig } from '@geonature_config/app.config';
import { MapListService } from '@geonature_common/map-list/map-list.service';





@Component({
    selector: "rnf-psdrf-dispositifs",
    templateUrl: "dispositifs.component.html",
    styleUrls: ["dispositifs.component.scss"]
  })
  export class DispositifsComponent implements OnInit {
    public dispositifs: Array<any>;
    public apiEndPoint: string;
    public statEndPoint: string = 'psdrf/global_stats';
    public stats: object;

    constructor(private _api: HttpClient, private _router: Router, public mapListService: MapListService) { }

    ngOnInit() {
        // Chargement des statistiques
        this._api.get<any>(`${AppConfig.API_ENDPOINT}/${this.statEndPoint}`)
          .subscribe(data => {this.stats = data});

        this.mapListService.originStyle = {
          color: 'green',
          radius: 8
        }

        this.mapListService.displayColumns = [{name: "Nom du dispositif", prop: "name"}];
        this.mapListService.idName = "id_dispositif";

        this.apiEndPoint = "psdrf/dispositifs";

        this.mapListService.getData('psdrf/dispositifs', [
          //  {param: "limit", value: 200}
        ])
    }

    onRowSelect(row): void {
      // Vérifie si la géométrie existe bien avant de lancer l'évenement
      const ft = this.mapListService.layerDict[row.selected[0][this.mapListService.idName]];
      if (ft) {
        this.mapListService.onRowSelect(row)
      }
    }

    onDetailDispositif(row): void {
      this._router.navigate(["psdrf/infodispositif", row])
    }
  }