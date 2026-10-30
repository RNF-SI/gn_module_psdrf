import { Component, OnInit } from "@angular/core";
import { Router } from "@angular/router";
import { ToastrService } from "ngx-toastr";
import { PsdrfDataService } from "../../services/route.service";

// Statuts calculés par /dispositifs/completion, du plus urgent au moins urgent.
const STATUTS: { [cle: string]: { libelle: string; aide: string } } = {
  incomplet: {
    libelle: "Incomplet",
    aide: "Des placettes du cycle précédent n'ont pas de relevé au dernier cycle, ni en production ni dans le staging-terrain",
  },
  en_cours: {
    libelle: "Campagne en cours",
    aide: "Une partie des placettes manquantes est déjà dans le staging-terrain (envoyée par Dendro3)",
  },
  a_importer: {
    libelle: "Complet, à importer",
    aide: "Toutes les placettes sont relevées, mais une partie n'est que dans le staging-terrain : à importer en production",
  },
  complet: {
    libelle: "Complet",
    aide: "Toutes les placettes du cycle précédent sont relevées au dernier cycle, en production",
  },
  premier_cycle: {
    libelle: "Premier cycle",
    aide: "Un seul cycle relevé : pas de cycle précédent à comparer",
  },
  aucun_releve: {
    libelle: "Aucun relevé",
    aide: "Aucun relevé de placette, ni en production ni dans le staging-terrain",
  },
};
const ORDRE = Object.keys(STATUTS);

/**
 * Onglet « Complétion » de la page admin (#77) : pour chaque dispositif, part
 * des placettes du cycle précédent relevées au dernier cycle (production, et
 * en plus dans le staging-terrain) et part des arbres retrouvés.
 */
@Component({
  selector: "psdrf-completion-dispositifs",
  templateUrl: "completion-dispositifs.component.html",
  styleUrls: ["completion-dispositifs.component.scss"],
})
export class CompletionDispositifsComponent implements OnInit {
  public lignes: any[] = [];
  public chargement = false;

  public recherche = "";
  public statut = "";
  public avecSansReleve = false;
  public readonly STATUTS = STATUTS;
  public readonly ORDRE = ORDRE;

  constructor(
    private dataSrv: PsdrfDataService,
    private router: Router,
    private toaster: ToastrService
  ) {}

  ngOnInit(): void {
    this.charger();
  }

  charger(): void {
    this.chargement = true;
    this.dataSrv.getCompletionDispositifs().subscribe(
      (lignes) => {
        this.lignes = lignes;
        this.chargement = false;
      },
      () => {
        this.chargement = false;
        this.toaster.error("Impossible de calculer la complétion des dispositifs", "Erreur");
      }
    );
  }

  /** Lignes filtrées, les plus urgentes d'abord puis par taux croissant. */
  get filtrees(): any[] {
    const termes = this.normaliser(this.recherche).split(/\s+/).filter(Boolean);
    return this.lignes
      .filter((l) => this.avecSansReleve || this.statut === "aucun_releve" || l.statut !== "aucun_releve")
      .filter((l) => !this.statut || l.statut === this.statut)
      .filter((l) => {
        const texte = this.normaliser(`${l.nom} n° ${l.id_dispositif}`);
        return termes.every((t) => texte.includes(t));
      })
      .sort(
        (a, b) =>
          ORDRE.indexOf(a.statut) - ORDRE.indexOf(b.statut) ||
          this.taux(a) - this.taux(b) ||
          (a.nom || "").localeCompare(b.nom || "", "fr")
      );
  }

  nbStatut(statut: string): number {
    return this.lignes.filter((l) => l.statut === statut).length;
  }

  get nbCompares(): number {
    return this.lignes.filter((l) => l.cycle_precedent != null).length;
  }

  /** Part des placettes attendues relevées en production (0-100). */
  taux(l: any): number {
    return l.placettes_attendues ? (100 * l.placettes_production) / l.placettes_attendues : 0;
  }

  /** Part supplémentaire relevée dans le staging-terrain (0-100). */
  tauxStaging(l: any): number {
    return l.placettes_attendues ? (100 * l.placettes_staging) / l.placettes_attendues : 0;
  }

  tauxArbres(l: any): number {
    return l.arbres_cycle_precedent ? (100 * l.arbres_retrouves) / l.arbres_cycle_precedent : null;
  }

  filtrerStatut(statut: string): void {
    this.statut = this.statut === statut ? "" : statut;
  }

  reinitialiser(): void {
    this.recherche = "";
    this.statut = "";
  }

  ouvrirDispositif(idDispositif: number): void {
    this.router.navigate(["psdrf/infodispositif", idDispositif]);
  }

  private normaliser(texte: string): string {
    return (texte || "")
      .toLowerCase()
      .normalize("NFD")
      .replace(/[̀-ͯ]/g, "");
  }
}
