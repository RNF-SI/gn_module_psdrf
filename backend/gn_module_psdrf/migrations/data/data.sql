SET search_path = ref_nomenclatures, pg_catalog, public;


-- Types d'espaces
INSERT INTO ref_geo.bib_areas_types (type_name, type_code)
VALUES ('Autre', 'X');
INSERT INTO ref_geo.bib_areas_types (type_name, type_code)
VALUES ('Projet de réserve biologique', 'PRBIOL');
INSERT INTO ref_geo.bib_areas_types (type_name, type_code)
VALUES ('Forêt domaniale', 'FDOM');
INSERT INTO ref_geo.bib_areas_types (type_name, type_code)
VALUES ('Réserve biologique dirigée', 'RBIOLD');


-- Types de nomenclatures
INSERT INTO bib_nomenclatures_types (mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut)
VALUES ('PSDRF_DURETE', 'Code dureté', 'Niveau de pourriture d''un billon de bois mort', 'Code dureté', 'Niveau de pourriture d''un billon de bois mort',  'PSDRF', 'Validé');
INSERT INTO bib_nomenclatures_types (mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut)
VALUES ('PSDRF_ECORCE', 'Code écorce', 'Aspect de l''écorce sur le billon', 'Code écorce', 'Aspect de l''écorce sur le billon',  'PSDRF', 'Validé');
INSERT INTO bib_nomenclatures_types (mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut)
VALUES ('PSDRF_ECOLOGIE', 'Code écologie', 'Dendromicrohabitats PSDRF (plusieurs référentiels possibles)', 'Code écologie', 'Dendromicrohabitats PSDRF (plusieurs référentiels possibles)',  'PSDRF', 'Validé');
INSERT INTO bib_nomenclatures_types (mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut)
VALUES ('PSDRF_CASTOR', 'Indice de présence de castors', '', 'Indice de présence de castors', '',  'PSDRF', 'Validé');
INSERT INTO bib_nomenclatures_types (mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut)
VALUES ('PSDRF_FROTTIS', 'Indice de présence de frottis', 'Indice de présence de frottis par des hebivores sauvages', 'Indice de présence de frottis', 'Indice de présence de frottis par des hebivores sauvages',  'PSDRF', 'Validé');
INSERT INTO bib_nomenclatures_types (mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut)
VALUES ('PSDRF_BOUTIS', 'Indice de présence de boutis de sanglier', '', 'Indice de présence de boutis de sanglier', '',  'PSDRF', 'Validé');
INSERT INTO bib_nomenclatures_types (mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut)
VALUES ('PSDRF_SANITAIRE', 'Etat sanitaire', 'Etat sanitaire de l''arbre (module alluvial)', 'Etat sanitaire', 'Etat sanitaire de l''arbre (module alluvial)',  'PSDRF', 'Validé');
INSERT INTO bib_nomenclatures_types (mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut)
VALUES ('PSDRF_TYPO_ARBRES', 'Type d''arbre', '', 'type d''arbre', '',  'PSDRF', 'Validé');
INSERT INTO bib_nomenclatures_types (mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut)
VALUES ('PSDRF_ABROUTIS', 'Abroutissement', 'Abroutissement (module alluvial)', 'Abroutissement', 'Abroutissement (module alluvial)',  'PSDRF', 'Validé');

