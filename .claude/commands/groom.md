---
description: Trie un lot d'issues pour réduire le backlog (ne corrige rien)
argument-hint: <numéros d'issues OU un label, ex: "priorité 4">
allowed-tools: Bash(gh:*), Bash(git log:*), Read
---

Cible à trier : $ARGUMENTS
(si l'argument ressemble à un label, résous d'abord la liste :
`gh issue list --label "$ARGUMENTS" --state open --json number -q '.[].number'`)

Objectif : RÉDUIRE le backlog. Tu ne modifies AUCUN code.

Pour chaque issue :
1. Lis-la : `gh issue view <n> --comments`.
2. Cherche si elle est DÉJÀ résolue sans être fermée :
   - `git log --all --oneline --grep "#<n>"` ;
   - les commits par mots-clés de l'issue (les anciens commits du dépôt ne
     citent pas toujours le numéro) : `git log --oneline -i --grep "<mot-clé>"` ;
   - `gh pr list --search "<n>" --state all` ;
   - attention aux issues antérieures à la bascule R → Python : celles qui
     visent `Rscripts/`, les `.Rnw` ou rpy2 sont probablement OBSOLÈTES, ou à
     reporter sur `RNF-SI/PermPSDRF4py` si le besoin subsiste dans le carnet.
3. Compare les issues du lot entre elles pour repérer les DOUBLONS (le backlog
   en contient : ex. doublon Taillis à l'export régé).

Classe chaque issue dans UNE disposition :
- FERMER — déjà résolue (commit/PR existant).
- DOUBLON #X — recouvre une autre issue.
- OBSOLÈTE — plus pertinente (fonctionnalité supprimée/refondue, chaîne R).
- DÉPLACER — relève de Dendro3 ou de PermPSDRF4py → issue sur l'autre dépôt.
- À TESTER — implémentée, en attente de validation manuelle → label `à tester`.
- DISCUSSION — ambiguë, feature lourde, règle métier à trancher
  → label `needs: discussion` (+ liste les questions précises à trancher).
- À CODER — nette, pas encore faite → label `à corriger` (prête pour /fix-issue).

Rends UNIQUEMENT un tableau (mode proposition, AUCUNE action) :
| Issue | Disposition | Justification (1 ligne) | Commande gh proposée |

Puis ARRÊTE et demande validation. Ne ferme, ne commente, ne ré-étiquette
RIEN tant que je n'ai pas écrit « applique » (en bloc, ou en listant les
numéros à appliquer). Les fermetures DOUBLON/OBSOLÈTE et les déplacements
exigent toujours ma confirmation explicite, jamais en automatique.
