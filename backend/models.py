# -*- encoding: utf-8 -*-

from geoalchemy2 import Geometry

from geonature.core.users.models import BibOrganismes
from geonature.core.ref_geo.models import LiMunicipalities, LAreas
from geonature.utils.utilssqlalchemy import serializable, geoserializable
from geonature.utils.env import DB


SCHEMA = 'pr_psdrf'


dispositifs_municipalities_assoc = DB.Table('cor_dispositif_municipality', DB.metadata,
    DB.Column('id_dispositif', DB.Integer, DB.ForeignKey(SCHEMA + '.t_dispositifs.id_dispositif')),
    DB.Column('id_municipality', DB.String, DB.ForeignKey('ref_geo.li_municipalities.id_municipality')),
    schema=SCHEMA
)

dispositifs_area_assoc = DB.Table('cor_dispositif_area', DB.metadata,
    DB.Column('id_dispositif', DB.Integer, DB.ForeignKey(SCHEMA + '.t_dispositifs.id_dispositif')),
    DB.Column('id_area', DB.Integer, DB.ForeignKey('ref_geo.l_areas.id_area')),
    schema=SCHEMA
)


# @serializable
class TDispositifs (DB.Model):
    __tablename__ = "t_dispositifs"
    __table_args__ = {'schema': SCHEMA}
    id_dispositif = DB.Column('id_dispositif', DB.Integer, primary_key = True)
    name = DB.Column('name', DB.String)
    id_organisme = DB.Column('id_organisme', DB.Integer, DB.ForeignKey('utilisateurs.bib_organismes.id_organisme'))
    alluvial = DB.Column('alluvial', DB.Boolean)
    organisme = DB.relationship('BibOrganismes')
    placettes = DB.relationship('TPlacettes', back_populates='dispositif')
    municipalities = DB.relationship('LiMunicipalities', secondary=dispositifs_municipalities_assoc)
    areas = DB.relationship('LAreas', secondary=dispositifs_area_assoc)


@serializable
@geoserializable
class TPlacettes (DB.Model):
    __tablename__ = "t_placettes"
    __table_args__ = {'schema': SCHEMA}
    id_placette = DB.Column('id_placette', DB.Integer, primary_key = True)
    id_dispositif = DB.Column('id_dispositif', DB.Integer, DB.ForeignKey('pr_psdrf.t_dispositifs.id_dispositif'))
    id_placette_orig = DB.Column('id_placette_orig', DB.String)
    strate = DB.Column('strate', DB.Integer)
    pente = DB.Column('pente', DB.Float)
    poids_placette = DB.Column('poids_placette', DB.Float)
    correction_pente = DB.Column('correction_pente', DB.Boolean)
    exposition = DB.Column('exposition', DB.Integer)
    profondeur_app = DB.Column('profondeur_app', DB.String)
    profondeur_hydr = DB.Column('profondeur_hydr', DB.Float)
    texture = DB.Column('texture', DB.String)
    habitat = DB.Column('habitat', DB.String)
    station = DB.Column('station', DB.String)
    typologie = DB.Column('typologie', DB.String)
    groupe = DB.Column('groupe', DB.String)
    groupe1 = DB.Column('groupe1', DB.String)
    groupe2 = DB.Column('groupe2', DB.String)
    ref_habitat = DB.Column('ref_habitat', DB.String)
    precision_habitat = DB.deferred(DB.Column('precision_habitat', DB.Text))
    ref_station = DB.Column('ref_station', DB.String)
    ref_typologie = DB.Column('ref_typologie', DB.String)
    descriptif_groupe = DB.deferred(DB.Column('descriptif_groupe', DB.Text))
    descriptif_groupe1 = DB.deferred(DB.Column('descriptif_groupe1', DB.Text))
    descriptif_groupe2 = DB.deferred(DB.Column('descriptif_groupe2', DB.Text))
    precision_gps = DB.Column('precision_gps', DB.String)
    cheminement = DB.deferred(DB.Column('cheminement', DB.Text))
    geom = DB.Column('geom', Geometry('POINT', 2154))
    geom_wgs84 = DB.Column('geom_wgs84', Geometry('POINT', 4326))

    dispositif = DB.relationship('TDispositifs', foreign_keys=id_dispositif, back_populates='placettes')


@serializable
class TReperes (DB.Model):
    __tablename__ = "t_reperes"
    __table_args__ = {'schema': SCHEMA}
    id_repere = DB.Column('id_repere', DB.Integer, primary_key = True)
    id_placette = DB.Column('id_placette', DB.Integer, DB.ForeignKey('pr_psdrf.t_placettes.id_placette'))
    azimut = DB.Column('azimut', DB.Float)
    distance = DB.Column('distance', DB.Float)
    diametre = DB.Column('diametre', DB.Float)
    observation = DB.deferred(DB.Column('observation', DB.Text))

    placette = DB.relationship('TPlacettes', foreign_keys=id_placette)


