import pandas as pd
import sqlite3
import os
import db
import utils
from datetime import datetime

#Fonction permettant d'avoir le bon format date
def get_right_date(input_date):
    if pd.isnull(input_date):
        return None

    try:
        input_date = datetime.strptime(input_date, "%Y-%m-%d")
    except ValueError:
        return None
    
    return input_date.strftime("%d-%m-%Y")


def extract():
    dataframes = {}

    print("Extracting the data from the input CSV files...")
    
    ### Extraction de nos données dans les trois fichiers CSV ###
    commune = pd.read_csv(
    r"data\dis-2024\DIS_COM_UDI_2024.csv",
    delimiter=',',
    low_memory=False)

    prelevement = pd.read_csv(
    r"data\dis-2024\DIS_PLV_2024.csv",
    delimiter=',',
    low_memory=False)

    resultat = pd.read_csv(
    r"data\dis-2024\DIS_RESULT_2024.csv",
    delimiter=',',
    low_memory=False)

    print(commune)
    print(prelevement)
    print(resultat)

    ### Récupération de nos données utiles pour chaque table de notre BDD ###
    reseau_df = commune[["cdreseau", "nomreseau"]]
    commune_df = commune[["cdreseau", "inseecommune", "nomcommune"]]
    prelevement_df = prelevement[["referenceprel", "cdreseau", "dateprel","plvconformitebacterio","plvconformitechimique","plvconformitereferencebact","plvconformitereferencechim"]] 
    parametre_df = resultat[["referenceprel", "libminparametre", "valtraduite", "cdunitereferencesiseeaux","refqual"]] # Ici on peut avoir des duplicas car par étudiant de base mais inscription la même année et le même prix

    ### Ajout des dataframes pour chaque table de notre BDD dans un même dictionnaire ###
    dataframes["Reseau"] = reseau_df
    dataframes["Commune"] = commune_df
    dataframes["Prelevement"] = prelevement_df
    dataframes["Parametre"] = parametre_df
    
    
    # Return the dataframe collection.
    return dataframes
    
def transform(dataframes):

    print("Transforming the data...")


    ### 1 - SUPPRESSION DES DUPLICAS DANS LES DONNEES ###
    dataframes["Reseau"] = dataframes["Reseau"].drop_duplicates(subset=["cdreseau"])
    dataframes["Commune"] = dataframes["Commune"].drop_duplicates(subset=["inseecommune"])
    dataframes["Prelevement"] = dataframes["Prelevement"].drop_duplicates(subset=["referenceprel"])
    dataframes["Parametre"] = dataframes["Parametre"].drop_duplicates()


    ### 2 - FORMATAGE DES DATES EN DD-MM-YYYY ###

    dataframes["Prelevement"]["dateprel"] = dataframes["Prelevement"]["dateprel"].map(get_right_date)
    
    print(dataframes["Prelevement"]["dateprel"])

    

    # Vérification du nombre de lignes
    print("\nLignes de chaque table pour vérifier:")
    for name, df in dataframes.items():
        print(f"{name}: {df.shape}")
    

    # Returns the dataframe collection after the transformations.
    return dataframes

def load(dataframes):
    #Nom de notre bdd
    database_file = "WaterQuality.db"

    if os.path.exists(database_file):
        #Si un fichier avec le même nom existe, on le supprime
        os.remove(database_file)
    
    # Ouverture de la connexion à notre bdd.
    conn = sqlite3.connect(database_file)

    cursor = conn.cursor()

    # Création de notre bdd
    db.create_database(conn, cursor)

    print("Loading the data into the database...")
    
    
    # Pour chaque table, on l'importe dans SQL 
    dataframes["Reseau"].to_sql("Reseau", conn, if_exists="append", index=False)
    dataframes["Commune"].to_sql("Commune", conn, if_exists="append", index=False)
    dataframes["Prelevement"].to_sql("Prelevement", conn, if_exists="append", index=False)
    dataframes["Parametre"].to_sql("Parametre", conn, if_exists="append", index=False)
        
    print("Done!")
    
    # Fermeture de la connexion à la bdd
    cursor.close()
    conn.close()

if __name__ == "__main__":

    dataframes = extract() # Extraction des données depuis un CSV
    dataframes= transform(dataframes) # Transformation des données
    load(dataframes) # Importation des données dans la BDD
   