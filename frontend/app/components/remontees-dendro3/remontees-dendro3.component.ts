import { Component, OnInit } from "@angular/core";
import { Router } from "@angular/router";
import { ToastrService } from "ngx-toastr";
import { PsdrfDataService } from "../../services/route.service";
import { libelleStatutExport, resumePlacettes, totalModifications } from "../dendro3-exports.utils";

const TAILLE_PAGE = 25;

/**
 * Onglet « Remontées Dendro3 » de la page admin (#69, #75) : chiffres clés,
 * recherche, graphiques de suivi et journal des envois.
 */
@Component({
  selector: "psdrf-remontees-dendro3",
  templateUrl: "remontees-dendro3.component.html",
  styleUrls: ["remontees-dendro3.component.scss"],
})
export class RemonteesDendro3Component implements OnInit {
  public exports: any[] = [];
  public chargement = false;

  // Filtres : texte libre (dispositif, n°, appareil, placette) et statut.
  public recherche = "";
  public statut = "";
  public readonly STATUTS = ["succes", "echec", "en_cours", "archive"];
  public nbAffiches = TAILLE_PAGE;

  public libelleStatutExport = libelleStatutExport;
  public resumePlacettes = resumePlacettes;
  public totalModifications = totalModifications;

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
    this.dataSrv.getDendro3Exports(500).subscribe(
      (exports) => {
        this.exports = exports;
        this.chargement = false;
      },
      () => {
        this.chargement = false;
        this.toaster.error("Impossible de charger les remontées Dendro3", "Erreur");
      }
    );
  }

  /** Envois correspondant à la recherche et au statut choisis. */
  get filtres(): any[] {
    const termes = this.normaliser(this.recherche).split(/\s+/).filter(Boolean);
    return this.exports.filter((e) => {
      if (this.statut && e.statut !== this.statut) {
        return false;
      }
      if (!termes.length) {
        return true;
      }
      const texte = this.normaliser(
        [e.nom_dispositif, `n° ${e.id_dispositif}`, e.device, resumePlacettes(e)].join(" ")
      );
      return termes.every((t) => texte.includes(t));
    });
  }

  get affiches(): any[] {
    return this.filtres.slice(0, this.nbAffiches);
  }

  // Chiffres clés, calculés sur les envois filtrés.
  get nbDispositifs(): number {
    return new Set(this.filtres.map((e) => e.id_dispositif)).size;
  }

  get nbEchecs(): number {
    return this.filtres.filter((e) => e.statut === "echec").length;
  }

  get dernier(): any {
    return this.filtres[0] || null;
  }

  get filtreActif(): boolean {
    return !!(this.recherche.trim() || this.statut);
  }

  reinitialiser(): void {
    this.recherche = "";
    this.statut = "";
    this.nbAffiches = TAILLE_PAGE;
  }

  afficherPlus(): void {
    this.nbAffiches += TAILLE_PAGE;
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