-- Code écologie
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '100', 'prosilva_100', '100 - Arbre mort sur pied', NULL, '100 - Arbre mort sur pied',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '110', 'prosilva_110', '110 - Arbre mort sur pied', NULL, '110 - Arbre mort sur pied',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '111', 'prosilva_111', '111 - Arbre mort sur pied de Diam > 30cm', NULL, '111 - Arbre mort sur pied de Diam > 30cm',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '112', 'prosilva_112', '112 - Arbre mort sur pied de Diam < 30cm', NULL, '112 - Arbre mort sur pied de Diam < 30cm',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '120', 'prosilva_120', '120 - Arbre mort sur pied - squelette du houppier présent', NULL, '120 - Arbre mort sur pied - squelette du houppier présent',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '130', 'prosilva_130', '130 - Arbre mort sur pied - champignons lignicoles', NULL, '130 - Arbre mort sur pied - champignons lignicoles',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '131', 'prosilva_131', '131 - Arbre mort sur pied - champignons lignicoles (< 3 carpophores)', NULL, '131 - Arbre mort sur pied - champignons lignicoles (< 3 carpophores)',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '132', 'prosilva_132', '132 - Arbre mort sur pied - champignons lignicoles (> 3 carpophores)', NULL, '132 - Arbre mort sur pied - champignons lignicoles (> 3 carpophores)',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '140', 'prosilva_140', '140 - Arbre mort sur pied - écorce présente', NULL, '140 - Arbre mort sur pied - écorce présente',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '141', 'prosilva_141', '141 - Arbre mort sur pied - écorce présente sur plus de la moitié du tronc', NULL, '141 - Arbre mort sur pied - écorce présente sur plus de la moitié du tronc',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '142', 'prosilva_142', '142 - Arbre mort sur pied - écorce présente sur moins de la moitié du tronc', NULL, '142 - Arbre mort sur pied - écorce présente sur moins de la moitié du tronc',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '200', 'prosilva_200', '200 - Arbre dépérissant', NULL, '200 - Arbre dépérissant',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '210', 'prosilva_210', '210 - Arbre dépérissant - à maintenir', NULL, '210 - Arbre dépérissant - à maintenir',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '220', 'prosilva_220', '220 - Arbre dépérissant - présence de champignons', NULL, '220 - Arbre dépérissant - présence de champignons',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '230', 'prosilva_230', '230 - Arbre dépérissant - creux', NULL, '230 - Arbre dépérissant - creux',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '300', 'prosilva_300', '300 - Arbre vivant', NULL, '300 - Arbre vivant',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '310', 'prosilva_310', '310 - Arbre vivant - < 3 branches mortes de Diam > 10cm', NULL, '310 - Arbre vivant - < 3 branches mortes de Diam > 10cm',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '311', 'prosilva_311', '311 - Arbre vivant - > 3 branches mortes de Diam > 10cm', NULL, '311 - Arbre vivant - > 3 branches mortes de Diam > 10cm',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '312', 'prosilva_312', '312 - Arbre vivant - < 3 branches mortes de faible diamètre', NULL, '312 - Arbre vivant - < 3 branches mortes de faible diamètre',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '313', 'prosilva_313', '313 - Arbre vivant - > 3 branches mortes de faible diamètre', NULL, '313 - Arbre vivant - > 3 branches mortes de faible diamètre',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '314', 'prosilva_314', '314 - Arbre vivant - branches mortes', NULL, '314 - Arbre vivant - branches mortes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '320', 'prosilva_320', '320 - Arbre vivant - mal conformé', NULL, '320 - Arbre vivant - mal conformé',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '321', 'prosilva_321', '321 - Arbre vivant - fourchu/jumelle avec pourriture', NULL, '321 - Arbre vivant - fourchu/jumelle avec pourriture',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '322', 'prosilva_322', '322 - Arbre vivant - massif, bas branchu, sinueux', NULL, '322 - Arbre vivant - massif, bas branchu, sinueux',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '323', 'prosilva_323', '323 - Arbre vivant - en cépée naturelle (AUG ou AUB)', NULL, '323 - Arbre vivant - en cépée naturelle (AUG ou AUB)',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '330', 'prosilva_330', '330 - Arbre vivant - cavités ou trous de pics', NULL, '330 - Arbre vivant - cavités ou trous de pics',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '331', 'prosilva_331', '331 - Arbre vivant - cavités ou trous de pics en hauteur', NULL, '331 - Arbre vivant - cavités ou trous de pics en hauteur',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '332', 'prosilva_332', '332 - Arbre vivant - cavités ou trous de pics au pied', NULL, '332 - Arbre vivant - cavités ou trous de pics au pied',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '333', 'prosilva_333', '333 - Arbre vivant - cavités ou trous de pics en-desssous d''une branche sèche', NULL, '333 - Arbre vivant - cavités ou trous de pics en-desssous d''une branche sèche',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '334', 'prosilva_334', '334 - Arbre vivant - série de trous de pics superposés', NULL, '334 - Arbre vivant - série de trous de pics superposés',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '335', 'prosilva_335', '335 - Arbre vivant - cavités ou trous de pics en formation', NULL, '335 - Arbre vivant - cavités ou trous de pics en formation',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '340', 'prosilva_340', '340 - Arbre vivant - fente(s)', NULL, '340 - Arbre vivant - fente(s)',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '341', 'prosilva_341', '341 - Arbre vivant - fente(s) en hauteur, longue', NULL, '341 - Arbre vivant - fente(s) en hauteur, longue',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '343', 'prosilva_343', '343 - Arbre vivant - fente(s) en hauteur, courte', NULL, '343 - Arbre vivant - fente(s) en hauteur, courte',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '345', 'prosilva_345', '345 - Arbre vivant - fente(s) près du sol, longue', NULL, '345 - Arbre vivant - fente(s) près du sol, longue',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '347', 'prosilva_347', '347 - Arbre vivant - fente(s) près du sol, courte', NULL, '347 - Arbre vivant - fente(s) près du sol, courte',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '349', 'prosilva_349', '349 - Arbre vivant - fente(s) en formation', NULL, '349 - Arbre vivant - fente(s) en formation',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '350', 'prosilva_350', '350 - Arbre vivant - blessure(s)', NULL, '350 - Arbre vivant - blessure(s)',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '351', 'prosilva_351', '351 - Arbre vivant - blessure(s) sur le tronc', NULL, '351 - Arbre vivant - blessure(s) sur le tronc',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '352', 'prosilva_352', '352 - Arbre vivant - blessure(s) au pied', NULL, '352 - Arbre vivant - blessure(s) au pied',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '360', 'prosilva_360', '360 - Arbre vivant - à maintenir (position)', NULL, '360 - Arbre vivant - à maintenir (position)',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '361', 'prosilva_361', '361 - Arbre vivant - en lisière/bordure de chemin/cloisonnement', NULL, '361 - Arbre vivant - en lisière/bordure de chemin/cloisonnement',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '362', 'prosilva_362', '362 - Arbre vivant - proche de bois mort au sol (rôle de couvert)', NULL, '362 - Arbre vivant - proche de bois mort au sol (rôle de couvert)',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '370', 'prosilva_370', '370 - Arbre vivant - à maintenir (essence)', NULL, '370 - Arbre vivant - à maintenir (essence)',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '371', 'prosilva_371', '371 - Arbre vivant - à maintenir pour diversifier espèce autochtone', NULL, '371 - Arbre vivant - à maintenir pour diversifier espèce autochtone',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '372', 'prosilva_372', '372 - Arbre vivant - à maintenir pour la part des feuillus', NULL, '372 - Arbre vivant - à maintenir pour la part des feuillus',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '380', 'prosilva_380', '380 - Arbre vivant - autres critères', NULL, '380 - Arbre vivant - autres critères',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '381', 'prosilva_381', '381 - Arbre vivant - gros bois', NULL, '381 - Arbre vivant - gros bois',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '382', 'prosilva_382', '382 - Arbre vivant - struturation du peuplement', NULL, '382 - Arbre vivant - struturation du peuplement',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '390', 'prosilva_390', '390 - Arbre vivant - autres critères', NULL, '390 - Arbre vivant - autres critères',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '391', 'prosilva_391', '391 - Arbre vivant - lierre sur le tronc', NULL, '391 - Arbre vivant - lierre sur le tronc',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '392', 'prosilva_392', '392 - Arbre vivant - lierre sur le tronc et dans le houppier', NULL, '392 - Arbre vivant - lierre sur le tronc et dans le houppier',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '393', 'prosilva_393', '393 - Arbre vivant - mousse(s) et/ou lichen(s) sur tout le tronc', NULL, '393 - Arbre vivant - mousse(s) et/ou lichen(s) sur tout le tronc',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'g1', 'engref_g1', 'g1 - Cavité sur le pied', NULL, 'g1 - Cavité sur le pied',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'g2', 'engref_g2', 'g2 - Cavité sur le fût', NULL, 'g2 - Cavité sur le fût',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'g3', 'engref_g3', 'g3 - Cavité dans le houppier', NULL, 'g3 - Cavité dans le houppier',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'h1', 'engref_h1', 'h1 - Loge au pied', NULL, 'h1 - Loge au pied',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'h2', 'engref_h2', 'h2 - Loge sur le fût', NULL, 'h2 - Loge sur le fût',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'h3', 'engref_h3', 'h3 - Loge dans le houppier', NULL, 'h3 - Loge dans le houppier',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'f1', 'engref_f1', 'f1 - Fente au pied', NULL, 'f1 - Fente au pied',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'f2', 'engref_f2', 'f2 - Fente sur le fût', NULL, 'f2 - Fente sur le fût',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'f3', 'engref_f3', 'f3 - Fente dans le houppier', NULL, 'f3 - Fente dans le houppier',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'a1', 'engref_a1', 'a1 - Attaques de pics au pied', NULL, 'a1 - Attaques de pics au pied',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'a2', 'engref_a2', 'a2 - Attaques de pics sur le fût', NULL, 'a2 - Attaques de pics sur le fût',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'a3', 'engref_a3', 'a3 - Attaques de pics dans le houppier', NULL, 'a3 - Attaques de pics dans le houppier',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'p1', 'engref_p1', 'p1 - Pourriture au pied', NULL, 'p1 - Pourriture au pied',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'p2', 'engref_p2', 'p2 - Pourriture sur le fût', NULL, 'p2 - Pourriture sur le fût',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'p3', 'engref_p3', 'p3 - Pourriture dans le houppier', NULL, 'p3 - Pourriture dans le houppier',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'i1', 'engref_i1', 'i1 - Blessure au pied', NULL, 'i1 - Blessure au pied',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'i2', 'engref_i2', 'i2 - Blessure sur le fût', NULL, 'i2 - Blessure sur le fût',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'i3', 'engref_i3', 'i3 - Blessure dans le houppier', NULL, 'i3 - Blessure dans le houppier',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'c1', 'engref_c1', 'c1 - Champignon au pied', NULL, 'c1 - Champignon au pied',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'c2', 'engref_c2', 'c2 - Champignon sur le fût', NULL, 'c2 - Champignon sur le fût',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'c3', 'engref_c3', 'c3 - Champignon dans le houppier', NULL, 'c3 - Champignon dans le houppier',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'e1', 'engref_e1', 'e1 - Écorce déhiscente au pied', NULL, 'e1 - Écorce déhiscente au pied',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'e2', 'engref_e2', 'e2 - Écorce déhiscente sur le fût', NULL, 'e2 - Écorce déhiscente sur le fût',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'e3', 'engref_e3', 'e3 - Écorce déhiscente dans le houppier', NULL, 'e3 - Écorce déhiscente dans le houppier',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'b1', 'engref_b1', 'b1 - Mousse au pied', NULL, 'b1 - Mousse au pied',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'b2', 'engref_b2', 'b2 - Mousse sur le fût', NULL, 'b2 - Mousse sur le fût',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'b3', 'engref_b3', 'b3 - Mousse dans le houppier', NULL, 'b3 - Mousse dans le houppier',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'l1', 'engref_l1', 'l1 - Lichen au pied', NULL, 'l1 - Lichen au pied',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'l2', 'engref_l2', 'l2 - Lichen sur le fût', NULL, 'l2 - Lichen sur le fût',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'l3', 'engref_l3', 'l3 - Lichen dans le houppier', NULL, 'l3 - Lichen dans le houppier',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'r1', 'engref_r1', 'r1 - Lierre au pied', NULL, 'r1 - Lierre au pied',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'r2', 'engref_r2', 'r2 - Lierre sur le fût', NULL, 'r2 - Lierre sur le fût',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'r3', 'engref_r3', 'r3 - Lierre dans le houppier', NULL, 'r3 - Lierre dans le houppier',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 't1', 'engref_t1', 't1 - pointe sèche', NULL, 't1 - pointe sèche',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 't2', 'engref_t2', 't2 - Tête cassée, sans nouvelle tête', NULL, 't2 - Tête cassée, sans nouvelle tête',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 't3', 'engref_t3', 't3 - Tête cassée, avec une nouvelle tête', NULL, 't3 - Tête cassée, avec une nouvelle tête',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 't4', 'engref_t4', 't4 - Têtes multiples', NULL, 't4 - Têtes multiples',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'ts', 'engref_ts', 'ts - Pointe sèche', NULL, 'ts - Pointe sèche',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'tc', 'engref_tc', 'tc - Tête cassée, sans nouvelle tête', NULL, 'tc - Tête cassée, sans nouvelle tête',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'tn', 'engref_tn', 'tn - Tête cassée, avec une nouvelle tête', NULL, 'tn - Tête cassée, avec une nouvelle tête',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'tx', 'engref_tx', 'tx - Têtes multiples', NULL, 'tx - Têtes multiples',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'k', 'engref_k', 'k - Fourche', NULL, 'k - Fourche',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 't', 'engref_t', 't - Tête cassée ou sèche', NULL, 't - Tête cassée ou sèche',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'd', 'engref_d', 'd - Individu dépérissant', NULL, 'd - Individu dépérissant',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'u', 'engref_u', 'u - Individu bas branchu, sinueux, tortueux', NULL, 'u - Individu bas branchu, sinueux, tortueux',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'n', 'engref_n', 'n - Lisière', NULL, 'n - Lisière',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'j', 'engref_j', 'j - Lisière', NULL, 'j - Lisière',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'm', 'engref_m', 'm - Individu mort', NULL, 'm - Individu mort',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'm1', 'engref_m1', 'm1 - Individu mort < 30 cm de diam', NULL, 'm1 - Individu mort < 30 cm de diam',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'm2', 'engref_m2', 'm2 - Individu mort > 30 cm de diam', NULL, 'm2 - Individu mort > 30 cm de diam',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'v', 'engref_v', 'v - Diversité en espèce autochtone', NULL, 'v - Diversité en espèce autochtone',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 's1', 'engref_s1', 's1 - Petites branches mortes', NULL, 's1 - Petites branches mortes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 's2', 'engref_s2', 's2 - Petites branches mortes', NULL, 's2 - Petites branches mortes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 's3', 'engref_s3', 's3 - Petites branches mortes', NULL, 's3 - Petites branches mortes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 's4', 'engref_s4', 's4 - Petites branches mortes', NULL, 's4 - Petites branches mortes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 's5', 'engref_s5', 's5 - Petites branches mortes', NULL, 's5 - Petites branches mortes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 's6', 'engref_s6', 's6 - Petites branches mortes', NULL, 's6 - Petites branches mortes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 's7', 'engref_s7', 's7 - Petites branches mortes', NULL, 's7 - Petites branches mortes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 's8', 'engref_s8', 's8 - Petites branches mortes', NULL, 's8 - Petites branches mortes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 's9', 'engref_s9', 's9 - Petites branches mortes', NULL, 's9 - Petites branches mortes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 's10', 'engref_s10', 's10 - Petites branches mortes', NULL, 's10 - Petites branches mortes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'x1', 'engref_x1', 'x1 - Moyennes branches mortes', NULL, 'x1 - Moyennes branches mortes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'x2', 'engref_x2', 'x2 - Moyennes branches mortes', NULL, 'x2 - Moyennes branches mortes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'x3', 'engref_x3', 'x3 - Moyennes branches mortes', NULL, 'x3 - Moyennes branches mortes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'x4', 'engref_x4', 'x4 - Moyennes branches mortes', NULL, 'x4 - Moyennes branches mortes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'x5', 'engref_x5', 'x5 - Moyennes branches mortes', NULL, 'x5 - Moyennes branches mortes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'x6', 'engref_x6', 'x6 - Moyennes branches mortes', NULL, 'x6 - Moyennes branches mortes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'x7', 'engref_x7', 'x7 - Moyennes branches mortes', NULL, 'x7 - Moyennes branches mortes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'x8', 'engref_x8', 'x8 - Moyennes branches mortes', NULL, 'x8 - Moyennes branches mortes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'x9', 'engref_x9', 'x9 - Moyennes branches mortes', NULL, 'x9 - Moyennes branches mortes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'x10', 'engref_x10', 'x10 - Moyennes branches mortes', NULL, 'x10 - Moyennes branches mortes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'y1', 'engref_y1', 'y1 - Grosses branches mortes', NULL, 'y1 - Grosses branches mortes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'y2', 'engref_y2', 'y2 - Grosses branches mortes', NULL, 'y2 - Grosses branches mortes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'y3', 'engref_y3', 'y3 - Grosses branches mortes', NULL, 'y3 - Grosses branches mortes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'y4', 'engref_y4', 'y4 - Grosses branches mortes', NULL, 'y4 - Grosses branches mortes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'y5', 'engref_y5', 'y5 - Grosses branches mortes', NULL, 'y5 - Grosses branches mortes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'y6', 'engref_y6', 'y6 - Grosses branches mortes', NULL, 'y6 - Grosses branches mortes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'y7', 'engref_y7', 'y7 - Grosses branches mortes', NULL, 'y7 - Grosses branches mortes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'y8', 'engref_y8', 'y8 - Grosses branches mortes', NULL, 'y8 - Grosses branches mortes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'y9', 'engref_y9', 'y9 - Grosses branches mortes', NULL, 'y9 - Grosses branches mortes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'y10', 'engref_y10', 'y10 - Grosses branches mortes', NULL, 'y10 - Grosses branches mortes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'z', 'engref_z', 'z - > 10 branches mortes', NULL, 'z - > 10 branches mortes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'CV', 'EFI_CV', 'CV - Cavités', NULL, 'CV - Cavités',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'CV1', 'EFI_CV1', 'CV1 - Cavités de pics', NULL, 'CV1 - Cavités de pics',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'CV11', 'EFI_CV11', 'CV11 - Cavités de pics - Diam = 4 cm', NULL, 'CV11 - Cavités de pics - Diam = 4 cm',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'CV12', 'EFI_CV12', 'CV12 - Cavités de pics - Diam = 5 - 6 cm', NULL, 'CV12 - Cavités de pics - Diam = 5 - 6 cm',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'CV13', 'EFI_CV13', 'CV13 - Cavités de pics - Diam > 10 cm', NULL, 'CV13 - Cavités de pics - Diam > 10 cm',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'CV14', 'EFI_CV14', 'CV14 - Cavités de pics - Diam ≥ 10 cm feeding hole', NULL, 'CV14 - Cavités de pics - Diam ≥ 10 cm feeding hole',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'CV15', 'EFI_CV15', 'CV15 - Cavités de pics en "flûte"/chaine de cavités', NULL, 'CV15 - Cavités de pics en "flûte"/chaine de cavités',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'CV2', 'EFI_CV2', 'CV2 - Cavités de tronc/à terreau', NULL, 'CV2 - Cavités de tronc/à terreau',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'CV21', 'EFI_CV21', 'CV21 - Cavités de tronc/à terreau - Diam ≥ 10 cm (en contact avec le sol)', NULL, 'CV21 - Cavités de tronc/à terreau - Diam ≥ 10 cm (en contact avec le sol)',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'CV22', 'EFI_CV22', 'CV22 - Cavités de tronc/à terreau - Diam ≥ 30 cm (en contact avec le sol)', NULL, 'CV22 - Cavités de tronc/à terreau - Diam ≥ 30 cm (en contact avec le sol)',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'CV23', 'EFI_CV23', 'CV23 - Cavités de tronc/à terreau - Diam ≥ 10 cm', NULL, 'CV23 - Cavités de tronc/à terreau - Diam ≥ 10 cm',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'CV24', 'EFI_CV24', 'CV24 - Cavités de tronc/à terreau - Diam ≥ 30 cm', NULL, 'CV24 - Cavités de tronc/à terreau - Diam ≥ 30 cm',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'CV25', 'EFI_CV25', 'CV25 - Cavités de tronc/à terreau - Diam ≥ 30 cm/semi-ouverte', NULL, 'CV25 - Cavités de tronc/à terreau - Diam ≥ 30 cm/semi-ouverte',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'CV26', 'EFI_CV26', 'CV26 - Cavités de tronc/à terreau - Diam ≥ 30 cm /ouverte vers le haut', NULL, 'CV26 - Cavités de tronc/à terreau - Diam ≥ 30 cm /ouverte vers le haut',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'CV3', 'EFI_CV3', 'CV3 - Cavités de branches', NULL, 'CV3 - Cavités de branches',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'CV31', 'EFI_CV31', 'CV31 - Cavités de branches - Diam ≥ 5 cm', NULL, 'CV31 - Cavités de branches - Diam ≥ 5 cm',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'CV32', 'EFI_CV32', 'CV32 - Cavités de branches - Diam ≥ 10 cm', NULL, 'CV32 - Cavités de branches - Diam ≥ 10 cm',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'CV33', 'EFI_CV33', 'CV33 - Cavités de branches - Branche creuse,Diam ≥ 10 cm', NULL, 'CV33 - Cavités de branches - Branche creuse,Diam ≥ 10 cm',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'CV4', 'EFI_CV4', 'CV4 - Dendrotelmes', NULL, 'CV4 - Dendrotelmes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'CV41', 'EFI_CV41', 'CV41 - Dendrotelmes - Diam ≥ 3 cm/à la base du tronc', NULL, 'CV41 - Dendrotelmes - Diam ≥ 3 cm/à la base du tronc',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'CV42', 'EFI_CV42', 'CV42 - Dendrotelmes - Diam ≥ 15 cm/à la base du tronc', NULL, 'CV42 - Dendrotelmes - Diam ≥ 15 cm/à la base du tronc',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'CV43', 'EFI_CV43', 'CV43 - Dendrotelmes - Diam ≥ 5cm/dans le houppier', NULL, 'CV43 - Dendrotelmes - Diam ≥ 5cm/dans le houppier',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'CV44', 'EFI_CV44', 'CV44 - Dendrotelmes - Diam ≥ 15 cm/dans le houppier', NULL, 'CV44 - Dendrotelmes - Diam ≥ 15 cm/dans le houppier',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'CV5', 'EFI_CV5', 'CV5 - Galeries et trous d''insecte', NULL, 'CV5 - Galeries et trous d''insecte',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'CV51', 'EFI_CV51', 'CV51 - Galerie avec d''uniques et petits trous', NULL, 'CV51 - Galerie avec d''uniques et petits trous',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'CV52', 'EFI_CV52', 'CV52 - Trous de gros insectes, Diam ≥ 2 cm', NULL, 'CV52 - Trous de gros insectes, Diam ≥ 2 cm',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'IN', 'EFI_IN', 'IN - Blessures et plaies', NULL, 'IN - Blessures et plaies',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'IN1', 'EFI_IN1', 'IN1 - Perte d''écorce/Aubier exposé', NULL, 'IN1 - Perte d''écorce/Aubier exposé',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'IN11', 'EFI_IN11', 'IN11 - Perte d’écorce sur 25- 600 cm2, Stade de décomposition < 3', NULL, 'IN11 - Perte d’écorce sur 25- 600 cm2, Stade de décomposition < 3',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'IN12', 'EFI_IN12', 'IN12 - Perte d’écorce > 600 cm2, Stade de décomposition < 3', NULL, 'IN12 - Perte d’écorce > 600 cm2, Stade de décomposition < 3',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'IN13', 'EFI_IN13', 'IN13 - Perte d’écorce 25- 600 cm2, Stade de décomposition = 3', NULL, 'IN13 - Perte d’écorce 25- 600 cm2, Stade de décomposition = 3',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'IN14', 'EFI_IN14', 'IN14 - Perte d’écorce > 600 cm2, Stade de décomposition = 3', NULL, 'IN14 - Perte d’écorce > 600 cm2, Stade de décomposition = 3',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'IN2', 'EFI_IN2', 'IN2 - Bois de cœur exposé/Bris de tronc et de houppier', NULL, 'IN2 - Bois de cœur exposé/Bris de tronc et de houppier',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'IN21', 'EFI_IN21', 'IN21 - Bris de tronc, Diam ≥ 20 cm à l’extrémité brisée', NULL, 'IN21 - Bris de tronc, Diam ≥ 20 cm à l’extrémité brisée',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'IN22', 'EFI_IN22', 'IN22 - Bris de houppier ou de fourche, bois exposé > 300 cm²', NULL, 'IN22 - Bris de houppier ou de fourche, bois exposé > 300 cm²',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'IN23', 'EFI_IN23', 'IN23 - Bris de charpentière Diam ≥ 20 cm à l’extrémité brisée', NULL, 'IN23 - Bris de charpentière Diam ≥ 20 cm à l’extrémité brisée',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'IN24', 'EFI_IN24', 'IN24 - Tige éclatée, Diam ≥ 20 cm à l’extrémité brisée', NULL, 'IN24 - Tige éclatée, Diam ≥ 20 cm à l’extrémité brisée',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'IN3', 'EFI_IN3', 'IN3 - Fentes et cicatrices', NULL, 'IN3 - Fentes et cicatrices',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'IN31', 'EFI_IN31', 'IN31 - Longueur  30-100 cm; Largeur > 1 cm; Profondeur > 10 cm', NULL, 'IN31 - Longueur  30-100 cm; Largeur > 1 cm; Profondeur > 10 cm',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'IN32', 'EFI_IN32', 'IN32 - Longueur ≥ 100 cm; Largeur > 1 cm; Profondeur > 10 cm', NULL, 'IN32 - Longueur ≥ 100 cm; Largeur > 1 cm; Profondeur > 10 cm',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'IN33', 'EFI_IN33', 'IN33 - Cicatrice due à la foudre', NULL, 'IN33 - Cicatrice due à la foudre',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'IN34', 'EFI_IN34', 'IN34 - Blessure due au feu ≥ 600 cm²', NULL, 'IN34 - Blessure due au feu ≥ 600 cm²',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'BA', 'EFI_BA', 'BA - Ecorce', NULL, 'BA - Ecorce',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'BA1', 'EFI_BA1', 'BA1 - Ecorce', NULL, 'BA1 - Ecorce',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'BA11', 'EFI_BA11', 'BA11 - Abri sous écorce, décollement > 1 cm; largeur > 10 cm; hauteur > 10 cm', NULL, 'BA11 - Abri sous écorce, décollement > 1 cm; largeur > 10 cm; hauteur > 10 cm',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'BA12', 'EFI_BA12', 'BA12 - Poche d’écorce décollement > 1 cm; profondeur > 10 cm; hauteur > 10 cm', NULL, 'BA12 - Poche d’écorce décollement > 1 cm; profondeur > 10 cm; hauteur > 10 cm',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'BA2', 'EFI_BA2', 'BA2 - Ecorce crevassée', NULL, 'BA2 - Ecorce crevassée',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'BA21', 'EFI_BA21', 'BA21 - Ecorce crevassée', NULL, 'BA21 - Ecorce crevassée',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'DE', 'EFI_DE', 'DE - Branches mortes', NULL, 'DE - Branches mortes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'DE1', 'EFI_DE1', 'DE1 - Branches mortes', NULL, 'DE1 - Branches mortes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'DE11', 'EFI_DE11', 'DE11 - Branches mortes de Diam 10-20 cm, L ≥ 50 cm, exposé au soleil', NULL, 'DE11 - Branches mortes de Diam 10-20 cm, L ≥ 50 cm, exposé au soleil',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'DE12', 'EFI_DE12', 'DE12 - Branches mortes de Diam > 20 cm, L ≥ 50 cm, exposé au soleil', NULL, 'DE12 - Branches mortes de Diam > 20 cm, L ≥ 50 cm, exposé au soleil',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'DE13', 'EFI_DE13', 'DE13 - Branches mortes de Diam 10-20 cm, L ≥ 50 cm, non exposé au soleil', NULL, 'DE13 - Branches mortes de Diam 10-20 cm, L ≥ 50 cm, non exposé au soleil',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'DE14', 'EFI_DE14', 'DE14 - Branches mortes de Diam > 20 cm, L ≥ 50 cm, non exposé au soleil', NULL, 'DE14 - Branches mortes de Diam > 20 cm, L ≥ 50 cm, non exposé au soleil',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'DE15', 'EFI_DE15', 'DE15 - Cime morte ø ≥ 10 cm', NULL, 'DE15 - Cime morte ø ≥ 10 cm',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'GR', 'EFI_GR', 'GR - Excroissance', NULL, 'GR - Excroissance',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'GR1', 'EFI_GR1', 'GR1 - Cavité des contreforts racinaires', NULL, 'GR1 - Cavité des contreforts racinaires',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'GR11', 'EFI_GR11', 'GR11 - Excroissance de Diam ≥ 5 cm', NULL, 'GR11 - Excroissance de Diam ≥ 5 cm',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'GR12', 'EFI_GR12', 'GR12 - Excroissance de Diam ≥ 10 cm', NULL, 'GR12 - Excroissance de Diam ≥ 10 cm',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'GR13', 'EFI_GR13', 'GR13 - Crevasse du tronc, longueur ≥ 30 cm', NULL, 'GR13 - Crevasse du tronc, longueur ≥ 30 cm',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'GR2', 'EFI_GR2', 'GR2 - Balais de sorcière', NULL, 'GR2 - Balais de sorcière',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'GR21', 'EFI_GR21', 'GR21 - Balais de sorcière, Diam > 50 cm', NULL, 'GR21 - Balais de sorcière, Diam > 50 cm',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'GR22', 'EFI_GR22', 'GR22 - Brogne, gourmands ou broussins', NULL, 'GR22 - Brogne, gourmands ou broussins',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'GR3', 'EFI_GR3', 'GR3 - Chancres et loupes', NULL, 'GR3 - Chancres et loupes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'GR31', 'EFI_GR31', 'GR31 - Loupe, Diam > 20 cm', NULL, 'GR31 - Loupe, Diam > 20 cm',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'GR32', 'EFI_GR32', 'GR32 - Chancre décomposé, Diam > 20 cm', NULL, 'GR32 - Chancre décomposé, Diam > 20 cm',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'EP', 'EFI_EP', 'EP - Épiphytes', NULL, 'EP - Épiphytes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'EP1', 'EFI_EP1', 'EP1 - Carpophores de champignons', NULL, 'EP1 - Carpophores de champignons',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'EP11', 'EFI_EP11', 'EP11 - Polypores annuels, Diam > 5cm', NULL, 'EP11 - Polypores annuels, Diam > 5cm',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'EP12', 'EFI_EP12', 'EP12 - Polypores pérennes, Diam > 10 cm', NULL, 'EP12 - Polypores pérennes, Diam > 10 cm',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'EP13', 'EFI_EP13', 'EP13 - Agaricales charnus, Diam > 5 cm', NULL, 'EP13 - Agaricales charnus, Diam > 5 cm',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'EP14', 'EFI_EP14', 'EP14 - Grands ascomycètes, Diam > 5 cm', NULL, 'EP14 - Grands ascomycètes, Diam > 5 cm',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'EP2', 'EFI_EP2', 'EP2 - Myxomycètes', NULL, 'EP2 - Myxomycètes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'EP21', 'EFI_EP21', 'EP21 - Myxomycètes, Diam > 5 cm', NULL, 'EP21 - Myxomycètes, Diam > 5 cm',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'EP3', 'EFI_EP3', 'EP3 - Cryptogames et phanérogames épiphytes', NULL, 'EP3 - Cryptogames et phanérogames épiphytes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'EP31', 'EFI_EP31', 'EP31 - Bryophytes épiphytes, surface couverte > 25 %', NULL, 'EP31 - Bryophytes épiphytes, surface couverte > 25 %',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'EP32', 'EFI_EP32', 'EP32 - Lichens épiphytes foliacés et ruticuleux ; surface couverte > 25 %', NULL, 'EP32 - Lichens épiphytes foliacés et ruticuleux ; surface couverte > 25 %',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'EP33', 'EFI_EP33', 'EP33 - Lianes; surface couverte > 25 %', NULL, 'EP33 - Lianes; surface couverte > 25 %',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'EP34', 'EFI_EP34', 'EP34 - Fougères épiphytes ; > 5 frondes', NULL, 'EP34 - Fougères épiphytes ; > 5 frondes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'EP35', 'EFI_EP35', 'EP35 - Gui', NULL, 'EP35 - Gui',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'NE', 'EFI_NE', 'NE - Nids et aires', NULL, 'NE - Nids et aires',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'NE1', 'EFI_NE1', 'NE1 - Nids de vertébrés', NULL, 'NE1 - Nids de vertébrés',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'NE11', 'EFI_NE11', 'NE11 - Nids de grands vertébrés, Diam > 80 cm', NULL, 'NE11 - Nids de grands vertébrés, Diam > 80 cm',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'NE12', 'EFI_NE12', 'NE12 - Nids de petits vertébrés, Diam > 10 cm', NULL, 'NE12 - Nids de petits vertébrés, Diam > 10 cm',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'NE2', 'EFI_NE2', 'NE2 - Nids d''invertébrés', NULL, 'NE2 - Nids d''invertébrés',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'NE21', 'EFI_NE21', 'NE21 - Nids d’invertébrés', NULL, 'NE21 - Nids d’invertébrés',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'OT', 'EFI_OT', 'OT - Autres microhabitats', NULL, 'OT - Autres microhabitats',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'OT1', 'EFI_OT1', 'OT1 - Coulées de sève ou de résine', NULL, 'OT1 - Coulées de sève ou de résine',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'OT11', 'EFI_OT11', 'OT11 - Coulée de sève, > 50 cm', NULL, 'OT11 - Coulée de sève, > 50 cm',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'OT12', 'EFI_OT12', 'OT12 - Coulées et poches de résine, > 50 cm', NULL, 'OT12 - Coulées et poches de résine, > 50 cm',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'OT2', 'EFI_OT2', 'OT2 - Microsols', NULL, 'OT2 - Microsols',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'OT21', 'EFI_OT21', 'OT21 - Microsol du houppier', NULL, 'OT21 - Microsol du houppier',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'OT22', 'EFI_OT22', 'OT22 - Microsol de l’écorce', NULL, 'OT22 - Microsol de l’écorce',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'OT23', 'EFI_OT23', 'OT23 - Microsol dans une chandelle', NULL, 'OT23 - Microsol dans une chandelle',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'OT3', 'EFI_OT3', 'OT3 - Galette de chablis', NULL, 'OT3 - Galette de chablis',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'OT31', 'EFI_OT31', 'OT31 - Cuvette dans le sol', NULL, 'OT31 - Cuvette dans le sol',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), 'OT32', 'EFI_OT32', 'OT32 - Entrelacs racinaires', NULL, 'OT32 - Entrelacs racinaires',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '500', 'IRSTEA_500', '500 - Individu - conformation arbre', NULL, '500 - Individu - conformation arbre',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '520', 'IRSTEA_520', '520 - Arbre mort sur pied - squelette du houppier présent', NULL, '520 - Arbre mort sur pied - squelette du houppier présent',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '530', 'IRSTEA_530', '530 - Arbre vivant - branches mortes', NULL, '530 - Arbre vivant - branches mortes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '531', 'IRSTEA_531', '531 - Arbre vivant - branches mortes (>10% et <25% du Vtot)', NULL, '531 - Arbre vivant - branches mortes (>10% et <25% du Vtot)',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '532', 'IRSTEA_532', '532 - Arbre vivant - branches mortes (>25% et <50% du Vtot)', NULL, '532 - Arbre vivant - branches mortes (>25% et <50% du Vtot)',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '533', 'IRSTEA_533', '533 - Arbre vivant - branches mortes (≥50% du Vtot)', NULL, '533 - Arbre vivant - branches mortes (≥50% du Vtot)',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '540', 'IRSTEA_540', '540 - Arbre vivant - tête cassée (non cicatrisé)', NULL, '540 - Arbre vivant - tête cassée (non cicatrisé)',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '550', 'IRSTEA_550', '550 - Fourche', NULL, '550 - Fourche',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '551', 'IRSTEA_551', '551 - Fourche cassée (charpentière)', NULL, '551 - Fourche cassée (charpentière)',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '560', 'IRSTEA_560', '560 - Rejets de souches', NULL, '560 - Rejets de souches',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '561', 'IRSTEA_561', '561 - Rejets de souches (+ de 5 ou > 50cm de long)', NULL, '561 - Rejets de souches (+ de 5 ou > 50cm de long)',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '600', 'IRSTEA_600', '600 - Présence de dendromicrohabitats', NULL, '600 - Présence de dendromicrohabitats',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '610', 'IRSTEA_610', '610 - Champignons', NULL, '610 - Champignons',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '611', 'IRSTEA_611', '611 - Carpophore de polypore (1-2; Diam > 5cm)', NULL, '611 - Carpophore de polypore (1-2; Diam > 5cm)',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '612', 'IRSTEA_612', '612 - Carpophore de polypore (> 3; Diam > 5cm)', NULL, '612 - Carpophore de polypore (> 3; Diam > 5cm)',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '613', 'IRSTEA_613', '613 - Carpophore de polypore (> 10cm couvert)', NULL, '613 - Carpophore de polypore (> 10cm couvert)',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '620', 'IRSTEA_620', '620 - Cavité de pic (ouverture > 2cm de Diam)', NULL, '620 - Cavité de pic (ouverture > 2cm de Diam)',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '621', 'IRSTEA_621', '621 - Cavité naturelle (ouverture > 2cm de Diam)', NULL, '621 - Cavité naturelle (ouverture > 2cm de Diam)',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '622', 'IRSTEA_622', '622 - Cavités de pic (ouverture > 2cm de Diam)', NULL, '622 - Cavités de pic (ouverture > 2cm de Diam)',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '623', 'IRSTEA_623', '623 - Cavité de pic (ouverture > 2cm de Diam)', NULL, '623 - Cavité de pic (ouverture > 2cm de Diam)',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '624', 'IRSTEA_624', '624 - Cavité de pic (ouverture > 2cm de Diam)', NULL, '624 - Cavité de pic (ouverture > 2cm de Diam)',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '625', 'IRSTEA_625', '625 - Cavité de pic (ouverture > 2cm de Diam)', NULL, '625 - Cavité de pic (ouverture > 2cm de Diam)',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '630', 'IRSTEA_630', '630 - Fentes', NULL, '630 - Fentes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '631', 'IRSTEA_631', '631 - Fente causée par la foudre (≥ 3m; aubier atteint)', NULL, '631 - Fente causée par la foudre (≥ 3m; aubier atteint)',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '632', 'IRSTEA_632', '632 - Fente (L ≥ 25cm; Profondeur ≥ 2cm)', NULL, '632 - Fente (L ≥ 25cm; Profondeur ≥ 2cm)',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '640', 'IRSTEA_640', '640 - Caractéristique de l''écorce', NULL, '640 - Caractéristique de l''écorce',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '641', 'IRSTEA_641', '641 - Ecorce déhiscente (≥ 5x5cm; 2cm de décollement)', NULL, '641 - Ecorce déhiscente (≥ 5x5cm; 2cm de décollement)',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '642', 'IRSTEA_642', '642 - Ecorce déhiscente avec pourriture (≥ 5x5cm; 2cm de décollement)', NULL, '642 - Ecorce déhiscente avec pourriture (≥ 5x5cm; 2cm de décollement)',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '643', 'IRSTEA_643', '643 - Écorce absente (≥ 5x5cm)', NULL, '643 - Écorce absente (≥ 5x5cm)',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '644', 'IRSTEA_644', '644 - Éclatement noir de l''écorce', NULL, '644 - Éclatement noir de l''écorce',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '650', 'IRSTEA_650', '650 - Blessures, galles', NULL, '650 - Blessures, galles',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '651', 'IRSTEA_651', '651 - Blessure récente ≥ 10cm de Diam', NULL, '651 - Blessure récente ≥ 10cm de Diam',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '652', 'IRSTEA_652', '652 - Présence d''un chancre (Diam ≥ 10cm de Diam)', NULL, '652 - Présence d''un chancre (Diam ≥ 10cm de Diam)',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '653', 'IRSTEA_653', '653 - Balais de sorcière/brogne', NULL, '653 - Balais de sorcière/brogne',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '660', 'IRSTEA_660', '660 - Présence de résine', NULL, '660 - Présence de résine',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '661', 'IRSTEA_661', '661 - Coulée de résine/sève, ≥ 30 cm', NULL, '661 - Coulée de résine/sève, ≥ 30 cm',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '662', 'IRSTEA_662', '662 - Faible coulée de résine/sève', NULL, '662 - Faible coulée de résine/sève',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '670', 'IRSTEA_670', '670 - Lierre, bryophytes', NULL, '670 - Lierre, bryophytes',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '671', 'IRSTEA_671', '671 - Bryophytes sur > 1/2 surface', NULL, '671 - Bryophytes sur > 1/2 surface',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECOLOGIE'), '672', 'IRSTEA_672', '672 - Lierre sur > 1/2 surface', NULL, '672 - Lierre sur > 1/2 surface',  NULL, 'PSDRF', 'Validé', true);

