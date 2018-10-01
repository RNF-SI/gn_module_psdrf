DO
$$
BEGIN

PERFORM pg_catalog.setval('ref_nomenclatures.bib_nomenclatures_types_id_type_seq', (SELECT max(id_type)+1 FROM ref_nomenclatures.bib_nomenclatures_types), false);
EXCEPTION WHEN unique_violation  THEN
        RAISE NOTICE 'Tentative d''insertion de valeur existante';
END
$$;

DO
$$
BEGIN

PERFORM pg_catalog.setval('ref_nomenclatures.t_nomenclatures_id_nomenclature_seq', (SELECT max(id_nomenclature)+1 FROM ref_nomenclatures.t_nomenclatures), false);
EXCEPTION WHEN unique_violation  THEN
        RAISE NOTICE 'Tentative d''insertion de valeur existante';
END
$$;

DO
$$
BEGIN

PERFORM pg_catalog.setval('gn_monitoring.t_base_sites_id_base_site_seq', (SELECT max(id_base_site)+1 FROM gn_monitoring.t_base_sites), false);
EXCEPTION WHEN unique_violation  THEN
        RAISE NOTICE 'Tentative d''insertion de valeur existante';
END
$$;

-- Add inserts here
