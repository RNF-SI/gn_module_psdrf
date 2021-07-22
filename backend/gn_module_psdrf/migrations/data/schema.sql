SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

CREATE SCHEMA pr_psdrf;

SET search_path = pr_psdrf, pg_catalog, public;

SET default_with_oids = false;


------------------------
------- TABLES ---------
------------------------

-- Table des dispositifs
CREATE TABLE t_dispositifs (
  id_dispositif serial NOT NULL,
  name character varying NOT NULL,
  id_organisme integer,
  alluvial boolean NOT NULL DEFAULT false
);

CREATE TABLE t_placettes (
  id_placette serial NOT NULL,
  id_dispositif integer NOT NULL,
  id_placette_orig character varying(10),
  strate integer,
  pente real,
  poids_placette real,
  correction_pente boolean,
  exposition integer,
  profondeur_app character varying,
  profondeur_hydr real,
  texture character varying,
  habitat character varying,
  station character varying,
  typologie character varying,
  groupe character varying,
  groupe1 character varying,
  groupe2 character varying,
  ref_habitat character varying,
  precision_habitat text,
  ref_station character varying,
  ref_typologie character varying,
  descriptif_groupe text,
  descriptif_groupe1 text,
  descriptif_groupe2 text,
  precision_gps character varying,
  cheminement text,
  geom geometry(POINT, 2154),
  geom_wgs84 geometry(POINT, 4326)
);

CREATE INDEX idx_t_placettes_geom
    ON t_placettes USING gist
    (geom);

CREATE TABLE t_reperes (
  id_repere serial NOT NULL,
  id_placette integer NOT NULL,
  azimut real,
  distance real,
  diametre real,
  observation text
);

CREATE TABLE t_cycles (
  id_cycle serial NOT NULL,
  id_dispositif integer NOT NULL,
  num_cycle integer NOT NULL,
  coeff integer,
  date_debut date,
  date_fin date,
  diam_lim real,
  monitor character varying (50)
);

CREATE INDEX idx_t_cycles_num_cycle on pr_psdrf.t_cycles (num_cycle);

CREATE TABLE t_arbres (
  id_arbre serial NOT NULL,
  id_arbre_orig integer,
  id_placette integer NOT NULL,
  code_essence character varying(4),
  azimut real,
  distance real,
  taillis boolean,
  observation text
);

CREATE TABLE t_arbres_mesures (
  id_arbre_mesure serial NOT NULL,
  id_arbre integer NOT NULL,
  id_cycle integer NOT NULL,
  diametre1 real,
  diametre2 real,
  type character varying(2),
  hauteur_totale real,
  hauteur_branche real,
  stade_durete integer,
  stade_ecorce integer,
  liane character varying(25),
  diametre_liane real,
  coupe char(1),
  limite boolean,
  id_nomenclature_code_sanitaire integer,
  code_ecolo character varying,
  ref_code_ecolo character varying,
  ratio_hauteur boolean,
  observation text
);

CREATE INDEX idx_t_arbres_mesures_id_cycle on pr_psdrf.t_arbres_mesures (id_cycle);

CREATE TABLE t_regenerations (
  id_regeneration serial NOT NULL,
  id_cycle_placette integer,
  sous_placette integer,
  code_essence character varying(4),
  recouvrement real,
  classe1 integer,
  classe2 integer,
  classe3 integer,
  taillis boolean,
  abroutissement boolean,
  id_nomenclature_abroutissement integer,
  observation text
);

-- Table contenant les limites des catégories de BM selon les dispositifs
CREATE TABLE t_categories (
	id_category serial NOT NULL,
	id_dispositif integer NOT NULL,
	pb real,
	bm real,
	gb real,
	tgb real
);

-- Table contenant les différentes essences
CREATE TABLE bib_essences (
  code_essence character varying(4) NOT NULL,
  cd_nom integer,
  nom character varying,
  nom_latin character varying,
  ess_reg character varying(4),
  couleur character varying(25)
);

CREATE TABLE t_bm_sup_30 (
  id_bm_sup_30 serial NOT NULL,
  id_bm_sup_30_orig integer,
  id_placette integer NOT NULL,
  id_arbre integer,
  code_essence character varying(4),
  azimut real,
  distance real,
  orientation real,
  azimut_souche real,
  distance_souche real,
  observation text
);

CREATE TABLE t_bm_sup_30_mesures (
  id_bm_sup_30_mesure serial NOT NULL,
  id_bm_sup_30 integer NOT NULL,
  id_cycle integer NOT NULL,
  diametre_ini real,
  diametre_med real,
  diametre_fin real,
  diametre_130 real,
  longueur real,
  ratio_hauteur boolean,
  contact real,
  chablis boolean,
  stade_durete integer,
  stade_ecorce integer,
  observation text
);