-- Code dureté
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_DURETE'), '1', '1', 'Dur ou non altéré', NULL, 'Dur ou non altéré',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_DURETE'), '2', '2', 'Pourriture <1/4 du diamètre', NULL, 'Pourriture <1/4 du diamètre',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_DURETE'), '3', '3', 'Pourriture entre 1/4 et 1/2 du diamètre', NULL, 'Pourriture entre 1/4 et 1/2 du diamètre',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_DURETE'), '4', '4', 'Pourriture entre 1/2 et 3/4 du diamètre', NULL, 'Pourriture entre 1/2 et 3/4 du diamètre',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_DURETE'), '5', '5', 'Pourriture supérieure à 3/4.', NULL, 'Pourriture supérieure à 3/4.',  NULL, 'PSDRF', 'Validé', true);

-- Code écorce
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECORCE'), '3', '3', 'Présente sur moins de 50% de la surface', NULL, 'Présente sur moins de 50% de la surface',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECORCE'), '4', '4', 'Absente du billon', NULL, 'Absente du billon',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECORCE'), '1', '1', 'Présente sur tout le billon', NULL, 'Présente sur tout le billon',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ECORCE'), '2', '2', 'Présente sur plus de 50% de la surface', NULL, 'Présente sur plus de 50% de la surface',  NULL, 'PSDRF', 'Validé', true);

