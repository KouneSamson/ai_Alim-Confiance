# coding: utf-8
from . import database as db
from flask_login import UserMixin

""" Gestionnaire de connexion des utilisateurs """

# t_inspecteur = Table(
#     'inspecteur', metadata,
#     Column('id_inspecteur', NullType),
#     Column('nom', NullType),
#     Column('prenom', NullType)
# )

class Inspecteur(db.Model, UserMixin):
    __tablename__ = 'inspecteur'
    
    id_inspecteur = db.Column(db.Integer,primary_key=True)
    nom = db.Column(db.String)
    prenom = db.Column(db.String)
    identifiant = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    
    def get_id(self):
        return self.id_inspecteur

"""Gestionnaire de la base de données Alim'Confiance"""

# t_activite = Table(
#     'activite', metadata,
#     Column('id_activite', NullType),
#     Column('nom_activite', NullType)
# )

class Activite(db.Model):
    __tablename__ = 'activite'
    
    id_activite = db.Column(db.Integer, primary_key=True)
    nom_activite = db.Column(db.String)
    
    def get_id(self):
        return self.id_activite

# t_add_geo = Table(
#     'add_geo', metadata,
#     Column('id_add_geo', NullType),
#     Column('id_etablissement', NullType),
#     Column('adress', NullType),
#     Column('geo', NullType)
# )

class Add_Geo(db.Model):
    __tablename__ = 'add_geo'
    
    id_add_geo = db.Column(db.Integer, primary_key=True)
    id_etablissement = db.Column(db.Integer,db.ForeignKey('etablissement.id_etablissement'))
    adress = db.Column(db.String, nullable=True)
    geo = db.Column(db.String, nullable=True)
    
    def get_id(self):
        return self.id_add_geo

# t_commune = Table(
#     'commune', metadata,
#     Column('id_commune', NullType),
#     Column('nom_commune', NullType)
# )

class Commune(db.Model):
    __tablename__ = 'commune'
    
    id_commune = db.Column(db.Integer, primary_key=True)
    nom_commune = db.Column(db.String)
    
    def get_id(self):
        return self.id_commune

# t_etablissement = Table(
#     'etablissement', metadata,
#     Column('id_etablissement', NullType),
#     Column('siret', NullType),
#     Column('nom_etablissement', NullType)
# )

class Etablissement(db.Model):
    __tablename__ = 'etablissement'
    
    id_etablissement = db.Column(db.Integer, primary_key=True)
    siret = db.Column(db.String, unique=True)
    nom_etablissement = db.Column(db.String)
    
    def get_id(self):
        return self.id_etablissement

# t_etablissement_activite = Table(
#     'etablissement_activite', metadata,
#     Column('id_e_a_i', NullType),
#     Column('id_etablissement', NullType),
#     Column('id_activite', NullType),
#     Column('Numero_inspection', NullType),
#     Column('date_inspection', NullType),
#     Column('synthese_eval', NullType),
#     Column('agrement', NullType)
# )

class Etablissement_Activite(db.Model):
    __tablename__ = 'etablissement_activite'
    
    id_e_a_i = db.Column(db.Integer, primary_key=True)
    id_etablissement = db.Column(db.Integer, db.ForeignKey('etablissement.id_etablissement'))
    id_activite = db.Column(db.Integer, db.ForeignKey('activite.id_activite'))
    Numero_inspection = db.Column(db.String)
    date_inspection = db.Column(db.String)
    synthese_eval = db.Column(db.String)
    agrement = db.Column(db.String)
    
    def get_id(self):
        return self.id_e_a_i

# t_etablissement_postal = Table(
#     'etablissement_postal', metadata,
#     Column('id_etablissement', NullType),
#     Column('id_postal', NullType)
# )

class Etablissement_Postal(db.Model):
    __tablename__ = 'etablissement_postal'
    
    id_etablissement = db.Column(db.Integer, db.ForeignKey('etablissement.id_etablissement'), primary_key=True)
    id_postal = db.Column(db.Integer, db.ForeignKey('postal.id_postal'), primary_key=True)

# t_postal = Table(
#     'postal', metadata,
#     Column('id_postal', NullType),
#     Column('id_commune', NullType),
#     Column('code_postal', NullType)
# )

class Postal(db.Model):
    __tablename__ = 'postal'
    
    id_postal = db.Column(db.Integer,primary_key=True)
    id_commune = db.Column(db.Integer,db.ForeignKey('commune.id_commune'))
    code_postal = db.Column(db.String)
    
    def get_id(self):
        return self.id_postal