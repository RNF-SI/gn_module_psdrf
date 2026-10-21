import { Component, OnInit } from "@angular/core";
import { ActivatedRoute, Router } from "@angular/router";
import { PsdrfDataService } from "../services/route.service";

export type StatutPlacette =
  | "prod_seul"
  | "staging_seul"
  | "different"
  | "identique";

export interface Releve {
  annee: number | null;
  date_releve: string | null;
  nb_arbres: number;
}

export interface PlacetteComparee {
  num_placette: string;
  statut: StatutPlacette;
  production: Releve | null;
  staging: Releve | null;
}

export interface CycleCompare {
  num_cycle: number;
  compte: { [statut in StatutPlacette]: number };
  placettes: PlacetteComparee[];
}

@Component({
  selector: "rnf-psdrf-comparaison-staging",
  templateUrl: "comparaison.staging.component.html",
  styleUrls: ["comparaison.staging.component.scss"],
})
export class ComparaisonStagingComponent implements OnInit {
  public id: number;
  public cycles: CycleCompare[] = [];
  public loading = true;
  public erreur = false;
  // Par défaut on ne montre que les écarts : c'est ce qu'on vient chercher.
  public ecartsSeulement = true;

  public libelles: { [statut in StatutPlacette]: string } = {
    prod_seul: "Production seule",
    staging_seul: "Staging seul",
    different: "Différent",
    identique: "Identique",
  };
  public statuts: StatutPlacette[] = [
    "staging_seul",
    "prod_seul",
    "different",
    "identique",
  ];

  constructor(
    private _route: ActivatedRoute,
    private _router: Router,
    private dataSrv: PsdrfDataService
  ) {}

  ngOnInit() {
    this._route.params.subscribe((params) => {
      this.id = params["id"];
      this.loading = true;
      this.dataSrv.getComparaisonStaging(this.id).subscribe(
        (data) => {
          this.cycles = data.cycles;
          this.loading = false;
        },
        () => {
          this.erreur = true;
          this.loading = false;
        }
      );
    });
  }

  placettesAffichees(cycle: CycleCompare): PlacetteComparee[] {
    return this.ecartsSeulement
      ? cycle.placettes.filter((p) => p.statut !== "identique")
      : cycle.placettes;
  }

  nbEcarts(cycle: CycleCompare): number {
    return cycle.placettes.length - cycle.compte.identique;
  }

  returnToDispositif(): void {
    this._router.navigate(["psdrf/infodispositif", this.id]);
  }
}
