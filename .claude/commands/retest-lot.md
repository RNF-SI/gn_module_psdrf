---
description: Reprend un lot d'issues après retour de test KO, chacune depuis son dernier commentaire (un commit par issue)
argument-hint: <numéros d'issues du lot, ex: "69 70">
allowed-tools: Bash(gh:*), Bash(git:*), Bash(grep:*), Bash(/home/aschlegel/GeoNature/backend/venv/bin/python:*), Bash(npx tsc:*), Bash(psql:*), Edit, Read, Write, AskUserQuestion
---

Lot à reprendre après retour KO : #$ARGUMENTS

Pour CHAQUE issue, c'est le DERNIER commentaire (pas le body) qui définit le
travail. Un commit et une trace par issue.

Contexte préchargé :
!`for n in $ARGUMENTS; do echo "===== #$n ====="; gh issue view $n --json title,labels,comments --jq '"TITRE: \(.title)\nLABELS: \([.labels[].name]|join(", "))\nDERNIER COMMENTAIRE:\n\(.comments[-1].author.login // "—"): \(.comments[-1].body // "(aucun commentaire)")"'; echo; done`

1. Une fois : `git checkout master && git pull --no-recurse-submodules` ;
   captures des derniers commentaires téléchargées et regardées ; fichiers
   visés lus.
2. Par issue : décompose le dernier commentaire en points (à corriger ici /
   déjà couvert / hors périmètre → nouvelle issue, ici ou sur Dendro3 /
   PermPSDRF4py).
3. Ordonne le lot ; sors les retours flous ; regroupe les questions en UN
   appel AskUserQuestion.
4. Pour chaque issue : points annoncés en une ligne → script du cas KO écrit
   d'abord et vu en ÉCHEC → correction → vérifications CIBLÉES (script +
   `py_compile`) → doc si besoin → commit `<Zone> : <nouveau symptôme> (#<n>)`
   → `gh issue comment` + `--remove-label "à corriger" --add-label "à tester"`,
   vérifiés, AVANT l'issue suivante. Jamais de fermeture. Hors périmètre →
   `gh issue create`, référencée dans le commentaire.
5. Retour trop flou : question d'abord ; sinon demande de précision en
   commentaire, label `à corriger` laissé, issue suivante.
6. FIN DU LOT, une seule fois : `npx tsc` (cf. /fix-issue) si le frontend a
   bougé, cycle upgrade/downgrade/upgrade si une migration a changé, scripts
   du lot relancés ensemble, régénération de carnet si le carnet est touché.
7. RÉCAP :
   | Issue | Ce qui était KO | Fichiers | Commit | Script (vu en échec ?) | Doc | Commenté | Hors-périmètre → issue |
   puis passe de fin, questions en suspens, issues créées. ARRÊTE.
