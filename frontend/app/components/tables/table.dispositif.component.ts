import { Component, OnInit } from "@angular/core";
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute, Router, ParamMap } from "@angular/router";
import { AppConfig } from '@geonature_config/app.config';

/*
    Composant contenant les différents onglets
    avec chargement des données à la volée
*/

@Component({
    selector: "rnf-psdrf-table-dispositif",
    templateUrl: "table.dispositif.component.html",
    styleUrls: ["table.dispositif.component.scss"]
})
export class TableDispositifComponent implements OnInit {
  public dispositif: object;
  public apiEndPoint: string;
  public id: number;
  public isLoading: boolean = false;
  public activeTab: string = 'placettes';
  public tabHeaders: Array<object>;
  public tableColumns: Array<object>;
  public tableRows: Array<object>;
  public selectedRow: Array<object> = [];
  public totalElements: number;

  private _tabs: object = {
      placettes: {
          label: 'Placettes',
          endPoint: "psdrf/placettes",
          columns: [
              {prop: "id_placette_orig", name: "NumPlac"},
              {prop: "cycle", name: "Cycle"},
              {prop: "strate", name: "Strate"},
              {prop: "poids_placette", name: "Poids"},
              {prop: "pente", name: "Pente"},
              {prop: "correction_pente", name: "CorrectionPente"},
              {prop: "exposition", name: "Exposition"},
              {prop: "habitat", name: "Habitat"},
              {prop: "ref_habitat", name: "RefHabitat"},
            ]
        },
        cycles: {
            label: 'Cycles',
            endPoint: "psdrf/cycles",
            columns: [
                {prop: "placette_id", name: "Num placette"},
                {prop: "original_id", name: "Num Cycle"},
                {prop: "cycle", name: "Cycle"},
                {prop: "coeff", name: "Coefficent"},
                {prop: "date", name: "Date"},
            ]
          },
        arbres: {
            label: 'Arbres',
            endPoint: "psdrf/arbres",
            columns: [
                {prop: "id_arbre_orig", name: "Num arbre"},
                {prop: "code_essence", name: "Essence"},
                {prop: "cycle", name: "Cycle"},
                {prop: "azimut", name: "Azimut"},
                {prop: "distance", name: "Distance"},
                {prop: "diametre1", name: "Diamètre 1"},
                {prop: "diametre2", name: "Diamètre 2"},
                {prop: "type", name: "Type"},
                {prop: "hauteur_totale", name: "Hauteur"},
                {prop: "stade_durete", name: "DistanceStade dureté"},
                {prop: "observation", name: "Observations"},
                {prop: "code_ecolo", name: "Code écologie"},
                {prop: "ref_code_ecolo", name: "Ref. code écolo"},
              ]
          },
  }

  constructor(
    private _api: HttpClient,
    private _router: Router,
    private _route: ActivatedRoute
  ) { }

  ngOnInit() {
    this.apiEndPoint = "psdrf/dispositif";
    this.dispositif = {"name": '<>'};

    this._route.params.subscribe(params => {
      this.id = params.id;

      let headers: Array<object> = [];
      for (let k in this._tabs) {
        headers.push({name: k, label: this._tabs[k].label});
      }
      this.tabHeaders = headers;

      this._api.get<any>(`${AppConfig.API_ENDPOINT}/${this.apiEndPoint}/${this.id}`)
          .subscribe(data => {
            this.dispositif = data;
          });

        this.loadTable();
    })
  }


  loadTable() {
      // Loads table data and sets variables
    const conf = this._tabs[this.activeTab];
    this.tableColumns = conf.columns;
    this.isLoading = true;
    this._api.get<any>(`${AppConfig.API_ENDPOINT}/${conf.endPoint}/${this.id}`).subscribe(data => {
        if (data.items.features) { // cas GeoJson
            this.tableRows = data.items.features.map(i => i.properties);
        } else {
            this.tableRows = data.items;
        }
        this.totalElements = data.total;
        this.isLoading = false;
    }, error => {
        this.tableRows = [];
        this.isLoading = false
    })
  }


  onTabClick(tabName) {
      this.activeTab = tabName;
      this.loadTable()
      return false;
  }

  onRowSelect(evt) {

  }
}