-- Code Castor
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_CASTOR'), '0', '0', 'absent', NULL, 'absent',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_CASTOR'), '1', '1', 'Quelques brins', NULL, 'Quelques brins',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_CASTOR'), '2', '2', '< 50% des brins', NULL, '< 50% des brins',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_CASTOR'), '3', '3', '> 50% des brins', NULL, '> 50% des brins',  NULL, 'PSDRF', 'Validé', true);

-- Code Frottis
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_FROTTIS'), '0', '0', 'absent', NULL, 'absent',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_FROTTIS'), '1', '1', 'Quelques brins', NULL, 'Quelques brins',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_FROTTIS'), '2', '2', '< 50% des brins', NULL, '< 50% des brins',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_FROTTIS'), '3', '3', '> 50% des brins', NULL, '> 50% des brins',  NULL, 'PSDRF', 'Validé', true);

-- Code Boutis
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_BOUTIS'), '0', '0', 'absent', NULL, 'absent',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_BOUTIS'), '1', '1', '< 5% de la placette', NULL, '< 5% de la placette',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_BOUTIS'), '2', '2', 'de 5 à 50% de la placette', NULL, 'de 5 à 50% de la placette',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_BOUTIS'), '3', '3', '> 50% des brins', NULL, '> 50% des brins',  NULL, 'PSDRF', 'Validé', true);