-- Table des transects : une ligne par bois mort
CREATE TABLE t_transects (
  id_transect serial NOT NULL,
  id_cycle_placette integer NOT NULL,
  code_essence character varying(4),
  ref_transect character varying(2),
  distance real,
  orientation real,
  azimut_souche real,
  distance_souche real,
  diametre real,
  diametre_130 real,
  ratio_hauteur boolean,
  contact boolean,
  angle real,
  chablis boolean,
  stade_durete integer,
  stade_ecorce integer,
  observation text
);

CREATE TABLE t_tarifs (
  id_tarif serial not null,
  id_dispositif integer NOT NULL,
  code_essence  character varying(4) NOT NULL,
  type_tarif character varying(10),
  num_tarif  real
);

CREATE TABLE t_regroupements_essences (
  id_dispositif integer NOT NULL,
  code_essence  character varying(4) NOT NULL,
  code_regroupement character varying(10),
  couleur  character varying(25)
);

CREATE TABLE cor_cycles_placettes (
    id_cycle_placette serial NOT NULL,
    id_cycle integer NOT NULL,
    id_placette integer NOT NULL,
    date_releve date,
    date_intervention character varying,
    nature_intervention character varying,
    gestion_placette character varying,
    id_nomenclature_castor integer,
    id_nomenclature_frottis integer,
    id_nomenclature_boutis integer,
    recouv_herbes_basses real,
    recouv_herbes_hautes real,
    recouv_buissons real,
    recouv_arbres real
);

CREATE INDEX idx_cor_cycles_placettes_id_cycle on pr_psdrf.cor_cycles_placettes (id_cycle);

CREATE TABLE cor_dispositif_area (
  id_dispositif integer NOT NULL,
  id_area integer NOT NULL,
  "order" integer
);

CREATE TABLE cor_dispositif_municipality (
  id_dispositif integer NOT NULL,
  id_municipality character varying(25) NOT NULL
);

-- Lien vers la table roles (utilisateurs)
CREATE TABLE cor_cycles_roles (
  id_cycle integer NOT NULL,
  id_role integer NOT NULL
);


---------------
--PRIMARY KEY--
---------------

ALTER TABLE ONLY t_dispositifs
ADD CONSTRAINT pk_t_dispositifs PRIMARY KEY (id_dispositif);

ALTER TABLE ONLY t_placettes
ADD CONSTRAINT pk_t_placettes PRIMARY KEY (id_placette);

ALTER TABLE ONLY t_reperes
ADD CONSTRAINT pk_t_reperes PRIMARY KEY (id_repere);

ALTER TABLE ONLY t_cycles
ADD CONSTRAINT pk_t_cycles PRIMARY KEY (id_cycle);

ALTER TABLE ONLY t_arbres
ADD CONSTRAINT pk_t_arbres PRIMARY KEY (id_arbre);

ALTER TABLE ONLY t_arbres_mesures
ADD CONSTRAINT pk_t_arbres_mesures PRIMARY KEY (id_arbre_mesure);

ALTER TABLE ONLY t_bm_sup_30
ADD CONSTRAINT pk_t_bm_sup_30 PRIMARY KEY (id_bm_sup_30);

ALTER TABLE ONLY t_bm_sup_30_mesures
ADD CONSTRAINT pk_t_bm_sup_30_mesures PRIMARY KEY (id_bm_sup_30_mesure);

ALTER TABLE ONLY t_regenerations
ADD CONSTRAINT pk_t_regenerations PRIMARY KEY (id_regeneration);

ALTER TABLE ONLY bib_essences
ADD CONSTRAINT pk_bib_essences PRIMARY KEY (code_essence);

ALTER TABLE ONLY t_transects
ADD CONSTRAINT pk_t_transects PRIMARY KEY (id_transect);

ALTER TABLE ONLY t_tarifs
ADD CONSTRAINT pk_t_tarifs PRIMARY KEY (id_tarif);

ALTER TABLE ONLY t_regroupements_essences
ADD CONSTRAINT pk_t_regroupements_essences PRIMARY KEY (id_dispositif, code_essence);

ALTER TABLE ONLY t_categories
ADD CONSTRAINT pk_t_categories PRIMARY KEY (id_category);

ALTER TABLE ONLY cor_cycles_placettes
ADD CONSTRAINT pk_cor_cycles_placettes PRIMARY KEY (id_cycle_placette);

