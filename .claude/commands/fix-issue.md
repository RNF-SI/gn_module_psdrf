---
description: Traite une issue GitHub de bout en bout (classe, corrige, vérifie, commente)
argument-hint: <numéro d'issue>
allowed-tools: Bash(gh:*), Bash(git:*), Bash(grep:*), Bash(/home/aschlegel/GeoNature/backend/venv/bin/python:*), Bash(npx tsc:*), Bash(psql:*), Edit, Read, Write, AskUserQuestion
---

Issue à traiter : #$ARGUMENTS

Contexte préchargé :
!`gh issue view $ARGUMENTS --json title,body,labels,comments,createdAt`

Repères (cf. `CLAUDE.md`) :
- runtime GeoNature de dev : `/home/aschlegel/GeoNature/backend` (venv
  `venv/bin/python`, `create_app()` + `app.app_context()`) ;
- BDD dev : Postgres hôte `127.0.0.1:5433`, base `geonature2db`, rôle
  `geonatadmin` (accès réseau : hors sandbox) ;
- app mobile Dendro3 : `~/dendro3` (Flutter) ; pipeline carnet : sous-module
  `backend/gn_module_psdrf/PermPSDRF4py` (lecture seule ici).

Procédure :

0. VÉRIFIE D'ABORD QUE CE N'EST PAS DÉJÀ FAIT :
   `git log --all --oneline --grep="#$ARGUMENTS"`, puis les commits postérieurs
   à l'ouverture (`createdAt`) sur les fichiers probablement concernés.
   Déjà fait → AUCUN commit : vérifie le comportement, puis passe à l'étape 7
   avec « ↳ Déjà fait — commit <sha> » et ce que tu as vérifié.

1. CLASSE l'issue :
   - A = vérifiable par un script : route Flask, requête SQL, tâche Celery,
     validation Excel, sortie du pipeline (ZIP, PDF, pickles) ;
   - B = visuel : mise en page Angular, carte, libellés, parcours dans l'UI ;
     validation à l'œil dans GeoNature ;
   - C = ambigu, trop large, décision métier PSDRF, ou `needs: discussion`.
   S'il y a des commentaires de retour de test, le DERNIER définit le travail
   à faire (l'historique = contexte).

2. POSE-MOI DES QUESTIONS (AskUserQuestion) dès qu'un choix change le résultat :
   deux lectures possibles, règle métier du protocole (ne JAMAIS assouplir une
   validation de `data_verification.py` sur un indice code-level), écart avec
   Dendro3, bug non reproductible. Cherche d'abord dans le code, l'historique,
   Dendro3 (`~/dendro3`) et la doc du sous-module ; ne me demande que ce
   qu'ils ne disent pas.
   - Bac C : ne corrige pas avant mes réponses. Ambiguïté levée → reclasse A/B.
     Sinon → commente tes questions sur l'issue, pose `needs: discussion`, ARRÊTE.
   - La correction relève de Dendro3 ou de PermPSDRF4py → ne modifie pas ce
     dépôt-là : propose une issue sur `RNF-SI/dendro3` / `RNF-SI/PermPSDRF4py`.

3. Travaille sur `master` : `git checkout master && git pull --no-recurse-submodules`.
   Ne committe jamais le pointeur du sous-module sans raison.

4. Plan court (fichiers + approche) si la correction n'est pas triviale.
   Schéma BDD modifié → migration Alembic dans `backend/gn_module_psdrf/migrations/`
   (chaînée sur le head `psdrf`), appliquée par `geonature db upgrade psdrf@head`,
   JAMAIS `alembic` en direct.

5. Bac A : ÉCRIS LE SCRIPT DE VÉRIFICATION AVANT LA CORRECTION (scratchpad, pas
   dans le dépôt : il n'y a pas de suite pytest) et lance-le : il doit ÉCHOUER
   pour la bonne raison. S'il passe déjà → le bug est ailleurs, ou déjà corrigé
   (étape 0). Puis corrige. Données de test en BDD dev : nettoie ce que tu crées.

6. VÉRIFICATIONS — BUDGET CIBLÉ :
   - le script de l'étape 5 ;
   - `python -m py_compile <fichiers .py modifiés>` ;
   - frontend modifié → `cd ~/GeoNature/frontend && npx tsc --noEmit -p tsconfig.json 2>&1 | grep external_modules/psdrf`
     (sortie vide = OK ; les templates HTML ne sont pas vérifiés : relis-les) ;
   - migration → `geonature db upgrade psdrf@head` puis `downgrade psdrf@-1`
     puis `upgrade` à nouveau sur la BDD dev ;
   - carnet touché → test rapide de génération (`CLAUDE.md`, section Test rapide).
   - Bac B : décris la validation manuelle dans le commentaire (étape 7).
   - DOC : si le comportement décrit change, mets à jour dans le même commit
     `CLAUDE.md` / `README.rst`. Sinon note « doc : RAS » dans le récap.

7. Commit atomique, au style du dépôt : `<Zone> : <résumé> (#$ARGUMENTS)`
   (ex. `Fiche dispositif : … (#68)`), doc comprise. Puis, OBLIGATOIRE et vérifié :
   a. `gh issue comment $ARGUMENTS --body "..."` : résumé + section
      « À vérifier » (dispositif à utiliser, étapes dans GeoNature, migration
      à passer en prod le cas échéant) ;
   b. `gh issue edit $ARGUMENTS --add-label "à tester"`.
   Ne FERME JAMAIS l'issue. Ne pousse pas sans que je le demande.

8. Récap compact : bac ; fichiers ; script (vu en échec : oui/non) ; autres
   vérifications ; migration ; doc ; questions posées ; confirmation que le
   commentaire est posté.
