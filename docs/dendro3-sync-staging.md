# Synchronisation dendro3 ↔ staging PSDRF — contrat backend

Mise en œuvre des 3 briques décrites dans
`dendro3/docs/prompt-psdrf-reprise-staging.md` : pull fusionné prod + staging,
traçabilité appareil/utilisateur, état des placettes.

## Fichiers créés / modifiés

| Fichier | Nature | Rôle |
|---|---|---|
| `pr_psdrf_staging_functions/merge_prod_staging.py` | **créé** | Fusion par id (prod ∪ staging-override) d'un dispositif sérialisé. Fonction pure, testée hors BDD. |
| `migrations/b2c3d4e5f6a7_create_dendro3_sync_log.py` | **créé** | Crée `pr_psdrf_staging.t_dendro3_sync_log` (+ index `(id_dispositif, id_placette)`). down_revision = `a1b2c3d4e5f6`. |
| `pr_psdrf_staging_functions/models_staging.py` | modifié | Ajout du modèle `TDendro3SyncLog`. |
| `tasks.py` | modifié | Helper `_query_dispositif_prod`, nouvelle tâche `fetch_dispositif_data_merged`, écriture du log dans `insert_or_update_data` (lecture `device`/`id_role`). |
| `blueprint.py` | modifié | 3 routes pull fusionné + route d'état des placettes ; docstring export. |

Aucune route ni tâche existante n'a changé de contrat (compat conservée).

> Migration : `alembic upgrade head` (le schéma `pr_psdrf_staging` est garanti par
> un `CREATE SCHEMA IF NOT EXISTS` ; la table de log n'a aucune FK vers les tables
> miroir staging, elle est donc autonome).

---

## Brique 1 — Pull fusionné (reprise/continuation de saisie)

Même patron asynchrone et **même format de réponse** que `/dispositif-complet`.

| Étape | Méthode & chemin | Réponse |
|---|---|---|
| Lancer | `GET /psdrf/dispositif-complet-staging/<int:id_dispositif>` | `202` `{ "task_id": "<id>" }` |
| Statut | `GET /psdrf/dispositif-complet-staging/status/<task_id>` | `202` `{ "state": "PENDING"\|"STARTED" }` · `200` `{ "state": "SUCCESS" }` · `500` `{ "state": "FAILURE", "error": "…" }` |
| Résultat | `GET /psdrf/dispositif-complet-staging/result/<task_id>` | `200` `{ "status": "SUCCESS", "data": <dispositif complet fusionné> }` · `202` (pas fini) · `500` (erreur) |

`data` a **strictement la même structure** que `/psdrf/dispositif-complet/result/<task_id>`
(clés `placettes` → `arbres` → `arbres_mesures`, `bmsSup30` → `bm_sup_30_mesures`,
`reperes` ; `cycles` → `corCyclesPlacettes` → `regenerations`, `transects`).
→ même mapper et même insert local côté app.

**Règle de fusion** (par `id`, à chaque niveau) :
- entité en prod **et** staging → la version **staging écrase** la prod (champ à champ), enfants fusionnés récursivement ;
- entité en prod seule → conservée (valeur prod) ;
- entité en staging seule (création terrain) → ajoutée ;
- aucun staging pour le dispositif → réponse = prod pur (identité).

---

## Brique 2 — Traçabilité appareil + utilisateur

L'export existant **`POST /psdrf/export_dispositif_from_dendro3`** accepte désormais,
**à la racine du payload**, deux champs optionnels (en plus des données du dispositif) :

```jsonc
{
  "id_dispositif": 239,
  "device": "Samsung-XCover-AB12",   // nom/identifiant de l'appareil (string, optionnel)
  "id_role": 42,                       // utilisateur connecté (int, optionnel)
  "cycles": [ … ],
  "placettes": [ … ]                   // deltas created/updated/deleted (inchangé)
}
```

Pour **chaque placette** présente dans `placettes`, la tâche insère une ligne dans
`pr_psdrf_staging.t_dendro3_sync_log` :
`(id_dispositif, id_placette, device, id_role, synced_at = now() UTC)`.

Le résultat de la tâche d'export expose en plus `sync_log_count` (nb de lignes écrites).
Les routes `…/export_dispositif_from_dendro3/status|result/<task_id>` sont inchangées.

Table : `pr_psdrf_staging.t_dendro3_sync_log`
`id` PK · `id_dispositif` int · `id_placette` int · `device` text · `id_role` int · `synced_at` timestamp.

---

## Brique 3 — État des placettes (tableau de bord multi-édition)

| Méthode & chemin | Réponse |
|---|---|
| `GET /psdrf/dispositif-placettes-state/<int:id_dispositif>` | `200` `{ "status": "success", "data": [ … ] }` (synchrone) |

Renvoie, **par placette** (le dernier log connu, le plus récent `synced_at`) :

```jsonc
{
  "status": "success",
  "data": [
    {
      "id_placette": 1024,
      "id_dispositif": 239,
      "device": "Samsung-XCover-AB12",
      "id_role": 42,
      "identifiant": "jdupont",          // identifiant de connexion (peut être null)
      "nom_complet": "Jean Dupont",       // "prenom_role nom_role" (peut être null)
      "synced_at": "2026-06-05T09:14:22.512000"  // ISO 8601
    }
  ]
}
```

Une seule entrée par placette (la plus récente). Une placette jamais synchronisée
en staging n'apparaît pas. Sert : signaler la propriété (« 1 mobile = 1 placette »),
prévenir d'une multi-édition, alimenter l'écran de comparaison local ↔ staging.

---

## Écarts de format Brique 1 vs `/dispositif-complet`

1. **Aucun écart structurel** : mêmes clés à tous les niveaux. Les modèles prod
   (`pr_psdrf`) et staging (`pr_psdrf_staging`) sont des miroirs colonne à colonne,
   et la sortie part toujours du dict prod (on n'y réinjecte que des clés déjà
   présentes).
2. **Format de date `updated_at` sur entités issues du staging** : le schéma
   staging des arbres sérialise `updated_at` en `"%Y-%m-%d %H:%M:%S"` (via
   `CustomDateTimeField`), là où le schéma prod émet de l'ISO 8601. Une entité
   éditée en staging ressort donc avec ce format sur `updated_at`. (Clé identique,
   seule la *valeur* diffère.)
3. **Suppressions non matérialisées** : la fonction d'import staging supprime la
   ligne staging sans tombstone. La fusion est donc **prod ∪ staging-override** :
   une entité supprimée sur le terrain mais encore présente en prod **ressort en
   version prod**. La résolution fine (et les suppressions) se fait **côté app**
   (comparaison local ↔ staging), conformément au cahier des charges.

---

## Tests

- **Brique 1 (logique de fusion)** — testée hors BDD :
  ```bash
  # voir le script de validation joint au commit (override, prod-only,
  # staging-only, nested, identité sans staging) — tous verts.
  ```
- **Brique 1 (chaîne web)** : sur un dispositif avec saisies staging, comparer
  `…/dispositif-complet-staging/result` à `…/dispositif-complet/result` ; vérifier
  qu'une entité modifiée en staging ressort en version staging, les autres en prod ;
  dispositif sans staging ⇒ identique à prod.
- **Brique 2** : `POST /export_dispositif_from_dendro3` avec `device` + `id_role`
  ⇒ une ligne par placette dans `t_dendro3_sync_log`.
- **Brique 3** : `GET /dispositif-placettes-state/<id>` ⇒ dernier
  appareil/utilisateur/horodatage par placette, cohérents avec le log.