ALTER TABLE ONLY cor_cycles_roles
ADD CONSTRAINT pk_cor_cycles_roles PRIMARY KEY (id_cycle, id_role);

ALTER TABLE ONLY cor_dispositif_area
ADD CONSTRAINT pk_cor_dispositifs_area PRIMARY KEY (id_dispositif, id_area);

ALTER TABLE ONLY cor_dispositif_municipality
ADD CONSTRAINT pk_cor_dispositifs_municipality PRIMARY KEY (id_dispositif, id_municipality);


---------------
--FOREIGN KEY--
---------------
ALTER TABLE ONLY bib_essences
  ADD CONSTRAINT fk_bib_essences_taxref_cd_nom FOREIGN KEY (cd_nom)
    REFERENCES taxonomie.taxref (cd_nom)
    ON UPDATE CASCADE;

ALTER TABLE ONLY t_dispositifs
  ADD CONSTRAINT fk_t_dispositifs_bib_organismes
  FOREIGN KEY (id_organisme) REFERENCES utilisateurs.bib_organismes (id_organisme)
  ON UPDATE CASCADE;

ALTER TABLE ONLY t_placettes
  ADD CONSTRAINT fk_t_placettes_t_dispositifs
  FOREIGN KEY (id_dispositif) REFERENCES t_dispositifs (id_dispositif)
  ON UPDATE CASCADE;

ALTER TABLE ONLY t_reperes
  ADD CONSTRAINT fk_t_reperes_t_placettes
  FOREIGN KEY (id_placette) REFERENCES t_placettes (id_placette)
  ON UPDATE CASCADE;

ALTER TABLE ONLY t_cycles
  ADD CONSTRAINT fk_t_cycles_t_placettes
  FOREIGN KEY (id_dispositif) REFERENCES t_dispositifs (id_dispositif)
  ON UPDATE CASCADE;

ALTER TABLE ONLY t_categories
  ADD CONSTRAINT fk_t_categories_t_dispositifs
  FOREIGN KEY (id_dispositif) REFERENCES t_dispositifs (id_dispositif)
  ON UPDATE CASCADE;

ALTER TABLE ONLY cor_cycles_placettes
  ADD CONSTRAINT fk_cor_cycles_placettes_t_cycles
  FOREIGN KEY (id_cycle) REFERENCES t_cycles (id_cycle)
  ON UPDATE CASCADE;

ALTER TABLE ONLY cor_cycles_placettes
  ADD CONSTRAINT fk_cor_cycles_placettes_t_placettes
  FOREIGN KEY (id_placette) REFERENCES t_placettes (id_placette)
  ON UPDATE CASCADE;

ALTER TABLE ONLY cor_dispositif_area
  ADD CONSTRAINT fk_cor_dispositifs_area_l_area
  FOREIGN KEY (id_area) REFERENCES ref_geo.l_areas (id_area)
  ON UPDATE CASCADE;

ALTER TABLE ONLY cor_dispositif_area
  ADD CONSTRAINT fk_cor_dispositifs_area_t_dispositifs
  FOREIGN KEY (id_dispositif) REFERENCES t_dispositifs (id_dispositif)
  ON UPDATE CASCADE;

ALTER TABLE ONLY cor_dispositif_municipality
  ADD CONSTRAINT fk_cor_dispositifs_municipality_t_dispositifs
  FOREIGN KEY (id_dispositif) REFERENCES t_dispositifs (id_dispositif)
  ON UPDATE CASCADE;

ALTER TABLE ONLY cor_dispositif_municipality
  ADD CONSTRAINT fk_cor_dispositifs_municipality_li_municipalities
  FOREIGN KEY (id_municipality) REFERENCES ref_geo.li_municipalities (id_municipality)
  ON UPDATE CASCADE;

ALTER TABLE ONLY t_tarifs
  ADD CONSTRAINT fk_t_tarifs_t_dispositifs
  FOREIGN KEY (id_dispositif) REFERENCES t_dispositifs (id_dispositif)
  ON UPDATE CASCADE;

ALTER TABLE ONLY t_tarifs
  ADD CONSTRAINT fk_t_tarifs_bib_essences
  FOREIGN KEY (code_essence) REFERENCES bib_essences (code_essence)
  ON UPDATE CASCADE;

ALTER TABLE ONLY t_regroupements_essences
  ADD CONSTRAINT fk_t_reg_essences_bib_essences
  FOREIGN KEY (code_essence) REFERENCES bib_essences (code_essence)
  ON UPDATE CASCADE;

