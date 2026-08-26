"""Structure du classeur PSDRF envoyé par le frontend.

Le front (`import.donnees.component.ts`) transmet le classeur sous forme d'une
liste de tableaux, un par onglet, **dans l'ordre du classeur**. Le backend les
dépaquetait par position sans rien vérifier : un classeur amputé d'un onglet
provoquait un `IndexError: list index out of range` remonté à l'utilisateur en
« Une erreur inconnue a eu lieu », impossible à diagnostiquer sans les logs.

Ce module centralise l'ordre attendu et le contrôle de forme.
"""

# Ordre imposé : le dépaquetage est positionnel, pas nominatif.
TABLE_NAMES = [
    "Placettes",
    "Cycles",
    "Arbres",
    "Regeneration",
    "Transect",
    "BMSsup30",
    "Reperes",
]


class TablesPsdrfError(ValueError):
    """Le classeur reçu n'a pas la forme attendue (message destiné à l'utilisateur)."""


def unpack_tables(data):
    """Vérifie que `data` contient les 7 onglets attendus et les retourne.

    Lève `TablesPsdrfError` avec un message actionnable sinon.
    """
    if not isinstance(data, (list, tuple)):
        raise TablesPsdrfError(
            "Les données reçues ne sont pas exploitables (aucun tableau transmis). "
            "Rechargez le fichier Excel puis relancez la vérification."
        )

    if len(data) < len(TABLE_NAMES):
        premier_manquant = TABLE_NAMES[len(data)]
        raise TablesPsdrfError(
            "Le fichier transmis ne contient que {recu} tableau(x) sur {attendu} : "
            "le premier onglet manquant est « {manquant} ». Vérifiez que le classeur "
            "comporte bien les 7 onglets, dans l'ordre {ordre}, et qu'aucun n'est "
            "entièrement vide — un onglet sans ligne d'en-tête interrompt le "
            "chargement du fichier dans le navigateur, qui n'envoie alors qu'une "
            "partie des données.".format(
                recu=len(data),
                attendu=len(TABLE_NAMES),
                manquant=premier_manquant,
                ordre=", ".join(TABLE_NAMES),
            )
        )

    if len(data) > len(TABLE_NAMES):
        raise TablesPsdrfError(
            "Le fichier transmis contient {recu} tableaux alors que {attendu} sont "
            "attendus. Supprimez les onglets supplémentaires : seuls {ordre} doivent "
            "être présents, dans cet ordre.".format(
                recu=len(data),
                attendu=len(TABLE_NAMES),
                ordre=", ".join(TABLE_NAMES),
            )
        )

    return list(data)
