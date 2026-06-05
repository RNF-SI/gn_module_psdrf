"""Fusion prod + staging d'un dispositif PSDRF sérialisé.

Les deux dictionnaires d'entrée proviennent de schémas Marshmallow miroirs
(``DispositifSchema`` côté prod, ``DispositifStagingSchema`` côté staging) : pour
une même entité ils exposent les MÊMES clés, car les modèles prod et staging
sont des miroirs colonne à colonne. La fusion se fait donc niveau par niveau,
par identifiant :

- entité présente en prod ET staging    -> la valeur staging écrase la valeur
  prod (champ à champ), puis les enfants sont fusionnés récursivement ;
- entité présente seulement en prod      -> conservée telle quelle ;
- entité présente seulement en staging   -> ajoutée (création terrain), ses
  enfants étant fusionnés contre une liste prod vide.

Le format de sortie est STRICTEMENT celui de ``/psdrf/dispositif-complet`` : pour
une entité fusionnée on part toujours du dictionnaire prod et on n'y réinjecte
que des clés déjà présentes ; on n'introduit jamais de clé absente de prod.

Limite connue : les suppressions faites côté mobile ne sont PAS matérialisées
dans le schéma staging (la fonction d'import supprime la ligne staging sans
laisser de tombstone). La fusion est donc « prod ∪ staging-override » : une
entité supprimée sur le terrain mais encore présente en prod ressort en version
prod.
"""

# Arbre de fusion. Chaque entrée : clé_de_liste -> (clé_identifiant, sous-enfants)
_CHILDREN = {
    "placettes": ("id_placette", {
        "arbres": ("id_arbre", {
            "arbres_mesures": ("id_arbre_mesure", {}),
        }),
        "bmsSup30": ("id_bm_sup_30", {
            "bm_sup_30_mesures": ("id_bm_sup_30_mesure", {}),
        }),
        "reperes": ("id_repere", {}),
    }),
    "cycles": ("id_cycle", {
        "corCyclesPlacettes": ("id_cycle_placette", {
            "regenerations": ("id_regeneration", {}),
            "transects": ("id_transect", {}),
        }),
    }),
}


def _merge_entity(prod, staging, children):
    """Fusionne une entité : staging écrase prod champ à champ, enfants fusionnés."""
    out = dict(prod)
    child_keys = set(children)
    for key, value in staging.items():
        if key in child_keys:
            continue
        if key in out:  # ne jamais introduire de clé absente de prod
            out[key] = value
    for list_key, (id_key, sub_children) in children.items():
        out[list_key] = _merge_list(
            prod.get(list_key) or [],
            staging.get(list_key) or [],
            id_key,
            sub_children,
        )
    return out


def _new_entity_from_staging(staging, children):
    """Construit une entité « création terrain » à partir du seul staging."""
    out = dict(staging)
    for list_key, (id_key, sub_children) in children.items():
        out[list_key] = _merge_list(
            [],
            staging.get(list_key) or [],
            id_key,
            sub_children,
        )
    return out


def _merge_list(prod_list, staging_list, id_key, children):
    """Fusionne deux listes d'entités par identifiant (str), ordre prod préservé."""
    staging_by_id = {}
    for item in staging_list:
        ident = item.get(id_key)
        if ident is not None:
            staging_by_id[str(ident)] = item

    merged = []
    consumed = set()
    for prod_item in prod_list:
        ident = prod_item.get(id_key)
        skey = str(ident) if ident is not None else None
        staging_item = staging_by_id.get(skey) if skey is not None else None
        if staging_item is None:
            merged.append(prod_item)
        else:
            consumed.add(skey)
            merged.append(_merge_entity(prod_item, staging_item, children))

    # Entités présentes uniquement en staging (créations terrain), ordre staging.
    for staging_item in staging_list:
        ident = staging_item.get(id_key)
        skey = str(ident) if ident is not None else None
        if skey is not None and skey in consumed:
            continue
        merged.append(_new_entity_from_staging(staging_item, children))

    return merged


def merge_dispositif_prod_staging(prod_data, staging_data):
    """Fusionne le dispositif prod (dict) avec sa version staging (dict ou None).

    :param prod_data: dispositif sérialisé par ``DispositifSchema`` (prod).
    :param staging_data: dispositif sérialisé par ``DispositifStagingSchema``
        (staging) ou ``None`` / ``{}`` si aucune saisie en staging.
    :return: dict au format identique à ``/psdrf/dispositif-complet``.
    """
    if not staging_data:
        return prod_data
    return _merge_entity(prod_data, staging_data, _CHILDREN)