@serializable
class TCycles (DB.Model):
    __tablename__ = "t_cycles"
    __table_args__ = {'schema': SCHEMA}
    id_cycle = DB.Column('id_cycle', DB.Integer, primary_key = True)
    id_dispositif = DB.Column('id_dispositif', DB.Integer, DB.ForeignKey('pr_psdrf.t_dispositifs.id_dispositif'))
    num_cycle = DB.Column('num_cycle', DB.Integer)
    coeff = DB.Column('coeff', DB.Integer)
    date_debut = DB.Column('date_debut', DB.Date)
    date_fin = DB.Column('date_fin', DB.Date)
    diam_lim = DB.Column('diam_lim', DB.Float)
    monitor = DB.Column('monitor', DB.String)

    dispositif = DB.relationship('TDispositifs', foreign_keys=id_dispositif, backref='cycles')


@serializable
class BibEssences (DB.Model):
    __tablename__ = "bib_essences"
    __table_args__ = {'schema': SCHEMA}
    code_essence = DB.Column('code_essence', DB.String, primary_key = True)
    cd_nom = DB.Column('cd_nom', DB.Integer)
    nom = DB.Column('nom', DB.String)
    nom_latin = DB.Column('nom_latin', DB.String)
    ess_reg = DB.Column('ess_reg', DB.String)
    couleur = DB.Column('couleur', DB.String)


@serializable
class CorCyclesPlacettes (DB.Model):
    __tablename__ = "cor_cycles_placettes"
    __table_args__ = {'schema': SCHEMA}
    id_cycle_placette = DB.Column('id_cycle_placette', DB.Integer, primary_key = True)
    id_cycle = DB.Column('id_cycle', DB.Integer, DB.ForeignKey('pr_psdrf.t_cycles.id_cycle'))
    id_placette = DB.Column('id_placette', DB.Integer, DB.ForeignKey('pr_psdrf.t_placettes.id_placette'))
    date_releve = DB.Column('date_releve', DB.Date)
    date_intervention = DB.Column('date_intervention', DB.String)
    nature_intervention = DB.Column('nature_intervention', DB.String)
    gestion_placette = DB.Column('gestion_placette', DB.String)
    id_nomenclature_castor = DB.Column('id_nomenclature_castor', DB.Integer)
    id_nomenclature_frottis = DB.Column('id_nomenclature_frottis', DB.Integer)
    id_nomenclature_boutis = DB.Column('id_nomenclature_boutis', DB.Integer)
    recouv_herbes_basses = DB.Column('recouv_herbes_basses', DB.Float)
    recouv_herbes_hautes = DB.Column('recouv_herbes_hautes', DB.Float)
    recouv_buissons = DB.Column('recouv_buissons', DB.Float)
    recouv_arbres = DB.Column('recouv_arbres', DB.Float)

    cycle = DB.relationship('TCycles', foreign_keys=id_cycle)
    placette = DB.relationship('TPlacettes', foreign_keys=id_placette)



class CorCyclesRoles (DB.Model):
    __tablename__ = "cor_cycles_roles"
    __table_args__ = {'schema': SCHEMA}
    id_cycle = DB.Column('id_cycle', DB.Integer, DB.ForeignKey('pr_psdrf.t_cycles.id_cycle'), primary_key = True)
    id_role = DB.Column('id_role', DB.Integer, primary_key = True)

    cycle = DB.relationship('TCycles', foreign_keys=id_cycle)


@serializable
class TArbres (DB.Model):
    __tablename__ = "t_arbres"
    __table_args__ = {'schema': SCHEMA}
    id_arbre = DB.Column('id_arbre', DB.Integer, primary_key = True)
    id_arbre_orig = DB.Column('id_arbre_orig', DB.Integer)
    id_placette = DB.Column('id_placette', DB.Integer, DB.ForeignKey('pr_psdrf.t_placettes.id_placette'))
    code_essence = DB.Column('code_essence', DB.String, DB.ForeignKey('pr_psdrf.bib_essences.code_essence'))
    azimut = DB.Column('azimut', DB.Float)
    distance = DB.Column('distance', DB.Float)
    taillis = DB.Column('taillis', DB.Boolean)
    observation = DB.deferred(DB.Column('observation', DB.Text))

    placette = DB.relationship('TPlacettes', foreign_keys=id_placette, backref='arbres')
    essence = DB.relationship('BibEssences', foreign_keys=code_essence)


