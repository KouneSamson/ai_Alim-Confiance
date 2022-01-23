from asyncio.windows_events import NULL
from unicodedata import category
from flask import Blueprint, redirect, render_template, request, flash
from sqlalchemy import null
from . import models
from flask_login import login_user, login_required, logout_user, current_user

views = Blueprint('views',__name__)

@views.route('/', methods=['GET','POST'])
def home():
    
    liste_Activites = get_Activites_DB()
    max_act = len(liste_Activites)
    half_act = int(max_act/2)
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
                print("ajout établissement")
            elif data.get('n-inspection'):
                print("ajout inspection")
    
    return render_template("AlimHome.html", user=current_user, awesome=100, list_act=liste_Activites, half_act=half_act, max_act=max_act) #Accueil.html

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