-- Etat sanitaire
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_SANITAIRE'), '0', '0',
'Absence de symptôme de dépérissement', 'Houppier opaque, ramification fine dense',
'Absence de symptôme de dépérissement', 'Houppier opaque, ramification fine dense', 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_SANITAIRE'), '1', '1',
'1', 'rameaux fins desséchés dans la périphérie du houppier ; Et/ou présence de « fenêtres disjointes » ; Et/ou rameaux en « fouets »',
'1', 'rameaux fins desséchés dans la périphérie du houppier ; Et/ou présence de « fenêtres disjointes » ; Et/ou rameaux en « fouets »', 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_SANITAIRE'), '2', '2',
'2', 'Branches desséchées dans le houppier, mais moins de 50% ; Et/ou échancrure nette dans le houppier ; Et/ou feuilles en paquets',
'2', 'Branches desséchées dans le houppier, mais moins de 50% ; Et/ou échancrure nette dans le houppier ; Et/ou feuilles en paquets', 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_SANITAIRE'), '3', '3',
'3', 'Branches mortes composant plus de 50% du houppier',
'3', 'Branches mortes composant plus de 50% du houppier', 'PSDRF', 'Validé', true);


-- Typo arbres
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_TYPO_ARBRES'), 'A', 'A', 'Arbres',
'il correspond aux bois morts qui peuvent être cubés en utilisant le même tarif de cubage que pour les arbres vivants. C''est le cas des arbres qui viennent de dépérir, ou bien des arbres qui ont perdu une partie de leurs rameaux fins, mais pas de parties importantes de leur squelette.', 'Arbres',
'il correspond aux bois morts qui peuvent être cubés en utilisant le même tarif de cubage que pour les arbres vivants. C''est le cas des arbres qui viennent de dépérir, ou bien des arbres qui ont perdu une partie de leurs rameaux fins, mais pas de parties importantes de leur squelette.', 'PSDRF', 'Validé',  true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_TYPO_ARBRES'), 'V', 'V', 'Chandelles',
'il comprend les volis  de hauteur supérieure à 1,30 m, ainsi que les arbres ayant perdu une partie importante de leur squelette. Ces objets seront cubés en appliquant au diamètre à 1,30m une décroissance métrique par défaut de 1cm/m et en estimant sur le terrain une hauteur. Le choix de la décroissance métrique pourra être adapté localement.', 'Chandelles',  'il comprend les volis  de hauteur supérieure à 1,30 m, ainsi que les arbres ayant perdu une partie importante de leur squelette. Ces objets seront cubés en appliquant au diamètre à 1,30m une décroissance métrique par défaut de 1cm/m et en estimant sur le terrain une hauteur. Le choix de la décroissance métrique pourra être adapté localement.', 'PSDRF', 'Validé',  true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_TYPO_ARBRES'), 'S', 'S', 'Souches',
'il comprend les volis  de hauteur inférieure à 1,30 m, ainsi que les souches non déracinées. Les souches sont échantillonnées quelque soit leur hauteur. Ce type de bois mort sur pied sera cubé à partir d''un diamètre médian et d''une hauteur (formule du cylindre). On distinguera les souches d''origine naturelle (SN) et les souches d''origine anthropique (SA), issues de la gestion forestière.', 'Souches',
'il comprend les volis  de hauteur inférieure à 1,30 m, ainsi que les souches non déracinées. Les souches sont échantillonnées quelque soit leur hauteur. Ce type de bois mort sur pied sera cubé à partir d''un diamètre médian et d''une hauteur (formule du cylindre). On distinguera les souches d''origine naturelle (SN) et les souches d''origine anthropique (SA), issues de la gestion forestière.', 'PSDRF', 'Validé',  true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_TYPO_ARBRES'), 'SA', 'SA', 'Souches d''origine anthropique', NULL, 'Souches d''origine anthropique',  NULL, 'PSDRF', 'Validé',  true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_TYPO_ARBRES'), 'SN', 'SN', 'Souches d''origine anthropique', NULL, 'Souches d''origine anthropique',  NULL, 'PSDRF', 'Validé', true);


