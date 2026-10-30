Module destiné à la gestion des données du PSDRF
================================================

Ce module GeoNature gère les données du Protocole de Suivi Dendrométrique des
Réserves Forestières (PSDRF) et génère, en **Python pur**, le carnet d'analyse et
le plan des arbres (le pipeline de calcul vit dans le sous-module
``PermPSDRF4py``). Plus aucune dépendance à R.

Prérequis
---------

* **LaTeX / pdflatex** : requis pour compiler les PDF (carnet, plan des arbres).
* **Sous-module ``PermPSDRF4py``** : le pipeline de calcul Python, intégré en
  sous-module git. Il doit être récupéré avant l'installation.
* Dépendances Python (pandas, numpy, scipy, matplotlib, jinja2, openpyxl) :
  installées automatiquement par ``geonature install_gn_module``.

Installer le module
-------------------

Récupérer le code **avec le sous-module** :

``git clone --recurse-submodules <url_du_module>``

Si le dépôt est déjà cloné sans le sous-module :

``git submodule update --init --recursive``

Installer les dépendances système (LaTeX) et le sous-module :

``bash install_env.sh``

Se placer dans le répertoire backend de GeoNature, activer le virtualenv, puis
lancer l'installation du module :

``source venv/bin/activate``

``geonature install_gn_module /home/<MON_CHEMIN_ABSOLU_VERS_LE_MODULE>/ /cmr``

Première mise en service (IMPORTANT)
------------------------------------

Après l'installation, **avant de pouvoir générer un carnet ou un plan des
arbres**, il faut charger le référentiel administrateur :

1. **Charger PsdrfListes** via la page d'administration du module
   (route ``/psdrfListe``). Cet upload :

   * enregistre ``PsdrfListes.xlsx`` dans ``media/psdrf/data/`` ;
   * crée/maj les **Dispositifs** et **Cycles** en base ;
   * met à jour le code écologique (nomenclature ``PSDRF_ECOLOGIE``) ;
   * génère ``media/psdrf/data/tables/psdrfCodes.pkl`` (les référentiels lus à la
     génération : essences, tarifs, regroupements, catégories de diamètre…).

   Tant que cet upload n'a pas été fait, la génération s'arrête avec un message
   explicite (« Référentiel introuvable… Charger d'abord PsdrfListes via
   /psdrfListe »). **Aucun fichier n'est à copier à la main** : tout passe par
   cet upload.

2. **Nomenclatures** : ``PSDRF_DURETE`` et ``PSDRF_ECORCE`` (stades de dureté /
   écorce) sont créées à l'installation du module (migrations) ; rien à faire.
   ``PSDRF_ECOLOGIE`` est alimentée par l'upload PsdrfListes ci-dessus.

3. **Ajouter un dispositif** : un dispositif doit figurer dans PsdrfListes
   (onglets ``Cycles``, ``Tarifs``, ``EssReg``, ``Cat``) **avant** de générer son
   carnet, sinon les volumes seront faux ou la génération échouera. Compléter
   ``PsdrfListes.xlsx`` puis le ré-uploader via ``/psdrfListe``.

Mises à jour
------------

* **Données / référentiels** (nouveau dispositif, tarifs, essences…) :
  ré-uploader ``PsdrfListes`` via ``/psdrfListe``. ``psdrfCodes.pkl`` est
  régénéré automatiquement.
* **Pipeline de calcul** (sous-module ``PermPSDRF4py``) : les évolutions se font
  dans le dépôt ``RNF-SI/PermPSDRF4py``, puis on met à jour le pointeur de
  sous-module ::

      cd backend/gn_module_psdrf/PermPSDRF4py && git pull origin main
      cd - && git add backend/gn_module_psdrf/PermPSDRF4py
      git commit -m "Maj sous-module PermPSDRF4py"

Déployer une nouvelle version du module
---------------------------------------

Sur le serveur, avec l'utilisateur propriétaire de GeoNature et le venv activé ::

    cd <chemin>/gn_module_psdrf
    git pull --no-recurse-submodules        # le sous-module privé ferait échouer un pull nu
    cd <chemin>/geonature
    geonature db upgrade psdrf@head         # si le commit apporte une migration
    cd frontend && nvm use
    nohup npm run build > ~/build.log 2>&1 &    # si le frontend du module a changé
    tail -f ~/build.log                         # attendre « Build at: … »
    sudo systemctl restart geonature geonature-worker

* **Build du frontend** : il recompile tout GeoNature et demande **2 à 3 Go de
  RAM libre**. Avec 4 Go au total, le serveur sature (ssh qui ne répond plus,
  build tué sans message, dossier ``frontend/dist`` absent → interface web
  cassée). Prévoir au moins 6 Go, ou arrêter ``geonature-worker`` pendant le
  build. Le lancer avec ``nohup`` (ou ``tmux``) : une coupure ssh ne l'interrompt
  pas. Un build qui aboutit affiche « Build at: … » et recrée ``frontend/dist``.
* **Worker Celery** : à redémarrer dès que ``tasks.py`` ou ce qu'il appelle
  change (exports Dendro3, génération du carnet).
* **Migrations** : les tables ``pr_psdrf*`` doivent appartenir au rôle de
  GeoNature (cf. ``CLAUDE.md``).

Suivi des remontées Dendro3
---------------------------

Chaque export reçu de Dendro3 est :

* **archivé tel quel** dans
  ``backend/gn_module_psdrf/debug_data/<id_dispositif>/<AAAAMMJJ_HHMMSS>.json``
  (hors git ; **ne pas purger** : c'est l'historique brut des envois) ;
* **journalisé** dans ``pr_psdrf_staging.t_dendro3_exports`` (statut,
  placettes et cycles touchés, appareil), affiché dans la page admin (onglet
  « Remontées Dendro3 », avec graphiques) et sur la fiche de chaque dispositif.

Le journal ne couvre que les envois reçus depuis sa mise en place. Pour y
reprendre les envois archivés auparavant (statut « Archive », relançable sans
doublon) ::

    geonature psdrf reprendre-archives-dendro3 --simulation   # compte sans écrire
    geonature psdrf reprendre-archives-dendro3

Avant le journal (et pour les campagnes terminées avant le changement de
serveur de juin 2026, dont les archives sont perdues), l'onglet et les fiches
montrent aussi les **saisies sur tablette** : horodatages conservés dans les
tables staging (depuis 2024), indépendants des envois.

``--dossier <chemin>`` permet de reprendre les archives d'un ancien serveur.
Les noms de fichiers sont horodatés dans le fuseau du processus gunicorn (UTC
en prod) : ``--fuseau`` (défaut ``UTC``) si ce n'est pas le cas. Relancer la
commande met à jour les lignes « Archive » déjà créées.

Tests
-----

``python -m pytest`` (depuis la racine du module, dans le venv GeoNature) lance
les tests de non-régression du pont (transformations BDD → pipeline).

Documentation
-------------

* Architecture du module : ``CLAUDE.md``.
* Pipeline de calcul / carnet : documentation du sous-module
  ``backend/gn_module_psdrf/PermPSDRF4py`` (``CLAUDE.md``,
  ``docs/contrat_donnees_carnet.md``).
* Documentation utilisateur (à venir).
