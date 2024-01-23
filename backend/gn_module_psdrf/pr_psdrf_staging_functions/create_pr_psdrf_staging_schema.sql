-- Filename: create_staging_schema.sql

CREATE SCHEMA pr_psdrf_staging;

CREATE TABLE pr_psdrf_staging.t_dispositifs AS TABLE pr_psdrf.t_dispositifs WITH NO DATA;
CREATE TABLE pr_psdrf_staging.t_placettes AS TABLE pr_psdrf.t_placettes WITH NO DATA;
CREATE TABLE pr_psdrf_staging.t_reperes AS TABLE pr_psdrf.t_reperes WITH NO DATA;
CREATE TABLE pr_psdrf_staging.t_cycles AS TABLE pr_psdrf.t_cycles WITH NO DATA;
CREATE TABLE pr_psdrf_staging.t_arbres AS TABLE pr_psdrf.t_arbres WITH NO DATA;
CREATE TABLE pr_psdrf_staging.t_arbres_mesures AS TABLE pr_psdrf.t_arbres_mesures WITH NO DATA;
CREATE TABLE pr_psdrf_staging.t_regenerations AS TABLE pr_psdrf.t_regenerations WITH NO DATA;
CREATE TABLE pr_psdrf_staging.t_bm_sup_30 AS TABLE pr_psdrf.t_bm_sup_30 WITH NO DATA;
CREATE TABLE pr_psdrf_staging.t_bm_sup_30_mesures AS TABLE pr_psdrf.t_bm_sup_30_mesures WITH NO DATA;
CREATE TABLE pr_psdrf_staging.t_transects AS TABLE pr_psdrf.t_transects WITH NO DATA;
CREATE TABLE pr_psdrf_staging.cor_cycles_placettes AS TABLE pr_psdrf.cor_cycles_placettes WITH NO DATA;

GRANT USAGE ON SCHEMA pr_psdrf_staging TO geonatadmin;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA pr_psdrf_staging TO geonatadmin;
ALTER DEFAULT PRIVILEGES IN SCHEMA pr_psdrf_staging GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO geonatadmin;
