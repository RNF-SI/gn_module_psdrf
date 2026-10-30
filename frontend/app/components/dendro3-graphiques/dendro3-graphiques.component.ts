import { Component, Input, OnChanges } from "@angular/core";
import { ChartConfiguration } from "chart.js";
import { PsdrfDataService } from "../../services/route.service";
import { libelleStatutExport } from "../dendro3-exports.utils";

// Une teinte par statut, toujours la même (palette catégorielle validée pour
// les daltonismes dans cet ordre d'empilement). Le statut est aussi porté par
// la légende et l'infobulle, jamais par la couleur seule.
const COULEURS_STATUT: { [statut: string]: string } = {
  archive: "#2a78d6",
  echec: "#eb6834",
  succes: "#1baf7a",
  en_cours: "#eda100",
};
// Série unique (nombre d'envois / de lignes) : teinte absente des statuts.
const COULEUR_SERIE = "#6250d6";
const ENCRE_SECONDAIRE = "#52514e";
const GRILLE = "#e8e7e3";

/**
 * Graphiques de suivi des envois Dendro3 (#75), à partir des agrégats de
 * /dendro3/statistiques : sans `idDispositif`, vue globale (page admin) ;
 * avec, vue d'un dispositif (fiche).
 */
@Component({
  selector: "psdrf-dendro3-graphiques",
  templateUrl: "dendro3-graphiques.component.html",
  styleUrls: ["dendro3-graphiques.component.scss"],
})
export class Dendro3GraphiquesComponent implements OnChanges {
  @Input() idDispositif: number = null;

  public chargement = false;
  public stats: any = null;

  public envoisParMois: ChartConfiguration<"bar">["data"] = null;
  public modificationsParMois: ChartConfiguration<"bar">["data"] = null;
  public envoisParDispositif: ChartConfiguration<"bar">["data"] = null;
  public envoisParAppareil: ChartConfiguration<"bar">["data"] = null;

  public optionsEmpilees = this.options({ empile: true, legende: true });
  public optionsVerticales = this.options({});
  public optionsHorizontales = this.options({ horizontal: true });

  constructor(private dataSrv: PsdrfDataService) {}

  ngOnChanges(): void {
    this.charger();
  }

  charger(): void {
    this.chargement = true;
    this.dataSrv.getStatistiquesDendro3(this.idDispositif).subscribe(
      (stats) => {
        this.stats = stats;
        this.construire(stats);
        this.chargement = false;
      },
      () => {
        this.stats = null;
        this.chargement = false;
      }
    );
  }

  /** Hauteur d'un graphique en barres horizontales : une ligne par barre. */
  hauteurHorizontale(nb: number): number {
    return Math.max(120, nb * 26 + 40);
  }

  private construire(stats: any): void {
    const mois = stats.par_mois || [];
    const libellesMois = mois.map((m) => this.libelleMois(m.mois));
    // Seuls les statuts présents ont une série, chacun gardant sa couleur.
    const statuts = Object.keys(COULEURS_STATUT).filter((s) => mois.some((m) => m[s]));
    this.envoisParMois = {
      labels: libellesMois,
      datasets: statuts.map((s) => ({
        ...this.barres(COULEURS_STATUT[s]),
        label: libelleStatutExport(s),
        data: mois.map((m) => m[s]),
      })),
    };
    this.modificationsParMois = {
      labels: libellesMois,
      datasets: [{ ...this.barres(COULEUR_SERIE), label: "Lignes envoyées", data: mois.map((m) => m.modifications) }],
    };
    const dispositifs = stats.par_dispositif || [];
    this.envoisParDispositif = {
      labels: dispositifs.map((d) => d.nom_dispositif || `Dispositif ${d.id_dispositif}`),
      datasets: [{ ...this.barres(COULEUR_SERIE), label: "Envois", data: dispositifs.map((d) => d.envois) }],
    };
    const appareils = stats.par_appareil || [];
    this.envoisParAppareil = {
      labels: appareils.map((a) => a.appareil),
      datasets: [{ ...this.barres(COULEUR_SERIE), label: "Envois", data: appareils.map((a) => a.envois) }],
    };
  }

  private barres(couleur: string) {
    // Liseré clair : sépare les segments empilés et les barres voisines.
    return {
      backgroundColor: couleur,
      hoverBackgroundColor: couleur,
      borderColor: "#ffffff",
      borderWidth: 1,
      borderRadius: 4,
      maxBarThickness: 28,
    };
  }

  private libelleMois(mois: string): string {
    const [annee, num] = mois.split("-").map(Number);
    return new Date(annee, num - 1, 1).toLocaleDateString("fr-FR", { month: "short", year: "numeric" });
  }

  private options({ empile = false, legende = false, horizontal = false }): ChartConfiguration<"bar">["options"] {
    const axeValeurs = {
      beginAtZero: true,
      stacked: empile,
      grid: { color: GRILLE },
      border: { display: false },
      ticks: { color: ENCRE_SECONDAIRE, precision: 0 },
    };
    const axeCategories = {
      stacked: empile,
      grid: { display: false },
      ticks: { color: ENCRE_SECONDAIRE, autoSkip: !horizontal },
    };
    return {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: horizontal ? "y" : "x",
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { display: legende, position: "bottom", labels: { color: ENCRE_SECONDAIRE, boxWidth: 12 } },
        tooltip: { enabled: true },
      },
      scales: horizontal ? { x: axeValeurs, y: axeCategories } : { x: axeCategories, y: axeValeurs },
    } as ChartConfiguration<"bar">["options"];
  }
}
