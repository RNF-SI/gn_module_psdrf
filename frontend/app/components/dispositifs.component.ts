import { Component, OnInit } from "@angular/core";
import { HttpClient, HttpParams } from '@angular/common/http';
import { Router } from "@angular/router";
import { FormControl, FormGroup } from "@angular/forms";
import { MapService } from "@geonature_common/map/map.service";
import { AppConfig } from '@geonature_config/app.config';

import { PsdrfDataService } from "../services/route.service";



@Component({
    selector: "rnf-psdrf-dispositifs",
    templateUrl: "dispositifs.component.html",
    styleUrls: ["dispositifs.component.scss"]
  })
  export class DispositifsComponent implements OnInit {
    public dispositifs: Array<any>;
    public apiEndPoint: string = 'psdrf/dispositifs';
    public statEndPoint: string = 'psdrf/global_stats';
    public stats: object;
    public geojson: object;
    public mapCenter: Array<number> = [47, 2];
    public mapZoom: number = 5;
    public tableData: any;
    public layerDict: object;
    public tableColumns: Array<object>;
    public isLoading: boolean = false;
    public searchForm = new FormGroup({
      region: new FormControl(''),
      alluvial: new FormControl(''),
      status: new FormControl(''),
    });
    public statusList: Array<object>;
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

    private _cycleColors: object = {
      1: 'yellow',
      2: 'orange',
      3: 'red'
    };

    constructor(
      private _api: HttpClient, 
      private _router: Router, 
      private mapservice: MapService,
      private dataSrv: PsdrfDataService
      ) { }

    ngOnInit() {
        // Chargement des statistiques
        this._api.get<any>(`${AppConfig.API_ENDPOINT}/${this.statEndPoint}`)
          .subscribe(data => {this.stats = data});


        this.tableColumns = [{name: "Nom du dispositif", prop: "name"}];

        this._api.get<any>(`${AppConfig.API_ENDPOINT}/psdrf/status_types`)
          .subscribe(data => {this.statusList = data});

        this.loadData();
    }

    loadData(): void {
      this.isLoading = true;
      const params = new HttpParams().set('region', this.searchForm.get('region').value)
        .set('alluvial', this.searchForm.get('alluvial').value)
        .set('status', this.searchForm.get('status').value);
      this._api.get<any>(`${AppConfig.API_ENDPOINT}/${this.apiEndPoint}`, {params: params})
          .subscribe(data => {
            this.layerDict = {};
            this.geojson = data.items;
            let rows = [];
            data.items.features.forEach(i => {
              rows.push(i.properties)
            });
            this.tableData = rows;
            this.isLoading = false;
          });
    }

    onEachFeature(feature, layer) {
      const cycle = feature.properties.cycle;
      const color = this._cycleColors[cycle];
      layer.setStyle({
        color: color,
        radius: 8
      });
      layer.bindPopup(feature.properties.leaflet_popup);
      this.layerDict[feature.properties.id_dispositif] = layer;
    }

    onRowSelect(row): void {
      const lyr = this.layerDict[row.selected[0].id_dispositif];
      if (lyr) {
        const center = lyr.getLatLng();
        this.mapservice.map.setView(center, 15);
      }
    }

    onDetailDispositif(row): void {
      this._router.navigate(["psdrf/infodispositif", row])
    }

    onSearch(): void {
      this.loadData()
    }

    openImportPage(): void {
      this._router.navigate(["psdrf/importdonnees"])
    }

    launchAnalysis(dispositifId: number): void{


      this.dataSrv
        .psdrf_data_analysis(dispositifId)
        .subscribe(
          (data: any) => {
            var file = new Blob([data.pdf], { type: 'application/pdf' })
            var fileURL = URL.createObjectURL(file);
  
            console.log(data)

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
            console.log('getPDF error: ',error);
          }
        );
    }

  }

