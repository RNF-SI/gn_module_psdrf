from datetime import datetime


def count_updates_and_creations(full_data, last_sync_date):
    counts = {
        'corCyclesPlacettes': {'created': 0, 'updated': 0},
        'regenerations': {'created': 0, 'updated': 0},
        'transects': {'created': 0, 'updated': 0},
        'arbres': {'created': 0, 'updated': 0},
        'arbres_mesures': {'created': 0, 'updated': 0},
        'bmsSup30': {'created': 0, 'updated': 0},
        'bm_sup_30_mesures': {'created': 0, 'updated': 0},
        'reperes': {'created': 0, 'updated': 0}
    }
    
    for placette in full_data.get('placettes', []):
        for arbre in placette.get('arbres', []):
            increment_counts(counts, arbre, 'arbres', last_sync_date)
            for mesure in arbre.get('arbres_mesures', []):
                increment_counts(counts, mesure, 'arbres_mesures', last_sync_date)

        for bms in placette.get('bmsSup30', []):
            increment_counts(counts, bms, 'bmsSup30', last_sync_date)
            for mesure in bms.get('bm_sup_30_mesures', []):
                increment_counts(counts, mesure, 'bm_sup_30_mesures', last_sync_date)

        for rep in placette.get('reperes', []):
            increment_counts(counts, rep, 'reperes', last_sync_date)

    for cycle in full_data.get('cycles', []):
        for corCyclePlacette in cycle.get('corCyclesPlacettes', []):
            increment_counts(counts, corCyclePlacette, 'corCyclesPlacettes', last_sync_date)
            for reg in corCyclePlacette.get('regenerations', []):
                increment_counts(counts, reg, 'regenerations', last_sync_date)
            for tran in corCyclePlacette.get('transects', []):
                increment_counts(counts, tran, 'transects', last_sync_date)
    
    return counts

def parse_datetime(date_str):
    if date_str and isinstance(date_str, str):
        try:
            # Normalize the string to replace 'T' with a space
            normalized_date_str = date_str.replace('T', ' ')
            # Parse the datetime with microseconds
            return datetime.strptime(normalized_date_str, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            try:
                # Attempt to parse without microseconds
                return datetime.strptime(normalized_date_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                # Log the unparseable date string and return None or raise an error
                print(f"Could not parse the date string: {date_str}")
                return None
    else:
        # Return None if date_str is None or not a string
        return None

def increment_counts(counts, entity, entity_type, last_sync_date):
    created_at = parse_datetime(entity.get('created_at'))
    updated_at = parse_datetime(entity.get('updated_at'))

    if created_at and created_at > last_sync_date:
        counts[entity_type]['created'] += 1
    elif updated_at and updated_at > last_sync_date:
        counts[entity_type]['updated'] += 1