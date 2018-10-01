
SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

CREATE SCHEMA pr_cmr;

SET search_path = pr_cmr, public, pg_catalog;

SET default_with_oids = false;


------------------------
------- TABLES ---------
------------------------

-- table des programmes du modules cmr
-- ex (CMR bouquetin, CMR iguanes ...)
CREATE TABLE t_programs(
    id_program serial NOT NULL,
    program_name character varying NOT NULL,
    program_desc text
);

-- table des sites d'un programme CMR
CREATE TABLE cor_site_program(
    id_site integer NOT NULL,
    id_program integer NOT NULL
);

-- Liste des champs additionnels d'un programme pour générer des pseudos-champs en interfaces sur la table
-- t_operations et cor_operation_extension
CREATE TABLE cor_program_attribut(
    id_attribut serial NOT NULL,
    id_program integer NOT NULL,
    attribut_name character varying(255) NOT NULL,
    attribut_label character varying(50) NOT NULL,
    attribut_value_list text NOT NULL,
    required boolean NOT NULL DEFAULT false,
    attribut_desc text,
    attribut_type character varying(50),
    widget_type character varying(50)
);

-- Table décrivant un individus lors de sa 1ere capture dans un site
CREATE TABLE t_individuals(
    id_individual serial NOT NULL,
    cd_nom integer NOT NULL,
    tag_code character varying(255) NOT NULL,
    tag_location character varying(255) NOT NULL,
    id_site_tag integer NOT NULL,
    id_nomenclature_sex integer,
    comment text
 );

-- Table des individus d'un programme
CREATE TABLE cor_individual_program(
    id_individual integer NOT NULL,
    id_program integer NOT NULL
 );

-- Table décrivant une opération sur un individus
-- Les éventuels médias peuvent être stocké dans la table gn_commons.t_medias via l'UUID unique_id_sinp
 CREATE TABLE t_operations(
     id_operation serial NOT NULL,
     id_individual integer NOT NULL,
     id_site integer NOT NULL,
     geom_point_4346 public.geometry(Geometry,4326),
     geom_point_local public.geometry(Geometry,2154),
     date_min timestamp NOT NULL,
     date_max timestamp NOT NULL,
     id_nomenclature_cmr_action integer,
     id_nomenclature_obs_method integer,
     id_nomenclature_life_stage integer,
     id_nomenclature_bio_condition integer,
     id_nomenclature_determination_method integer,
     determiner character varying,
     unique_id_sinp uuid NOT NULL DEFAULT public.uuid_generate_v4(),
     comment text
 );

-- Table des observateurs d'une opération
 CREATE TABLE cor_operation_observer(
     id_operation integer NOT NULL,
     id_observer integer NOT NULL
 );

-- Table des champs additions collecté lors d'une opérations (facultatif)
CREATE TABLE cor_operation_attribut(
    id_operation integer NOT NULL,
    id_attribut integer NOT NULL,
    attribut_value character varying
);

---------------
--PRIMARY KEY--
---------------
ALTER TABLE ONLY t_programs
    ADD CONSTRAINT pk_t_program_cmr PRIMARY KEY (id_program);

ALTER TABLE ONLY cor_site_program
    ADD CONSTRAINT pk_cor_site_program PRIMARY KEY (id_site, id_program);

ALTER TABLE ONLY cor_program_attribut
    ADD CONSTRAINT pk_cor_site_attribut PRIMARY KEY (id_attribut);

ALTER TABLE ONLY t_individuals
    ADD CONSTRAINT pk_t_individuals PRIMARY KEY (id_individual);

ALTER TABLE ONLY cor_individual_program
    ADD CONSTRAINT pk_cor_individual_program PRIMARY KEY (id_individual, id_program);

ALTER TABLE ONLY t_operations
    ADD CONSTRAINT pk_t_operations PRIMARY KEY (id_operation);

ALTER TABLE ONLY cor_operation_observer
    ADD CONSTRAINT pk_cor_operation_observer PRIMARY KEY (id_operation, id_observer);

ALTER TABLE ONLY cor_operation_attribut
    ADD CONSTRAINT pk_cor_operation_attributs PRIMARY KEY (id_operation, id_attribut);

---------------
--FOREIGN KEY--
---------------

ALTER TABLE ONLY cor_site_program
    ADD CONSTRAINT fk_cor_site_program_t_sites FOREIGN KEY (id_site) REFERENCES gn_monitoring.t_base_sites(id_base_site) ON UPDATE CASCADE;

