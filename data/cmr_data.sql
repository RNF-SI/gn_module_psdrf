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


INSERT INTO pr_cmr.t_programs (program_name, program_desc)
 VALUES ('Sonneur à ventre jaune', 'CMR des sonneurs à ventre jaune sur la plaine du Roc à Embrun');

INSERT INTO gn_monitoring.t_base_sites (id_inventor, id_digitiser, id_nomenclature_type_site, base_site_name, base_site_description, base_site_code, geom, uuid_base_site) 
VALUES(1,1, ref_nomenclatures.get_id_nomenclature('TYPE_SITE', '7'),'Plaine du roc','Une belle plaine','PLAINE_ROC','0101000020E61000008D976E1283C0F33F16FBCBEEC9C30240','2af0dad6-afa8-4389-a8d5-a5800e3acce6');

INSERT INTO ref_nomenclatures.bib_nomenclatures_types (mnemonique, label_default, definition_default, label_fr, definition_fr, source)
VALUES ('CMR_ACTION', 'Action de CMR', 'Nomenclature des type d actions CMR', 'Type d action CMR', 'Nomenclatures des types d action CMR', 'NSP');

INSERT INTO ref_nomenclatures.t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, id_broader) VALUES 
(ref_nomenclatures.get_id_nomenclature_type('CMR_ACTION'), 'CAPT', 'Capture', 'Capture', 'Capture d un individu', 'Capture', 'Capture d un individu', 0),
(ref_nomenclatures.get_id_nomenclature_type('CMR_ACTION'), 'RECAPT_MARQ', 'Recapture et marquage', 'Recapture et marquage', 'Capture d un individu et remarquage', 'Recapture et marquage', 'Recapture et marquage d un individu', 0);


INSERT INTO pr_cmr.cor_site_program (id_site, id_program)
SELECT id_base_site, 1
FROM gn_monitoring.t_base_sites
WHERE base_site_code = 'PLAINE_ROC';

INSERT INTO pr_cmr.t_individuals (id_individual, cd_nom, tag_code, tag_location, id_site_tag, comment) 
SELECT 1, 212, 'Numero 1', 'Sur le ventre', id_base_site, 'Un beau sonneur en pleine forme'
FROM gn_monitoring.t_base_sites
WHERE base_site_code = 'PLAINE_ROC';

INSERT INTO pr_cmr.cor_individual_program(id_individual, id_program) VALUES (1,1);

INSERT INTO pr_cmr.t_operations (id_operation, id_individual, id_site, date_min, date_max, determiner, comment) 
SELECT 1, 1, id_base_site, '2017-01-01', '2017-01-01', 'Donovan Maillard', 'il pleuvait'
FROM gn_monitoring.t_base_sites
WHERE base_site_code = 'PLAINE_ROC';

INSERT INTO pr_cmr.cor_operation_observer (id_operation, id_observer) VALUES (1,1);