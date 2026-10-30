import { Component, Input, OnChanges, OnInit, SimpleChanges } from "@angular/core";
import { ChartConfiguration } from "chart.js";
import { PsdrfDataService } from "../../services/route.service";
import { libelleStatutExport } from "../dendro3-exports.utils";

// Couleurs tirées de la palette du module (vert sapin, vert clair, brique,
// ocre, brun). Une teinte par statut, toujours la même ; l'ordre d'empilement
// archive / échec / réussi / en cours est validé pour les daltonismes. Le
// statut est aussi porté par la légende et l'infobulle.
const COULEURS_STATUT: { [statut: string]: string } = {
  archive: "#8AAC3E",
  echec: "#A8322A",
  succes: "#178F6A",
  en_cours: "#BE7600",
};
// Séries uniques : vert sapin pour les envois, brun pour les saisies terrain.
const COULEUR_ENVOIS = "#598979";
const COULEUR_SAISIES = "#8B5500";
const ENCRE_SECONDAIRE = "#5d6660";
const GRILLE = "#ece8da";

/**
 * Graphiques de suivi Dendro3 (#75, #76) : envois (journal, agrégats de
 * /dendro3/statistiques) et saisies sur tablette (/dendro3/activite-terrain).
 * Sans `idDispositif`, vue globale (page admin) ; avec, vue d'un dispositif
 * (fiche). `recherche` filtre les classements par dispositif / appareil.
 */
@Component({
  selector: "psdrf-dendro3-graphiques",
  templateUrl: "dendro3-graphiques.component.html",
  styleUrls: ["dendro3-graphiques.component.scss"],
})
export class Dendro3GraphiquesComponent implements OnInit, OnChanges {
  @Input() idDispositif: number = null;
  @Input() recherche = "";

  public chargement = false;
  public stats: any = null;
  public activite: any = null;

  public envoisParMois: ChartConfiguration<"bar">["data"] = null;
  public modificationsParMois: ChartConfiguration<"bar">["data"] = null;
  public envoisParDispositif: ChartConfiguration<"bar">["data"] = null;
  public envoisParAppareil: ChartConfiguration<"bar">["data"] = null;
  public saisiesParMois: ChartConfiguration<"bar">["data"] = null;
  public saisiesParDispositif: ChartConfiguration<"bar">["data"] = null;

  public optionsEmpilees = this.options({ empile: true, legende: true });
  public optionsVerticales = this.options({});
  public optionsHorizontales = this.options({ horizontal: true });
  public optionsSaisiesParDispositif = this.options({ horizontal: true });

  constructor(private dataSrv: PsdrfDataService) {}

