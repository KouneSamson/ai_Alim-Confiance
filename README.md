# ai_Alim-Confiance

### Initialisation du Venv nécessaire :
Faites les commandes suivantes dans votre terminal bash à la racine du projet:
```bash
$ python -m venv alim_confiance_venv  
$ alim_confiance_venv/Scripts/activate.bat  
$ pip install -r requirements.txt  
```
---

### Base de données nécessaire :
L'application fonctionne sur une base de donnée MySQL en local, il est donc nécessaire que celle-ci soit initialisée avec le nom `alimconfiance`.  
Pour permettre à l'application de se connecter il faut aller dans le fichier `appli/website/__init__.py` et modifier dans la linge 12 les informations de connexion :  
`f'mysql+pymysql://root:password@localhost/{DB_NAME}'`
  > - root = l'utilisateur de la base de donné  
  > - password = le mot de passe pour s'y connecter  
  > - localhost = le chemin d'accès à la base  

---

### Appli :  
Ici se trouve les sources de l'application doccumentés, permettant de **se connecter**, **d'ajouter** des éléments en base, de la **questionner**, et **d'appliquer** un *modèles de classification* pour prédire une évalutation sanitaire pour un établissement donné.

---

### Back Office Admin :  
Regroupe les scripts de peuplement de la base de données, ainsi que l'ensemble de scripts de nettoyage des données, d'entrainement et de sauvegarde du modèle de classification. 
