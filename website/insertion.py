import pandas

from . import models
from . import database

def insertion():
    alim_csv = pandas.read_csv("static/alimconfiance_propre_mieux.csv",sep=";")
    alim_df = alim_csv.copy()

    print(alim_df['l_activite'])
    

insertion()
