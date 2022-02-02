from flask import Blueprint, render_template, request, flash
from . import database
from . import models2
import pandas
import pickle
from datetime import datetime
from sqlalchemy import func, text
from flask_login import login_user, login_required, logout_user, current_user

views = Blueprint('views',__name__)


    
@views.route('/', methods=['GET','POST'])
def home():
    """
    Traitement global du coté serveur de tout le site web en fonctionnement "One Page".

    Returns:
        function: render_template() - Fonction de la bibliothèque Flask permettant de générer une page html en fonction d'un template encapsulé avec Jinja
                                        et les paramètres fournis afin de l'afficher dans le navigateur web de l'utilisateur.
    """
    codepostal = 0
    
    liste_Activites = get_Activites_DB()
    max_act = len(liste_Activites)
    
    awsm = 25
    grt = 25
    bd = 25
    awfl = 25
    
    siret = None
    postal = None
    agrement = None
    activite = None
    predictions = None
    
    data = request.form
    print(len(data))
    if len(data) != 0:
        if len(data) == 1:
            if data.get('logout'):
                deconnexion()
            elif data.get('postal-map'):
                codepostal = data.get('postal-map')
        elif len(data) == 2:
            connexion(data)
        elif len(data) == 4 or len(data) == 3:
            resultats = precition_alimconfiance(data)
            if resultats is not None:
                siret, postal, agrement, activite, predictions = resultats
                bd, awfl, awsm, grt = predictions[0]
                awfl = int(awfl*100)
                bd = int(bd*100)
                grt = int(grt*100)
                awsm = int(awsm*100)
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
    return render_template("AlimHome.html", user=current_user, awesome=awsm, great=grt, bad=bd, aweful=awfl, list_act=liste_Activites, max_act=max_act, titres=inspections_titre, t_size=len(inspections), insplist=insp_list, siret=siret, postal=postal, agrement=agrement, activite=activite)

def connexion(data):
    """
        Récupère les données d'un formulaire de connexion (identifiant et mot de passe) 
        et vérifie en base s'ils sont correct pour se connecter au site. 

        Args:
            data (dict): dictionnaire de données récupéré via un formulaire web
    """
    identifiant = data.get('identifiant')
    password = data.get('password')
    
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
    """
        Déconnecte l'utilisateur.
    """
    print('Déconnexion réussie.')
    logout_user()

def get_Activites_DB():
    """
        Lance une requête à la base de données pour récupérer le nom de chaque activité
        et les retrourner sous forme de liste.

        Returns:
            list: l'ensemble des activités trouvé dans la base de données sous forme de liste
    """
    activite_query = models2.Activite.query.with_entities(models2.Activite.nom_activite)
    
    activites = []
    for act in activite_query:
        activites.append(act[0])
    activites.sort()
    return activites

def insertion_inspection(data):
    """
        Récupère les informations d'un formulaire, vérifie leur justesse par rapport à la base de données,
        s'assure de l'intégrité de celle-ci, ajoute une inspections dans la base de données et
        met à jour toutes les tables impliquées.

        Args:
            data (dict): dictionnaire de données récupéré via un formulaire web

        Returns:
            int: 0 - avorte l'oppération car quelque chose n'est pas conforme
    """
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
    """
        Récupère les informations d'un formulaire, vérifie leur justesse par rapport à la base de données,
        s'assure de l'intégrité de celle-ci, ajoute un établissement dans la base de données et
        met à jour toutes les tables impliquées.

        Args:
            data (dict): dictionnaire de données récupéré via un formulaire web

        Returns:
            int: 0 - avorte l'oppération car quelque chose n'est pas conforme
    """
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
    """
        Lance une requête à la base de données pour récupérer: 
            - le numéro de siret
            - le code postal
            - le nom de l'activité
            - la date d'inspection
            - le résultat de l'évaluation
        des 10 dernières inspection selon le code postal donné en argument.
        Si celui vaut 0 ou n'est pas trouvé dans la base de données,
        alors le filtre s'applique à toutes les inspections de la base de données
        indépendamment du code postal. 

        Args:
            codepostal (string): chaine de caractère symbolisant un code postal - Par défaut : 0

        Returns:
            pandas.DataFrame: Dictionnaire particulier comprenant différentes informations donc chaque colonne est assigné à une clef et chaque ligne à un indice
    """
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

def precition_alimconfiance(data):
    """
        Récupère des données passé via un formulaire,
        vérifie la justesse de celles-ci,
        calcule l'année et le mois de la date actuel,
        charge le modèle de prediciton et l'encoder de données correspondant,
        lance une prédiciton à partir des paramètres s'ils sont considéré correcte,
        retourne les paramètres ainsi que les poucentage d'appartenances aux 4 classes du modèle de classification :
            - Très satisfaisant
            - Satisfaisant
            - A améliorer
            - A corriger de manière urgente

        Args:
            data (dict): dictionnaire de données récupéré via un formulaire web

        Returns:
            tuple: 
                - str: siret - numéro de siret passé en paramètre pour l'affichage
                - str: postal - code postal passé en paramètre pour l'affichage et le modèle
                - int: agrement - présence ou non (1 , 0) d'un numéro d'agrément passé en paramètre pour l'affichage et le modèle
                - str: l_activite - libellé de l'activité excercée passé en paramètre pour l'affichage et le modèle
                - 2d array: predicitons - tableau de tableau de pourcentage d'appartenance a chacune des classes du modèles prédiciton pour les paramètres donnés
                - None : Uniquement si l'un des paramètres est reconnu comme erroné
    """
    with open('appli/website/static/activite_ohe_encoder','rb') as encoder_file:
        encoder = pickle.load(encoder_file)
    
    with open('appli/website/static/alim_confiance_ai','rb') as classifier_file:
        classifier = pickle.load(classifier_file)
    
    siret = data.get('siret-predict')
    postal = data.get('postal-predict')
    agrement = data.get('agrement-predict')
    l_activite = data.get('activite-predict')
    
    today = datetime.today().strftime('%Y-%m-%d')
    annee,mois,jour = today.split('-')
    
    if l_activite == '--Activité--':
        print('Une activité doit être séléctionnée.')
        flash('Une activité doit être séléctionnée.', category='error')
        return None
    elif not postal.isnumeric() :
        print('Mauvais Code Postal.')
        flash('Mauvais Code Postal.', category='error')
        return None
    elif models2.Postal.query.filter_by(code_postal=postal).first() is None:
        print('Code Postal inconnu.')
        flash('Code Postal inconnu.', category='error')
        return None
    else:
        if agrement is None:
            agrement = 0
        else:
            agrement = 1
        
        activite = pandas.DataFrame([l_activite],columns=['l_activite'])
        feature = pandas.DataFrame([[postal,agrement,annee,mois]],columns=['postal','agrement','annee','mois'], index=[0])
        activite_encode = encoder.transform(activite)
        activite_encode_df = pandas.DataFrame(activite_encode, columns=encoder.categories_)
        feature = pandas.concat([feature,activite_encode_df],axis=1)
        predictions = classifier.predict_proba(feature)
        
        print('Prédiciton réalisée avec succès.')
        flash('Prédiciton réalisée avec succès.', category='success')
        return (siret,postal,agrement,l_activite,predictions)