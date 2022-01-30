from flask import Blueprint, render_template, request, flash
# from . import models
from . import database
from . import models2
import pandas
import folium
from sqlalchemy import func, text
from flask_login import login_user, login_required, logout_user, current_user

views = Blueprint('views',__name__)

@views.route('/', methods=['GET','POST'])
def home():
    start_point = (46.227638,2.213749)
    carte = folium.Map(location=start_point, zoom_start=6)
    carte.save('website/templates/carte.html')
    
    codepostal = 0
    
    liste_Activites = get_Activites_DB()
    max_act = len(liste_Activites)
    
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
                codepostal = data.get('postal-map')
        elif len(data) == 2:
            connexion(data)
        elif len(data) < 6:
            flash('Formulaire invalide.', category='error')
        else:
            if data.get('n-siret'):
                insertion_etablissement(data)
            elif data.get('n-inspection'):
                insertion_inspection(data)
    
    inspections = dernieres_inspections_DB(codepostal)
    inspections_titre = inspections.keys()
    insp_list = inspections.to_numpy()
    return render_template("AlimHome.html", user=current_user, awesome=awsm, great=grt, bad=bd, aweful=awfl, list_act=liste_Activites, max_act=max_act, titres=inspections_titre, t_size=len(inspections), insplist=insp_list)

def connexion(data):
    identifiant = data.get('identifiant')
    password = data.get('password')
    
    # user = models.User.query.filter_by(identifiant=identifiant).first()
    user = models2.Inspecteur.query.filter_by(identifiant=identifiant).first()
    
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
    # activite_query = models.Activite.query.with_entities(models.Activite.l_activite)
    activite_query = models2.Activite.query.with_entities(models2.Activite.nom_activite)
    
    activites = []
    for act in activite_query:
        activites.append(act[0])
    activites.sort()
    return activites

def insertion_inspection(data):
    if data.get('evaluation') == '--Evaluation--':
        print('Une évaluation doit être séléctionnée.')
        flash('Une évaluation doit être séléctionnée.', category='error')
    else:
        siret = data.get('siret-inspection')
        if database.session.query(models2.Etablissement.id_etablissement).filter_by(siret=siret).first() is not None:
            n_insp = data.get('n-inspection')
            if database.session.query(models2.Etablissement_Activite).filter_by(Numero_inspection=n_insp).first() is not None:
                print('Cette inspection existe déjà dans la base de données.')
                flash('Cette inspection existe déjà dans la base de données.', category='error')
            else :
                etablissement_id = models2.Etablissement.query.filter_by(siret=siret).first().id_etablissement
                
                postal = data.get('postal-inspection')
                les_activites = data.getlist('activite-inspecte')
                date_inspection = data.get('date-inspection')
                evaluation = data.get('evaluation')
                
                for activite in les_activites:
                    activite_id = models2.Activite.query.filter_by(nom_activite=activite).first().id_activite
                    if database.session.query(models2.Etablissement_Activite.id_etablissement).filter_by(id_etablissement=etablissement_id,id_activite=activite_id).first() is None:
                        print("L'activiter "+activite+" n'est pas exercer.")
                        flash("L'activiter "+activite+" n'est pas exercer.", category='error')
                        return 0
                
                for activite in les_activites:
                    activite_id = models2.Activite.query.filter_by(nom_activite=activite).first().id_activite
                    
                    last_id_e_a_i = models2.Etablissement_Activite.query.with_entities(func.max(models2.Etablissement_Activite.id_e_a_i)).first()
                    inspection_id = last_id_e_a_i[0] + 1
                    
                    n_agrement = models2.Etablissement_Activite.query.filter_by(id_etablissement=etablissement_id,id_activite=activite_id).first().agrement
                    
                    new_inspection = models2.Etablissement_Activite(id_e_a_i=inspection_id, id_etablissement=etablissement_id, id_activite=activite_id, Numero_inspection=n_insp, date_inspection=date_inspection, synthese_eval=evaluation, agrement=n_agrement)
                    
                    database.session.add(new_inspection)
                    database.session.commit()
                
                print('Inspection ajoutée avec succès.')
                flash('Inspection ajoutée avec succès.', category='success')
        else:
            print("Ce SIRET n'est pas dans la base de données.")
            flash("Ce SIRET n'est pas dans la base de données.", category='error')

