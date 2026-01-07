# CREATION BDD

### BIBLIOTHEQUES ###
import sqlite3
import utils

def create_database(conn, cursor):
    """Creates the WaterQuality database

    Parameters
    ----------
    conn : 
        The object used to manage the database connection.
    cursor : 
        The object used to query the database.

    Returns
    -------
    bool
        True if the database could be created, False otherwise.
    
    """

    cursor.execute("BEGIN")
    
    # Création des tables
    try:
        # Création de la table commune (attribut zone temporairement en texte pour voir délimitaion des communes)
        # Contient les communes
        print("CREATION TABLE COMMUNE")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Commune(
                id_reseau INT PRIMARY KEY,
                code_insee INT,
                nom_commune TEXT,
                zone TEXT
            )
        ''')

        # Création de la table paramètre
        # Contient les paramètres de qualité
        print("CREATION TABLE PARAMETRE")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Parametre(
                id_param INT PRIMARY KEY,
                nom_param TEXT,
                unite TEXT,
                seuil_qualite FLOAT
            )
        ''')
    
        # Création de la table prelèvement
        # Contient l'association des communes et le prélèvement de leurs paramètres ainsi que leurs conformités
        print("CREATION TABLE PRELEVEMENT")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Prelevement(
                id_reseau INT,
                id_param INT,
                date_prelev DATE,
                valeur_param FLOAT,
                conformite_bacterio TEXT, 
                conformite_chimique TEXT,
                conformite_refbact TEXT,
                conformite_refchim TEXT,
                PRIMARY KEY (id_reseau, id_param),
		        FOREIGN KEY (id_reseau) REFERENCES Commune(id_reseau),
		        FOREIGN KEY (id_param) REFERENCES Parametre(id_param)
            )
        ''')
       
        
       ###################################################################
        
    # Exception raised when something goes wrong while creating the tables.
    except sqlite3.Error as error:
        print("An error occurred while creating the tables: {}".format(error))
        # IMPORTANT : we rollback the transaction! No table is created in the database.
        conn.rollback()
        # Return False to indicate that something went wrong.
        return False

    # If we arrive here, that means that no error occurred.
    # IMPORTANT : we must COMMIT the transaction, so that all tables are actually created in the database.
    conn.commit()    
    print("Database created successfully")
    # Returns True to indicate that everything went well!
    return True

# The entry point of this module.
if __name__ == "__main__":

    # Chemin de la BDD
    db_file = "WaterQuality.db"

    # Open a connection to the database.
    conn = sqlite3.connect(db_file)

    # The cursor is used to execute queries to the database.
    cursor = conn.cursor()

    # Creates the database. THIS IS THE FUNCTION THAT YOU'LL NEED TO MODIFY
    create_database(conn, cursor)

    # Closes the connection to the database
    cursor.close()
    conn.close()