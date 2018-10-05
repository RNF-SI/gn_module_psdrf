
SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

CREATE SCHEMA pr_psdrf;

SET search_path = pr_psdrf, public, pg_catalog;

SET default_with_oids = false;


------------------------
------- TABLES ---------
------------------------

-- Table des dispositifs
CREATE TABLE t_dispositifs (
  id_dispositif serial NOT NULL,
  id_dispositif_orig integer,
  name character varying NOT NULL,
  id_organisme integer
);

CREATE TABLE t_placettes (
  id_placette serial NOT NULL,
  id_dispositif integer NOT NULL,
  id_placette_orig integer,
  strate integer,
  pente real,
  poids_placette real,
  correction_pente boolean NOT NULL DEFAULT TRUE,
  exposition integer,
  habitat character varying (50),
  station character varying,
  typologie character varying,
  groupe character varying,
  groupe1 character varying,
  groupe2 character varying,
  ref_habitat character varying (20),
  precision_habitat text,
  ref_station character varying,
  ref_typologie character varying,
  descriptif_groupe text,
  descriptif_groupe1 text,
  descriptif_groupe2 text,
  precision_gps integer,
  cheminement text,
  geom geometry(POINT, 4326)
);

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
  id_placette integer NOT NULL,
  num_cycle integer,
  coeff integer,
  date_debut date,
  date_fin date,
  diam_lim real,
  date_intervention date,
  nature_intervention character varying,
  gestion character varying
);

CREATE TABLE t_arbres (
  id_arbre serial NOT NULL,
  id_placette integer NOT NULL,
  code_essence character varying(4),
  azimut real,
  distance real,
  tallis boolean,
  observation text
);

CREATE TABLE t_arbres_mesures (
  id_arbre_mesure serial NOT NULL,
  id_arbre integer NOT NULL,
  id_cycle integer NOT NULL,
  diametre1 real,
  diametre2 real,
  type integer,
  hauteur_totale real,
  stade_durete integer,
  stade_ecorce integer,
  coupe char(1),
  limite boolean,
  code_ecolo character varying,
  ref_code_ecolo character varying
);

CREATE TABLE t_regenerations (
  id_regeneration serial NOT NULL,
  id_cycle integer,
  code_essence character varying(4),
  recouvrement real,
  classe1 integer,
  classe2 integer,
  classe3 integer,
  taillis boolean,
  abroutissement boolean,
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
  ess_reg character varying(4),
  couleur character varying(10)
);

CREATE TABLE t_bm_sup_30 (
  id_bm_sup_30 serial NOT NULL,
  id_placette integer NOT NULL,
  id_arbre integer NOT NULL,
  code_essence character varying(4),
  azimut real,
  distance real,
  observation text
);

CREATE TABLE t_bm_sup_30_mesures (
  id_bm_sup_30_mesure serial NOT NULL,
  id_bm_sup_30 integer NOT NULL,
  id_cycle integer NOT NULL,
  diametre_ini real,
  diametre_med real,
  diametre_fin real,
  longueur real,
  contact boolean,
  chablis boolean,
  stade_durete integer,
  stade_ecorce integer,
  observation text
);

-- Table des transects : une ligne par bois mort
CREATE TABLE t_transects (
  id_transect serial NOT NULL,
  id_cycle integer NOT NULL,
  code_essence character varying(4),
  ref_transect char(2),
  distance real,
  diametre real,
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
  num_tarif  character varying(4)
);

CREATE TABLE cor_dispositif_area (
  id_dispositif integer NOT NULL,
  id_area integer NOT NULL
);

