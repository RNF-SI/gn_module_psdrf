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

  public libelles: { [statut in StatutPlacette]: string } = {
    staging_seul: "Staging-terrain seul",
    prod_seul: "Production seule",
    different: "Différent",
    identique: "Identique",
  };
  public statuts: StatutPlacette[] = [
    "staging_seul",
    "prod_seul",
    "different",
    "identique",
  ];

  // Filtres communs à tous les cycles. Par défaut on montre les écarts :
  // c'est ce qu'on vient chercher.
  public statutsAffiches = new Set<StatutPlacette>([
    "staging_seul",
    "prod_seul",
    "different",
  ]);
  public recherche = "";
  public triParStatut = false;

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

  basculerStatut(statut: StatutPlacette): void {
    if (this.statutsAffiches.has(statut)) {
      this.statutsAffiches.delete(statut);
    } else {
      this.statutsAffiches.add(statut);
    }
  }

  placettesAffichees(cycle: CycleCompare): PlacetteComparee[] {
    const recherche = this.recherche.trim().toLowerCase();
    const placettes = cycle.placettes.filter(
      (p) =>
        this.statutsAffiches.has(p.statut) &&
        (!recherche || p.num_placette.toLowerCase().includes(recherche))
    );
    if (this.triParStatut) {
      // Tri stable : l'ordre par numéro (celui du serveur) est conservé dans un statut.
      return placettes.sort(
        (a, b) => this.statuts.indexOf(a.statut) - this.statuts.indexOf(b.statut)
      );
    }
    return placettes;
  }

  nbEcarts(cycle: CycleCompare): number {
    return cycle.placettes.length - cycle.compte.identique;
  }

  /** Une phrase par cycle pour le bandeau de synthèse. */
  synthese(cycle: CycleCompare): string {
    const c = cycle.compte;
    if (this.nbEcarts(cycle) === 0) {
      return `${c.identique} placettes identiques en production et en staging-terrain.`;
    }
    const parties = [];
    if (c.staging_seul) {
      parties.push(`${c.staging_seul} en staging-terrain à importer`);
    }
    if (c.different) {
      parties.push(`${c.different} différente(s)`);
    }
    if (c.prod_seul) {
      parties.push(`${c.prod_seul} en production seulement`);
    }
    return `${parties.join(", ")} ; ${c.identique} identique(s).`;
  }

  aDesEcarts(): boolean {
    return this.cycles.some((c) => this.nbEcarts(c) > 0);
  }

  returnToDispositif(): void {
    this._router.navigate(["psdrf/infodispositif", this.id]);
  }
}