@serializable
class TArbresMesures (DB.Model):
    __tablename__ = "t_arbres_mesures"
    __table_args__ = {'schema': SCHEMA}
    id_arbre_mesure = DB.Column('id_arbre_mesure', DB.Integer, primary_key = True)
    id_arbre = DB.Column('id_arbre', DB.Integer, DB.ForeignKey('pr_psdrf.t_arbres.id_arbre'))
    id_cycle = DB.Column('id_cycle', DB.Integer, DB.ForeignKey('pr_psdrf.t_cycles.id_cycle'))
    diametre1 = DB.Column('diametre1', DB.Float)
    diametre2 = DB.Column('diametre2', DB.Float)
    type = DB.Column('type', DB.String)
    hauteur_totale = DB.Column('hauteur_totale', DB.Float)
    hauteur_branche = DB.Column('hauteur_branche', DB.Float)
    stade_durete = DB.Column('stade_durete', DB.Integer)
    stade_ecorce = DB.Column('stade_ecorce', DB.Integer)
    liane = DB.Column('liane', DB.String)
    diametre_liane = DB.Column('diametre_liane', DB.Float)
    coupe = DB.Column('coupe', DB.Unicode)
    limite = DB.Column('limite', DB.Boolean)
    id_nomenclature_code_sanitaire = DB.Column('id_nomenclature_code_sanitaire', DB.Integer)
    code_ecolo = DB.Column('code_ecolo', DB.String)
    ref_code_ecolo = DB.Column('ref_code_ecolo', DB.String)
    ratio_hauteur = DB.Column('ratio_hauteur', DB.Boolean)
    observation = DB.deferred(DB.Column('observation', DB.Text))

    arbre = DB.relationship('TArbres', foreign_keys=id_arbre, backref='mesures')
    cycle = DB.relationship('TCycles', foreign_keys=id_cycle)


@serializable
class TRegenerations (DB.Model):
    __tablename__ = "t_regenerations"
    __table_args__ = {'schema': SCHEMA}
    id_regeneration = DB.Column('id_regeneration', DB.Integer, primary_key = True)
    id_cycle_placette = DB.Column('id_cycle_placette', DB.Integer, DB.ForeignKey('pr_psdrf.cor_cycles_placettes.id_cycle_placette'))
    sous_placette = DB.Column('sous_placette', DB.Integer)
    code_essence = DB.Column('code_essence', DB.String)
    recouvrement = DB.Column('recouvrement', DB.Float)
    classe1 = DB.Column('classe1', DB.Integer)
    classe2 = DB.Column('classe2', DB.Integer)
    classe3 = DB.Column('classe3', DB.Integer)
    taillis = DB.Column('taillis', DB.Boolean)
    abroutissement = DB.Column('abroutissement', DB.Boolean)
    id_nomenclature_abroutissement = DB.Column('id_nomenclature_abroutissement', DB.Integer)
    observation = DB.deferred(DB.Column('observation', DB.Text))

    cor_cycles_placettes = DB.relationship('CorCyclesPlacettes', foreign_keys=id_cycle_placette)


@serializable
class TCategories (DB.Model):
    __tablename__ = "t_categories"
    __table_args__ = {'schema': SCHEMA}
    id_category = DB.Column('id_category', DB.Integer, primary_key = True)
    id_dispositif = DB.Column('id_dispositif', DB.Integer, DB.ForeignKey('pr_psdrf.t_dispositifs.id_dispositif'))
    pb = DB.Column('pb', DB.Float)
    bm = DB.Column('bm', DB.Float)
    gb = DB.Column('gb', DB.Float)
    tgb = DB.Column('tgb', DB.Float)

    dispositif = DB.relationship('TDispositifs', foreign_keys=id_dispositif)


@serializable
class TBmSup30 (DB.Model):
    __tablename__ = "t_bm_sup_30"
    __table_args__ = {'schema': SCHEMA}
    id_bm_sup_30 = DB.Column('id_bm_sup_30', DB.Integer, primary_key = True)
    id_bm_sup_30_orig = DB.Column('id_bm_sup_30_orig', DB.Integer)
    id_placette = DB.Column('id_placette', DB.Integer, DB.ForeignKey('pr_psdrf.t_placettes.id_placette'))
    id_arbre = DB.Column('id_arbre', DB.Integer, DB.ForeignKey('pr_psdrf.t_arbres.id_arbre'))
    code_essence = DB.Column('code_essence', DB.String, DB.ForeignKey('pr_psdrf.bib_essences.code_essence'))
    azimut = DB.Column('azimut', DB.Float)
    distance = DB.Column('distance', DB.Float)
    orientation = DB.Column('orientation', DB.Float)
    azimut_souche = DB.Column('azimut_souche', DB.Float)
    distance_souche = DB.Column('distance_souche', DB.Float)
    observation = DB.deferred(DB.Column('observation', DB.Text))

    placette = DB.relationship('TPlacettes', foreign_keys=id_placette)
    essence = DB.relationship('BibEssences', foreign_keys=code_essence)
    arbre = DB.relationship('TArbres', foreign_keys=id_arbre)


