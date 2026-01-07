"""The ETL module.

Look at the instructions after the statement if __name__ == "__main__":

* First, we extract the data from the input CSV files into a collection of Pandas dataframes.
  Each dataframe corresponds to a table in the target relational database.
* Then, we transform the data in the dataframes.
* Finally, we load the data into the database.

"""

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
    """Gets a date as a string in the format mm-dd-yyyy and 
    returns that date as a string in the format "dd-mm-yyyy".

    Parameters
    ----------
        input_date : string
            The input date (in the format mm-dd-yyyy)

    Returns
    -------
        A string
            The input date in the format dd-mm-yyyy, or None if the input date is null.
    """
    
    # In case we have an empty string we return None
    if pd.isnull(input_date):
        return None

    # In order to convert the input date into the right format, we can use 
    # a function that is called "strftime() that is defined in the 
    # Python module datetime.
    # Unfortunately, this function cannot directly convert a string to another string;
    # but it can convert a variable of type "datetime" to a string.
    # Therefore, we must first convert the input_date from a string to a datetime object;
    # then, we can apply the function strftime() 
    # 
    # In order to turn the input date into a datetime object, the type "datetime" provides a function
    # called strptime() that takes in two arguments:
    # 
    # * First argument: a string containing a date.
    # * Second argumnet: a string describing the format of the date given in the first argument.
    # The format must be expressed according to a well-defined code.
    # For instance:
    # * %m indicates a month as a zero-padded decimal number (01, 02, ....);
    # * %y indicates a year without century as a zero-padded decimal number (19, 20, ...99);
    # * %Y indicates a year as a decimal number (2019, 2020)...
    # 
    # The complete list of the format codes can be found at the following address:
    # https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    #
    # In the code below, the format "%m/%d/%Y" indicates that the date 
    # given in the first argument must be mm/dd/yyyy. 
    # If the date is not in this format  or the date is not valid (for instance, 
    # in the input file we find 11/31/2000), a ValueError exception is raised. 
    try:
        input_date = datetime.strptime(input_date, "%Y-%m-%d")
    except ValueError:
        return None
    
    # Now input_date is an object of type datetime.
    #  We finally convert the date to a string, enforcing the format that we want
    # that is dd/mm/yyyy.
    return input_date.strftime("%d-%m-%Y")

#Question 11
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
    r"C:\Users\gatie\Downloads\dis-2024\DIS_COM_UDI_2024.csv",
    delimiter=',',
    low_memory=False)

    prelevement = pd.read_csv(
    r"C:\Users\gatie\Downloads\dis-2024\DIS_PLV_2024.csv",
    delimiter=',',
    low_memory=False)

    resultat = pd.read_csv(
    r"C:\Users\gatie\Downloads\dis-2024\DIS_RESULT_2024.csv",
    delimiter=',',
    low_memory=False)

    print(commune)
    print(prelevement)
    print(resultat)

    ### Récupération de nos données utiles pour chaque table de notre BDD ###

    commune_df = commune[["cdreseau", "inseecommune", "nomcommune"]]
    prelevement_df = prelevement[["cdreseau", "referenceprel","dateprel","plvconformitebacterio","plvconformitechimique","plvconformitereferencebact","plvconformitereferencechim"]] 
    parametre_df = resultat[["libminparametre","cdunitereference","refqual","valtraduite","referenceprel"]] # Ici on peut avoir des duplicas car par étudiant de base mais inscription la même année et le même prix
    

    ### Ajout des dataframes pour chaque table de notre BDD dans un même dictionnaire ###

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
    dataframes["Commune"] = dataframes["Commune"].drop_duplicates()
    dataframes["Prelevement"] = dataframes["Prelevement"].drop_duplicates()
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
    for table_name, df in dataframes.items():
        df.to_sql(table_name, conn, if_exists="append", index=False)
    
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
    