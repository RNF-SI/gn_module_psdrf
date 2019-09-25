import { Component, OnInit } from "@angular/core";
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute, Router, ParamMap } from "@angular/router";
import { AppConfig } from '@geonature_config/app.config';
import { MapListService } from '@geonature_common/map-list/map-list.service';



@Component({
    selector: "rnf-psdrf-info-dispositif",
    templateUrl: "info.dispositif.component.html",
    styleUrls: ["info.dispositif.component.scss"]
})
export class InfoDispositifComponent implements OnInit {
  public dispositif: object;
  public id: number;
  public apiEndPoint: string;
  public placettesEndPoint: string;
  public editing: boolean = false;
  public canEdit: boolean;

  constructor(
    private _api: HttpClient,
    private _router: Router,
    private _route: ActivatedRoute,
    public mapListService: MapListService
  ) { }

  ngOnInit() {
    this.apiEndPoint = "psdrf/dispositif";
    this.placettesEndPoint = "psdrf/placettes"
    this.dispositif = {"name": '<>'};
    this.canEdit = true; // TODO: implement CRUVED

    this.mapListService.displayColumns = [
      {name: "N°", prop: "id_placette_orig"},
      {name: "Nombre d'arbres", prop: "nb_arbres"}
    ];
    this.mapListService.idName = "id_placette";
    this.mapListService.page.size = 20;

    this._route.params.subscribe(params => {
      this.id = params.id;
      this.placettesEndPoint = "psdrf/placettes/" + this.id;

      this._api.get<any>(`${AppConfig.API_ENDPOINT}/${this.apiEndPoint}/${this.id}`)
          .subscribe(data => {
            this.dispositif = data;
          });

      this.mapListService.getData('psdrf/placettes/' + this.id, []);

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

}