ALTER TABLE ONLY cor_site_program
    ADD CONSTRAINT fk_cor_site_program_t_program FOREIGN KEY (id_program) REFERENCES pr_cmr.t_programs(id_program) ON UPDATE CASCADE;


ALTER TABLE ONLY cor_program_attribut
    ADD CONSTRAINT fk_cor_program_attribut_t_programms FOREIGN KEY (id_program) REFERENCES pr_cmr.t_programs(id_program) ON UPDATE CASCADE;


ALTER TABLE ONLY t_individuals
    ADD CONSTRAINT fk_t_individuals_t_sites FOREIGN KEY (id_site_tag) REFERENCES gn_monitoring.t_base_sites(id_base_site) ON UPDATE CASCADE;

ALTER TABLE ONLY t_individuals
    ADD CONSTRAINT fk_t_individuals_sex FOREIGN KEY (id_nomenclature_sex) REFERENCES ref_nomenclatures.t_nomenclatures(id_nomenclature) ON UPDATE CASCADE;

ALTER TABLE ONLY cor_individual_program
    ADD CONSTRAINT fk_cor_individual_program_id_individual FOREIGN KEY (id_individual) REFERENCES pr_cmr.t_individuals(id_individual) ON UPDATE CASCADE;

ALTER TABLE ONLY cor_individual_program
    ADD CONSTRAINT fk_cor_individual_program_id_program FOREIGN KEY (id_program) REFERENCES pr_cmr.t_programs(id_program) ON UPDATE CASCADE;

ALTER TABLE ONLY t_operations
    ADD CONSTRAINT fk_t_operations_t_sites FOREIGN KEY (id_site) REFERENCES gn_monitoring.t_base_sites(id_base_site) ON UPDATE CASCADE;

ALTER TABLE ONLY t_operations
    ADD CONSTRAINT fk_t_operations_obs_meth FOREIGN KEY (id_nomenclature_obs_method) REFERENCES ref_nomenclatures.t_nomenclatures(id_nomenclature) ON UPDATE CASCADE;


ALTER TABLE ONLY t_operations
    ADD CONSTRAINT fk_t_operations_life_stage FOREIGN KEY (id_nomenclature_life_stage) REFERENCES ref_nomenclatures.t_nomenclatures(id_nomenclature) ON UPDATE CASCADE;

ALTER TABLE ONLY t_operations
    ADD CONSTRAINT fk_t_operations_bio_condition FOREIGN KEY (id_nomenclature_bio_condition) REFERENCES ref_nomenclatures.t_nomenclatures(id_nomenclature) ON UPDATE CASCADE;

ALTER TABLE ONLY t_operations
    ADD CONSTRAINT fk_t_operations_cmr_action FOREIGN KEY (id_nomenclature_cmr_action) REFERENCES ref_nomenclatures.t_nomenclatures(id_nomenclature) ON UPDATE CASCADE;


ALTER TABLE ONLY cor_operation_observer
    ADD CONSTRAINT fk_cor_operation_observer_id_op FOREIGN KEY (id_operation) REFERENCES pr_cmr.t_operations(id_operation) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE ONLY cor_operation_observer
    ADD CONSTRAINT fk_cor_operation_observer_id_role FOREIGN KEY (id_observer) REFERENCES utilisateurs.t_roles(id_role) ON UPDATE CASCADE;


--------------
--CONSTRAINS--
--------------
ALTER TABLE t_individuals
  ADD CONSTRAINT check_id_nomenclature_sex CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature_sex,'SEXE')) NOT VALID;

ALTER TABLE ONLY t_operations
    ADD CONSTRAINT check_t_operations_occtax_date_max CHECK (date_max >= date_min);

ALTER TABLE t_operations
  ADD CONSTRAINT check_id_nomenclature_cmr_action CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature_cmr_action,'CMR_ACTION')) NOT VALID;

ALTER TABLE t_operations
  ADD CONSTRAINT check_id_nomenclature_obs_method CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature_obs_method,'METH_OBS')) NOT VALID;

ALTER TABLE t_operations
  ADD CONSTRAINT check_id_nomenclature_life_stage CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature_life_stage,'STADE_VIE')) NOT VALID;

ALTER TABLE t_operations
  ADD CONSTRAINT check_id_nomenclature_bio_condition CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature_bio_condition,'ETA_BIO')) NOT VALID;
