from time import time
start_time = time()

import pandas
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

splitvar = "|"
splitvar2 = "T"
splitvar3 = "P"
splitvar4 = "SIRET"
splitvar5 = "F"
splitvar6 = "A"
splitvar7 = "J"

dataFrameBrut = pandas.read_csv('back_office_admin/donnees_brutes/export_alimconfiance.csv',sep=';')
dataFrameNettoyee = dataFrameBrut.copy()

dataFrameNettoyee.rename(columns={'APP_Libelle_etablissement':'l_etablissement','SIRET':'siret','Adresse_2_UA':'adresse'}, inplace = True)
dataFrameNettoyee.rename(columns={'Code_postal':'postal','Libelle_commune':'commune',
                                    'Numero_inspection':'n_inspection','Date_inspection':'date_insp','APP_Libelle_activite_etablissement':'l_activite',
                                    'Synthese_eval_sanit':'eval','Agrement':'agrement','geores':'geo'}, inplace=True)

dataFrameNettoyee.fillna('_',inplace=True) # Autre façon de faire -> dataFrameNettoyee.replace(numpy.nan,'_',inplace=True)
dataFrameNettoyee.drop(columns='filtre', inplace=True)

nbRow = len(dataFrameNettoyee)
for r in range(0,nbRow):
    row = dataFrameNettoyee.iloc[r]
    if row['l_activite'] == '_':
        if row['ods_type_activite'] == '_':
            row['l_activite'] = "Autres"
        else:
            row['l_activite'] = row['ods_type_activite']

dataFrameNettoyee.drop(columns='ods_type_activite',inplace=True)

print("Avant date = " + str(len(dataFrameNettoyee)))
nbRow = len(dataFrameNettoyee)
for r in range(0,nbRow):
    row = dataFrameNettoyee.iloc[r]
    lesDates = row['date_insp'].split(splitvar2)
    row['date_insp'] = lesDates[0]

print("Avant siret = " + str(len(dataFrameNettoyee)))
nbRow = len(dataFrameNettoyee)
for r in range(0,nbRow):
    row = dataFrameNettoyee.iloc[r]
    lesSiret = row['siret'].split(splitvar3)
    if len(lesSiret) > 1:
        row['siret'] = lesSiret[1]
    else:
        lesSiret = row['siret'].split(splitvar4)
        if len(lesSiret) >1:
            row['siret'] = lesSiret[1]
        else:
            lesSiret = row['siret'].split(splitvar5)
            if len(lesSiret) >1:
                row['siret'] = lesSiret[1]
            else:
                lesSiret = row['siret'].split(splitvar6)
                if len(lesSiret) >1:
                    row['siret'] = lesSiret[1]
                else:
                    lesSiret = row['siret'].split(splitvar7)
                    if len(lesSiret) >1:
                        row['siret'] = lesSiret[1]

print("Avant agrements = " + str(len(dataFrameNettoyee)))
nbRow = len(dataFrameNettoyee)
for r in range(0,nbRow):
    row = dataFrameNettoyee.iloc[r]
    row_copy = row.copy()
    str_agrement = row['agrement']
    lesAgrements = str_agrement.split(splitvar)
    if len(lesAgrements) > 1:
        row['agrement'] = lesAgrements[0]
        row_copy['agrement'] = lesAgrements[1]
        newDataFrame = pandas.DataFrame(row_copy)
        newDataFrame = pandas.DataFrame.transpose(newDataFrame)
        dataFrameNettoyee = dataFrameNettoyee.append(newDataFrame)

print("Avant activite = " + str(len(dataFrameNettoyee)))
nbRow = len(dataFrameNettoyee)
for r in range(0,nbRow):
    row = dataFrameNettoyee.iloc[r]
    str_activite = row['l_activite']
    lesActivites = str_activite.split(splitvar)
    if len(lesActivites) > 1:
        row['l_activite'] = lesActivites[0]
        for a in range(1,len(lesActivites)):
            row_copy = row.copy()
            row_copy['l_activite'] = lesActivites[a]
            nDF = pandas.DataFrame(row_copy)
            nDF = pandas.DataFrame.transpose(nDF)
            dataFrameNettoyee = dataFrameNettoyee.append(nDF)

print("Avant postal = " + str(len(dataFrameNettoyee)))
nbRow = len(dataFrameNettoyee)
for r in range(0,nbRow):
    row = dataFrameNettoyee.iloc[r]
    lesPostals = row['postal'].split()
    if len(lesPostals) > 1:
        n_postal = ""
        for c in range(0,len(lesPostals)):
            n_postal += lesPostals[c]
        row['postal'] = n_postal

dataFrameNettoyee['postal'].replace('000NR','00000', inplace=True)

print("Avant drop = " + str(len(dataFrameNettoyee)))
dataFrameNettoyee.drop_duplicates(inplace=True)
print("Finale = " + str(len(dataFrameNettoyee)))

dataFrameNettoyee.to_csv('back_office_admin/donnees_brutes/alimconfiance_propre_mieux.csv',sep=';',index=False)

print("Done")
print("--- %s seconds ---" % (time() - start_time))