ALTER TABLE ONLY t_regroupements_essences
  ADD CONSTRAINT fk_t_reg_essences_t_dispositifs
  FOREIGN KEY (id_dispositif) REFERENCES t_dispositifs (id_dispositif)
  ON UPDATE CASCADE;

ALTER TABLE ONLY cor_cycles_roles
  ADD CONSTRAINT fk_cor_cycles_roles_t_dispositifs
  FOREIGN KEY (id_cycle) REFERENCES t_cycles (id_cycle)
  ON UPDATE CASCADE;

ALTER TABLE ONLY cor_cycles_roles
  ADD CONSTRAINT fk_cor_cycles_roles_t_roles
  FOREIGN KEY (id_role) REFERENCES utilisateurs.t_roles (id_role)
  ON UPDATE CASCADE;

ALTER TABLE ONLY t_arbres
  ADD CONSTRAINT fk_t_arbres_t_placettes
  FOREIGN KEY (id_placette) REFERENCES t_placettes (id_placette)
  ON UPDATE CASCADE;

ALTER TABLE ONLY t_arbres
  ADD CONSTRAINT fk_t_arbres_bib_essences
  FOREIGN KEY (code_essence) REFERENCES bib_essences (code_essence)
  ON UPDATE CASCADE;

ALTER TABLE ONLY t_arbres_mesures
  ADD CONSTRAINT fk_t_arbres_mesures_t_arbres
  FOREIGN KEY (id_arbre) REFERENCES t_arbres (id_arbre)
  ON UPDATE CASCADE;

ALTER TABLE ONLY t_arbres_mesures
  ADD CONSTRAINT fk_t_arbres_mesures_t_cycles
  FOREIGN KEY (id_cycle) REFERENCES t_cycles (id_cycle)
  ON UPDATE CASCADE;

--ALTER TABLE ONLY t_arbres_mesures
--  ADD CONSTRAINT fk_t_arbres_mesures_type
--  FOREIGN KEY ("type") REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature)
--  ON UPDATE CASCADE;

ALTER TABLE ONLY t_arbres_mesures
  ADD CONSTRAINT fk_t_arbres_mesures_stade_durete
  FOREIGN KEY ("stade_durete") REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature)
  ON UPDATE CASCADE;

ALTER TABLE ONLY t_arbres_mesures
  ADD CONSTRAINT fk_t_arbres_mesures_stade_ecorce
  FOREIGN KEY ("stade_ecorce") REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature)
  ON UPDATE CASCADE;

ALTER TABLE ONLY t_bm_sup_30
  ADD CONSTRAINT fk_t_bm_sup_30_t_placettes
  FOREIGN KEY (id_placette) REFERENCES t_placettes (id_placette)
  ON UPDATE CASCADE;

ALTER TABLE ONLY t_bm_sup_30
  ADD CONSTRAINT fk_t_bm_sup_30_bib_essences
  FOREIGN KEY (code_essence) REFERENCES bib_essences (code_essence)
  ON UPDATE CASCADE;

ALTER TABLE ONLY t_bm_sup_30
  ADD CONSTRAINT fk_t_bm_sup_30_t_arbres
  FOREIGN KEY (id_arbre) REFERENCES t_arbres (id_arbre)
  ON UPDATE CASCADE;

ALTER TABLE ONLY t_bm_sup_30_mesures
  ADD CONSTRAINT fk_t_bm_sup_30_mesures_t_bm_sup_30
  FOREIGN KEY (id_bm_sup_30) REFERENCES t_bm_sup_30 (id_bm_sup_30)
  ON UPDATE CASCADE;

ALTER TABLE ONLY t_bm_sup_30_mesures
  ADD CONSTRAINT fk_t_bm_sup_30_mesures_t_cycles
  FOREIGN KEY (id_cycle) REFERENCES t_cycles (id_cycle)
  ON UPDATE CASCADE;

ALTER TABLE ONLY t_bm_sup_30_mesures
  ADD CONSTRAINT fk_t_bm_sup_30_mesures_stade_durete
  FOREIGN KEY ("stade_durete") REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature)
  ON UPDATE CASCADE;

ALTER TABLE ONLY t_bm_sup_30_mesures
  ADD CONSTRAINT fk_t_bm_sup_30_mesures_stade_ecorce
  FOREIGN KEY ("stade_ecorce") REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature)
  ON UPDATE CASCADE;