  // Chargement au démarrage : ngOnChanges n'est appelé que si une entrée est
  // liée, ce qui n'est pas le cas dans la page admin.
  ngOnInit(): void {
    this.charger();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes.idDispositif && !changes.idDispositif.firstChange) {
      this.charger();
    } else if (changes.recherche && !changes.recherche.firstChange) {
      this.construireClassements();
    }
  }

  charger(): void {
    this.chargement = true;
    this.dataSrv.getStatistiquesDendro3(this.idDispositif).subscribe(
      (stats) => {
        this.stats = stats;
        this.construireEnvois();
        this.construireClassements();
        this.chargement = false;
      },
      () => {
        this.stats = null;
        this.chargement = false;
      }
    );
    this.dataSrv.getActiviteTerrainDendro3(this.idDispositif).subscribe(
      (activite) => {
        this.activite = activite;
        this.construireSaisies();
        this.construireClassements();
      },
      () => (this.activite = null)
    );
  }

  get vueGlobale(): boolean {
    return this.idDispositif == null;
  }

  /** Hauteur d'un graphique en barres horizontales : une ligne par barre. */
  hauteurHorizontale(data: ChartConfiguration<"bar">["data"]): number {
    return Math.max(120, ((data && data.labels.length) || 0) * 26 + 40);
  }

  nbBarres(data: ChartConfiguration<"bar">["data"]): number {
    return (data && data.labels.length) || 0;
  }

  private construireEnvois(): void {
    const mois = this.stats.par_mois || [];
    const libelles = mois.map((m) => this.libelleMois(m.mois));
    // Seuls les statuts présents ont une série, chacun gardant sa couleur.
    const statuts = Object.keys(COULEURS_STATUT).filter((s) => mois.some((m) => m[s]));
    this.envoisParMois = {
      labels: libelles,
      datasets: statuts.map((s) => ({
        ...this.barres(COULEURS_STATUT[s]),
        label: libelleStatutExport(s),
        data: mois.map((m) => m[s]),
      })),
    };
    this.modificationsParMois = {
      labels: libelles,
      datasets: [{ ...this.barres(COULEUR_ENVOIS), label: "Lignes envoyées", data: mois.map((m) => m.modifications) }],
    };
  }

  private construireSaisies(): void {
    const mois = this.activite.par_mois || [];
    this.saisiesParMois = {
      labels: mois.map((m) => this.libelleMois(m.mois)),
      datasets: [{ ...this.barres(COULEUR_SAISIES), label: "Saisies", data: mois.map((m) => m.total) }],
    };
  }

  /** Classements par dispositif / appareil, restreints par la recherche. */
  private construireClassements(): void {
    if (this.stats) {
      const dispositifs = (this.stats.par_dispositif || []).filter((d) =>
        this.correspond(d.nom_dispositif, `n° ${d.id_dispositif}`)
      );
      this.envoisParDispositif = {
        labels: dispositifs.map((d) => d.nom_dispositif || `Dispositif ${d.id_dispositif}`),
        datasets: [{ ...this.barres(COULEUR_ENVOIS), label: "Envois", data: dispositifs.map((d) => d.envois) }],
      };
      const appareils = (this.stats.par_appareil || []).filter((a) => this.correspond(a.appareil));
      this.envoisParAppareil = {
        labels: appareils.map((a) => a.appareil),
        datasets: [{ ...this.barres(COULEUR_ENVOIS), label: "Envois", data: appareils.map((a) => a.envois) }],
      };
    }
    if (this.activite) {
      const dispositifs = (this.activite.par_dispositif || []).filter((d) =>
        this.correspond(d.nom_dispositif, `n° ${d.id_dispositif}`)
      );
      this.saisiesParDispositif = {
        labels: dispositifs.map((d) => d.nom_dispositif || `Dispositif ${d.id_dispositif}`),
        datasets: [{ ...this.barres(COULEUR_SAISIES), label: "Saisies", data: dispositifs.map((d) => d.saisies) }],
      };
      // Infobulle : période d'activité du dispositif.
      const options: any = this.options({ horizontal: true });
      options.plugins.tooltip.callbacks = {
        afterLabel: (ctx) => {
          const d = dispositifs[ctx.dataIndex];
          return d.premier === d.dernier
            ? this.libelleMois(d.premier)
            : `${this.libelleMois(d.premier)} → ${this.libelleMois(d.dernier)}`;
        },
      };
      this.optionsSaisiesParDispositif = options;
    }
  }

  private correspond(...champs: string[]): boolean {
    const termes = this.normaliser(this.recherche).split(/\s+/).filter(Boolean);
    const texte = this.normaliser(champs.filter(Boolean).join(" "));
    return termes.every((t) => texte.includes(t));
  }

  private normaliser(texte: string): string {
    return (texte || "")
      .toLowerCase()
      .normalize("NFD")
      .replace(/[̀-ͯ]/g, "");
  }

  private barres(couleur: string) {
    // Liseré blanc : sépare les segments empilés et les barres voisines.
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
        legend: {
          display: legende,
          position: "bottom",
          labels: { color: ENCRE_SECONDAIRE, boxWidth: 12, usePointStyle: true, pointStyle: "rectRounded" },
        },
        tooltip: {
          enabled: true,
          backgroundColor: "#1a1a18",
          padding: 10,
          cornerRadius: 6,
          boxPadding: 4,
        },
      },
      scales: horizontal ? { x: axeValeurs, y: axeCategories } : { x: axeCategories, y: axeValeurs },
    } as ChartConfiguration<"bar">["options"];
  }
}
