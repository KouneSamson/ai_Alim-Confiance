from . import database
from flask_login import UserMixin
from sqlalchemy.sql import func


"""Gestion de connexion des inspecteurs sur le site"""
class User(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True)
    identifiant = database.Column(database.String(150), unique=True)
    password = database.Column(database.String(150))


"""Gestion de la base de données Alim'Confiance basé sur le MCD"""
class Etablissement(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    siret = database.Column(database.String(20), unique=True)
    l_etablissement = database.Column(database.String(255))
    adresse = database.Column(database.String(255))
    postal = database.Column(database.String(5))
    commune = database.Column(database.String(100))
    geo = database.Column(database.String(50))

class Activite(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    l_activite = database.Column(database.String(255), unique=True)

class Exercer(database.Model):
    etablissement_id = database.Column(database.Integer, database.ForeignKey('etablissement.id'), primary_key=True)
    activite_id = database.Column(database.Integer, database.ForeignKey('activite.id'), primary_key=True)
    agrement = database.Column(database.String(20))

class Inspection(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    n_inspection = database.Column(database.String(20), unique=True)
    date_insp = database.Column(database.DateTime(timezone=True), default=func.now())
    eval = database.Column(database.String(30))
    etablissement_id = database.Column(database.Integer, database.ForeignKey('etablissement.id'))
    activites = database.relationship('Activite_Inspecte')

class Activite_Inspecte(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    inspection_id = database.Column(database.Integer, database.ForeignKey('inspection.id'))
    activite_id = database.Column(database.Integer, database.ForeignKey('activite.id'))