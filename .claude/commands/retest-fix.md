---
description: Reprend une issue après un retour de test KO, en partant du dernier commentaire
argument-hint: <numéro d'issue>
allowed-tools: Bash(gh:*), Bash(git:*), Bash(grep:*), Bash(/home/aschlegel/GeoNature/backend/venv/bin/python:*), Bash(npx tsc:*), Bash(psql:*), Edit, Read, Write, AskUserQuestion
---

Issue à reprendre : #$ARGUMENTS

Contexte :
!`gh issue view $ARGUMENTS --json title,body,labels,comments`

1. Le DERNIER commentaire de retour est ta LISTE DE TRAVAIL. Décompose-le en
   points distincts et liste-les. Pour chacun : à corriger ici / déjà couvert /
   hors périmètre (→ nouvelle issue, pas noyée ici ; sur `RNF-SI/dendro3` ou
   `RNF-SI/PermPSDRF4py` si c'est là que ça se corrige). Les « ↳ Fait » disent
   ce qui a déjà été tenté.
   Les captures du commentaire : télécharge-les et regarde-les.
2. Retour flou ou non reproductible → AskUserQuestion d'abord. Doute levé →
   continue ; sinon commente une demande de précision et ARRÊTE.
3. `git checkout master && git pull --no-recurse-submodules`.
4. Script de vérification (scratchpad) qui couvre CE cas précis, écrit
   d'abord, lancé, vu en ÉCHEC. Puis corrige.
5. Vérifications ciblées : le script de l'étape 4, `py_compile` des fichiers
   touchés, `npx tsc` (cf. /fix-issue) si le frontend a bougé, cycle
   upgrade/downgrade si une migration change. Régénération de carnet seulement
   si le retour porte sur le carnet. Doc (`CLAUDE.md`, `README.rst`) si le
   comportement décrit change.
6. Commit atomique `<Zone> : <nouveau symptôme> (#$ARGUMENTS)`.
7. `gh issue comment` (ce qui était KO, ce qui change, « À vérifier ») puis
   `gh issue edit $ARGUMENTS --remove-label "à corriger" --add-label "à tester"`.
   Vérifie les deux. Ne ferme pas. Hors périmètre → propose une issue dédiée.
8. Récap : KO, correction, script (vu en échec ?), vérifications lancées,
   migration, doc, questions, commentaire posté.