-- Lien vers la table roles (utilisateurs)
CREATE TABLE cor_placettes_roles (
  id_placette integer NOT NULL,
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

ALTER TABLE ONLY t_categories
ADD CONSTRAINT pk_t_categories PRIMARY KEY (id_category);

ALTER TABLE ONLY cor_dispositif_area
ADD CONSTRAINT pk_cor_dispositifs_area PRIMARY KEY (id_dispositif, id_area);


ALTER TABLE ONLY cor_placettes_roles
ADD CONSTRAINT pk_cor_placettes_roles PRIMARY KEY (id_placette, id_role);

---------------
--FOREIGN KEY--
---------------

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
  FOREIGN KEY (id_placette) REFERENCES t_placettes (id_placette)
  ON UPDATE CASCADE;

ALTER TABLE ONLY t_categories
  ADD CONSTRAINT fk_t_categories_t_dispositifs
  FOREIGN KEY (id_dispositif) REFERENCES t_dispositifs (id_dispositif)
  ON UPDATE CASCADE;

ALTER TABLE ONLY cor_dispositif_area
  ADD CONSTRAINT fk_cor_dispositifs_area_l_area
  FOREIGN KEY (id_area) REFERENCES ref_geo.l_areas (id_area)
  ON UPDATE CASCADE;

ALTER TABLE ONLY cor_dispositif_area
  ADD CONSTRAINT fk_cor_dispositifs_area_t_dispositifs
  FOREIGN KEY (id_dispositif) REFERENCES t_dispositifs (id_dispositif)
  ON UPDATE CASCADE;

ALTER TABLE ONLY t_tarifs
  ADD CONSTRAINT fk_t_tarifs_t_dispositifs
  FOREIGN KEY (id_dispositif) REFERENCES t_dispositifs (id_dispositif)
  ON UPDATE CASCADE;

ALTER TABLE ONLY t_tarifs
  ADD CONSTRAINT fk_t_tarifs_bib_essences
  FOREIGN KEY (code_essence) REFERENCES bib_essences (code_essence)
  ON UPDATE CASCADE;

ALTER TABLE ONLY cor_placettes_roles
  ADD CONSTRAINT fk_cor_placettes_roles_t_placettes
  FOREIGN KEY (id_placette) REFERENCES t_placettes (id_placette)
  ON UPDATE CASCADE;

ALTER TABLE ONLY cor_placettes_roles
  ADD CONSTRAINT fk_cor_placettes_roles_t_roles
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

ALTER TABLE ONLY t_arbres_mesures
  ADD CONSTRAINT fk_t_arbres_mesures_type
  FOREIGN KEY ("type") REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature)
  ON UPDATE CASCADE;

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
  ADD CONSTRAINT fk_t_regenerations_t_cycles
  FOREIGN KEY (id_cycle) REFERENCES t_cycles (id_cycle)
  ON UPDATE CASCADE;

ALTER TABLE ONLY t_regenerations
  ADD CONSTRAINT fk_t_regenerations_bib_essences
  FOREIGN KEY (code_essence) REFERENCES bib_essences (code_essence)
  ON UPDATE CASCADE;

ALTER TABLE ONLY t_transects
  ADD CONSTRAINT fk_t_transects_t_cycles
  FOREIGN KEY (id_cycle) REFERENCES t_cycles (id_cycle)
  ON UPDATE CASCADE;

ALTER TABLE ONLY t_transects
  ADD CONSTRAINT fk_t_transects_stade_durete
  FOREIGN KEY ("stade_durete") REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature)
  ON UPDATE CASCADE;

ALTER TABLE ONLY t_bm_sup_30_mesures
  ADD CONSTRAINT fk_t_transects_stade_ecorce
  FOREIGN KEY ("stade_ecorce") REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature)
  ON UPDATE CASCADE;

--------------
--CONSTRAINTS--
--------------

-- TODO : contraintes de check_nomenclatures_by_mnemonique

ALTER TABLE t_arbres ADD CONSTRAINT check_t_arbres_azimut
  CHECK (azimut BETWEEN 0 AND 360);

ALTER TABLE t_bm_sup_30 ADD CONSTRAINT check_t_bm_sup_30_azimut
  CHECK (azimut BETWEEN 0 AND 360);
