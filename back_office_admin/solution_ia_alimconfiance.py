###########
# IMPORTS #
###########
print("Importing...")
from time import time
start_time = time()

import pickle

from numpy import ravel

from pandas import options, read_csv, DataFrame, concat
options.mode.chained_assignment = None

from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

from warnings import filterwarnings
filterwarnings("ignore", category=DeprecationWarning)
filterwarnings("ignore", category=FutureWarning)

###################################
# LECTURE ET ENCODAGE DES DONNEES # 
###################################
print("Reading...")
alim_csv = read_csv("back_office_admin/donnees_brutes/alimconfiance_propre_mieux.csv", sep=";")
alim_data = alim_csv.copy()

print("Cleaning...")
alim_data[['annee','mois','jour']] = alim_data['date_insp'].str.split("-",expand=True)

alim_data = alim_data.drop(columns=['l_etablissement','adresse','commune','n_inspection','date_insp','geo','jour','siret'])

alim_data['agrement'].replace('_',0,inplace=True)
alim_data.loc[alim_data.agrement != 0, 'agrement'] = 1

alim_data = alim_data.astype({'postal':'int64'})
alim_data = alim_data.astype({'agrement':'Int64'})
alim_data = alim_data.astype({'annee':'int64'})
alim_data = alim_data.astype({'mois':'int64'})
alim_data = alim_data.convert_dtypes()

print("Spliting...")
raw_features = alim_data.loc[:, alim_data.columns != 'eval'].copy()
raw_labels = alim_data.loc[:, alim_data.columns == 'eval'].copy()

print("Encoding...")
ohe_encoder = OneHotEncoder(sparse=False)
encoded_activity = ohe_encoder.fit_transform(DataFrame(raw_features.loc[:,'l_activite']))
encoded_activity_df = DataFrame(encoded_activity, columns=ohe_encoder.categories_)
features = concat([raw_features,encoded_activity_df],axis=1).drop('l_activite',axis=1)
labels = ravel(raw_labels)

################################################################
# DECOUPAGE DU JEU DE DONNEES EN DEUX ( ENTRAINEMENT ET TEST ) #
################################################################
print("Spliting...")
X_train, X_test, y_train, y_test = train_test_split(features,labels, test_size=0.30, random_state=666, stratify=labels)

cv_sets = StratifiedKFold(n_splits=10, shuffle=True, random_state=666)

#######################################################
# INITIALISATION DE GRID SEARCH AVEC STRATIFIED KFOLD #
#                    RANDOM FOREST                    #
#######################################################
print("RANDOM FOREST - Preparing...")
random_forest = RandomForestClassifier(bootstrap=True, n_jobs=-1)
rf_params = dict(n_estimators=range(60,86,5))

print("RANDOM FOREST - Training...")
grid_cv_rf = GridSearchCV(random_forest,rf_params,cv=cv_sets, scoring='accuracy', verbose=1)
grid_cv_rf.fit(X_train,y_train)

print("RANDOM FOREST - Extracting...")
best_rforest = grid_cv_rf.best_estimator_
best_rf_params = grid_cv_rf.best_params_
print(best_rforest)
print(best_rf_params)

#########################################
# UTILISATION DU MEILLEUR MODELE TROUVE #
#            RANDOM FOREST              #
#########################################
print("RANDOM FOREST - Evaluating...")
best_rf_pred = best_rforest.predict(X_test)
best_rf_pred_proba = best_rforest.predict_proba(X_test)
best_rf_accuracy = accuracy_score(y_test, best_rf_pred)
print('RANDOM FOREST - Accuracy : ' + str(best_rf_accuracy))
print(classification_report(y_test,best_rf_pred))
# print('RANDOM FOREST - proba :')
# print(best_rf_pred_proba)

#######################################################
# INITIALISATION DE GRID SEARCH AVEC STRATIFIED KFOLD #
#               REGRESSION LOGISTIQUE                 #
#######################################################
print("REGRESSION LOGISTIQUE - Preparing...")
logistic_regression = LogisticRegression()
lr_params = dict(penalty=['none','l2'], max_iter=range(100,151,10))

print("REGRESSION LOGISTIQUE - Training...")
grid_cv_lr = GridSearchCV(logistic_regression,lr_params,cv=cv_sets, scoring='accuracy', verbose=1)
grid_cv_lr.fit(X_train,y_train)

print("REGRESSION LOGISTIQUE - Extracting...")
best_lregression = grid_cv_lr.best_estimator_
best_lr_params = grid_cv_lr.best_params_
print(best_lregression)
print(best_lr_params)

#########################################
# UTILISATION DU MEILLEUR MODELE TROUVE #
#        REGRESSION LOGISTIQUE          #
#########################################
print("REGRESSION LOGISTIQUE - Evaluating...")
best_lr_pred = best_lregression.predict(X_test)
best_lr_pred_proba = best_lregression.predict_proba(X_test)
best_lr_accuracy = accuracy_score(y_test, best_lr_pred)
print('REGRESSION LOGISTIQUE - Accuracy : ' + str(best_lr_accuracy))
# print('REGRESSION LOGISTIQUE - proba : ')
# print(best_lr_pred_proba)

##############################################################
# SAUVEGARDE DU MEILLEUR MODELE ET DES ENCODEURS AVEC PICKLE #
##############################################################
print("Pickling...")
best_model = (best_lregression, best_rforest)[best_rf_accuracy > best_lr_accuracy]
with open('back_office_admin/alim_confiance_ai','wb') as model_file:
    pickle.dump(best_model,model_file)

with open('back_office_admin/activite_ohe_encoder','wb') as encoder_file:
    pickle.dump(ohe_encoder,encoder_file)

print("Done")
print("--- %s seconds ---" % (time() - start_time))