ALTER TABLE ONLY t_regenerations
  ADD CONSTRAINT fk_t_regenerations_cor_cycles_placettes
  FOREIGN KEY (id_cycle_placette) REFERENCES cor_cycles_placettes (id_cycle_placette)
  ON UPDATE CASCADE;

ALTER TABLE ONLY t_regenerations
  ADD CONSTRAINT fk_t_regenerations_abroutissement
  FOREIGN KEY ("id_nomenclature_abroutissement") REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature)
  ON UPDATE CASCADE;

-- ALTER TABLE ONLY t_regenerations
--  ADD CONSTRAINT fk_t_regenerations_bib_essences
--  FOREIGN KEY (code_essence) REFERENCES bib_essences (code_essence)
--  ON UPDATE CASCADE;

ALTER TABLE ONLY t_transects
  ADD CONSTRAINT fk_t_transects_cor_cycles_placettes
  FOREIGN KEY (id_cycle_placette) REFERENCES cor_cycles_placettes (id_cycle_placette)
  ON UPDATE CASCADE;

ALTER TABLE ONLY t_transects
  ADD CONSTRAINT fk_t_transects_stade_durete
  FOREIGN KEY ("stade_durete") REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature)
  ON UPDATE CASCADE;

--------------
--CONSTRAINTS--
--------------

ALTER TABLE t_arbres_mesures
  ADD CONSTRAINT chk_t_arbres_nom_stade_durete
  CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(stade_durete, 'PSDRF_DURETE'));

ALTER TABLE t_arbres_mesures
  ADD CONSTRAINT chk_t_arbres_nom_stade_ecorce
  CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(stade_ecorce, 'PSDRF_ECORCE'));

ALTER TABLE t_arbres_mesures
  ADD CONSTRAINT chk_t_arbres_nom_sanitaire
  CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature_code_sanitaire, 'PSDRF_SANITAIRE'));

ALTER TABLE t_regenerations
  ADD CONSTRAINT chk_t_regenerations_abroutis
  CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature_abroutissement, 'PSDRF_ABROUTIS'));

ALTER TABLE cor_cycles_placettes
  ADD CONSTRAINT chk_cor_cycles_placettes_castor
  CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature_castor, 'PSDRF_CASTOR'));

ALTER TABLE cor_cycles_placettes
  ADD CONSTRAINT chk_cor_cycles_placettes_frottis
  CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature_frottis, 'PSDRF_FROTTIS'));

ALTER TABLE cor_cycles_placettes
  ADD CONSTRAINT chk_cor_cycles_placettes_boutis
  CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature_boutis, 'PSDRF_BOUTIS'));

ALTER TABLE t_transects
  ADD CONSTRAINT chk_t_transects_durete
  CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(stade_durete, 'PSDRF_DURETE'));

ALTER TABLE t_transects
  ADD CONSTRAINT chk_t_transects_ecorce
  CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(stade_ecorce, 'PSDRF_ECORCE'));

ALTER TABLE t_bm_sup_30_mesures
  ADD CONSTRAINT check_t_bm_sup_30_durete
  CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(stade_durete, 'PSDRF_DURETE'));

ALTER TABLE t_bm_sup_30_mesures
  ADD CONSTRAINT check_t_bm_sup_30_ecorce
  CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(stade_ecorce, 'PSDRF_ECORCE'));

ALTER TABLE t_arbres ADD CONSTRAINT check_t_arbres_azimut
  CHECK (azimut BETWEEN 0 AND 400);

ALTER TABLE t_bm_sup_30 ADD CONSTRAINT check_t_bm_sup_30_azimut
  CHECK (azimut BETWEEN 0 AND 400);

ALTER TABLE t_regenerations ADD CONSTRAINT check_t_regenerations_ssplac
  CHECK (sous_placette in (1,2,3));

ALTER TABLE t_cycles
  ADD CONSTRAINT unique_t_cycles_id_disp_num_cycle
  UNIQUE (id_dispositif, num_cycle);


--------
-- VUES
-------

CREATE VIEW v_arbres_geom AS
 SELECT a.id_arbre,
    a.id_placette,
    a.code_essence,
    a.azimut,
    a.distance,
    a.taillis,
    a.observation,
    a.id_arbre_orig,
    st_setsrid(st_point(st_x(p.geom) + a.distance * sin(a.azimut * pi() / 200), st_y(p.geom) + a.distance * cos(a.azimut * pi() / 200)), 2154)::geometry(Point,2154) AS g
   FROM pr_psdrf.t_arbres a
     JOIN pr_psdrf.t_placettes p ON a.id_placette = p.id_placette
  WHERE p.geom IS NOT NULL;