def insertion_etablissement(data):
    siret = data.get('n-siret')
    
    if database.session.query(models2.Etablissement.id_etablissement).filter_by(siret=siret).first() is not None:
        print('Ce SIRET est déjà dans la base de données.')
        flash('Ce SIRET est déjà dans la base de données.', category='error')
    else:
        l_etablissement = data.get('l-etablissement')
        commune = data.get('commune')
        postal = data.get('postal-etablissement')
        
        if not postal.isnumeric():
            print('Code Postal incorrect.')
            flash('Code Postal incorrect.', category='error')
            return 0
        
        adresse = data.get('adresse')
        adresse = adresse.strip()
        if adresse == '':
            adresse = 'NULL'
        
        geoloc = data.get('geoloc')
        geoloc = geoloc.strip()
        if geoloc == '':
            geoloc = '0,0'
        
        les_activites = data.getlist('activite-etablissement')
        
        agrement = data.get('agrement')
        agrement = agrement.strip()
        if agrement == '':
            agrement = 'NULL'
            
        last_id_e = models2.Etablissement.query.with_entities(func.max(models2.Etablissement.id_etablissement)).first()
        etablissement_id = last_id_e[0] + 1
        
        new_etablissement = models2.Etablissement(id_etablissement=etablissement_id, siret=siret,nom_etablissement=l_etablissement)
        
        database.session.add(new_etablissement)
        database.session.commit()
        
        last_id_ag = models2.Add_Geo.query.with_entities(func.max(models2.Add_Geo.id_add_geo)).first()
        add_geo_id = last_id_ag[0] + 1
        new_adresse = models2.Add_Geo(id_add_geo=add_geo_id,id_etablissement=etablissement_id,adress=adresse,geo=geoloc)
        
        database.session.add(new_adresse)
        database.session.commit()
        
        postal_id_temp = models2.Postal.query.filter_by(code_postal=postal).first()
        postal_id = 0
        
        if postal_id_temp is None:
            
            last_id_c = models2.Commune.query.with_entities(func.max(models2.Commune.id_commune)).first()
            commune_id = last_id_c[0] + 1
            new_commune = models2.Commune(id_commune=commune_id,nom_commune=commune)
            database.session.add(new_commune)
            database.session.commit()
            
            last_id_p = models2.Postal.query.with_entities(func.max(models2.Postal.id_postal)).first()
            postal_id = last_id_p[0] + 1
            new_postal = models2.Postal(id_postal=postal_id,id_commune=commune_id,code_postal=postal)
            database.session.add(new_postal)
            database.session.commit()
        else :
            postal_id = models2.Postal.query.filter_by(code_postal=postal).first().id_postal
        
        new_etablissement_postal = models2.Etablissement_Postal(id_etablissement=etablissement_id,id_postal=postal_id)
        database.session.add(new_etablissement_postal)
        database.session.commit()
        
        for activite in les_activites:
            activite_id = models2.Activite.query.filter_by(nom_activite=activite).first().id_activite
            new_exercer = models2.Etablissement_Activite(id_etablissement=etablissement_id,id_activite=activite_id,agrement=agrement) 
            #.Exercer(etablissement_id=etablissement_id,activite_id=activite_id,agrement=agrement)
            database.session.add(new_exercer)
        
        database.session.commit()
        print('Etablissement ajouté avec succès.')
        flash('Etablissement ajouté avec succès.',category='success')

def dernieres_inspections_DB(codepostal):
    big_bad_query = text('SELECT siret, code_postal, nom_activite, e_a.date_inspection, e_a.synthese_eval, e_a.id_etablissement, e_a.id_activite, e_p.id_postal FROM etablissement_activite e_a JOIN etablissement e ON e.id_etablissement=e_a.id_etablissement JOIN etablissement_postal e_p ON e_p.id_etablissement=e_a.id_etablissement JOIN postal p ON p.id_postal=e_p.id_postal JOIN activite a ON a.id_activite=e_a.id_activite ORDER BY date_inspection DESC;')
    inspections = pandas.read_sql_query(big_bad_query,database.engine)
    print(len(inspections))
    inspections.drop(['id_etablissement','id_activite','id_postal'],axis=1,inplace=True)
    
    
    if int(codepostal) == 0:
        return inspections.head(10)
    else:
        if not codepostal.isnumeric():
            print('Mauvais Code Postal.')
            flash('Mauvais Code Postal.', category='error')
            return inspections.head(10)
        else:
            inspections_2 = inspections.loc[inspections['code_postal'] == codepostal]
            print(type(inspections_2))
            
            if len(inspections_2) == 0:
                print('Aucune inspection pour ce Code Postal.')
                flash('Aucune inspection pour ce Code Postal.', category='warning')
                return inspections.head(10)
            return inspections_2.head(10)