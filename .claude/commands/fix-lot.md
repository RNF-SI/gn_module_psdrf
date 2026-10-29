---
description: Traite un lot d'issues « mêmes fichiers » en séquentiel (un commit par issue, vérifications complètes une seule fois à la fin)
argument-hint: <numéros d'issues du lot, ex: "69 70">
allowed-tools: Bash(gh:*), Bash(git:*), Bash(grep:*), Bash(/home/aschlegel/GeoNature/backend/venv/bin/python:*), Bash(npx tsc:*), Bash(psql:*), Edit, Read, Write, AskUserQuestion
---

Lot à traiter : #$ARGUMENTS

Issues regroupées parce qu'elles touchent les MÊMES fichiers (ou une même
brique, ex. une table partagée) : traitement séquentiel dans une session, un
commit et une trace par issue.

Contexte préchargé :
!`for n in $ARGUMENTS; do echo "===== #$n ====="; gh issue view $n --json title,body,labels,comments,createdAt --jq '"TITRE: \(.title)\nOUVERTE LE: \(.createdAt)\nLABELS: \([.labels[].name]|join(", "))\nBODY:\n\(.body)\nCOMMENTAIRES: \(.comments|length)"'; echo; done`

1. PRÉPARE la session une fois : `git checkout master && git pull --no-recurse-submodules` ;
   lis les fichiers communs du lot ; pour chaque issue, vérifie qu'elle n'est
   pas déjà faite (`git log --all --oneline --grep="#<n>"`). Déjà faite →
   aucun commit, commentaire « ↳ Déjà fait — commit <sha> » + label `à tester`.

2. CLASSE chaque issue (A / B / C, comme /fix-issue) ; le DERNIER commentaire de
   retour de test, s'il existe, définit le travail.

3. ORDONNE le lot pour que les corrections ne se marchent pas dessus (la brique
   partagée — migration, modèle, route — d'abord, dans le commit de la première
   issue qui en a besoin) ; signale les dépendances ; sors les bac C du flux.
   Regroupe tes questions en UN appel AskUserQuestion (cherche d'abord dans le
   code, `~/dendro3` et la doc du sous-module PermPSDRF4py).

   RÉTROCOMPATIBILITÉ DENDRO3 (cf. /fix-issue, étape 2) : vérifiée pour chaque
   issue qui touche une route ou une tâche appelée par l'appli.

4. Pour CHAQUE issue A/B, en boucle :
   a. Plan en une ligne si non trivial.
   b. Bac A : script de vérification (scratchpad) écrit AVANT la correction,
      lancé, vu en ÉCHEC.
   c. Correction (migration Alembic chaînée sur le head `psdrf` si le schéma
      change ; jamais le pointeur du sous-module par accident).
   d. Vérifications CIBLÉES seulement : le script de b + `py_compile` des
      fichiers touchés. PAS de tsc ni de cycle de migration complet à ce stade.
   e. Doc (`CLAUDE.md`, `README.rst`) dans le commit si le comportement décrit change.
   f. Commit atomique `<Zone> : <résumé> (#<n>)` — jamais deux issues dans un commit.
   g. OBLIGATOIRE avant l'issue suivante : `gh issue comment <n>` (résumé +
      « À vérifier ») et `gh issue edit <n> --add-label "à tester"`, vérifiés.
   h. Ne ferme jamais l'issue. Ne pousse pas sans que je le demande.

5. Bac C : questions d'abord ; si l'ambiguïté persiste → commentaire +
   `needs: discussion`, puis issue suivante.

6. FIN DU LOT — la seule passe lourde :
   - `cd ~/GeoNature/frontend && npx tsc --noEmit -p tsconfig.json 2>&1 | grep external_modules/psdrf`
     (vide = OK) si le frontend a bougé ;
   - migration : `geonature db upgrade psdrf@head`, `downgrade psdrf@-1`,
     `upgrade psdrf@head` sur la BDD dev ;
   - tous les scripts de vérification du lot relancés ensemble ;
   - si le carnet est touché : UN test rapide de génération (`CLAUDE.md`).
   Un échec → corrige dans le commit de l'issue responsable (fixup) ou un
   commit dédié qui cite l'issue.

7. RÉCAP en tableau :
   | Issue | Bac | Fichiers | Commit | Script (vu en échec ?) | Doc | Commenté | Statut |
   puis le résultat de la passe de fin, les validations manuelles (bac B) et
   les questions en suspens. ARRÊTE.
