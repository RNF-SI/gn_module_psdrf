import { Component, OnInit } from "@angular/core";
import { HttpClient } from '@angular/common/http';
import { Router } from "@angular/router";
import { FormControl, FormGroup } from "@angular/forms";
import { AppConfig } from '@geonature_config/app.config';
import { MapListService } from '@geonature_common/map-list/map-list.service';


@Component({
    selector: "rnf-psdrf-dispositifs",
    templateUrl: "dispositifs.component.html",
    styleUrls: ["dispositifs.component.scss"]
  })
  export class DispositifsComponent implements OnInit {
    public dispositifs: Array<any>;
    public apiEndPoint: string = 'psdrf/global_stats';
    public statEndPoint: string = 'psdrf/global_stats';
    public stats: object;
    public searchForm = new FormGroup({
      region: new FormControl('')
    });
    public regions = [ // NB : dans l'idéal, les récupérer depuis l'API
      {insee: '84', name: 'Auvergne-Rhône-Alpes'},
      {insee: '27', name: 'Bourgogne-Franche-Comté'},
      {insee: '53', name: 'Bretagne'},
      {insee: '24', name: 'Centre-Val de Loire'},
      {insee: '94', name: 'Corse'},
      {insee: '44', name: 'Grand Est'},
      {insee: '32', name: 'Hauts-de-France'},
      {insee: '11', name: 'Île-de-France'},
      {insee: '28', name: 'Normandie'},
      {insee: '75', name: 'Nouvelle-Aquitaine'},
      {insee: '76', name: 'Occitanie'},
      {insee: '52', name: 'Pays de la Loire'},
      {insee: '93', name: 'Provence-Alpes-Côte d\'Azur'},
    ];

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

        this.mapListService.getData(this.apiEndPoint, [
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

    onSearch(): void {
      this.mapListService.refreshData(this.apiEndPoint, 'set', [
        {param: 'region', value: this.searchForm.get('region').value || '' }
      ]);
    }
  }