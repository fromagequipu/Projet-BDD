"""The ETL module.

Look at the instructions after the statement if __name__ == "__main__":

* First, we extract the data from the input CSV files into a collection of Pandas dataframes.
  Each dataframe corresponds to a table in the target relational database.
* Then, we transform the data in the dataframes.
* Finally, we load the data into the database.

"""
import sys
print(sys.executable)
import pandas as pd
import sqlite3
import os
import db
import utils

#The Python module datetime defines the necessary types for manipulating 
# dates and times.
# Among these types, we find one called datetime (the same name as the module) 
# that is used to express a combination of date and time. 
from datetime import datetime

def get_right_date(input_date):
    
    
    # In case we have an empty string we return None
    if pd.isnull(input_date):
        return None

   
    try:
        input_date = datetime.strptime(input_date, "%Y-%m-%d")
    except ValueError:
        return None
    
    return input_date.strftime("%d-%m-%Y")


def extract():
    """Implementation of the extraction submodule.

    Returns
    -------
    dictionary
        The collection of dataframes containing the data of the input CSV files.
        You should have as many dataframes as tables in your relational database.
        Each dataframe corresponds to a table in the relational database.
        The dictionary contains a set of key-value pairs where
            * the value is a dataframe. 
            * the key is the name of the table corresponding to the dataframe  (e.g., "Student", "EmailAddress"...)
            
    """

    # This is the dictonary containing the collection of dataframes.
    # Each item of this dictionary is a key-value pair; the key is the name of a database table;
    # the value is a Pandas dataframe with the content of the table.
    dataframes = {}

    print("Extracting the data from the input CSV files...")

    ################## TODO: COMPLETE THE CODE OF THIS FUNCTION  #####################
    
    ### Extraction de nos données dans les deux fichiers CSV ###
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
    
    ##################################################################################

    # Return the dataframe collection.
    return dataframes
    
def transform(dataframes):
    """Implementation of the transformation submodule.

    Parameters
    ----------
    dataframes : dictionary
        This is the dictionary returned by the function load()
    
    Returns 
    -------
    The input dictionary (after the transformations).
    """

    print("Transforming the data...")

    ################## TODO: COMPLETE THE CODE OF THIS FUNCTION  #####################

    ### 1 - SUPPRESSION DES DUPLICAS DANS LES DONNEES ###
    #dataframes["Commune"] = dataframes["Commune"].drop_duplicates()
    #dataframes["Prelevement"] = dataframes["Prelevement"].drop_duplicates()
    #dataframes["Parametre"] = dataframes["Parametre"].drop_duplicates()
    #dataframes["Reseau"] = dataframes["Reseau"].drop_duplicates()
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
    
    ##################################################################################

    # Returns the dataframe collection after the transformations.
    return dataframes

def load(dataframes):
    """Implementation of the load submodule.

    Parameters:
    ----------
    dataframes : dictionary
        The dictionary returned by the function extract()
    """
    # Loads the application configuration.
   

    # Gets the path to the database file.
    database_file = "WaterQuality.db"

    # You might bump into some errors while debugging your code which 
    # This might result in a database that is partially filled with some data.
    # Each time you rerun the ETL module, you want the database to be in the same state as when
    # you first created. 
    # The simpler solution here is to remove the database and recreate the tables back again.
    if os.path.exists(database_file):
        # If the database file already exists, we remove it.
        # In order to test the existence of a file, and to remove it, we use functions that are 
        # available in a Python module called "os".
        os.remove(database_file)
    
    # We open a connection to the database.
    conn = sqlite3.connect(database_file)

    # We get the cursor to query the database.
    cursor = conn.cursor()

    # We create the tables in the database, by using the function create_database that you implemented in the module
    # db.
    db.create_database(conn, cursor)

    print("Loading the data into the database...")
    
    ################## TODO: COMPLETE THE CODE OF THIS FUNCTION  #####################
    
    # Pour chaque table, on l'importe dans SQL 
    dataframes["Reseau"].to_sql("Reseau", conn, if_exists="append", index=False)
    dataframes["Commune"].to_sql("Commune", conn, if_exists="append", index=False)
    dataframes["Prelevement"].to_sql("Prelevement", conn, if_exists="append", index=False)
    dataframes["Parametre"].to_sql("Parametre", conn, if_exists="append", index=False)
    
    ##################################################################################
    
    print("Done!")
    
    # We close the connection to the database.
    cursor.close()
    conn.close()

# Entry point of the ETL module.
if __name__ == "__main__":

    ################## TODO: COMPLETE THE CODE OF THIS FUNCTION  #####################
    
    # REMOVE THIS BEFORE WRITING YOUR CODE.
    # pass is only added here to avoid the error mark that Visual Studio Code 
    # uses to indicate some missing code.
    dataframes = extract() # Extraction des données depuis un CSV
    dataframes= transform(dataframes) # Transformation des données
    load(dataframes) # Importation des données dans la BDD
    ##################################################################################
    