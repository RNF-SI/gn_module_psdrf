// Mise en forme des lignes du journal des exports Dendro3
// (routes /dendro3/exports et /dispositif/<id>/dendro3).

const LIBELLES_STATUT: { [statut: string]: string } = {
  succes: "Réussi",
  echec: "Échec",
  en_cours: "En cours",
};

export function libelleStatutExport(statut: string): string {
  return LIBELLES_STATUT[statut] || statut;
}

/** Total des créations / modifications / suppressions d'un export réussi. */
export function totalModifications(exportDendro3: any): number {
  const compteurs = exportDendro3.compteurs || {};
  let total = 0;
  Object.keys(compteurs).forEach((entite) => {
    ["created", "updated", "deleted"].forEach((cat) => {
      total += compteurs[entite][cat] || 0;
    });
  });
  return total;
}

/** « 12, 14, 15 (cycle 2) » : placettes touchées et cycles concernés. */
export function resumePlacettes(exportDendro3: any): string {
  const placettes: any[] = exportDendro3.placettes || [];
  if (!placettes.length) {
    return "aucune modification";
  }
  const cycles = new Set<number>();
  placettes.forEach((p) => (p.cycles || []).forEach((c) => cycles.add(c)));
  const nums = placettes.map((p) => p.num_placette).join(", ");
  const listeCycles = Array.from(cycles).sort((a, b) => a - b);
  if (!listeCycles.length) {
    return nums;
  }
  return `${nums} (cycle${listeCycles.length > 1 ? "s" : ""} ${listeCycles.join(", ")})`;
}