-- Abroutissement
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ABROUTIS'), '0', '0', 'absent', NULL, 'absent',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ABROUTIS'), '1', '1', 'Quelques brins', NULL, 'Quelques brins',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ABROUTIS'), '2', '2', '< 50% des brins de l''essence concernée', NULL, '< 50% des brins de l''essence concernée',  NULL, 'PSDRF', 'Validé', true);
INSERT INTO t_nomenclatures (id_type, cd_nomenclature, mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut, active)
VALUES (ref_nomenclatures.get_id_nomenclature_type('PSDRF_ABROUTIS'), '3', '3', '> 50% des brins de l''essence concernée', NULL, '> 50% des brins de l''essence concernée',  NULL, 'PSDRF', 'Validé', true);


-- Essences
SET search_path = pr_psdrf, pg_catalog, public;

INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('ALI', 197762, 'Alisier sp.', 'AF', 'cyan4', 'Sorbus sp');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('AIL', 80824, 'Ailante', 'AF', 'azure2', 'Ailantus altissima');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('AUBE', 191232, 'Aubépine sp.', 'AF', 'deepskyblue2', 'Crataegus sp');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('AUL', 188987, 'Aulne sp.', 'AF', 'azure2', 'Alnus sp');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('BER', 189836, 'Berberis', 'AF', 'azure2', 'Berberis sp');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('BOU', 189857, 'Bouleau sp.', 'AF', 'cyan4', 'Betula sp');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('BRA', 190021, 'Barchypode sp.', 'AF', 'azure2', 'Brachypodium sp');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('AJE', 128114, 'Ajonc d''Europe', 'AF', 'azure2', 'Ulex europaeus');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('ALF', 124325, 'Alisier de Fontainebleau', 'AF', 'cyan4', 'Sorbus latifolia');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('ALB', 124306, 'Alisier blanc', 'AF', 'cyan4', 'Sorbus aria');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('ALN', 124314, 'Alisier nain', 'AF', NULL, 'Sorbus chamaemespilus');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('ALT', 124346, 'Alisier torminal', 'AF', 'cyan4', 'Sorbus torminalis');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('AME', 82103, 'Amélanchier', 'AF', 'azure2', 'Amelanchier ovalis');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('ARB', 83481, 'Arbousier commun', 'AF', 'azure2', 'Arbutus unedo');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('AUBP', 92864, 'Aubépine épineuse', 'AF', 'azure2', 'Crataegus laevigata');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('AUBM', 92876, 'Aubépine monogyne', 'AF', 'azure2', 'Crataegus monogyna');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('AUB', 81570, 'Aulne blanc', 'AF', 'cyan4', 'Alnus incana');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('AUG', 81569, 'Aulne glutineux', 'AF', 'cyan4', 'Alnus glutinosa');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('AUV', 81563, 'Aulne vert', 'AF', 'cyan4', 'Alnus viridis');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('BAH', 103547, 'Baslamine Himalaya', 'HER', 'azure2', 'Impatiens glandulifera');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('BOJ', 94435, 'Bois-joli', 'AF', 'azure2', 'Daphne mezereum');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('BOP', 85904, 'Bouleau blanc', 'AF', 'cyan4', 'Betula pubescens');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('BOV', 85903, 'Bouleau verruqueux', 'AF', 'cyan4', 'Betula pendula');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('BOUR', 98887, 'Bourdaine', 'AF', 'azure2', 'Frangula alnus');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('BRU', 96691, 'Bruyere à balais', 'AF', 'azure2', 'Erica scoparia');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('CAM', 106595, 'Camerisier à balais', 'AF', 'azure2', 'Lonicera xylosteum');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('CAB', 106555, 'Camerisier bleu', 'AF', 'azure2', 'Lonicera caerulea');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('CEA', 89452, 'Cèdre Atlas', 'AR', 'thistle2', 'Cedrus atlantica');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('CEL', 89455, 'Cèdre du Liban', 'AR', 'thistle2', 'Cedrus libani');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('CEG', 116109, 'Cerisier à grappe', 'AF', 'cyan4', 'Prunus padus');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('CER', 116054, 'Cerisier aigre', 'AF', 'cyan4', 'Prunus cerasus');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('CST', 116096, 'Cerisier de Sainte Lucie', 'AF', 'cyan4', 'Prunus mahaleb');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('CET', 116137, 'Cerisier tardif', 'AF', 'cyan4', 'Prunus serotina');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('CHA', 89200, 'Charme', 'CHA', 'dodgerblue', 'Carpinus betulus');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('CHT', 89304, 'Châtaignier', 'CHT', 'gold3', 'Castanea sativa');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('CHC', 116670, 'Chêne chevelu', 'CHE', 'gold', 'Quercus cerris');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('CHL', 116774, 'Chêne liège', 'CHE', 'gold', 'Quercus suber');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('CHP', 116759, 'Chêne pédonculé', 'CHE', 'gold', 'Quercus robur');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('CHY', 116751, 'Chêne pubescent', 'CHE', 'gold', 'Quercus pubescens');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('CHR', 116762, 'Chêne rouge', 'CHE', 'gold', 'Quercus rubra');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('CHS', 521658, 'Chêne sessile', 'CHE', 'gold', 'Quercus petraea');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('CHV', 116704, 'Chêne vert', 'CHE', 'gold', 'Quercus ilex');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('CHEV', 106581, 'Chêvrefeuille', 'AF', 'azure2', 'Lonicera periclymenum');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('SOD', 124319, 'Cormier', 'AF', 'cyan4', 'Sorbus domestica');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('COM', 92497, 'Cornouiller mâle', 'AF', 'azure2', 'Cornus mas');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('COS', 92501, 'Cornouiller sanguin', 'AF', 'darkorange', 'Cornus sanguinea');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('CYV', 93590, 'Cyprès de Provence', 'AR', 'thistle2', 'Cupressus sempervirens');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('CYA', 104715, 'Cytise des Alpes', 'AF', 'azure2', 'Laburnum alpinum');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('CYC', 104716, 'Cytise commun', 'AF', 'azure2', 'Laburnum vulgare');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('DOU', 116216, 'Douglas', 'AR', 'thistle2', 'Pseudotsuga menziesii');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('EGL', 118073, 'Eglantier commun', 'AF', 'azure2', 'Rosa canina');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('EPC', 113432, 'Epicea commun', 'EPI', 'dodgerblue4', 'Picea abies');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('ERO', 79770, 'Erable à feuilles obier', 'AF', 'cyan4', 'Acer opalus');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('ERC', 79734, 'Erable champêtre', 'ERA', 'lightblue2', 'Acer campestre');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('ERM', 79763, 'Erable Montpellier', 'ERA', 'lightblue2', 'Acer monspessulanum');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('ERN', 79766, 'Erable negundo', 'ERA', 'dodgerblue4', 'Acer negundo');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('ERP', 79779, 'Erable plane', 'ERA', 'lightblue2', 'Acer platanoides');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('ERS', 79783, 'Erable sycomore', 'ERA', 'lightblue2', 'Acer pseudoplatanus');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('IND', NULL, 'Espèce indéterminée', 'AF', 'azure2', NULL);
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('F.D', NULL, 'Feuillus divers', 'AF', 'darkolivegreen4', NULL);
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('FOU', NULL, 'Fougère sp.', 'AF', 'azure2', 'Filicophyta sp');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('FRAM', 119149, 'Framboisier', 'AF', 'azure2', 'Rubus idaeus');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('FRAG', 119698, 'Fragon petit houx', 'AF', 'azure2', 'Ruscus aculeatus');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('FRF', 98933, 'Frêne à fleurs', 'FRE', 'lightseagreen', 'Fraxinus ornus');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('FRC', 98921, 'Frêne commun', 'FRE', 'lightseagreen', 'Fraxinus excelsior');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('FRO', 98910, 'Frêne oxyphylle', 'FRE', 'lightseagreen', 'Fraxinus angustifolia');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('FRU', NULL, 'Fruitier', 'AF', 'azure2', NULL);
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('FUS', 609982, 'Fusain Europe', 'AF', 'azure2', 'Euonymus europaeus');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('GEB', 94164, 'Genêt à balais', 'AF', 'azure2', 'Cytisus scoparius');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('GEC', 104397, 'Genévrier commun', 'AF', 'azure2', 'Juniperus communis');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('GEN', 136974, 'Genévrier nain', 'AF', 'azure2', 'Juniperus sibirica');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('GET', 104419, 'Genévrier thurifere', 'AF', 'azure2', 'Juniperus thurifera');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('HET', 97947, 'Hêtre', 'HET', 'green3', 'Fagus sylvatica');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('HOU', 103514, 'Houx', 'AF', 'azure2', 'Ilex aquifolium');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('IF', 125816, 'If commun', 'AR', 'thistle2', 'Taxus baccata');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('LAU', 94432, 'Laurier des bois', 'AF', 'azure2', 'Daphne laureola');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('LIA', NULL, 'Liane sp.', 'AF', 'azure2', NULL);
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('MAR', 80334, 'Marronnier', 'AF', 'azure2', 'Aesculus hippocastanum');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('BUD', 190093, 'Arbre à papillon', 'AF', 'azure2', 'Buddleja sp');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('BUI', 190133, 'Buis', 'AF', 'azure2', 'Buxus sp');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('CAL', 190223, 'Callune sp.', 'AF', 'azure2', 'Calluna sp');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('CALO', 190229, 'Calocedre sp.', 'AR', 'thistle2', 'Calocedrus sp');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('CAR', 190355, 'Carex sp.', 'AF', 'azure2', 'Carex sp');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('CED', 190425, 'Cedre sp.', 'AR', 'thistle2', 'Cedrus sp');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('CHE', 197006, 'Chêne sp.', 'CHE', 'gold', 'Quercus sp');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('CHX', 116842, 'Chêne hybride', 'CHE', 'gold', 'Quercus rosacea');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('COR', 191160, 'Cornouiller sp.', 'AF', 'azure2', 'Cornus sp');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('CIS', 190862, 'Ciste sp.', 'AF', 'azure2', 'Cistus sp');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('CLEM', 190914, 'Clematite', 'AF', 'azure2', 'Clematis sp');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('CHZ', 116754, 'Chêne tauzin', 'CHE', 'gold', 'Quercus pyrenaica');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('COT', 191211, 'Cotoneaster', 'AF', 'azure2', 'Cotoneaster sp');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('CYT', 193767, 'Cytise sp.', 'AF', 'azure2', 'Laburnum sp');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('ERA', 188731, 'Erable sp.', 'ERA', 'lightblue2', 'Acer sp');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('FIL', 196107, 'Filaire sp.', 'AF', 'azure2', 'Phillyrea sp');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('FRE', 192622, 'Frêne sp.', 'FRE', 'lightseagreen', 'Fraxinus sp');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('GRO', 197220, 'Groseiller', 'AF', 'azure2', 'Ribes sp');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('HOP', 103031, 'Houblon', 'AF', 'azure2', 'Humulus lupulus');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('LIE', 193114, 'Lierre', 'AF', 'azure2', 'Hedera sp');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('MEE', 105042, 'Mélèze d''Europe', 'MEL', 'darkorchid4', 'Larix decidua');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('MER', 116043, 'Merisier', 'AF', 'cyan4', 'Prunus avium');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('NEF', 92854, 'Néflier', 'AF', 'azure2', 'Mespilus germanica');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('NER', 117526, 'Nerprun alaterne', 'AF', 'azure2', 'Rhamnus alaternus');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('NEA', 117528, 'Nerprun des Alpes', 'AF', 'azure2', 'Rhamnus alpina');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('NEN', 117548, 'Nerprun nain', 'AF', 'azure2', 'Rhamnus pumila');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('NEP', 117530, 'Nerprun purgatif', 'AF', 'azure2', 'Rhamnus cathartica');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('NOY', 104076, 'Noyer commun', 'AF', 'azure2', 'Juglans regia');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('NON', 104074, 'Noyer noir d''Amérique', 'AF', 'azure2', 'Juglans nigra');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('ORC', 128175, 'Orme champêtre', 'AF', 'cyan4', 'Ulmus minor');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('ORT', 128169, 'Orme de montagne (blanc)', 'AF', 'cyan4', 'Ulmus glabra');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('ORD', 128171, 'Orme diffus', 'AF', 'cyan4', 'Ulmus laevis');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('OSJ', 120512, 'Osier jaune', 'AF', 'cyan4', 'Salix x rubens');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('PAU', 112560, 'Paulownia tomentosa', 'AF', 'cyan4', 'Paulownia tomentosa');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('PEB', 115110, 'Peuplier blanc', 'PEU', 'gray80', 'Populus alba');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('PEN', 115145, 'Peuplier noir', 'PEU', 'gray80', 'Populus nigra');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('TRE', 115156, 'Peuplier tremble', 'PEU', 'gray80', 'Populus tremula');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('P.X', 138840, 'Pin à crochets', 'PIN', 'orangered3', 'Pinus uncinata');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('P.B', 162292, 'Pin brutia', 'PIN', 'orangered3', 'Pinus brutia');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('P.C', 113651, 'Pin cembro', 'PIN', 'orangered3', 'Pinus cembra');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('P.A', 113665, 'Pin Alep', 'PIN', 'orangered3', 'Pinus halepensis');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('P.M', 113689, 'Pin maritime', 'PIN', 'orangered3', 'Pinus pinaster');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('P.MU', 113682, 'Pin mugo', 'PIN', 'orangered3', 'Pinus mugo');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('P.P', 113690, 'Pin pignon', 'PIN', 'orangered3', 'Pinus pinea');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('P.S', 113703, 'Pin sylvestre', 'PIN', 'orangered3', 'Pinus sylvestris');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('P.W', 113702, 'Pin Weymouth', 'PIN', 'orangered3', 'Pinus strobus');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('POI', 116574, 'Poirier sauvage', 'AF', 'cyan4', 'Pyrus communis');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('POM', 107217, 'Pommier sauvage', 'AF', 'cyan4', 'Malus sylvestris');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('POD', 107207, 'Pommier domestique', 'AF', 'azure2', 'Malus domestica');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('PRU', 116142, 'Prunellier', 'AF', 'darkorange3', 'Prunus spinosa');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('PRB', 116050, 'Prunier de Briancon', 'AF', 'darkorange3', 'Prunus brigantina');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('R.D', NULL, 'Résineux divers', 'AR', 'thistle2', NULL);
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('RUS', 119698, 'Ruscus', 'AF', 'azure2', 'Ruscus aculeatus');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('S.P', 79319, 'Sapin pectiné', 'SAP', 'darkviolet', 'Abies alba');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('S.V', 79333, 'Sapin de Vancouver', 'SAP', 'darkviolet', 'Abies grandis');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('S.N', 79345, 'Sapin de Nordmann', 'SAP', 'darkviolet', 'Abies nordmanniana');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('SAT', 120246, 'Saule à trois étamines', 'AF', 'cyan4', 'Salix triandra');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('SAO', 119952, 'Saule à oreillettes', 'AF', 'cyan4', 'Salix aurita');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('SAB', 119915, 'Saule blanc', 'AF', 'cyan4', 'Salix alba');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('SAF', 120040, 'Saule fragile', 'AF', 'cyan4', 'Salix fragilis');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('SAM', 119977, 'Saule Marsault', 'AF', 'cyan4', 'Salix caprea');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('SAMU', 120459, 'Saule Multinervé', 'AF', 'cyan4', 'Salix x multinervis');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('SAR', 119948, 'Saule roux', 'AF', 'cyan4', 'Salix atrocinerea');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('SARU', 120513, 'Saule rouge', 'AF', 'cyan4', 'Salix x rubra');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('SAV', 120260, 'Saule des Vanniers', 'AF', 'cyan4', 'Salix viminalis');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('SOR', 124308, 'Sorbier oiseleurs', 'AF', 'cyan4', 'Sorbus aucuparia');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('SUN', 120717, 'Sureau noir', 'AF', 'azure2', 'Sambucus nigra');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('THU', NULL, 'Thuya sp.', 'AR', 'thistle2', 'Thuya sp');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('TIG', 126650, 'Tilleul gde feuille', 'AF', 'cyan4', 'Tilia platyphyllos');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('TIP', 126628, 'Tilleul petite feuille', 'AF', 'cyan4', 'Tilia cordata');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('VIOL', 129083, 'Viorne lantane', 'AF', 'azure2', 'Viburnum lantana');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('VIOO', 129087, 'Viorne obier', 'AF', 'azure2', 'Viburnum opulus');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('PRUM', 116142, 'Prunelier', 'AF', 'azure2', 'Prunus spinosa');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('PRUS', 116142, 'Prunelier', 'AF', 'azure2', 'Prunus spinosa');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('MEL', 193857, 'Mélèze', 'MEL', 'darkorchid4', 'Larix sp');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('MYR', 198842, 'Myrtille', 'AF', 'azure2', 'Vaccinium sp');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('NOI', 92606, 'Noisetier', 'AF', 'azure2', 'Corylus avellana');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('ORM', 198789, 'Orme sp.', 'AF', 'cyan4', 'Ulmus sp');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('PEI', 149993, 'Peuplier Italie', 'PEU', 'gray80', 'Populus nigra Italica');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('PEU', 196579, 'Peuplier sp.', 'PEU', 'gray80', 'Populus sp.');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('PEX', 115168, 'Peuplier hybride', 'PEU', 'gray80', 'Populus ×canescens');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('PIN', 196293, 'Pin', 'PIN', 'orangered3', 'Pinus sp');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('P.L', 138841, 'Pin laricio', 'PIN', 'orangered3', 'Pinus nigra ssp laricio');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('PLA', 196366, 'Platane', 'AF', 'azure2', 'Platanus sp');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('P.O', 113683, 'Pin noir Autriche', 'PIN', 'orangered3', 'Pinus nigra ssp nigra');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('PYR', 196996, 'Pyrus sp.', 'AF', 'azure2', 'Pyrus sp.');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('P.Z', 138844, 'Pin de Salzmann', 'PIN', 'orangered3', 'Pinus nigra ssp salzmanni');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('REN', 192520, 'Rénouée', NULL, 'azure2', 'Fallopia sp.');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('RHO', 197174, 'Rhododendron', 'AF', 'azure2', 'Rhododendron sp');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('ROB', 117860, 'Robinier faux acacia', 'AF', 'cyan4', 'Robinia pseudoacacia');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('RON', 197281, 'Ronce', 'AF', 'azure2', 'Rubus sp');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('SAC', 119948, 'Saule cendré', 'AF', 'cyan4', 'Salix cinerea ssp. oleifolia');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('SAL', 140470, 'Saule de Lambert', 'AF', 'cyan4', 'Salix purpurea subsp Lambertiana');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('SAP', 188665, 'Sapin sp.', 'SAP', 'darkviolet', 'Abies sp.');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('SAU', 197334, 'Saule sp.', 'AF', 'cyan4', 'Salix sp');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('SUR', 445553, 'Sureau sp.', 'AF', 'azure2', 'Sambucus sp');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('TIL', 198461, 'Tilleul sp.', 'AF', 'cyan4', 'Tilia sp');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('TRO', 194125, 'Troëne', 'AF', 'azure2', 'Ligustrum sp');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('FIG', 98653, 'Figuier', 'AF', 'azure2', 'Ficus carica');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('MUR', 194913, 'Murier', 'AF', 'azure2', 'Morus sp');
INSERT INTO bib_essences (code_essence, cd_nom, nom, ess_reg, couleur, nom_latin) VALUES ('MIC', 190439, 'Micocoulier', 'AF', 'azure2', 'Celtis sp');
