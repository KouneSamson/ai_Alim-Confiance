from asyncio.windows_events import NULL
from flask import Blueprint, redirect, render_template, request, flash
from sqlalchemy import null
from . import models
from . import database
from flask_login import login_user, login_required, logout_user, current_user

views = Blueprint('views',__name__)

@views.route('/', methods=['GET','POST'])
def home():
    
    liste_Activites = get_Activites_DB()
    max_act = len(liste_Activites)
    half_act = int(max_act/2)
    
    awsm = 25
    grt = 25
    bd = 25
    awfl = 25
    
    # gmap = "https://maps.google.com/maps?output=embed&amp;q=57000&amp;z=10&amp;t=m"
    
    data = request.form
    print(data)

    """ Vérification des formulaires."""
    if len(data) != 0:
        if len(data) == 1:
            if data.get('logout'):
                deconnexion()
            elif data.get('postal-map'):
                pass
        elif len(data) == 2:
            connexion(data)
        elif len(data) < 6:
            flash('Formulaire invalide.', category='error')
        else:
            if data.get('n-siret'):
                insertion_etablissement(data)
            elif data.get('n-inspection'):
                insertion_inspection(data)
    
    return render_template("AlimHome.html", user=current_user, awesome=awsm, great=grt, bad=bd, aweful=awfl, list_act=liste_Activites, half_act=half_act, max_act=max_act) #Accueil.html

def connexion(data):
    identifiant = data.get('identifiant')
    password = data.get('password')
    
    user = models.User.query.filter_by(identifiant=identifiant).first()
    if user:
        if user.password == password:
            print('Connexion réussie.')
            flash('Connexion réussie.', category='success')
            login_user(user, remember=True)
        else:
            print('Mauvais mot de passe.')
            flash('Mauvais mot de passe.', category='error')
    else:
        print('Utilisateur inconnu.')
        flash('Utilisateur inconnu.', category='error')

@login_required
def deconnexion():
    print('Déconnexion réussie.')
    logout_user()

def get_Activites_DB():
    activite_query = models.Activite.query.with_entities(models.Activite.l_activite)
    activites = []
    for act in activite_query:
        activites.append(act[0])
    return activites

def insertion_inspection(data):
    if data.get('evaluation') == '--Evaluation--':
        print('Une évaluation doit être séléctionnée.')
        flash('Une évaluation doit être séléctionnée.', category='error')
    else:
        n_insp = data.get('n-inspection')
        if database.session.query(models.Inspection.id).filter_by(n_inspection=n_insp).first() is not None:
            print('Ce N°Inspection est déjà dans la base de données.')
            flash('Ce N°Inspection est déjà dans la base de données.', category='error')
        else :
            siret = data.get('siret-inspection')
            if database.session.query(models.Etablissement.id).filter_by(siret=siret).first() is not None:
                postal = data.get('postal-inspection')
                les_activites = data.getlist('activite-inspecte')
                date_inspection = data.get('date-inspection')
                evaluation = data.get('evaluation')
                
                etablissement_id = models.Etablissement.query.filter_by(siret=siret).first().id
                
                for activite in les_activites:
                    activite_id = models.Activite.query.filter_by(l_activite=activite).first().id
                    if database.session.query(models.Exercer.etablissement_id).filter_by(etablissement_id=etablissement_id,activite_id=activite_id).first() is None:
                        print("L'activiter "+activite+" n'est pas exercer.")
                        flash("L'activiter "+activite+" n'est pas exercer.", category='error')
                        return 0
                
                new_inspection = models.Inspection(n_inspection=n_insp,date_insp=date_inspection,eval=evaluation,etablissement_id=etablissement_id)
                
                database.session.add(new_inspection)
                database.session.commit()
                
                inspection_id = models.Inspection.query.filter_by(n_inspection=n_insp).first().id
                
                for activite in les_activites:
                    activite_id = models.Activite.query.filter_by(l_activite=activite).first().id
                    new_activite_insp = models.Activite_Inspecte(inspection_id=inspection_id,activite_id=activite_id)
                    
                    database.session.add(new_activite_insp)
                    database.session.commit()
                
                print('Inspection ajoutée avec suuccès.')
                flash('Inspection ajoutée avec suuccès.', category='success')
                
            else:
                print("Ce SIRET n'est pas dans la base de données.")
                flash("Ce SIRET n'est pas dans la base de données.", category='error')

def insertion_etablissement(data):
    siret = data.get('n-siret')
    if database.session.query(models.Etablissement.id).filter_by(siret=siret).first() is not None:
        print('Ce SIRET est déjà dans la base de données.')
        flash('Ce SIRET est déjà dans la base de données.', category='error')
    else:
        l_etablissement = data.get('l-etablissement')
        commune = data.get('commune')
        postal = data.get('postal-etablissement')
        
        adresse = data.get('adresse')
        adresse = adresse.strip()
        if adresse == '':
            adresse = 'NULL'
        
        geoloc = data.get('geoloc')
        geoloc = geoloc.strip()
        if geoloc == '':
            geoloc = 'NULL'
        
        les_activites = data.getlist('activite-etablissement')
        
        agrement = data.get('agrement')
        agrement = agrement.strip()
        if agrement == '':
            agrement = 'NULL'
        
        new_etablissement = models.Etablissement(siret=siret,l_etablissement=l_etablissement,adresse=adresse,postal=postal,commune=commune,geo=geoloc)
        database.session.add(new_etablissement)
        database.session.commit()
        
        etablissement_id = models.Etablissement.query.filter_by(siret=siret).first().id
        
        for activite in les_activites:
            activite_id = models.Activite.query.filter_by(l_activite=activite).first().id
            new_exercer = models.Exercer(etablissement_id=etablissement_id,activite_id=activite_id,agrement=agrement)
            database.session.add(new_exercer)
            database.session.commit()
        
        print('Etablissement ajouté avec succès.')
        flash('Etablissement ajouté avec succès.',category='success')