@serializable
class TBmSup30Mesures (DB.Model):
    __tablename__ = "t_bm_sup_30_mesures"
    __table_args__ = {'schema': SCHEMA}
    id_bm_sup_30_mesure = DB.Column('id_bm_sup_30_mesure', DB.Integer, primary_key = True)
    id_bm_sup_30 = DB.Column('id_bm_sup_30', DB.Integer, DB.ForeignKey('pr_psdrf.t_bm_sup_30.id_bm_sup_30'))
    id_cycle = DB.Column('id_cycle', DB.Integer, DB.ForeignKey('pr_psdrf.t_cycles.id_cycle'))
    diametre_ini = DB.Column('diametre_ini', DB.Float)
    diametre_med = DB.Column('diametre_med', DB.Float)
    diametre_fin = DB.Column('diametre_fin', DB.Float)
    diametre_130 = DB.Column('diametre_130', DB.Float)
    longueur = DB.Column('longueur', DB.Float)
    ratio_hauteur = DB.Column('ratio_hauteur', DB.Boolean)
    contact = DB.Column('contact', DB.Float)
    chablis = DB.Column('chablis', DB.Boolean)
    stade_durete = DB.Column('stade_durete', DB.Integer)
    stade_ecorce = DB.Column('stade_ecorce', DB.Integer)
    observation = DB.deferred(DB.Column('observation', DB.Text))

    bm_sup_30 = DB.relationship('TBmSup30', foreign_keys=id_bm_sup_30)
    cycle = DB.relationship('TCycles', foreign_keys=id_cycle)


@serializable
class TTransects (DB.Model):
    __tablename__ = "t_transects"
    __table_args__ = {'schema': SCHEMA}
    id_transect = DB.Column('id_transect', DB.Integer, primary_key = True)
    id_cycle_placette = DB.Column('id_cycle_placette', DB.Integer, DB.ForeignKey('pr_psdrf.cor_cycles_placettes.id_cycle_placette'))
    code_essence = DB.Column('code_essence', DB.String)
    ref_transect = DB.Column('ref_transect', DB.String)
    distance = DB.Column('distance', DB.Float)
    orientation = DB.Column('orientation', DB.Float)
    azimut_souche = DB.Column('azimut_souche', DB.Float)
    distance_souche = DB.Column('distance_souche', DB.Float)
    diametre = DB.Column('diametre', DB.Float)
    diametre_130 = DB.Column('diametre_130', DB.Float)
    ratio_hauteur = DB.Column('ratio_hauteur', DB.Boolean)
    contact = DB.Column('contact', DB.Boolean)
    angle = DB.Column('angle', DB.Float)
    chablis = DB.Column('chablis', DB.Boolean)
    stade_durete = DB.Column('stade_durete', DB.Integer)
    stade_ecorce = DB.Column('stade_ecorce', DB.Integer)
    observation = DB.deferred(DB.Column('observation', DB.Text))

    cor_cycles_placettes = DB.relationship('CorCyclesPlacettes', foreign_keys=id_cycle_placette)


@serializable
class TTarifs (DB.Model):
    __tablename__ = "t_tarifs"
    __table_args__ = {'schema': SCHEMA}
    id_tarif = DB.Column('id_tarif', DB.Integer, primary_key = True)
    id_dispositif = DB.Column('id_dispositif', DB.Integer, DB.ForeignKey('pr_psdrf.t_dispositifs.id_dispositif'))
    code_essence = DB.Column('code_essence', DB.String, DB.ForeignKey('pr_psdrf.bib_essences.code_essence'))
    type_tarif = DB.Column('type_tarif', DB.String)
    num_tarif = DB.Column('num_tarif', DB.Float)

    dispositif = DB.relationship('TDispositifs', foreign_keys=id_dispositif)
    essence = DB.relationship('BibEssences', foreign_keys=code_essence)


@serializable
class TRegroupementsEssences (DB.Model):
    __tablename__ = "t_regroupements_essences"
    __table_args__ = {'schema': SCHEMA}
    id_dispositif = DB.Column('id_dispositif', DB.Integer, DB.ForeignKey('pr_psdrf.t_dispositifs.id_dispositif'), primary_key = True)
    code_essence = DB.Column('code_essence', DB.String, DB.ForeignKey('pr_psdrf.bib_essences.code_essence'), primary_key = True)
    code_regroupement = DB.Column('code_regroupement', DB.String)
    couleur = DB.Column('couleur', DB.String)

    essence = DB.relationship('BibEssences', foreign_keys=code_essence)
    dispositif = DB.relationship('TDispositifs', foreign_keys=id_dispositif)
